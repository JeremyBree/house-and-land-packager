import { useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import {
  Download,
  Edit,
  FileUp,
  MoreHorizontal,
  Plus,
  Trash2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { DataTable } from '@/components/common/DataTable'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { PageHeader } from '@/components/common/PageHeader'
import { PackageFormDialog } from './PackageFormDialog'
import { listPackages, deletePackage, uploadFlyer, deleteFlyer } from '@/api/packages'
import { listEstates } from '@/api/estates'
import { listStages } from '@/api/stages'
import type { PackageRead } from '@/api/types'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const PAGE_SIZE = 20
const BRANDS = ['All', 'Hermitage', 'Kingsbridge'] as const

export default function PackagesPage() {
  const queryClient = useQueryClient()
  const { hasRole } = useAuth()
  const { toast } = useToast()
  const isAdmin = hasRole('admin')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [page, setPage] = useState(1)
  const [estateFilter, setEstateFilter] = useState<number | ''>('')
  const [stageFilter, setStageFilter] = useState<number | ''>('')
  const [brandFilter, setBrandFilter] = useState<string>('All')
  const [designFilter, setDesignFilter] = useState('')
  const [facadeFilter, setFacadeFilter] = useState('')

  const [showNew, setShowNew] = useState(false)
  const [editPkg, setEditPkg] = useState<PackageRead | null>(null)
  const [deletePkg, setDeletePkg] = useState<PackageRead | null>(null)
  const [flyerUploadPkg, setFlyerUploadPkg] = useState<PackageRead | null>(null)

  const { data: estatesData } = useQuery({
    queryKey: ['estates', { page: 1, size: 200 }],
    queryFn: () => listEstates({ page: 1, size: 200 }),
  })

  const selectedEstateId = estateFilter || undefined

  const { data: stages } = useQuery({
    queryKey: ['stages', selectedEstateId],
    queryFn: () => listStages(selectedEstateId!),
    enabled: !!selectedEstateId,
  })

  const { data: packagesData, isLoading } = useQuery({
    queryKey: [
      'packages',
      {
        estate_id: estateFilter || undefined,
        stage_id: stageFilter || undefined,
        brand: brandFilter !== 'All' ? brandFilter : undefined,
        design: designFilter || undefined,
        facade: facadeFilter || undefined,
        page,
        size: PAGE_SIZE,
      },
    ],
    queryFn: () =>
      listPackages({
        estate_id: estateFilter || undefined,
        stage_id: stageFilter || undefined,
        brand: brandFilter !== 'All' ? brandFilter : undefined,
        design: designFilter || undefined,
        facade: facadeFilter || undefined,
        page,
        size: PAGE_SIZE,
      }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deletePackage(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] })
      toast({ title: 'Package deleted', variant: 'success' })
      setDeletePkg(null)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const uploadFlyerMutation = useMutation({
    mutationFn: ({ id, file }: { id: number; file: File }) => uploadFlyer(id, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] })
      toast({ title: 'Flyer uploaded', variant: 'success' })
      setFlyerUploadPkg(null)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const deleteFlyerMutation = useMutation({
    mutationFn: (id: number) => deleteFlyer(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] })
      toast({ title: 'Flyer deleted', variant: 'success' })
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  function handleFlyerFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file && flyerUploadPkg) {
      uploadFlyerMutation.mutate({ id: flyerUploadPkg.package_id, file })
    }
    e.target.value = ''
  }

  const brandBadgeClass = (brand: string) => {
    switch (brand) {
      case 'Hermitage':
        return 'bg-blue-100 text-blue-800'
      case 'Kingsbridge':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-secondary text-secondary-foreground'
    }
  }

  const columns = useMemo<ColumnDef<PackageRead>[]>(
    () => [
      {
        accessorKey: 'lot_number',
        header: 'Lot #',
        cell: ({ row }) => <span className="font-medium">{row.original.lot_number}</span>,
      },
      { accessorKey: 'estate_id', header: 'Estate' },
      { accessorKey: 'stage_id', header: 'Stage' },
      { accessorKey: 'design', header: 'Design' },
      { accessorKey: 'facade', header: 'Facade' },
      {
        accessorKey: 'brand',
        header: 'Brand',
        cell: ({ row }) => (
          <span
            className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${brandBadgeClass(row.original.brand)}`}
          >
            {row.original.brand}
          </span>
        ),
      },
      {
        accessorKey: 'colour_scheme',
        header: 'Colour',
        cell: ({ row }) => row.original.colour_scheme ?? '-',
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => row.original.status ?? '-',
      },
      {
        id: 'flyer',
        header: 'Flyer',
        cell: ({ row }) =>
          row.original.flyer_path ? (
            <a
              href={row.original.flyer_path}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
              onClick={(e) => e.stopPropagation()}
            >
              <Download className="h-4 w-4" />
            </a>
          ) : (
            <span className="text-muted-foreground">-</span>
          ),
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => {
          const p = row.original
          if (!isAdmin) return null
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" onClick={(e) => e.stopPropagation()}>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setEditPkg(p)}>
                  <Edit className="h-4 w-4" /> Edit
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => {
                    setFlyerUploadPkg(p)
                    setTimeout(() => fileInputRef.current?.click(), 100)
                  }}
                >
                  <FileUp className="h-4 w-4" /> Upload Flyer
                </DropdownMenuItem>
                {p.flyer_path && (
                  <DropdownMenuItem onClick={() => deleteFlyerMutation.mutate(p.package_id)}>
                    <Trash2 className="h-4 w-4" /> Delete Flyer
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => setDeletePkg(p)}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="h-4 w-4" /> Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )
        },
      },
    ],
    [isAdmin, deleteFlyerMutation],
  )

  return (
    <div>
      <PageHeader
        title="Packages"
        description="House & land packages across all estates."
        actions={
          isAdmin ? (
            <Button onClick={() => setShowNew(true)}>
              <Plus className="h-4 w-4" /> New Package
            </Button>
          ) : undefined
        }
      />

      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Estate</label>
          <select
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            value={estateFilter}
            onChange={(e) => {
              setEstateFilter(e.target.value ? Number(e.target.value) : '')
              setStageFilter('')
              setPage(1)
            }}
          >
            <option value="">All estates</option>
            {estatesData?.items.map((e) => (
              <option key={e.estate_id} value={e.estate_id}>
                {e.estate_name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Stage</label>
          <select
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            value={stageFilter}
            onChange={(e) => {
              setStageFilter(e.target.value ? Number(e.target.value) : '')
              setPage(1)
            }}
            disabled={!selectedEstateId}
          >
            <option value="">All stages</option>
            {stages?.map((s) => (
              <option key={s.stage_id} value={s.stage_id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Brand</label>
          <select
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            value={brandFilter}
            onChange={(e) => {
              setBrandFilter(e.target.value)
              setPage(1)
            }}
          >
            {BRANDS.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Design</label>
          <Input
            className="h-10 w-40"
            placeholder="Filter design..."
            value={designFilter}
            onChange={(e) => {
              setDesignFilter(e.target.value)
              setPage(1)
            }}
          />
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Facade</label>
          <Input
            className="h-10 w-40"
            placeholder="Filter facade..."
            value={facadeFilter}
            onChange={(e) => {
              setFacadeFilter(e.target.value)
              setPage(1)
            }}
          />
        </div>
      </div>

      <DataTable
        data={packagesData?.items ?? []}
        columns={columns}
        loading={isLoading}
        emptyTitle="No packages found"
        emptyDescription="Try adjusting your filters or create a new package."
        pagination={{
          page: packagesData?.page ?? 1,
          size: packagesData?.size ?? PAGE_SIZE,
          total: packagesData?.total ?? 0,
          pages: packagesData?.pages ?? 1,
          onPageChange: setPage,
        }}
      />

      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".pdf,.jpg,.jpeg,.png"
        onChange={handleFlyerFileChange}
      />

      <PackageFormDialog open={showNew} onOpenChange={setShowNew} />
      <PackageFormDialog
        open={!!editPkg}
        onOpenChange={(open) => !open && setEditPkg(null)}
        pkg={editPkg}
      />
      <ConfirmDialog
        open={!!deletePkg}
        onOpenChange={(open) => !open && setDeletePkg(null)}
        title="Delete package?"
        description={
          deletePkg
            ? `Package for lot ${deletePkg.lot_number} (${deletePkg.design} / ${deletePkg.facade}) will be permanently removed.`
            : ''
        }
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={() => deletePkg && deleteMutation.mutate(deletePkg.package_id)}
        loading={deleteMutation.isPending}
      />
    </div>
  )
}
