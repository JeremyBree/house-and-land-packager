import { Card, CardContent, CardHeader } from '@/components/ui/card'
import type { ConflictRead } from '@/api/types'

const SEVERITY_BADGE: Record<string, string> = {
  high: 'bg-amber-100 text-amber-800',
  critical: 'bg-red-100 text-red-800',
}

const TYPE_LABEL: Record<string, string> = {
  'design-facade': 'Design + Facade',
  'design-facade-colour': 'Design + Facade + Colour',
}

interface ConflictCardProps {
  conflict: ConflictRead
}

export function ConflictCard({ conflict }: ConflictCardProps) {
  const { package_a, package_b, severity, conflict_type, lot_numbers } = conflict

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${SEVERITY_BADGE[severity] ?? 'bg-secondary'}`}
          >
            {severity}
          </span>
          <span className="text-sm text-muted-foreground">
            {TYPE_LABEL[conflict_type] ?? conflict_type}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <PackageColumn label="Package A" pkg={package_a} />
          <PackageColumn label="Package B" pkg={package_b} />
        </div>
        <div className="mt-3 rounded-md bg-muted px-3 py-2 text-sm text-muted-foreground">
          Rule: Lots {lot_numbers.join(' & ')} cannot share {TYPE_LABEL[conflict_type]?.toLowerCase() ?? conflict_type}
        </div>
      </CardContent>
    </Card>
  )
}

function PackageColumn({ label, pkg }: { label: string; pkg: ConflictRead['package_a'] }) {
  return (
    <div>
      <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
      <dl className="space-y-1 text-sm">
        <div className="flex justify-between">
          <dt className="text-muted-foreground">Lot</dt>
          <dd className="font-medium">{pkg.lot_number}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-muted-foreground">Design</dt>
          <dd>{pkg.design}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-muted-foreground">Facade</dt>
          <dd>{pkg.facade}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-muted-foreground">Colour</dt>
          <dd>{pkg.colour_scheme ?? '-'}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-muted-foreground">Brand</dt>
          <dd>{pkg.brand}</dd>
        </div>
      </dl>
    </div>
  )
}
