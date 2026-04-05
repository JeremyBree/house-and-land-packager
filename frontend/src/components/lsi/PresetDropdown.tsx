import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Bookmark, Trash2, Check } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import { deletePreset } from '@/api/filterPresets'
import type { FilterPresetRead } from '@/api/types'

interface PresetDropdownProps {
  presets: FilterPresetRead[]
  activePresetId: number | null
  onLoad: (preset: FilterPresetRead) => void
}

function countFilters(f: FilterPresetRead['filters']): number {
  let c = 0
  if (f.estate_ids?.length) c++
  if (f.developer_ids?.length) c++
  if (f.region_ids?.length) c++
  if (f.suburbs?.length) c++
  if (f.statuses?.length) c++
  if (f.price_min || f.price_max) c++
  if (f.size_min || f.size_max) c++
  if (f.frontage_min) c++
  if (f.depth_min) c++
  if (f.corner_block != null) c++
  if (f.title_date_from || f.title_date_to) c++
  if (f.text_search) c++
  return c
}

export function PresetDropdown({ presets, activePresetId, onLoad }: PresetDropdownProps) {
  const [open, setOpen] = useState(false)
  const { toast } = useToast()
  const qc = useQueryClient()

  const delMutation = useMutation({
    mutationFn: (id: number) => deletePreset(id),
    onSuccess: () => {
      toast({ variant: 'success', title: 'Preset deleted' })
      qc.invalidateQueries({ queryKey: ['filter-presets'] })
    },
    onError: () => {
      toast({ variant: 'destructive', title: 'Failed to delete preset' })
    },
  })

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">
          <Bookmark className="h-4 w-4" />
          Load preset...
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[300px]">
        <DropdownMenuLabel>Your presets</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {presets.length === 0 ? (
          <div className="px-2 py-4 text-center text-xs text-slate-500">
            No saved presets yet.
          </div>
        ) : (
          <div className="max-h-80 overflow-y-auto">
            {presets.map((p) => {
              const active = activePresetId === p.preset_id
              return (
                <div
                  key={p.preset_id}
                  className="group flex items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-accent"
                >
                  <button
                    type="button"
                    className="flex flex-1 items-center justify-between text-left"
                    onClick={() => {
                      onLoad(p)
                      setOpen(false)
                    }}
                  >
                    <div className="flex items-center gap-2">
                      {active && <Check className="h-3 w-3 text-emerald-600" />}
                      <span className="font-medium">{p.name}</span>
                    </div>
                    <span className="text-xs text-slate-500">
                      {countFilters(p.filters)} filter{countFilters(p.filters) === 1 ? '' : 's'}
                    </span>
                  </button>
                  <button
                    type="button"
                    className="rounded p-1 opacity-0 transition-opacity hover:bg-red-100 group-hover:opacity-100"
                    onClick={(e) => {
                      e.stopPropagation()
                      if (confirm(`Delete preset "${p.name}"?`)) {
                        delMutation.mutate(p.preset_id)
                      }
                    }}
                  >
                    <Trash2 className="h-3.5 w-3.5 text-red-600" />
                  </button>
                </div>
              )
            })}
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
