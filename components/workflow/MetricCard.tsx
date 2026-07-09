// Internal imports
import { Card } from "@/components/ui/Card";

// Types
type MetricCardProps = {
  label: string;
  value: string | number;
};

// Component
export function MetricCard({ label, value }: MetricCardProps) {
  return (
    <Card className="flex flex-col gap-1 p-4">
      <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">{label}</span>
      <span className="text-2xl font-semibold text-text-primary">{value}</span>
    </Card>
  );
}
