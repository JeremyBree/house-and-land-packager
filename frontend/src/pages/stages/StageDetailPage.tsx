import { useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import {
  ArrowLeft,
  BookOpen,
  Edit,
  History,
  MoreHorizontal,
  Plus,
  RefreshCw,
  Trash2,
  Upload,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { DataTable } from '@/components/common/DataTable'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { LotStatusBadge } from '@/components/common/LotStatusBadge'
import { StageStatusBadge } from '@/components/common/StageStatusBadge'
import { StageFormDialog } from '@/components/stages/StageFormDialog'
import { LotFormDialog } from '@/components/lots/LotFormDialog'
import { BulkUploadDialog } from '@/components/lots/BulkUploadDialog'
import { StatusTransitionDialog } from '@/components/lots/StatusTransitionDialog'
import { StatusHistoryDrawer } from '@/components/lots/StatusHistoryDrawer'
import { ClashRuleEditor } from '@/components/clash-rules/ClashRuleEditor'
import { deleteStage, getStage } from '@/api/stages'
import { deleteLot, listLots } from '@/api/lots'
import { getEstate } from '@/api/estates'
import {
  LOT_STATUSES,
  type LotRead,
  type LotStatus,
} from '@/api/types'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const PAGE_SIZE = 20

const STATUS_BAR_COLORS: Record<LotStatus, string> = {
  Available: 'bg-green-500',
  Hold: 'bg-amber-500',
  'Deposit Taken': 'bg-orange-500',
  Sold: 'bg-red-500',
  Unavailable: 'bg-slate-400',
}

function formatCurrency(value: string | null): string {
  if (!value) return '—'
  const num = Number(value)
  if (Number.isNaN(num)) return value
  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
    maximumFractionDigits: 0,
  }).format(num)
}

function formatDecimal(value: string | null): string {
  if (!value) return '—'
  const num = Number(value)
  if (Number.isNaN(num)) return value
  return num.toString()
}

export default function StageDetailPage() {
  const { estateId: estateIdParam, stageId: stageIdParam } = useParams<{
    estateId: string
    stageId: string
  }>()
  const estateId = Number(estateIdParam)
  const stageId = Number(stageIdParam)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { hasRole, hasAnyRole } = useAuth()
  const { toast } = useToast()
  const isAdmin = hasRole('admin')
  const canTransition = hasAnyRole(['admin', 'pricing'])

  const [statusFilter, setStatusFilter] = useState<LotStatus | ''>('')
  const [page, setPage] = useState(1)
  const [showEditStage, setShowEditStage] = useState(false)
  const [showDeleteStage, setShowDeleteStage] = useState(false)
  const [showNewLot, setShowNewLot] = useState(false)
  const [showBulkUpload, setShowBulkUpload] = useState(false)
  const [editLot, setEditLot] = useState<LotRead | null>(null)
  const [statusLot, setStatusLot] = useState<LotRead | null>(null)
  const [historyLot, setHistoryLot] = useState<LotRead | null>(null)
  const [deleteLotTarget, setDeleteLotTarget] = useState<LotRead | null>(null)

  const { data: estate } = useQuery({
    queryKey: ['estate', estateId],
    queryFn: () => getEstate(estateId),
    enabled: Number.isFinite(estateId),
  })

  const { data: stage, isLoading: stageLoading, error: stageError } = useQuery({
    queryKey: ['stage', stageId],
    queryFn: () => getStage(stageId),
    enabled: Number.isFinite(stageId),
  })

  const { data: lotsData, isLoading: lotsLoading } = useQuery({
    queryKey: ['lots', stageId, { status: statusFilter, page }],
    queryFn: () =>
      listLots(stageId, {
        page,
        size: PAGE_SIZE,
        status: statusFilter || undefined,
      }),
    enabled: Number.isFinite(stageId),
  })

  const deleteStageMutation = useMutation({
    mutationFn: () => deleteStage(stageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stages', estateId] })
      toast({ title: 'Stage deleted', variant: 'success' })
      navigate(`/estates/${estateId}`)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const deleteLotMutation = useMutation({
    mutationFn: (lotId: number) => deleteLot(lotId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lots', stageId] })
      queryClient.invalidateQueries({ queryKey: ['stage', stageId] })
      toast({ title: 'Lot deleted', variant: 'success' })
      setDeleteLotTarget(null)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const columns = useMemo<ColumnDef<LotRead>[]>(
    () => [
      {
        accessorKey: 'lot_number',
        header: 'Lot #',
        cell: ({ row }) => <span className="font-medium">{row.original.lot_number}</span>,
      },
      {
        accessorKey: 'frontage',
        header: 'Frontage',
        cell: ({ row }) => formatDecimal(row.original.frontage),
      },
      {
        accessorKey: 'depth',
        header: 'Depth',
        cell: ({ row }) => formatDecimal(row.original.depth),
      },
      {
        accessorKey: 'size_sqm',
        header: 'Size',
        cell: ({ row }) => formatDecimal(row.original.size_sqm),
      },
      {
        accessorKey: 'corner_block',
        header: 'Corner',
        cell: ({ row }) => (row.original.corner_block ? 'Yes' : '—'),
      },
      {
        accessorKey: 'orientation',
        header: 'Orientation',
        cell: ({ row }) => row.original.orientation ?? '—',
      },
      {
        accessorKey: 'street_name',
        header: 'Street',
        cell: ({ row }) => row.original.street_name ?? '—',
      },
      {
        accessorKey: 'land_price',
        header: 'Land Price',
        cell: ({ row }) => formatCurrency(row.original.land_price),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => <LotStatusBadge status={row.original.status} />,
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => {
          const lot = row.original
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" onClick={(e) => e.stopPropagation()}>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {isAdmin && (
                  <DropdownMenuItem onClick={() => setEditLot(lot)}>
                    <Edit className="h-4 w-4" /> Edit
                  </DropdownMenuItem>
                )}
                {canTransition && (
                  <DropdownMenuItem onClick={() => setStatusLot(lot)}>
                    <RefreshCw className="h-4 w-4" /> Change Status
                  </DropdownMenuItem>
                )}
                <DropdownMenuItem onClick={() => setHistoryLot(lot)}>
                  <History className="h-4 w-4" /> History
                </DropdownMenuItem>
                {isAdmin && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      onClick={() => setDeleteLotTarget(lot)}
                      className="text-destructive focus:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" /> Delete
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )
        },
      },
    ],
    [isAdmin, canTransition],
  )

  if (stageLoading) {
    return <div className="text-sm text-muted-foreground">Loading...</div>
  }

  if (stageError || !stage) {
    return (
      <div>
        <Button variant="outline" size="sm" asChild>
          <Link to={`/estates/${estateId}`}>
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>
        </Button>
        <div className="mt-6 text-sm text-muted-foreground">Stage not found.</div>
      </div>
    )
  }

  const totalActual = stage.lot_count_actual
  const breakdownEntries = LOT_STATUSES.map((s) => ({
    status: s,
    count: stage.status_breakdown[s] ?? 0,
  }))

  return (
    <div>
      <Button variant="ghost" size="sm" asChild className="mb-4 -ml-2">
        <Link to={`/estates/${estateId}`}>
          <ArrowLeft className="h-4 w-4" />{' '}
          {estate ? `Back to ${estate.estate_name}` : 'Back to estate'}
        </Link>
      </Button>

      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">{stage.name}</h2>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            <StageStatusBadge status={stage.status} />
            <span>·</span>
            <span>
              {totalActual} lot{totalActual === 1 ? '' : 's'}
            </span>
            {stage.release_date && (
              <>
                <span>·</span>
                <span>Release {new Date(stage.release_date).toLocaleDateString()}</span>
              </>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link to={`/admin/estate-guidelines?estate_id=${estateId}&stage_id=${stageId}`}>
            <Button variant="outline" size="sm">
              <BookOpen className="h-4 w-4" /> Guidelines
            </Button>
          </Link>
          {isAdmin && (
            <>
              <Button variant="outline" onClick={() => setShowEditStage(true)}>
                <Edit className="h-4 w-4" /> Edit
              </Button>
              <Button variant="destructive" onClick={() => setShowDeleteStage(true)}>
                <Trash2 className="h-4 w-4" /> Delete
              </Button>
            </>
          )}
        </div>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">Status breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          {totalActual === 0 ? (
            <div className="text-sm text-muted-foreground">No lots yet.</div>
          ) : (
            <>
              <div className="mb-3 flex h-3 w-full overflow-hidden rounded-full bg-muted">
                {breakdownEntries.map(({ status, count }) =>
                  count > 0 ? (
                    <div
                      key={status}
                      className={STATUS_BAR_COLORS[status]}
                      style={{ width: `${(count / totalActual) * 100}%` }}
                      title={`${status}: ${count}`}
                    />
                  ) : null,
                )}
              </div>
              <div className="flex flex-wrap gap-4 text-sm">
                {breakdownEntries.map(({ status, count }) => (
                  <div key={status} className="flex items-center gap-2">
                    <span className={`h-2.5 w-2.5 rounded-full ${STATUS_BAR_COLORS[status]}`} />
                    <span className="text-muted-foreground">{status}</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <select
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as LotStatus | '')
              setPage(1)
            }}
          >
            <option value="">All statuses</option>
            {LOT_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        {isAdmin && (
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => setShowBulkUpload(true)}>
              <Upload className="h-4 w-4" /> Bulk Upload CSV
            </Button>
            <Button onClick={() => setShowNewLot(true)}>
              <Plus className="h-4 w-4" /> New Lot
            </Button>
          </div>
        )}
      </div>

      <DataTable
        data={lotsData?.items ?? []}
        columns={columns}
        loading={lotsLoading}
        emptyTitle="No lots found"
        emptyDescription={
          statusFilter
            ? 'Try clearing the status filter.'
            : isAdmin
              ? 'Add lots manually or upload a CSV.'
              : 'No lots have been added yet.'
        }
        pagination={{
          page: lotsData?.page ?? 1,
          size: lotsData?.size ?? PAGE_SIZE,
          total: lotsData?.total ?? 0,
          pages: lotsData?.pages ?? 1,
          onPageChange: setPage,
        }}
      />

      <div className="mt-6">
        <ClashRuleEditor estateId={estateId} stageId={stageId} isAdmin={isAdmin} />
      </div>

      <StageFormDialog
        open={showEditStage}
        onOpenChange={setShowEditStage}
        estateId={estateId}
        stage={stage}
      />
      <LotFormDialog open={showNewLot} onOpenChange={setShowNewLot} stageId={stageId} />
      <LotFormDialog
        open={!!editLot}
        onOpenChange={(open) => !open && setEditLot(null)}
        stageId={stageId}
        lot={editLot}
      />
      <BulkUploadDialog
        open={showBulkUpload}
        onOpenChange={setShowBulkUpload}
        stageId={stageId}
      />
      <StatusTransitionDialog
        open={!!statusLot}
        onOpenChange={(open) => !open && setStatusLot(null)}
        lot={statusLot}
      />
      <StatusHistoryDrawer
        open={!!historyLot}
        onOpenChange={(open) => !open && setHistoryLot(null)}
        lot={historyLot}
      />
      <ConfirmDialog
        open={showDeleteStage}
        onOpenChange={setShowDeleteStage}
        title="Delete stage?"
        description={`"${stage.name}" and all its lots will be permanently deleted. This cannot be undone.`}
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={() => deleteStageMutation.mutate()}
        loading={deleteStageMutation.isPending}
      />
      <ConfirmDialog
        open={!!deleteLotTarget}
        onOpenChange={(open) => !open && setDeleteLotTarget(null)}
        title="Delete lot?"
        description={
          deleteLotTarget
            ? `Lot ${deleteLotTarget.lot_number} will be permanently removed.`
            : ''
        }
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={() =>
          deleteLotTarget && deleteLotMutation.mutate(deleteLotTarget.lot_id)
        }
        loading={deleteLotMutation.isPending}
      />
    </div>
  )
}
