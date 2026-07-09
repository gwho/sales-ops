// Internal imports
import { ReportCard } from "@/components/workflow/ReportCard";
import { reportManifests } from "@/lib/mock-data";

// Component
export default function ReportsPage() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <h1 className="text-2xl font-semibold text-text-primary">Reports &amp; Export</h1>
      <p className="mt-2 text-sm text-text-secondary">
        One report per workflow, generated from this session&apos;s results.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {reportManifests.map((manifest) => (
          <ReportCard key={manifest.report_id} state="Ready" manifest={manifest} />
        ))}
      </div>
    </div>
  );
}
