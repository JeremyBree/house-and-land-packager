import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { Plus, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable } from '@/components/common/DataTable'
import { EstateFormDialog } from './EstateFormDialog'
import { listEstates } from '@/api/estates'
import { listDevelopers } from '@/api/developers'
import { listRegions } from '@/api/regions'
import type { EstateRead } from '@/api/types'
import { useAuth } from '@/hooks/useAuth'

const PAGE_SIZE = 20

export default function EstatesListPage() {
  const navigate = useNavigate()
  const { hasRole } = useAuth()
  const isAdmin = hasRole('admin')

  const [search, setSearch] = useState('')
  const [developerId, setDeveloperId] = useState<string>('')
  const [regionId, setRegionId] = useState<string>('')
  const [activeFilter, setActiveFilter] = useState<string>('true')
  const [page, setPage] = useState(1)
  const [showCreate, setShowCreate] = useState(false)

  const { data: developers } = useQuery({ queryKey: ['developers'], queryFn: listDevelopers })
  const { data: regions } = useQuery({ queryKey: ['regions'], queryFn: listRegions })

  const { data, isLoading } = useQuery({
    queryKey: ['estates', { search, developerId, regionId, activeFilter, page }],
    queryFn: () =>
      listEstates({
        page,
        size: PAGE_SIZE,
        search: search || undefined,
        developer_id: developerId ? Number(developerId) : undefined,
        region_id: regionId ? Number(regionId) : undefined,
        active: activeFilter === '' ? undefined : activeFilter === 'true',
      }),
  })

  const developerMap = useMemo(() => {
    const m = new Map<number, string>()
    developers?.forEach((d) => m.set(d.developer_id, d.developer_name))
    return m
  }, [developers])

  const regionMap = useMemo(() => {
    const m = new Map<number, string>()
    regions?.forEach((r) => m.set(r.region_id, r.name))
    return m
  }, [regions])

  const columns = useMemo<ColumnDef<EstateRead>[]>(
    () => [
      {
        accessorKey: 'estate_name',
        header: 'Estate',
        cell: ({ row }) => <span className="font-medium">{row.original.estate_name}</span>,
      },
      {
        accessorKey: 'developer_id',
        header: 'Developer',
        cell: ({ row }) => developerMap.get(row.original.developer_id) ?? '—',
      },
      {
        accessorKey: 'region_id',
        header: 'Region',
        cell: ({ row }) => (row.original.region_id ? regionMap.get(row.original.region_id) ?? '—' : '—'),
      },
      { accessorKey: 'suburb', header: 'Suburb', cell: ({ row }) => row.original.suburb ?? '—' },
      { accessorKey: 'state', header: 'State', cell: ({ row }) => row.original.state ?? '—' },
      {
        accessorKey: 'active',
        header: 'Status',
        cell: ({ row }) =>
          row.original.active ? (
            <Badge variant="success">Active</Badge>
          ) : (
            <Badge variant="secondary">Inactive</Badge>
          ),
      },
    ],
    [developerMap, regionMap],
  )

  return (
    <div>
      <PageHeader
        title="Estates"
        description="Browse and manage estates across developers and regions."
        actions={
          isAdmin && (
            <Button onClick={() => setShowCreate(true)}>
              <Plus className="h-4 w-4" />
              New Estate
            </Button>
          )
        }
      />

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[240px] max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search estates..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            className="pl-9"
          />
        </div>
        <select
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          value={developerId}
          onChange={(e) => {
            setDeveloperId(e.target.value)
            setPage(1)
          }}
        >
          <option value="">All developers</option>
          {developers?.map((d) => (
            <option key={d.developer_id} value={d.developer_id}>
              {d.developer_name}
            </option>
          ))}
        </select>
        <select
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          value={regionId}
          onChange={(e) => {
            setRegionId(e.target.value)
            setPage(1)
          }}
        >
          <option value="">All regions</option>
          {regions?.map((r) => (
            <option key={r.region_id} value={r.region_id}>
              {r.name}
            </option>
          ))}
        </select>
        <select
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          value={activeFilter}
          onChange={(e) => {
            setActiveFilter(e.target.value)
            setPage(1)
          }}
        >
          <option value="true">Active only</option>
          <option value="false">Inactive only</option>
          <option value="">All</option>
        </select>
      </div>

      <DataTable
        data={data?.items ?? []}
        columns={columns}
        loading={isLoading}
        onRowClick={(estate) => navigate(`/estates/${estate.estate_id}`)}
        emptyTitle="No estates found"
        emptyDescription="Try adjusting your filters or create a new estate."
        pagination={{
          page: data?.page ?? 1,
          size: data?.size ?? PAGE_SIZE,
          total: data?.total ?? 0,
          pages: data?.pages ?? 1,
          onPageChange: setPage,
        }}
      />

      <EstateFormDialog open={showCreate} onOpenChange={setShowCreate} />
    </div>
  )
}
