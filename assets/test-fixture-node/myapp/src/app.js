// Node.js Express API — hardened via the codebase-audit skill.
//
// Fixes applied (each maps to a BUG-### in the engineering report):
//   1.  SQL injection        — getUserByEmail now parameterized.
//   2.  Unhandled rejections — asyncHandler wraps every async route so errors
//                               flow into Express' error chain instead of
//                               crashing the process.
//   3.  No error middleware  — 4-arg error middleware registered last; plus
//                               a 404 catch-all.
//   4.  Mass assignment      — PUT /api/users/:id allowlists fields only.
//   5.  IDOR                 — auth + requireOwnership middleware on
//                               /api/users/:id routes.
//   6.  Missing validation  — email/password validated before DB hit.
//   7.  No rate limiting     — in-memory limiter on /login and /password-reset.
//   8.  Hardcoded JWT secret — read from env; fail-fast in production.
//   9.  Reset token no exp  — 15-minute expiry added.
//  10.  Pool connection leak — try/finally guarantees release().
//
// Additional hardening found during the audit:
//  11. POST /api/password-reset crashed when email was unknown (user.id on
//      undefined) — now handled gracefully without leaking account existence.
//  12. Global process.on('unhandledRejection' / 'uncaughtException') safety
//      nets added — directly addresses the production crash complaint.
//  13. express.json() now capped at 1mb to mitigate large-payload DoS.
//  14. POST /api/orders mass-assignment + user_id spoofing — payload is
//      allowlisted and user_id is bound to the authenticated user.
//  15. Server 'error' handler + graceful SIGTERM/SIGINT shutdown that
//      drains the DB pool before exit.

const express = require('express');
const mysql = require('mysql2/promise');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json({ limit: '1mb' })); // BUG-013: cap body size.

// ----------------------------------------------------------------------------
// Configuration
// ----------------------------------------------------------------------------

// BUG-008 fix: JWT secret must come from the environment. Fail-fast in
// production; warn loudly in dev.
const JWT_SECRET_RAW = process.env.JWT_SECRET;
if (!JWT_SECRET_RAW || String(JWT_SECRET_RAW).length < 32) {
  if (process.env.NODE_ENV === 'production') {
    // Failing fast here is strictly safer than running with a guessable secret.
    throw new Error(
      'FATAL: JWT_SECRET must be set in the environment and be at least 32 characters long.'
    );
  }
  console.warn(
    '[security] JWT_SECRET missing or <32 chars — using insecure dev-only fallback. ' +
      'Set JWT_SECRET in the environment before deploying.'
  );
}
const JWT_SECRET = JWT_SECRET_RAW || 'dev-only-insecure-secret-please-set-JWT_SECRET-32chars';

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'myapp',
  connectionLimit: 10,
  waitForConnections: true,
});

// ----------------------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------------------

// BUG-002 fix: forwards async errors to Express' error chain via next(err).
// Used to wrap every async route handler so a rejected promise never becomes
// an unhandled rejection that crashes the process.
function asyncHandler(fn) {
  return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}

// Minimal email validator — no new dependencies.
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
function isValidEmail(email) {
  return typeof email === 'string' && email.length <= 254 && EMAIL_RE.test(email);
}

// BUG-004 / BUG-014 fix: copy only allowlisted fields from an arbitrary
// object — defends against mass assignment.
function pickAllowed(body, allowed) {
  const out = {};
  for (const key of allowed) {
    if (Object.prototype.hasOwnProperty.call(body, key)) {
      out[key] = body[key];
    }
  }
  return out;
}

// BUG-007 fix: in-memory sliding-window rate limiter (no new deps).
// NOTE: per-process only — see "Remaining Issues" for multi-instance caveat.
function makeRateLimiter({ windowMs, max }) {
  const hits = new Map(); // key -> [timestamp, ...]
  return function rateLimit(req, res, next) {
    const ip = req.ip || (req.socket && req.socket.remoteAddress) || 'unknown';
    const email = (req.body && req.body.email) || '';
    const key = `${ip}:${email}`;
    const now = Date.now();
    const arr = (hits.get(key) || []).filter((t) => now - t < windowMs);
    if (arr.length >= max) {
      res.setHeader('Retry-After', Math.ceil(windowMs / 1000));
      return res.status(429).json({ error: 'Too many attempts. Try again later.' });
    }
    arr.push(now);
    hits.set(key, arr);
    next();
  };
}

const loginLimiter = makeRateLimiter({ windowMs: 15 * 60 * 1000, max: 5 });
const resetLimiter = makeRateLimiter({ windowMs: 15 * 60 * 1000, max: 3 });

// BUG-005 fix: verifies Bearer JWT and attaches req.user.
function auth(req, res, next) {
  const header = req.headers.authorization || '';
  const tokenMatch = /^Bearer\s+(.+)$/.exec(header);
  if (!tokenMatch) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  try {
    req.user = jwt.verify(tokenMatch[1], JWT_SECRET);
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
  next();
}

// BUG-005 fix: the authenticated user must match the :id param.
function requireOwnership(req, res, next) {
  const paramId = String(req.params.id);
  const userId = req.user && String(req.user.id);
  if (!userId || userId !== paramId) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  next();
}

// BUG-001 fix: parameterized query — no string concatenation.
async function getUserByEmail(email) {
  const [rows] = await pool.query(
    'SELECT * FROM users WHERE email = ?',
    [email]
  );
  return rows[0];
}

// ----------------------------------------------------------------------------
// Routes
// ----------------------------------------------------------------------------

// BUG-002 / BUG-006 / BUG-007 fix: try/catch via asyncHandler, input
// validation, and rate limiting on login.
app.post('/api/login', loginLimiter, asyncHandler(async (req, res) => {
  const { email, password } = req.body || {};

  // BUG-006 fix: validate before hitting the DB.
  if (!isValidEmail(email) || typeof password !== 'string' || password.length === 0) {
    return res.status(400).json({ error: 'Valid email and password are required' });
  }

  const user = await getUserByEmail(email); // parameterized — no SQLi
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // NOTE: plaintext password comparison is a pre-existing issue NOT in scope
  // for this audit; see "Remaining Issues" for the recommended bcrypt upgrade.
  if (user.password !== password) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Token now also expires (login session expiry).
  const token = jwt.sign(
    { id: user.id, email: user.email },
    JWT_SECRET,
    { expiresIn: '1h' }
  );
  res.json({ token });
}));

// BUG-004 fix: allowlist fields; never let role/id/password/is_verified flow
// through req.body. Also BUG-005: protected by auth + ownership.
app.put('/api/users/:id', auth, requireOwnership, asyncHandler(async (req, res) => {
  const { id } = req.params;
  const allowed = pickAllowed(req.body || {}, ['name', 'email']);
  if (Object.keys(allowed).length === 0) {
    return res.status(400).json({ error: 'No updatable fields supplied' });
  }
  if (allowed.email !== undefined && !isValidEmail(allowed.email)) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  await pool.query('UPDATE users SET ? WHERE id = ?', [allowed, id]);
  res.json({ success: true });
}));

// BUG-005 fix: auth + ownership required before querying orders.
app.get('/api/users/:id/orders', auth, requireOwnership, asyncHandler(async (req, res) => {
  const { id } = req.params;
  const [rows] = await pool.query('SELECT * FROM orders WHERE user_id = ?', [id]);
  res.json(rows);
}));

// BUG-010 fix: connection released in finally — no leak even on INSERT
// failure. BUG-014 fix: payload allowlisted; user_id bound to the
// authenticated user, never to req.body.
app.post('/api/orders', auth, asyncHandler(async (req, res) => {
  const userId = req.user.id;
  const payload = pickAllowed(req.body || {}, ['product_id', 'quantity']);
  if (
    payload.product_id === undefined ||
    !Number.isInteger(payload.quantity) ||
    payload.quantity <= 0
  ) {
    return res.status(400).json({ error: 'Valid product_id and quantity are required' });
  }
  payload.user_id = userId; // bind to authenticated user, not req.body

  let conn;
  try {
    conn = await pool.getConnection();
    const [result] = await conn.query('INSERT INTO orders SET ?', payload);
    res.json({ id: result.insertId });
  } finally {
    if (conn) {
      try { conn.release(); } catch (e) { console.error('[release error]', e); }
    }
  }
}));

// BUG-009 fix: reset token now expires in 15 minutes. BUG-011 fix: unknown
// email no longer crashes; same response returned regardless to prevent
// account enumeration. BUG-007 fix: rate-limited.
app.post('/api/password-reset', resetLimiter, asyncHandler(async (req, res) => {
  const { email } = req.body || {};
  if (!isValidEmail(email)) {
    return res.status(400).json({ error: 'Valid email is required' });
  }

  const user = await getUserByEmail(email);
  if (user) {
    // Token expires — mitigates stolen-token reuse.
    const resetToken = jwt.sign(
      { id: user.id, purpose: 'password_reset' },
      JWT_SECRET,
      { expiresIn: '15m' }
    );
    // TODO: send email containing a link with `resetToken`. Do NOT return
    // the token in the HTTP response.
    void resetToken; // referenced for clarity; email send is mocked.
  }
  res.json({ message: 'Reset link sent' });
}));

// ----------------------------------------------------------------------------
// Global error handling
// ----------------------------------------------------------------------------

// 404 catch-all for unmatched routes (previously Express' default HTML 404).
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// BUG-003 fix: 4-arg error middleware, registered LAST. Catches anything
// forwarded via next(err) — including rejections surfaced by asyncHandler.
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  console.error('[unhandled error]', err);
  if (res.headersSent) return; // Express will close the response itself.
  // Never leak internal error details to clients.
  if (err && err.code && String(err.code).startsWith('ER_')) {
    return res.status(500).json({ error: 'Database error' });
  }
  res.status(500).json({ error: 'Internal server error' });
});

// BUG-012 fix: global safety nets. Directly addresses the production
// "unhandled promise rejection" crash complaint.
process.on('unhandledRejection', (reason) => {
  // Route handlers should never reach here — asyncHandler routes errors to
  // the Express error middleware. If this fires, log and continue serving
  // rather than terminating (Node's default since v15).
  console.error('[unhandledRejection]', reason);
});

process.on('uncaughtException', (err) => {
  // Process state may be corrupted after an uncaught exception — exit and
  // let the orchestrator (PM2, systemd, k8s, Docker restart policy) restart
  // cleanly. This is the documented safe practice.
  console.error('[uncaughtException]', err);
  process.exit(1);
});

// BUG-015 fix: server error handler + graceful shutdown that drains the
// DB pool before exiting.
const server = app.listen(3000, () => console.log('Server on :3000'));
server.on('error', (err) => {
  console.error('[server error]', err);
  process.exit(1);
});

function shutdown(signal) {
  console.log(`Received ${signal}, shutting down...`);
  server.close(() => {
    pool.end().then(() => {
      console.log('Closed HTTP server and DB pool');
      process.exit(0);
    }).catch((e) => {
      console.error('Error closing DB pool', e);
      process.exit(1);
    });
  });
  // Force-exit after 10s if draining hangs.
  setTimeout(() => process.exit(1), 10000).unref();
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
