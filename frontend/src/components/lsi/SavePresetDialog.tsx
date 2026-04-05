import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/toast'
import { createPreset } from '@/api/filterPresets'
import type { LotSearchFilters } from '@/api/types'

interface SavePresetDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  filters: LotSearchFilters
}

function summarizeFilters(f: LotSearchFilters): string[] {
  const parts: string[] = []
  if (f.region_ids?.length) parts.push(`${f.region_ids.length} region(s)`)
  if (f.developer_ids?.length) parts.push(`${f.developer_ids.length} developer(s)`)
  if (f.estate_ids?.length) parts.push(`${f.estate_ids.length} estate(s)`)
  if (f.statuses?.length) parts.push(`status: ${f.statuses.join(', ')}`)
  if (f.price_min || f.price_max) parts.push(`price: ${f.price_min ?? '*'}–${f.price_max ?? '*'}`)
  if (f.size_min || f.size_max) parts.push(`size: ${f.size_min ?? '*'}–${f.size_max ?? '*'}`)
  if (f.frontage_min) parts.push(`frontage ≥ ${f.frontage_min}`)
  if (f.depth_min) parts.push(`depth ≥ ${f.depth_min}`)
  if (f.corner_block != null) parts.push(`corner: ${f.corner_block ? 'yes' : 'no'}`)
  if (f.title_date_from || f.title_date_to) parts.push(`title: ${f.title_date_from ?? '*'}–${f.title_date_to ?? '*'}`)
  if (f.text_search) parts.push(`search: "${f.text_search}"`)
  if (f.exclude_null_price) parts.push('exclude null prices')
  return parts
}

export function SavePresetDialog({ open, onOpenChange, filters }: SavePresetDialogProps) {
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()
  const qc = useQueryClient()

  const mutation = useMutation({
    mutationFn: () => createPreset({ name: name.trim(), filters }),
    onSuccess: () => {
      toast({ variant: 'success', title: 'Preset saved', description: `"${name}" is now available.` })
      qc.invalidateQueries({ queryKey: ['filter-presets'] })
      setName('')
      setError(null)
      onOpenChange(false)
    },
    onError: (err: unknown) => {
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        setError('A preset with that name already exists.')
      } else if (axios.isAxiosError(err)) {
        setError((err.response?.data as { detail?: string })?.detail ?? 'Failed to save preset.')
      } else {
        setError('Failed to save preset.')
      }
    },
  })

  const summary = summarizeFilters(filters)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Save filter preset</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium">Preset name</label>
            <Input
              placeholder="e.g. Available lots under $500k"
              value={name}
              onChange={(e) => {
                setName(e.target.value)
                setError(null)
              }}
              autoFocus
            />
            {error && <div className="mt-1 text-xs text-red-600">{error}</div>}
          </div>
          <div>
            <div className="mb-1 text-xs font-medium text-slate-600">Current filters</div>
            <div className="rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700">
              {summary.length === 0 ? (
                <span className="text-slate-500">No filters applied</span>
              ) : (
                <ul className="space-y-1">
                  {summary.map((s, i) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            disabled={!name.trim() || mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            {mutation.isPending ? 'Saving...' : 'Save preset'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
