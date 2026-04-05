import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronDown, ChevronRight, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import { cn } from '@/lib/utils'
import { listRegions } from '@/api/regions'
import { listDevelopers } from '@/api/developers'
import { listEstates } from '@/api/estates'
import { LOT_STATUSES, type LotSearchFilters, type LotStatus } from '@/api/types'

interface FilterPanelProps {
  filters: LotSearchFilters
  onChange: (next: LotSearchFilters) => void
  onReset: () => void
}

const STATUS_COLORS: Record<LotStatus, string> = {
  Available: 'bg-green-500',
  Hold: 'bg-amber-500',
  'Deposit Taken': 'bg-orange-500',
  Sold: 'bg-red-500',
  Unavailable: 'bg-slate-500',
}

interface SectionProps {
  title: string
  children: React.ReactNode
  defaultOpen?: boolean
}

function Section({ title, children, defaultOpen = true }: SectionProps) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border-b border-slate-200">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-700 hover:bg-slate-50"
      >
        <span>{title}</span>
        {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>
      {open && <div className="px-4 pb-4 space-y-3">{children}</div>}
    </div>
  )
}

interface MultiCheckProps<T extends string | number> {
  options: { value: T; label: string }[]
  selected: T[] | null | undefined
  onChange: (next: T[] | null) => void
  maxHeight?: string
}

function MultiCheck<T extends string | number>({
  options,
  selected,
  onChange,
  maxHeight = 'max-h-40',
}: MultiCheckProps<T>) {
  const current = selected ?? []
  const toggle = (val: T) => {
    const has = current.includes(val)
    const next = has ? current.filter((v) => v !== val) : [...current, val]
    onChange(next.length === 0 ? null : next)
  }
  return (
    <div className={cn('space-y-1.5 overflow-y-auto rounded border border-slate-200 bg-white p-2', maxHeight)}>
      {options.length === 0 ? (
        <div className="text-xs text-slate-500">No options</div>
      ) : (
        options.map((opt) => (
          <Checkbox
            key={String(opt.value)}
            label={opt.label}
            checked={current.includes(opt.value)}
            onChange={() => toggle(opt.value)}
          />
        ))
      )}
    </div>
  )
}

export function FilterPanel({ filters, onChange, onReset }: FilterPanelProps) {
  const { data: regions } = useQuery({ queryKey: ['regions'], queryFn: listRegions })
  const { data: developers } = useQuery({ queryKey: ['developers'], queryFn: listDevelopers })
  const { data: estatesResp } = useQuery({
    queryKey: ['estates', 'all-for-lsi'],
    queryFn: () => listEstates({ page: 1, size: 500 }),
  })

  const regionOptions = useMemo(
    () => (regions ?? []).map((r) => ({ value: r.region_id, label: r.name })),
    [regions],
  )
  const developerOptions = useMemo(
    () => (developers ?? []).map((d) => ({ value: d.developer_id, label: d.developer_name })),
    [developers],
  )
  const estateOptions = useMemo(
    () => (estatesResp?.items ?? []).map((e) => ({ value: e.estate_id, label: e.estate_name })),
    [estatesResp],
  )

  const update = (patch: Partial<LotSearchFilters>) => onChange({ ...filters, ...patch })

  const cornerValue: string =
    filters.corner_block == null ? '' : filters.corner_block ? 'yes' : 'no'

  return (
    <aside className="sticky top-0 flex h-[calc(100vh-4rem)] w-[320px] shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div className="text-sm font-semibold text-slate-800">Filters</div>
        <Button variant="ghost" size="sm" onClick={onReset}>
          <X className="h-3 w-3" /> Reset
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto">
        <Section title="Location">
          <div>
            <div className="mb-1 text-xs font-medium text-slate-600">Regions</div>
            <MultiCheck
              options={regionOptions}
              selected={filters.region_ids}
              onChange={(v) => update({ region_ids: v })}
            />
          </div>
          <div>
            <div className="mb-1 text-xs font-medium text-slate-600">Developers</div>
            <MultiCheck
              options={developerOptions}
              selected={filters.developer_ids}
              onChange={(v) => update({ developer_ids: v })}
            />
          </div>
          <div>
            <div className="mb-1 text-xs font-medium text-slate-600">Estates</div>
            <MultiCheck
              options={estateOptions}
              selected={filters.estate_ids}
              onChange={(v) => update({ estate_ids: v })}
            />
          </div>
        </Section>

        <Section title="Status">
          <div className="space-y-2">
            {LOT_STATUSES.map((s) => {
              const selected = filters.statuses ?? []
              const checked = selected.includes(s)
              return (
                <label key={s} className="flex cursor-pointer items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-input"
                    checked={checked}
                    onChange={() => {
                      const next = checked ? selected.filter((x) => x !== s) : [...selected, s]
                      update({ statuses: next.length === 0 ? null : next })
                    }}
                  />
                  <span className={cn('h-2 w-2 rounded-full', STATUS_COLORS[s])} />
                  <span>{s}</span>
                </label>
              )
            })}
          </div>
        </Section>

        <Section title="Price">
          <div className="grid grid-cols-2 gap-2">
            <Input
              type="number"
              placeholder="Min"
              value={filters.price_min ?? ''}
              onChange={(e) => update({ price_min: e.target.value || null })}
            />
            <Input
              type="number"
              placeholder="Max"
              value={filters.price_max ?? ''}
              onChange={(e) => update({ price_max: e.target.value || null })}
            />
          </div>
          <Checkbox
            label="Exclude null prices"
            checked={filters.exclude_null_price ?? true}
            onChange={(e) => update({ exclude_null_price: e.target.checked })}
          />
        </Section>

        <Section title="Size (m²)">
          <div className="grid grid-cols-2 gap-2">
            <Input
              type="number"
              placeholder="Min"
              value={filters.size_min ?? ''}
              onChange={(e) => update({ size_min: e.target.value || null })}
            />
            <Input
              type="number"
              placeholder="Max"
              value={filters.size_max ?? ''}
              onChange={(e) => update({ size_max: e.target.value || null })}
            />
          </div>
        </Section>

        <Section title="Dimensions">
          <div>
            <div className="mb-1 text-xs font-medium text-slate-600">Min frontage (m)</div>
            <Input
              type="number"
              placeholder="Min frontage"
              value={filters.frontage_min ?? ''}
              onChange={(e) => update({ frontage_min: e.target.value || null })}
            />
          </div>
          <div>
            <div className="mb-1 text-xs font-medium text-slate-600">Min depth (m)</div>
            <Input
              type="number"
              placeholder="Min depth"
              value={filters.depth_min ?? ''}
              onChange={(e) => update({ depth_min: e.target.value || null })}
            />
          </div>
          <div>
            <div className="mb-1 text-xs font-medium text-slate-600">Corner block</div>
            <select
              className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={cornerValue}
              onChange={(e) => {
                const v = e.target.value
                update({ corner_block: v === '' ? null : v === 'yes' })
              }}
            >
              <option value="">Any</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </div>
        </Section>

        <Section title="Date" defaultOpen={false}>
          <div>
            <div className="mb-1 text-xs font-medium text-slate-600">Title date from</div>
            <Input
              type="date"
              value={filters.title_date_from ?? ''}
              onChange={(e) => update({ title_date_from: e.target.value || null })}
            />
          </div>
          <div>
            <div className="mb-1 text-xs font-medium text-slate-600">Title date to</div>
            <Input
              type="date"
              value={filters.title_date_to ?? ''}
              onChange={(e) => update({ title_date_to: e.target.value || null })}
            />
          </div>
        </Section>
      </div>
    </aside>
  )
}
