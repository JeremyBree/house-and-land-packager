import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Download, Save, Search as SearchIcon } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import { FilterPanel } from '@/components/lsi/FilterPanel'
import { ResultsTable } from '@/components/lsi/ResultsTable'
import { LotDetailDrawer } from '@/components/lsi/LotDetailDrawer'
import { SavePresetDialog } from '@/components/lsi/SavePresetDialog'
import { PresetDropdown } from '@/components/lsi/PresetDropdown'
import { searchLots, exportCsv, exportXlsx } from '@/api/lotSearch'
import { listPresets } from '@/api/filterPresets'
import type {
  FilterPresetRead,
  LotSearchFilters,
  LotSearchResult,
  LotSearchSortBy,
} from '@/api/types'

const DEFAULT_FILTERS: LotSearchFilters = {
  estate_ids: null,
  developer_ids: null,
  region_ids: null,
  suburbs: null,
  statuses: ['Available'],
  price_min: null,
  price_max: null,
  size_min: null,
  size_max: null,
  frontage_min: null,
  depth_min: null,
  corner_block: null,
  title_date_from: null,
  title_date_to: null,
  exclude_null_price: true,
  text_search: null,
}

function timestampForFilename(): string {
  const d = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export default function LsiPage() {
  const { toast } = useToast()

  const [filters, setFilters] = useState<LotSearchFilters>(DEFAULT_FILTERS)
  const [textSearchInput, setTextSearchInput] = useState('')
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(25)
  const [sortBy, setSortBy] = useState<LotSearchSortBy>('estate_name')
  const [sortDesc, setSortDesc] = useState(false)

  const [selectedLot, setSelectedLot] = useState<LotSearchResult | null>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [savePresetOpen, setSavePresetOpen] = useState(false)
  const [activePresetId, setActivePresetId] = useState<number | null>(null)
  const [exporting, setExporting] = useState<'csv' | 'xlsx' | null>(null)

  // Debounce text search
  useEffect(() => {
    const handle = setTimeout(() => {
      setFilters((prev) =>
        prev.text_search === (textSearchInput || null)
          ? prev
          : { ...prev, text_search: textSearchInput || null },
      )
      setPage(1)
    }, 300)
    return () => clearTimeout(handle)
  }, [textSearchInput])

  // Reset page when filters change (excluding page/size/sort)
  useEffect(() => {
    setPage(1)
  }, [filters, sortBy, sortDesc])

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['lot-search', filters, page, size, sortBy, sortDesc],
    queryFn: () => searchLots({ filters, page, size, sort_by: sortBy, sort_desc: sortDesc }),
    placeholderData: (prev) => prev,
  })

  const { data: presets = [] } = useQuery({
    queryKey: ['filter-presets'],
    queryFn: listPresets,
    staleTime: 60_000,
  })

  const total = data?.total ?? 0
  const pages = data?.pages ?? 1
  const items = data?.items ?? []

  const handleLoadPreset = (preset: FilterPresetRead) => {
    setFilters({ ...DEFAULT_FILTERS, ...preset.filters })
    setTextSearchInput(preset.filters.text_search ?? '')
    setActivePresetId(preset.preset_id)
    setPage(1)
    toast({ title: 'Preset loaded', description: preset.name })
  }

  const handleReset = () => {
    setFilters(DEFAULT_FILTERS)
    setTextSearchInput('')
    setActivePresetId(null)
    setPage(1)
  }

  const handleFiltersChange = (next: LotSearchFilters) => {
    setFilters(next)
    setActivePresetId(null)
  }

  const handleExport = async (kind: 'csv' | 'xlsx') => {
    setExporting(kind)
    try {
      const blob = kind === 'csv' ? await exportCsv(filters) : await exportXlsx(filters)
      downloadBlob(blob, `lots_export_${timestampForFilename()}.${kind}`)
      toast({ variant: 'success', title: `Export ready`, description: `${kind.toUpperCase()} downloaded.` })
    } catch {
      toast({ variant: 'destructive', title: 'Export failed' })
    } finally {
      setExporting(null)
    }
  }

  const countLabel = useMemo(() => {
    if (isLoading) return 'Loading...'
    return `${total.toLocaleString()} lot${total === 1 ? '' : 's'}`
  }, [isLoading, total])

  return (
    <div className="-m-6 flex h-[calc(100vh-4rem)] min-h-0">
      <FilterPanel filters={filters} onChange={handleFiltersChange} onReset={handleReset} />

      <div className="flex-1 overflow-y-auto">
        <div className="border-b border-slate-200 bg-white px-6 py-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative min-w-[260px] flex-1 max-w-md">
              <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search lots, estates, suburbs..."
                className="pl-9"
                value={textSearchInput}
                onChange={(e) => setTextSearchInput(e.target.value)}
              />
            </div>
            <PresetDropdown
              presets={presets}
              activePresetId={activePresetId}
              onLoad={handleLoadPreset}
            />
            <Button variant="outline" onClick={() => setSavePresetOpen(true)}>
              <Save className="h-4 w-4" /> Save Preset
            </Button>
            <Button
              variant="outline"
              onClick={() => handleExport('csv')}
              disabled={exporting !== null}
            >
              <Download className="h-4 w-4" /> {exporting === 'csv' ? 'Exporting...' : 'Export CSV'}
            </Button>
            <Button
              variant="outline"
              onClick={() => handleExport('xlsx')}
              disabled={exporting !== null}
            >
              <Download className="h-4 w-4" /> {exporting === 'xlsx' ? 'Exporting...' : 'Export XLSX'}
            </Button>
            <div className="ml-auto text-sm text-slate-600">
              {countLabel}
              {isFetching && !isLoading && <span className="ml-2 text-slate-400">updating...</span>}
            </div>
          </div>
        </div>

        <div className="p-6">
          <ResultsTable
            data={items}
            loading={isLoading}
            total={total}
            page={page}
            size={size}
            pages={pages}
            sortBy={sortBy}
            sortDesc={sortDesc}
            onSortChange={(by, desc) => {
              setSortBy(by)
              setSortDesc(desc)
            }}
            onPageChange={setPage}
            onSizeChange={(s) => {
              setSize(s)
              setPage(1)
            }}
            onRowClick={(row) => {
              setSelectedLot(row)
              setDrawerOpen(true)
            }}
          />
        </div>
      </div>

      <LotDetailDrawer
        lot={selectedLot}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
      <SavePresetDialog
        open={savePresetOpen}
        onOpenChange={setSavePresetOpen}
        filters={filters}
      />
    </div>
  )
}
