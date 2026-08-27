# Codebase Audit Skill — Reference: Bug Patterns Cheatsheet

This file is loaded on demand. Read it when you need a deeper checklist of patterns to look for during Phase 2 (Systematic Bug Hunt).

## Table of Contents

1. [Runtime Error Patterns](#1-runtime-error-patterns)
2. [Logic Bug Patterns](#2-logic-bug-patterns)
3. [State Management Anti-Patterns](#3-state-management-anti-patterns)
4. [Async & Concurrency Pitfalls](#4-async--concurrency-pitfalls)
5. [API & Backend Mismatches](#5-api--backend-mismatches)
6. [Database & Data Integrity Risks](#6-database--data-integrity-risks)
7. [Authentication & Authorization Holes](#7-authentication--authorization-holes)
8. [Edge Case Checklist](#8-edge-case-checklist)

---

## 1. Runtime Error Patterns

- Accessing `.length`, `.map`, `.forEach`, `.then`, `.catch` on a possibly-undefined value.
- `JSON.parse` without try/catch on user-supplied or API-supplied strings.
- `localStorage.getItem(...)` returning `null` then `.split()` / `.startsWith()` blowing up.
- Forgetting `await` (returns a Promise instead of the value; downstream code silently uses a Promise object).
- Mixing default and named imports (`import Foo from` vs `import { Foo } from`).
- Circular imports causing `undefined` at module-eval time.
- `process.env.X` assumed to be defined — crashes when missing.
- Calling a hook conditionally or inside a loop (React rules of hooks violation).
- `parseInt(x)` without radix, or `parseInt("0x10")` surprises.
- Floating point comparisons (`0.1 + 0.2 === 0.3` is `false`).

## 2. Logic Bug Patterns

- Off-by-one in loops (`<` vs `<=`).
- `===` vs `==` mistakes, especially with `null`/`undefined`/`0`/`""`.
- Negation precedence: `!a === b` parses as `(!a) === b`, not `!(a === b)`.
- Short-circuit side effects: `a && b()` — `b()` never runs if `a` is falsy.
- Truthy traps: `0`, `""`, `false`, `null`, `undefined`, `NaN` are all falsy.
- `Array.sort()` default lexicographic order (`[10, 2, 1].sort()` → `[1, 10, 2]`).
- Mutating shared arrays/objects passed as arguments.
- `switch` without `break` (fall-through bugs).
- `for...in` over arrays (iterates string keys, includes prototype chain).
- `Object.keys` ordering assumption (insertion order for string keys, numeric order for integer-like keys).
- Timezone bugs: `new Date("2024-01-01")` parsed as UTC vs local time depending on format.
- `setTimeout(0)` race with state update.

## 3. State Management Anti-Patterns

- Direct state mutation: `state.foo = bar` instead of `setState({...state, foo: bar})`.
- Stale closure in `setInterval` / `setTimeout` callbacks referencing old state.
- `useEffect` with missing or wrong dependency arrays.
- `useEffect` without cleanup → subscription leak, memory leak, "setState on unmounted component".
- Multiple `setState` calls in a row relying on previous state — use the updater form `setState(prev => ...)`.
- Optimistic UI update that isn't rolled back on API failure.
- Form state reset on prop change forgotten → stale form after navigation.
- Cached/derived value stored in state instead of computed each render.
- `localStorage` / `sessionStorage` write without JSON.stringify, or read without JSON.parse + null guard.
- IndexedDB / Zustand / Redux store mutations that bypass the dispatch path.

## 4. Async & Concurrency Pitfalls

- Promise.all rejecting on first failure (use Promise.allSettled when partial success is OK).
- No request cancellation on unmount → old response overwrites new state.
- `await` inside a loop when `Promise.all` would do.
- Forgetting `await` before an async call → unhandled promise rejection swallowed.
- `.then().catch()` chains where catch returns `undefined` and downstream breaks.
- Race: two parallel requests, the older one resolves last and overwrites the new state.
- Debounce/throttle missing on rapid input (search-as-you-type, button mashing).
- Retry without backoff → thundering herd on a recovering backend.
- Retry without cap → infinite retry loop.
- Mutex / lock missing on a shared resource (file write, DB row update).
- Web Worker posting messages while worker is still busy → message queue storm.

## 5. API & Backend Mismatches

- Frontend expects `data.results` but backend returns `data.items` (or `data.data`).
- Frontend expects array but backend returns `{ results: [] }` or `null` on empty.
- Frontend expects `200 OK` but backend returns `201 Created` (or `204 No Content`).
- Auth header format mismatch: `Bearer <token>` vs `<token>` vs `Token <token>`.
- Content-Type mismatch — `application/json` body sent as form-encoded.
- CORS preflight failing because custom header not allowed by backend.
- CSRF token missing or stale.
- Pagination: zero-indexed vs one-indexed page numbers.
- Date format mismatch: ISO 8601 vs unix seconds vs unix millis.
- Number precision: backend returns `123456789012345678` as a number, JS truncates to float.
- Enum case sensitivity: backend `"ACTIVE"` vs frontend `"active"`.
- Error response shape: backend returns `{ error: { code, message } }` but frontend reads `error.message` from a top-level `error` string.
- Missing 404/401/403 handling → silent failures, infinite spinners.

## 6. Database & Data Integrity Risks

- Update without `WHERE` clause (or with a wrong WHERE).
- Delete cascade not configured → orphaned records.
- Missing unique constraint → duplicate inserts on retry.
- Missing transaction around multi-step write → partial commit on failure.
- `SELECT ... LIMIT 1` returning null but code assumes a row exists.
- N+1 query patterns (loop with a query inside).
- SQL injection via string concatenation (`"... WHERE name = '" + input + "'"`).
- ORM `update` silently dropping fields not in the schema.
- Migration that doesn't backfill existing rows.
- Optimistic concurrency: no `version` field → lost updates when two users edit the same row.
- Time field stored as string instead of timestamp → range queries break.
- Float used for monetary values (use decimal/cents).

## 7. Authentication & Authorization Holes

- Token in `localStorage` (XSS-vulnerable) instead of httpOnly cookie.
- Token in URL query string (logged in server logs, referrer headers).
- No expiry check on JWT — token works forever.
- Refresh token rotation missing → stolen refresh token works forever.
- Logout doesn't invalidate server-side session.
- Client-side route guards with no server-side authorization (any user can call any API).
- IDOR: `/api/users/123/orders` — user can change `123` to `124` and see someone else's data.
- Mass assignment: `User.update(req.body)` lets user set `role: 'admin'`.
- Password reset token reusable after use.
- Password reset token never expires.
- Email verification not enforced for sensitive actions.
- Admin endpoints exposed under user routes by accident.

## 8. Edge Case Checklist

- Empty array / empty object / empty string
- `null` vs `undefined` vs `NaN` vs `0` vs `false`
- Very large numbers (exceeds `Number.MAX_SAFE_INTEGER`)
- Very long strings (memory, UI overflow)
- Unicode: emoji length, combining characters, RTL text, zero-width chars
- Duplicate submissions (double-click, refresh during submit, network retry)
- Slow network → loading state must be visible, optimistic UI must be reversible
- Offline mode → queued writes, conflict resolution
- Page refresh mid-operation
- Multiple tabs editing the same record
- User navigating away during async operation
- Daylight saving time transitions
- Leap year (Feb 29)
- Timezone differences between client and server
- Concurrent edits to the same record (lost update)
- Back button after logout
- Deep linking into a page that requires auth
- Copy-paste with trailing whitespace
- File upload with weird MIME type or extension mismatch
- File upload with 0 bytes
- Concurrent requests modifying the same DB row
