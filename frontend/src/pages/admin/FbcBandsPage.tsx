import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import {
  listFbcBands,
  createFbcBand,
  updateFbcBand,
  deleteFbcBand,
} from '@/api/pricingReference'
import type { FbcEscalationBandRead, FbcEscalationBandInput } from '@/api/pricingReference'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const BRANDS = ['Hermitage Homes', 'Kingsbridge Homes']

const emptyForm: FbcEscalationBandInput = {
  brand: BRANDS[0],
  day_start: 0,
  day_end: 0,
  multiplier: 1,
}

export default function FbcBandsPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [brandFilter, setBrandFilter] = useState<string | undefined>(undefined)
  const [editing, setEditing] = useState<FbcEscalationBandRead | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [form, setForm] = useState<FbcEscalationBandInput>(emptyForm)
  const [deleteTarget, setDeleteTarget] = useState<FbcEscalationBandRead | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['fbc-bands', brandFilter],
    queryFn: () => listFbcBands(brandFilter),
  })

  const save = useMutation({
    mutationFn: async () => {
      if (editing) return updateFbcBand(editing.band_id, form)
      return createFbcBand(form)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fbc-bands'] })
      toast({ title: editing ? 'Band updated' : 'Band created', variant: 'success' })
      setFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const remove = useMutation({
    mutationFn: (id: number) => deleteFbcBand(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fbc-bands'] })
      toast({ title: 'Band deleted', variant: 'success' })
      setDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const openNew = () => {
    setEditing(null)
    setForm({ ...emptyForm, brand: brandFilter || BRANDS[0] })
    setFormOpen(true)
  }

  const openEdit = (item: FbcEscalationBandRead) => {
    setEditing(item)
    setForm({
      brand: item.brand,
      day_start: item.day_start,
      day_end: item.day_end,
      multiplier: item.multiplier,
    })
    setFormOpen(true)
  }

  return (
    <div>
      <PageHeader
        title="FBC Escalation Bands"
        description="Future build cost escalation multipliers by day range and brand."
        actions={
          <div className="flex items-center gap-3">
            <Select
              value={brandFilter || 'all'}
              onValueChange={(v) => setBrandFilter(v === 'all' ? undefined : v)}
            >
              <SelectTrigger className="w-52">
                <SelectValue placeholder="All brands" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All brands</SelectItem>
                {BRANDS.map((b) => (
                  <SelectItem key={b} value={b}>{b}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={openNew}>
              <Plus className="h-4 w-4" /> New Band
            </Button>
          </div>
        }
      />

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Brand</TableHead>
              <TableHead className="text-right">Day Start</TableHead>
              <TableHead className="text-right">Day End</TableHead>
              <TableHead className="text-right">Multiplier</TableHead>
              <TableHead className="w-32 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">
                  Loading...
                </TableCell>
              </TableRow>
            ) : data?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">
                  No FBC bands yet.
                </TableCell>
              </TableRow>
            ) : (
              data?.map((b) => (
                <TableRow key={b.band_id}>
                  <TableCell className="font-medium">{b.brand}</TableCell>
                  <TableCell className="text-right">{b.day_start}</TableCell>
                  <TableCell className="text-right">{b.day_end}</TableCell>
                  <TableCell className="text-right">{b.multiplier.toFixed(4)}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" onClick={() => openEdit(b)}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:text-destructive"
                      onClick={() => setDeleteTarget(b)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit band' : 'New band'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label htmlFor="brand">Brand</Label>
              <Select value={form.brand} onValueChange={(v) => setForm({ ...form, brand: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {BRANDS.map((b) => (
                    <SelectItem key={b} value={b}>{b}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="day_start">Day start</Label>
                <Input
                  id="day_start"
                  type="number"
                  value={form.day_start}
                  onChange={(e) => setForm({ ...form, day_start: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div>
                <Label htmlFor="day_end">Day end</Label>
                <Input
                  id="day_end"
                  type="number"
                  value={form.day_end}
                  onChange={(e) => setForm({ ...form, day_end: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="multiplier">Multiplier</Label>
              <Input
                id="multiplier"
                type="number"
                step="0.0001"
                value={form.multiplier}
                onChange={(e) => setForm({ ...form, multiplier: parseFloat(e.target.value) || 0 })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setFormOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => save.mutate()} disabled={!form.brand.trim() || save.isPending}>
              {save.isPending ? 'Saving...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete band?"
        description={deleteTarget ? `Band "${deleteTarget.brand} (${deleteTarget.day_start}-${deleteTarget.day_end})" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={remove.isPending}
        onConfirm={() => deleteTarget && remove.mutate(deleteTarget.band_id)}
      />
    </div>
  )
}
