import { useQuery } from '@tanstack/react-query'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { LotStatusBadge } from '@/components/common/LotStatusBadge'
import { getStatusHistory } from '@/api/lots'
import type { LotRead } from '@/api/types'
import { ArrowRight } from 'lucide-react'

interface StatusHistoryDrawerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  lot: LotRead | null
}

export function StatusHistoryDrawer({ open, onOpenChange, lot }: StatusHistoryDrawerProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['status-history', lot?.lot_id],
    queryFn: () => getStatusHistory(lot!.lot_id),
    enabled: open && !!lot,
  })

  const sorted = [...(data ?? [])].sort(
    (a, b) => new Date(b.changed_at).getTime() - new Date(a.changed_at).getTime(),
  )

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Status history</DialogTitle>
          <DialogDescription>
            {lot ? `Lot ${lot.lot_number}` : 'Timeline of status changes.'}
          </DialogDescription>
        </DialogHeader>
        <div className="max-h-[60vh] overflow-y-auto">
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Loading...</div>
          ) : sorted.length === 0 ? (
            <div className="text-sm text-muted-foreground">No history yet.</div>
          ) : (
            <ol className="space-y-3">
              {sorted.map((entry) => (
                <li
                  key={entry.history_id}
                  className="rounded-md border bg-card p-3 text-sm"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    {entry.previous_status ? (
                      <LotStatusBadge status={entry.previous_status} />
                    ) : (
                      <span className="text-xs text-muted-foreground">Initial</span>
                    )}
                    <ArrowRight className="h-3 w-3 text-muted-foreground" />
                    <LotStatusBadge status={entry.new_status} />
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    <span>{new Date(entry.changed_at).toLocaleString()}</span>
                    <span>·</span>
                    <span>by {entry.triggering_agent}</span>
                  </div>
                  {entry.source_detail && (
                    <div className="mt-2 whitespace-pre-wrap text-xs">
                      {entry.source_detail}
                    </div>
                  )}
                </li>
              ))}
            </ol>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
