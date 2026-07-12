/**
 * Low-level API-client mechanics shared by the three live workflow pages
 * (Phase 10) -- deliberately NOT a shared state hook. Each page owns its own
 * request/result/error state (RequestStatus, currentResult, errorDetail) and
 * calls these functions directly. See
 * docs/architect/phase-10-fastapi-integration/decisions.md #4.
 */

// 127.0.0.1, not localhost: the FastAPI dev server binds IPv4-only, but
// /etc/hosts commonly maps "localhost" to both 127.0.0.1 and ::1 -- a browser
// that tries the IPv6 loopback first (Happy Eyeballs / RFC 8305) gets a
// connection failure before the request ever reaches the backend, since
// nothing listens on [::1]:8000. Using the literal IPv4 address removes the
// ambiguity. See docs/recover/ for the diagnosis.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

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
    response = await fetch(`${API_BASE_URL}${path}`, { method: "POST", body: formData });
  } catch {
    throw new ApiError(NETWORK_ERROR_MESSAGE);
  }

  if (!response.ok) {
    throw new ApiError(await parseErrorDetail(response));
  }

  return response;
}

/** POST a Workflow Request, returning the parsed Workflow Result JSON. */
export async function postJSON<T>(path: string, formData: FormData): Promise<T> {
  const response = await postFormData(path, formData);
  return (await response.json()) as T;
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
