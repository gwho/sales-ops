/**
 * Low-level API-client mechanics shared by the three live workflow pages
 * (Phase 10) -- deliberately NOT a shared state hook. Each page owns its own
 * request/result/error state (RequestStatus, currentResult, errorDetail) and
 * calls these functions directly. See
 * docs/architect/phase-10-fastapi-integration/decisions.md #4.
 *
 * Phase 12 (docs/adr/0007-session-scoped-workflow-result-persistence.md)
 * adds the X-Session-Id header (browser-only, see lib/session-id.ts) to
 * every workflow/report request, and a dashboard read helper. Browser-only:
 * nothing in this file may run in a Server Component.
 */

import { getOrCreateSessionId } from "@/lib/session-id";
import type { DashboardLatestResults, PersistenceOutcome } from "@/types/dashboard";

// 127.0.0.1, not localhost: the FastAPI dev server binds IPv4-only, but
// /etc/hosts commonly maps "localhost" to both 127.0.0.1 and ::1 -- a browser
// that tries the IPv6 loopback first (Happy Eyeballs / RFC 8305) gets a
// connection failure before the request ever reaches the backend, since
// nothing listens on [::1]:8000. Using the literal IPv4 address removes the
// ambiguity. See docs/recover/ for the diagnosis.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

/**
 * X-Session-Id, attached only when an ID is actually available -- never an
 * empty-string header. An empty string is not the same as an absent header
 * server-side: get_session_id treats it as malformed (400), not "no session
 * yet" (see ADR 0007's "Session identity" section).
 */
function sessionHeaders(): Record<string, string> {
  const sessionId = getOrCreateSessionId();
  return sessionId ? { "X-Session-Id": sessionId } : {};
}

const NETWORK_ERROR_MESSAGE =
  "Could not reach the API server. Make sure the FastAPI backend is running and try again.";
const GENERIC_ERROR_MESSAGE = "Something went wrong processing this request. Please try again.";

/** Carries the API's business-readable `detail` string -- safe to render directly in BusinessErrorMessage. */
export class ApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseErrorDetail(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (
      typeof body === "object" &&
      body !== null &&
      "detail" in body &&
      typeof (body as { detail: unknown }).detail === "string"
    ) {
      return (body as { detail: string }).detail;
    }
  } catch {
    // Response wasn't JSON -- fall through to the generic message.
  }
  return GENERIC_ERROR_MESSAGE;
}

async function postFormData(path: string, formData: FormData): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      body: formData,
      headers: sessionHeaders(),
    });
  } catch {
    throw new ApiError(NETWORK_ERROR_MESSAGE);
  }

  if (!response.ok) {
    throw new ApiError(await parseErrorDetail(response));
  }

  return response;
}

export type WorkflowResponse<T> = {
  data: T;
  /** X-Persisted from the response -- see ADR 0007. Defaults to "skipped"
   * only if the header is somehow missing entirely (older/report responses
   * never carry it, but postJSON is only ever called for workflow
   * endpoints, which always set it). */
  persisted: PersistenceOutcome;
};

/** POST a Workflow Request, returning the parsed Workflow Result JSON plus its Persistence Outcome. */
export async function postJSON<T>(path: string, formData: FormData): Promise<WorkflowResponse<T>> {
  const response = await postFormData(path, formData);
  const data = (await response.json()) as T;
  const persisted = (response.headers.get("x-persisted") as PersistenceOutcome | null) ?? "skipped";
  return { data, persisted };
}

export type ReportDownload = {
  blob: Blob;
  filename: string;
  reportId: string | null;
  generatedAt: string | null;
};

function parseFilename(contentDisposition: string | null, fallback: string): string {
  if (!contentDisposition) return fallback;
  const match = /filename="?([^";]+)"?/.exec(contentDisposition);
  return match?.[1] ?? fallback;
}

/** POST a Report Export Request, returning the .xlsx blob plus its download metadata. */
export async function postReport(
  path: string,
  formData: FormData,
  fallbackFilename: string,
): Promise<ReportDownload> {
  const response = await postFormData(path, formData);
  const blob = await response.blob();
  return {
    blob,
    filename: parseFilename(response.headers.get("content-disposition"), fallbackFilename),
    reportId: response.headers.get("x-report-id"),
    generatedAt: response.headers.get("x-generated-at"),
  };
}

/** Trigger a browser download for an already-fetched blob (the Report Artifact). */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/** GET URL for an allowlisted Sample File download -- a plain browser navigation, no fetch/CORS involved. */
export function getSampleFileUrl(templateName: string): string {
  return `${API_BASE_URL}/api/templates/${templateName}`;
}

/**
 * Fetch an allowlisted Sample File and wrap it as a File, for the "Run sample
 * data" action -- the fetched File is submitted through the exact same
 * FormData path as a manually uploaded one. Unlike getSampleFileUrl (a plain
 * browser navigation), this is a real cross-origin fetch and goes through the
 * same CORS/error handling as postJSON/postReport.
 */
export async function fetchSampleFile(templateName: string, filename: string): Promise<File> {
  let response: Response;
  try {
    response = await fetch(getSampleFileUrl(templateName));
  } catch {
    throw new ApiError(NETWORK_ERROR_MESSAGE);
  }

  if (!response.ok) {
    throw new ApiError(await parseErrorDetail(response));
  }

  const blob = await response.blob();
  return new File([blob], filename, { type: blob.type });
}

/**
 * GET the session's Dashboard Latest Results. Browser-only (reads the
 * Anonymous Session ID from localStorage) -- must only ever be called from a
 * Client Component, never a Server Component render (see ADR 0007's
 * "Frontend read boundary" section for why). A 503 (genuine database
 * outage, distinct from "nothing saved yet") surfaces the same as any other
 * ApiError -- the backend's `detail` message already distinguishes it in
 * business-readable terms, so no separate handling is needed here.
 */
export async function getDashboardResults(): Promise<DashboardLatestResults> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/dashboard`, { headers: sessionHeaders() });
  } catch {
    throw new ApiError(NETWORK_ERROR_MESSAGE);
  }

  if (!response.ok) {
    throw new ApiError(await parseErrorDetail(response));
  }

  return (await response.json()) as DashboardLatestResults;
}
