import { cn } from '@/lib/utils'
import type { LotStatus } from '@/api/types'

const STYLES: Record<LotStatus, { wrap: string; dot: string }> = {
  Available: { wrap: 'bg-green-100 text-green-700', dot: 'bg-green-500' },
  Hold: { wrap: 'bg-amber-100 text-amber-700', dot: 'bg-amber-500' },
  'Deposit Taken': { wrap: 'bg-orange-100 text-orange-700', dot: 'bg-orange-500' },
  Sold: { wrap: 'bg-red-100 text-red-700', dot: 'bg-red-500' },
  Unavailable: { wrap: 'bg-slate-200 text-slate-600', dot: 'bg-slate-500' },
}

interface LotStatusBadgeProps {
  status: LotStatus
  className?: string
}

export function LotStatusBadge({ status, className }: LotStatusBadgeProps) {
  const styles = STYLES[status]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium',
        styles.wrap,
        className,
      )}
    >
      <span className={cn('h-1.5 w-1.5 rounded-full', styles.dot)} />
      {status}
    </span>
  )
}
