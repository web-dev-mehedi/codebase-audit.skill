// React dashboard — audited and hardened by codebase-audit skill.
//
// Original planted bugs (all fixed below):
//   1. Race condition: fetch in useEffect without AbortController + no
//      cleanup. Clicking sidebar items quickly showed stale data then crashed
//      with "Cannot read property map of undefined".
//   2. Search-as-you-type: no debounce, no cancellation — last responder won.
//   3. Stale closure: setTimeout in handleSubmit captured an old `items`.
//   4. Direct state mutation: results.push() mutated the API response array.
//   5. Missing dependency: `selectedId` was not in the data-effect dep array,
//      so the effect never re-fired when the user picked a new sidebar item.
//   6. useState initialized from localStorage without try/catch — corrupt
//      storage (or unavailable storage) crashed the app on mount.
//   7. No error UI: a failed fetch left `loading` true forever.
//
// Additional issues found during the audit and fixed:
//   8. `data.items.map(...)` threw whenever `data` was null or the response
//      shape didn't include `items` (the user-reported crash site).
//   9. Initial fetch fired `/items/null` because selectedId started at null
//      and the effect didn't guard against it.
//  10. Search query was not URL-encoded, so special characters produced
//      malformed requests.
//  11. Search results were not cleared when the query shrank below the
//      minimum length, leaving stale results on screen.
//  12. Sidebar / SearchBox had no TypeScript prop types (the file is .tsx).

import React, { useState, useEffect, useRef, useCallback } from 'react';

type Item = { id: string | number; name: string };
type SearchResult = { id: string | number; name: string };

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:3000/api';

export function Dashboard() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [data, setData] = useState<{ items?: Item[]; error?: string } | null>(
    null,
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);

  const [items] = useState<Item[]>(() => {
    // FIX (BUG 6): wrap localStorage + JSON.parse in try/catch so corrupt
    // storage (or unavailable storage, e.g. private mode / SSR) cannot crash
    // the app on mount. Fall back to an empty list.
    try {
      const stored = localStorage.getItem('cachedItems');
      const parsed = stored ? JSON.parse(stored) : null;
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  });

  // Keep a ref of the latest `items` so deferred callbacks (handleSubmit's
  // setTimeout) always read the current value instead of a stale snapshot.
  const itemsRef = useRef(items);
  useEffect(() => {
    itemsRef.current = items;
  }, [items]);

  // FIX (BUGS 1, 5, 9 + crash site): include `selectedId` in the dependency
  // array so the effect actually re-fires when the user picks a sidebar item,
  // skip when nothing is selected yet, and use an AbortController + cleanup
  // so a slow response from a previous selection cannot overwrite the current
  // one (the root cause of the "data from the previous item" flake).
  useEffect(() => {
    if (selectedId === null) return;

    const controller = new AbortController();
    setLoading(true);
    setError(null);

    fetch(`${API_BASE}/items/${selectedId}`, { signal: controller.signal })
      .then(res => {
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        return res.json();
      })
      .then(json => {
        if (controller.signal.aborted) return;
        setData(json);
        setLoading(false);
      })
      .catch(err => {
        // Ignore AbortError — that's the expected path when a newer fetch
        // supersedes this one (or the component unmounted).
        if (controller.signal.aborted) return;
        setError(err?.message || 'Failed to load data');
        setLoading(false);
      });

    return () => controller.abort();
  }, [selectedId]);

  // FIX (BUGS 2, 4, 10, 11): debounce the query (no fetch per keystroke),
  // abort in-flight search requests when the query changes (no last-responder
  // race), clear stale results when the query is too short, URL-encode the
  // query, and never mutate the API response array.
  useEffect(() => {
    const trimmed = searchQuery.trim();
    if (trimmed.length < 2) {
      setSearchResults([]);
      return;
    }

    const controller = new AbortController();
    const debounceId = window.setTimeout(() => {
      fetch(`${API_BASE}/search?q=${encodeURIComponent(trimmed)}`, {
        signal: controller.signal,
      })
        .then(res => {
          if (!res.ok) throw new Error(`Search failed: ${res.status}`);
          return res.json();
        })
        .then(json => {
          if (controller.signal.aborted) return;
          const results: SearchResult[] = Array.isArray(json?.results)
            ? json.results
            : [];
          // Immutable update — never mutate the API response array in place.
          setSearchResults([
            ...results,
            { id: 'debug', name: 'DEBUG ENTRY' },
          ]);
        })
        .catch(err => {
          if (controller.signal.aborted) return;
          // Swallow search errors but don't leave stale results on screen.
          setSearchResults([]);
        });
    }, 250);

    return () => {
      window.clearTimeout(debounceId);
      controller.abort();
    };
  }, [searchQuery]);

  const handleSubmit = useCallback(() => {
    // FIX (BUG 3): read the latest items from a ref instead of capturing the
    // items snapshot at call time. The setTimeout closure now sees whatever
    // `items` is when the timeout fires, not what it was 500ms earlier.
    // Also guard localStorage write in try/catch (quota / private mode).
    window.setTimeout(() => {
      try {
        localStorage.setItem('cachedItems', JSON.stringify(itemsRef.current));
      } catch {
        // Storage may be unavailable or full; ignore — caching is best-effort.
      }
    }, 500);
  }, []);

  return (
    <div className="dashboard">
      <Sidebar selectedId={selectedId} onSelect={setSelectedId} />
      <main>
        {loading && <Spinner />}
        {error && <div className="error">{error}</div>}
        {/* FIX (BUG 8): defensively guard `data.items` so an unexpected
            response shape (e.g. `{ error: 'not found' }`) or a still-null
            `data` cannot throw "Cannot read property map of undefined".
            Using `data?.items ?? []` is narrowing-safe under strict TS. */}
        <ul>
          {(data?.items ?? []).map(item => (
            <li key={item.id}>{item.name}</li>
          ))}
        </ul>
        <SearchBox
          query={searchQuery}
          onQueryChange={setSearchQuery}
          results={searchResults}
        />
        <button onClick={handleSubmit}>Save</button>
      </main>
    </div>
  );
}

function Sidebar({
  selectedId,
  onSelect,
}: {
  selectedId: number | null;
  onSelect: (id: number) => void;
}) {
  return (
    <aside>
      <button onClick={() => onSelect(1)}>Item 1</button>
      <button onClick={() => onSelect(2)}>Item 2</button>
    </aside>
  );
}

function SearchBox({
  query,
  onQueryChange,
  results,
}: {
  query: string;
  onQueryChange: (q: string) => void;
  results: SearchResult[];
}) {
  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={e => onQueryChange(e.target.value)}
        placeholder="Search..."
      />
      <ul>
        {results.map(r => (
          <li key={r.id}>{r.name}</li>
        ))}
      </ul>
    </div>
  );
}

function Spinner() {
  return <div className="spinner">Loading...</div>;
}
