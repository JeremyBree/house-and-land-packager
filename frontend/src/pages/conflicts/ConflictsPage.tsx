import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CheckCircle2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageHeader } from '@/components/common/PageHeader'
import { ConflictCard } from './ConflictCard'
import { listConflicts, getConflictSummary } from '@/api/conflicts'
import { listEstates } from '@/api/estates'

export default function ConflictsPage() {
  const [estateFilter, setEstateFilter] = useState<number | ''>('')

  const { data: summary } = useQuery({
    queryKey: ['conflicts-summary'],
    queryFn: getConflictSummary,
  })

  const { data: conflicts, isLoading } = useQuery({
    queryKey: ['conflicts', { estate_id: estateFilter || undefined }],
    queryFn: () => listConflicts(estateFilter || undefined),
  })

  const { data: estatesData } = useQuery({
    queryKey: ['estates', { page: 1, size: 200 }],
    queryFn: () => listEstates({ page: 1, size: 200 }),
  })

  const totalConflicts = summary?.total_conflicts ?? 0

  return (
    <div>
      <PageHeader
        title="Conflicts"
        description="Clash rule violations across packages."
      />

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Conflicts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div
              className={`text-3xl font-bold ${totalConflicts > 0 ? 'text-red-600' : 'text-green-600'}`}
            >
              {totalConflicts}
            </div>
          </CardContent>
        </Card>

        {summary?.by_type && Object.keys(summary.by_type).length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                By Type
              </CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="space-y-1 text-sm">
                {Object.entries(summary.by_type).map(([type, count]) => (
                  <div key={type} className="flex justify-between">
                    <dt className="text-muted-foreground">{type}</dt>
                    <dd className="font-medium">{count}</dd>
                  </div>
                ))}
              </dl>
            </CardContent>
          </Card>
        )}

        {summary?.by_estate && summary.by_estate.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                By Estate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="space-y-1 text-sm">
                {summary.by_estate.map((e) => (
                  <div key={e.estate_id} className="flex justify-between">
                    <dt className="text-muted-foreground">{e.estate_name}</dt>
                    <dd className="font-medium">{e.count}</dd>
                  </div>
                ))}
              </dl>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="mb-4">
        <label className="mb-1 block text-xs font-medium text-muted-foreground">
          Filter by estate
        </label>
        <select
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          value={estateFilter}
          onChange={(e) => setEstateFilter(e.target.value ? Number(e.target.value) : '')}
        >
          <option value="">All estates</option>
          {estatesData?.items.map((e) => (
            <option key={e.estate_id} value={e.estate_id}>
              {e.estate_name}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="text-sm text-muted-foreground">Loading conflicts...</div>
      ) : conflicts && conflicts.length > 0 ? (
        <div className="space-y-4">
          {conflicts.map((c, idx) => (
            <ConflictCard key={idx} conflict={c} />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16 text-center">
          <div className="mb-3 rounded-full bg-green-100 p-3">
            <CheckCircle2 className="h-6 w-6 text-green-600" />
          </div>
          <h3 className="text-base font-semibold">No conflicts detected</h3>
          <p className="mt-1 max-w-sm text-sm text-muted-foreground">
            All packages comply with the clash rules.
          </p>
        </div>
      )}
    </div>
  )
}
