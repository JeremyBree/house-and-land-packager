import { flexRender, getCoreRowModel, useReactTable, type ColumnDef } from '@tanstack/react-table'
import { ArrowDown, ArrowUp, ArrowUpDown, ChevronLeft, ChevronRight, Search } from 'lucide-react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/common/EmptyState'
import { LotStatusBadge } from '@/components/common/LotStatusBadge'
import { cn } from '@/lib/utils'
import type { LotSearchResult, LotSearchSortBy } from '@/api/types'

interface ResultsTableProps {
  data: LotSearchResult[]
  loading: boolean
  total: number
  page: number
  size: number
  pages: number
  sortBy: LotSearchSortBy
  sortDesc: boolean
  onSortChange: (sortBy: LotSearchSortBy, sortDesc: boolean) => void
  onPageChange: (page: number) => void
  onSizeChange: (size: number) => void
  onRowClick: (row: LotSearchResult) => void
}

interface SortableHeaderProps {
  label: string
  field: LotSearchSortBy
  sortBy: LotSearchSortBy
  sortDesc: boolean
  onSortChange: (sortBy: LotSearchSortBy, sortDesc: boolean) => void
}

function SortableHeader({ label, field, sortBy, sortDesc, onSortChange }: SortableHeaderProps) {
  const active = sortBy === field
  return (
    <button
      type="button"
      className={cn(
        'inline-flex items-center gap-1 text-left text-xs font-medium uppercase tracking-wide',
        active ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700',
      )}
      onClick={() => {
        if (active) onSortChange(field, !sortDesc)
        else onSortChange(field, false)
      }}
    >
      {label}
      {active ? (
        sortDesc ? (
          <ArrowDown className="h-3 w-3" />
        ) : (
          <ArrowUp className="h-3 w-3" />
        )
      ) : (
        <ArrowUpDown className="h-3 w-3 opacity-50" />
      )}
    </button>
  )
}

function formatNumber(v: string | null | undefined, digits = 0): string {
  if (v == null || v === '') return '—'
  const n = Number(v)
  if (Number.isNaN(n)) return v
  return n.toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits })
}

function formatCurrency(v: string | null | undefined): string {
  if (v == null || v === '') return '—'
  const n = Number(v)
  if (Number.isNaN(n)) return v
  return n.toLocaleString(undefined, { style: 'currency', currency: 'AUD', maximumFractionDigits: 0 })
}

function formatDate(v: string | null | undefined): string {
  if (!v) return '—'
  return v.slice(0, 10)
}

export function ResultsTable({
  data,
  loading,
  total,
  page,
  size,
  pages,
  sortBy,
  sortDesc,
  onSortChange,
  onPageChange,
  onSizeChange,
  onRowClick,
}: ResultsTableProps) {
  const columns: ColumnDef<LotSearchResult>[] = [
    {
      id: 'estate',
      header: () => (
        <SortableHeader
          label="Estate"
          field="estate_name"
          sortBy={sortBy}
          sortDesc={sortDesc}
          onSortChange={onSortChange}
        />
      ),
      cell: ({ row }) => <span className="font-medium">{row.original.estate_name}</span>,
    },
    { id: 'developer', header: 'Developer', cell: ({ row }) => row.original.developer_name },
    { id: 'stage', header: 'Stage', cell: ({ row }) => row.original.stage_name },
    {
      id: 'lot_number',
      header: () => (
        <SortableHeader
          label="Lot #"
          field="lot_number"
          sortBy={sortBy}
          sortDesc={sortDesc}
          onSortChange={onSortChange}
        />
      ),
      cell: ({ row }) => row.original.lot_number,
    },
    { id: 'suburb', header: 'Suburb', cell: ({ row }) => row.original.estate_suburb ?? '—' },
    {
      id: 'status',
      header: 'Status',
      cell: ({ row }) => <LotStatusBadge status={row.original.status} />,
    },
    {
      id: 'frontage',
      header: () => (
        <SortableHeader
          label="Frontage"
          field="frontage"
          sortBy={sortBy}
          sortDesc={sortDesc}
          onSortChange={onSortChange}
        />
      ),
      cell: ({ row }) => formatNumber(row.original.frontage, 1),
    },
    { id: 'depth', header: 'Depth', cell: ({ row }) => formatNumber(row.original.depth, 1) },
    {
      id: 'size',
      header: () => (
        <SortableHeader
          label="Size"
          field="size_sqm"
          sortBy={sortBy}
          sortDesc={sortDesc}
          onSortChange={onSortChange}
        />
      ),
      cell: ({ row }) => formatNumber(row.original.size_sqm, 0),
    },
    {
      id: 'corner',
      header: 'Corner',
      cell: ({ row }) => (row.original.corner_block ? 'Yes' : 'No'),
    },
    {
      id: 'land_price',
      header: () => (
        <SortableHeader
          label="Land Price"
          field="land_price"
          sortBy={sortBy}
          sortDesc={sortDesc}
          onSortChange={onSortChange}
        />
      ),
      cell: ({ row }) => formatCurrency(row.original.land_price),
    },
    {
      id: 'title_date',
      header: 'Title Date',
      cell: ({ row }) => formatDate(row.original.title_date),
    },
  ]

  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() })

  return (
    <div className="space-y-4">
      <div className="rounded-lg border bg-card overflow-x-auto">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 8 }).map((_, i) => (
                <TableRow key={i}>
                  {columns.map((_c, j) => (
                    <TableCell key={j}>
                      <div className="h-4 w-full animate-pulse rounded bg-slate-100" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="p-0">
                  <EmptyState
                    icon={Search}
                    title="No lots match your filters"
                    description="Try adjusting the filter panel on the left."
                  />
                </TableCell>
              </TableRow>
            ) : (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  onClick={() => onRowClick(row.original)}
                  className="cursor-pointer"
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {total > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="text-sm text-muted-foreground">
              Showing {(page - 1) * size + 1}-{Math.min(page * size, total)} of {total}
            </div>
            <select
              className="h-8 rounded-md border border-input bg-background px-2 text-xs"
              value={size}
              onChange={(e) => onSizeChange(Number(e.target.value))}
            >
              <option value={25}>25 / page</option>
              <option value={50}>50 / page</option>
              <option value={100}>100 / page</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
            >
              <ChevronLeft className="h-4 w-4" /> Previous
            </Button>
            <div className="text-sm">
              Page {page} of {pages || 1}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= pages}
            >
              Next <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
