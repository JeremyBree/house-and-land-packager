import { useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import type { ColumnDef } from '@tanstack/react-table'
import { Eye, MoreHorizontal, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { DataTable } from '@/components/common/DataTable'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { PageHeader } from '@/components/common/PageHeader'
import {
  listPricingRequests,
  deletePricingRequest,
  type PricingRequestRead,
} from '@/api/pricingRequests'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import { Badge } from '@/components/ui/badge'

const PAGE_SIZE = 25
const STATUSES = ['All', 'Pending', 'In Progress', 'Completed'] as const
const BRANDS = ['All', 'Hermitage Homes', 'Kingsbridge Homes'] as const

function statusVariant(status: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'Completed': return 'default'
    case 'In Progress': return 'secondary'
    case 'Pending': return 'outline'
    default: return 'default'
  }
}

export default function PricingRequestsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>('All')
  const [brandFilter, setBrandFilter] = useState<string>('All')
  const [deleteReq, setDeleteReq] = useState<PricingRequestRead | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['pricing-requests', { page, status: statusFilter, brand: brandFilter }],
    queryFn: () =>
      listPricingRequests({
        page,
        size: PAGE_SIZE,
        status: statusFilter === 'All' ? undefined : statusFilter,
        brand: brandFilter === 'All' ? undefined : brandFilter,
      }),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => deletePricingRequest(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pricing-requests'] })
      toast({ title: 'Request deleted' })
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const columns: ColumnDef<PricingRequestRead>[] = useMemo(
    () => [
      { accessorKey: 'request_id', header: 'ID', size: 60 },
      { accessorKey: 'brand', header: 'Brand', size: 150 },
      {
        accessorKey: 'lot_numbers',
        header: 'Lots',
        cell: ({ row }) => row.original.lot_numbers.join(', '),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => (
          <Badge variant={statusVariant(row.original.status)}>{row.original.status}</Badge>
        ),
      },
      {
        accessorKey: 'submitted_at',
        header: 'Submitted',
        cell: ({ row }) =>
          row.original.submitted_at
            ? new Date(row.original.submitted_at).toLocaleDateString()
            : '-',
      },
      {
        id: 'actions',
        header: '',
        size: 50,
        cell: ({ row }) => {
          const req = row.original
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => navigate(`/pricing-requests/${req.request_id}`)}>
                  <Eye className="mr-2 h-4 w-4" />
                  View
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => setDeleteReq(req)}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )
        },
      },
    ],
    [navigate],
  )

  return (
    <div className="p-6">
      <PageHeader
        title="Pricing Requests"
        description="Submit and track pricing requests for house & land packages"
        actions={
          <Button onClick={() => navigate('/pricing-requests/new')}>
            <Plus className="mr-2 h-4 w-4" />
            New Request
          </Button>
        }
      />

      <div className="mb-4 flex gap-3">
        <select
          className="rounded-md border px-3 py-2 text-sm"
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select
          className="rounded-md border px-3 py-2 text-sm"
          value={brandFilter}
          onChange={(e) => { setBrandFilter(e.target.value); setPage(1) }}
        >
          {BRANDS.map((b) => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        pagination={
          data
            ? {
                page,
                size: PAGE_SIZE,
                total: data.total,
                pages: data.pages,
                onPageChange: (p: number) => setPage(p),
              }
            : undefined
        }
        loading={isLoading}
      />

      <ConfirmDialog
        open={!!deleteReq}
        title="Delete Pricing Request"
        description={`Are you sure you want to delete request #${deleteReq?.request_id}?`}
        onOpenChange={() => setDeleteReq(null)}
        onConfirm={() => {
          if (deleteReq) {
            deleteMut.mutate(deleteReq.request_id)
            setDeleteReq(null)
          }
        }}
      />
    </div>
  )
}
