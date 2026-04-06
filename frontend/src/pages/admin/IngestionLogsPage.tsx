import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { PageHeader } from '@/components/common/PageHeader'
import {
  listIngestionLogs,
  getIngestionLog,
  type IngestionLogRead,
} from '@/api/ingestionLogs'

const statusBadge: Record<string, string> = {
  success: 'bg-green-100 text-green-800',
  partial: 'bg-yellow-100 text-yellow-800',
  failed: 'bg-red-100 text-red-800',
}

const agentLabels: Record<string, string> = {
  email: 'Email',
  scraper: 'Scraper',
  portal: 'Portal',
  pdf: 'PDF',
}

export default function IngestionLogsPage() {
  const [page, setPage] = useState(1)
  const [agentFilter, setAgentFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [detailLog, setDetailLog] = useState<IngestionLogRead | null>(null)
  const [detailOpen, setDetailOpen] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['ingestion-logs', page, agentFilter, statusFilter],
    queryFn: () =>
      listIngestionLogs({
        page,
        size: 25,
        agent_type: agentFilter || undefined,
        status: statusFilter || undefined,
      }),
  })

  async function openDetail(logId: number) {
    try {
      const log = await getIngestionLog(logId)
      setDetailLog(log)
      setDetailOpen(true)
    } catch {
      // silently ignore
    }
  }

  const items = data?.items ?? []
  const totalPages = data?.pages ?? 0

  return (
    <div>
      <PageHeader
        title="Ingestion Logs"
        description="View agent run history and results"
      />

      {/* Filters */}
      <div className="mb-4 flex gap-3">
        <Select value={agentFilter} onValueChange={(v) => { setAgentFilter(v === 'all' ? '' : v); setPage(1) }}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="All Agents" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Agents</SelectItem>
            <SelectItem value="email">Email</SelectItem>
            <SelectItem value="scraper">Scraper</SelectItem>
            <SelectItem value="portal">Portal</SelectItem>
            <SelectItem value="pdf">PDF</SelectItem>
          </SelectContent>
        </Select>

        <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v === 'all' ? '' : v); setPage(1) }}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="success">Success</SelectItem>
            <SelectItem value="partial">Partial</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>Agent</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Records</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground">
                    No logs found
                  </TableCell>
                </TableRow>
              ) : (
                items.map((log) => (
                  <TableRow key={log.log_id}>
                    <TableCell className="text-sm">
                      {new Date(log.run_timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {agentLabels[log.agent_type] ?? log.agent_type}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-[200px] truncate text-sm">
                      {log.source_identifier}
                    </TableCell>
                    <TableCell className="text-sm">
                      <span title="Found">{log.records_found}</span>
                      {' / '}
                      <span title="Created" className="text-green-600">{log.records_created}</span>
                      {' / '}
                      <span title="Updated" className="text-blue-600">{log.records_updated}</span>
                      {' / '}
                      <span title="Deactivated" className="text-gray-500">{log.records_deactivated}</span>
                    </TableCell>
                    <TableCell>
                      <Badge className={statusBadge[log.status] ?? 'bg-gray-100 text-gray-800'}>
                        {log.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openDetail(log.log_id)}
                      >
                        Detail
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage(page + 1)}
          >
            Next
          </Button>
        </div>
      )}

      {/* Detail Dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ingestion Log Detail</DialogTitle>
          </DialogHeader>
          {detailLog && (
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div className="text-muted-foreground">Agent Type</div>
                <div>{agentLabels[detailLog.agent_type] ?? detailLog.agent_type}</div>
                <div className="text-muted-foreground">Source</div>
                <div className="break-all">{detailLog.source_identifier}</div>
                <div className="text-muted-foreground">Timestamp</div>
                <div>{new Date(detailLog.run_timestamp).toLocaleString()}</div>
                <div className="text-muted-foreground">Status</div>
                <div>
                  <Badge className={statusBadge[detailLog.status] ?? ''}>
                    {detailLog.status}
                  </Badge>
                </div>
                <div className="text-muted-foreground">Records Found</div>
                <div>{detailLog.records_found}</div>
                <div className="text-muted-foreground">Records Created</div>
                <div>{detailLog.records_created}</div>
                <div className="text-muted-foreground">Records Updated</div>
                <div>{detailLog.records_updated}</div>
                <div className="text-muted-foreground">Records Deactivated</div>
                <div>{detailLog.records_deactivated}</div>
              </div>
              {detailLog.error_detail && (
                <div className="rounded border border-red-200 bg-red-50 p-3">
                  <div className="mb-1 font-medium text-red-700">Error Detail</div>
                  <pre className="whitespace-pre-wrap text-xs text-red-600">
                    {detailLog.error_detail}
                  </pre>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
