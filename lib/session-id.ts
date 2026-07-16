/**
 * Anonymous Session ID -- a UUID generated once in the browser and stored in
 * localStorage, sent as the X-Session-Id header on workflow/report requests
 * (see docs/adr/0007-session-scoped-workflow-result-persistence.md). No
 * cookies, no authentication -- this identifies a browser profile only.
 *
 * Browser-only. Never call this from a Server Component or any server-side
 * fetch -- localStorage doesn't exist there, and session identity is
 * deliberately client-only (see ADR 0007's "Frontend read boundary" section
 * on why the dashboard's live sections are a Client Component, not an RSC).
 */

const STORAGE_KEY = "salesOpsAnonymousSessionId";

/**
 * Returns the existing Anonymous Session ID, creating and persisting a new
 * one on first use. Always returns a non-empty string -- callers (see
 * lib/api-client.ts) must still omit the X-Session-Id header entirely if
 * this ever can't run (no window/localStorage), rather than sending an
 * empty string, which the backend treats as malformed, not absent.
 */
export function getOrCreateSessionId(): string | null {
  if (typeof window === "undefined") return null;

  try {
    const existing = window.localStorage.getItem(STORAGE_KEY);
    if (existing) return existing;

    const created = crypto.randomUUID();
    window.localStorage.setItem(STORAGE_KEY, created);
    return created;
  } catch {
    // Storage unavailable (private browsing, quota, etc.) -- fall back to no
    // session identity for this request rather than throwing.
    return null;
  }
}
