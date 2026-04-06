import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, CheckCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PageHeader } from '@/components/common/PageHeader'
import { listNotifications, markRead, markAllRead } from '@/api/notifications'

const PAGE_SIZE = 25

export default function NotificationsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['notifications', page],
    queryFn: () => listNotifications({ page, size: PAGE_SIZE }),
  })

  const markReadMut = useMutation({
    mutationFn: (id: number) => markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notifications-unread-count'] })
    },
  })

  const markAllMut = useMutation({
    mutationFn: markAllRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notifications-unread-count'] })
    },
  })

  const items = data?.items ?? []
  const total = data?.total ?? 0
  const pages = data?.pages ?? 0

  return (
    <div className="p-6">
      <PageHeader
        title="Notifications"
        description={`${total} notification${total !== 1 ? 's' : ''}`}
        actions={
          <Button variant="outline" onClick={() => markAllMut.mutate()} disabled={markAllMut.isPending}>
            <CheckCheck className="mr-2 h-4 w-4" />
            Mark All Read
          </Button>
        }
      />

      {isLoading ? (
        <div>Loading...</div>
      ) : items.length === 0 ? (
        <div className="py-12 text-center text-muted-foreground">No notifications</div>
      ) : (
        <div className="space-y-2">
          {items.map((n) => (
            <div
              key={n.notification_id}
              className={`flex cursor-pointer items-start justify-between rounded-lg border p-4 transition-colors hover:bg-muted/50 ${
                !n.read ? 'border-primary/30 bg-primary/5' : ''
              }`}
              onClick={() => navigate(`/pricing-requests/${n.pricing_request_id}`)}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  {!n.read && <span className="h-2 w-2 rounded-full bg-primary" />}
                  <span className={`text-sm font-medium ${n.read ? 'text-muted-foreground' : ''}`}>
                    {n.title}
                  </span>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">{n.message}</p>
                <span className="mt-1 text-xs text-muted-foreground">
                  {new Date(n.created_at).toLocaleString()}
                </span>
              </div>
              {!n.read && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    markReadMut.mutate(n.notification_id)
                  }}
                >
                  <Check className="h-4 w-4" />
                </Button>
              )}
            </div>
          ))}
        </div>
      )}

      {pages > 1 && (
        <div className="mt-4 flex items-center justify-center gap-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {pages}
          </span>
          <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => setPage(page + 1)}>
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
