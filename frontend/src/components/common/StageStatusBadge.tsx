import { cn } from '@/lib/utils'
import type { StageStatus } from '@/api/types'

const STYLES: Record<StageStatus, { wrap: string; dot: string }> = {
  Active: { wrap: 'bg-green-100 text-green-700', dot: 'bg-green-500' },
  Upcoming: { wrap: 'bg-blue-100 text-blue-700', dot: 'bg-blue-500' },
  Completed: { wrap: 'bg-slate-200 text-slate-600', dot: 'bg-slate-500' },
}

interface StageStatusBadgeProps {
  status: StageStatus
  className?: string
}

export function StageStatusBadge({ status, className }: StageStatusBadgeProps) {
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
