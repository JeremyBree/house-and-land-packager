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
import { CsvImportButton } from '@/components/common/CsvImportButton'
import {
  listSiteCostTiers,
  createSiteCostTier,
  updateSiteCostTier,
  deleteSiteCostTier,
  listSiteCostItems,
  createSiteCostItem,
  updateSiteCostItem,
  deleteSiteCostItem,
} from '@/api/pricingReference'
import type { SiteCostTierRead, SiteCostTierInput, SiteCostItemRead, SiteCostItemInput } from '@/api/pricingReference'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

// ── Tier form defaults ────────────────────────────────────────────

const emptyTierForm: SiteCostTierInput = { tier_name: '', fall_min_mm: 0, fall_max_mm: 0 }

const emptyItemForm: SiteCostItemInput = {
  tier_id: null,
  item_name: '',
  condition_type: '',
  condition_description: '',
  cost_single_lt190: null,
  cost_double_lt190: null,
  cost_single_191_249: null,
  cost_double_191_249: null,
  cost_single_250_300: null,
  cost_double_250_300: null,
  cost_single_300plus: null,
  cost_double_300plus: null,
  sort_order: 0,
}

const costColumns = [
  { key: 'cost_single_lt190', label: 'Sgl <190' },
  { key: 'cost_double_lt190', label: 'Dbl <190' },
  { key: 'cost_single_191_249', label: 'Sgl 191-249' },
  { key: 'cost_double_191_249', label: 'Dbl 191-249' },
  { key: 'cost_single_250_300', label: 'Sgl 250-300' },
  { key: 'cost_double_250_300', label: 'Dbl 250-300' },
  { key: 'cost_single_300plus', label: 'Sgl 300+' },
  { key: 'cost_double_300plus', label: 'Dbl 300+' },
] as const

export default function SiteCostsPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  // ── Tier state ────────────────────────────────────────────────
  const [tierEditing, setTierEditing] = useState<SiteCostTierRead | null>(null)
  const [tierFormOpen, setTierFormOpen] = useState(false)
  const [tierForm, setTierForm] = useState<SiteCostTierInput>(emptyTierForm)
  const [tierDeleteTarget, setTierDeleteTarget] = useState<SiteCostTierRead | null>(null)

  // ── Item state ────────────────────────────────────────────────
  const [selectedTierId, setSelectedTierId] = useState<number | undefined>(undefined)
  const [itemEditing, setItemEditing] = useState<SiteCostItemRead | null>(null)
  const [itemFormOpen, setItemFormOpen] = useState(false)
  const [itemForm, setItemForm] = useState<SiteCostItemInput>(emptyItemForm)
  const [itemDeleteTarget, setItemDeleteTarget] = useState<SiteCostItemRead | null>(null)

  const { data: tiers, isLoading: tiersLoading } = useQuery({
    queryKey: ['site-cost-tiers'],
    queryFn: listSiteCostTiers,
  })

  const { data: items, isLoading: itemsLoading } = useQuery({
    queryKey: ['site-cost-items', selectedTierId],
    queryFn: () => listSiteCostItems(selectedTierId),
  })

  // ── Tier mutations ────────────────────────────────────────────
  const saveTier = useMutation({
    mutationFn: async () => {
      if (tierEditing) return updateSiteCostTier(tierEditing.tier_id, tierForm)
      return createSiteCostTier(tierForm)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site-cost-tiers'] })
      toast({ title: tierEditing ? 'Tier updated' : 'Tier created', variant: 'success' })
      setTierFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const removeTier = useMutation({
    mutationFn: (id: number) => deleteSiteCostTier(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site-cost-tiers'] })
      toast({ title: 'Tier deleted', variant: 'success' })
      setTierDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  // ── Item mutations ────────────────────────────────────────────
  const saveItem = useMutation({
    mutationFn: async () => {
      if (itemEditing) return updateSiteCostItem(itemEditing.item_id, itemForm)
      return createSiteCostItem(itemForm)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site-cost-items'] })
      toast({ title: itemEditing ? 'Item updated' : 'Item created', variant: 'success' })
      setItemFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const removeItem = useMutation({
    mutationFn: (id: number) => deleteSiteCostItem(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site-cost-items'] })
      toast({ title: 'Item deleted', variant: 'success' })
      setItemDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const openNewTier = () => {
    setTierEditing(null)
    setTierForm(emptyTierForm)
    setTierFormOpen(true)
  }

  const openEditTier = (t: SiteCostTierRead) => {
    setTierEditing(t)
    setTierForm({ tier_name: t.tier_name, fall_min_mm: t.fall_min_mm, fall_max_mm: t.fall_max_mm })
    setTierFormOpen(true)
  }

  const openNewItem = () => {
    setItemEditing(null)
    setItemForm({ ...emptyItemForm, tier_id: selectedTierId ?? null })
    setItemFormOpen(true)
  }

  const openEditItem = (i: SiteCostItemRead) => {
    setItemEditing(i)
    setItemForm({
      tier_id: i.tier_id,
      item_name: i.item_name,
      condition_type: i.condition_type || '',
      condition_description: i.condition_description || '',
      cost_single_lt190: i.cost_single_lt190,
      cost_double_lt190: i.cost_double_lt190,
      cost_single_191_249: i.cost_single_191_249,
      cost_double_191_249: i.cost_double_191_249,
      cost_single_250_300: i.cost_single_250_300,
      cost_double_250_300: i.cost_double_250_300,
      cost_single_300plus: i.cost_single_300plus,
      cost_double_300plus: i.cost_double_300plus,
      sort_order: i.sort_order,
    })
    setItemFormOpen(true)
  }

  const setItemCost = (key: string, raw: string) => {
    const val = raw === '' ? null : parseFloat(raw)
    setItemForm({ ...itemForm, [key]: val != null && isNaN(val) ? null : val })
  }

  return (
    <div>
      <PageHeader
        title="Site Costs"
        description="Manage site cost tiers and line items with width-based pricing."
        actions={
          <div className="flex gap-2">
            <CsvImportButton endpoint="/api/pricing-reference/site-cost-tiers/upload-csv" label="Import Tiers" onSuccess={() => queryClient.invalidateQueries({ queryKey: ['site-cost-tiers'] })} />
            <CsvImportButton endpoint="/api/pricing-reference/site-cost-items/upload-csv" label="Import Items" onSuccess={() => queryClient.invalidateQueries({ queryKey: ['site-cost-items'] })} />
          </div>
        }
      />

      {/* ── Tiers section ──────────────────────────────────────── */}
      <div className="mb-8">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Tiers</h2>
          <Button size="sm" onClick={openNewTier}>
            <Plus className="h-4 w-4" /> New Tier
          </Button>
        </div>
        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tier Name</TableHead>
                <TableHead>Fall Min (mm)</TableHead>
                <TableHead>Fall Max (mm)</TableHead>
                <TableHead className="w-32 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tiersLoading ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : tiers?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">No tiers yet.</TableCell>
                </TableRow>
              ) : (
                tiers?.map((t) => (
                  <TableRow key={t.tier_id}>
                    <TableCell className="font-medium">{t.tier_name}</TableCell>
                    <TableCell>{t.fall_min_mm}</TableCell>
                    <TableCell>{t.fall_max_mm}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => openEditTier(t)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive" onClick={() => setTierDeleteTarget(t)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* ── Items section ──────────────────────────────────────── */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">Items</h2>
            <Select
              value={selectedTierId != null ? String(selectedTierId) : 'all'}
              onValueChange={(v) => setSelectedTierId(v === 'all' ? undefined : Number(v))}
            >
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All tiers" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All tiers</SelectItem>
                {tiers?.map((t) => (
                  <SelectItem key={t.tier_id} value={String(t.tier_id)}>
                    {t.tier_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button size="sm" onClick={openNewItem}>
            <Plus className="h-4 w-4" /> New Item
          </Button>
        </div>
        <div className="rounded-lg border bg-card overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="min-w-[180px]">Item Name</TableHead>
                <TableHead className="min-w-[100px]">Condition</TableHead>
                <TableHead className="min-w-[80px]">Sort</TableHead>
                {costColumns.map((c) => (
                  <TableHead key={c.key} className="min-w-[90px] text-right">{c.label}</TableHead>
                ))}
                <TableHead className="w-32 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {itemsLoading ? (
                <TableRow>
                  <TableCell colSpan={11 + costColumns.length} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : items?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={11 + costColumns.length} className="text-center text-sm text-muted-foreground">No items yet.</TableCell>
                </TableRow>
              ) : (
                items?.map((i) => (
                  <TableRow key={i.item_id}>
                    <TableCell className="font-medium">{i.item_name}</TableCell>
                    <TableCell>{i.condition_type || '-'}</TableCell>
                    <TableCell>{i.sort_order}</TableCell>
                    {costColumns.map((c) => {
                      const val = i[c.key as keyof SiteCostItemRead] as number | null
                      return (
                        <TableCell key={c.key} className="text-right">
                          {val != null ? val.toFixed(2) : '-'}
                        </TableCell>
                      )
                    })}
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => openEditItem(i)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive" onClick={() => setItemDeleteTarget(i)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* ── Tier dialog ────────────────────────────────────────── */}
      <Dialog open={tierFormOpen} onOpenChange={setTierFormOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{tierEditing ? 'Edit tier' : 'New tier'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label htmlFor="tier_name">Tier name</Label>
              <Input id="tier_name" value={tierForm.tier_name} onChange={(e) => setTierForm({ ...tierForm, tier_name: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="fall_min">Fall min (mm)</Label>
                <Input id="fall_min" type="number" value={tierForm.fall_min_mm} onChange={(e) => setTierForm({ ...tierForm, fall_min_mm: parseInt(e.target.value) || 0 })} />
              </div>
              <div>
                <Label htmlFor="fall_max">Fall max (mm)</Label>
                <Input id="fall_max" type="number" value={tierForm.fall_max_mm} onChange={(e) => setTierForm({ ...tierForm, fall_max_mm: parseInt(e.target.value) || 0 })} />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setTierFormOpen(false)}>Cancel</Button>
            <Button onClick={() => saveTier.mutate()} disabled={!tierForm.tier_name.trim() || saveTier.isPending}>
              {saveTier.isPending ? 'Saving...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Item dialog ────────────────────────────────────────── */}
      <Dialog open={itemFormOpen} onOpenChange={setItemFormOpen}>
        <DialogContent className="sm:max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{itemEditing ? 'Edit item' : 'New item'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="item_name">Item name</Label>
                <Input id="item_name" value={itemForm.item_name} onChange={(e) => setItemForm({ ...itemForm, item_name: e.target.value })} />
              </div>
              <div>
                <Label htmlFor="item_tier">Tier</Label>
                <Select
                  value={itemForm.tier_id != null ? String(itemForm.tier_id) : 'none'}
                  onValueChange={(v) => setItemForm({ ...itemForm, tier_id: v === 'none' ? null : Number(v) })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="None" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    {tiers?.map((t) => (
                      <SelectItem key={t.tier_id} value={String(t.tier_id)}>{t.tier_name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="condition_type">Condition type</Label>
                <Input id="condition_type" value={itemForm.condition_type || ''} onChange={(e) => setItemForm({ ...itemForm, condition_type: e.target.value || null })} />
              </div>
              <div>
                <Label htmlFor="sort_order">Sort order</Label>
                <Input id="sort_order" type="number" value={itemForm.sort_order ?? 0} onChange={(e) => setItemForm({ ...itemForm, sort_order: parseInt(e.target.value) || 0 })} />
              </div>
            </div>
            <div>
              <Label htmlFor="condition_desc">Condition description</Label>
              <Input id="condition_desc" value={itemForm.condition_description || ''} onChange={(e) => setItemForm({ ...itemForm, condition_description: e.target.value || null })} />
            </div>
            <div className="grid grid-cols-4 gap-3">
              {costColumns.map((c) => (
                <div key={c.key}>
                  <Label htmlFor={c.key} className="text-xs">{c.label}</Label>
                  <Input
                    id={c.key}
                    type="number"
                    step="0.01"
                    value={itemForm[c.key as keyof SiteCostItemInput] as number | string ?? ''}
                    onChange={(e) => setItemCost(c.key, e.target.value)}
                  />
                </div>
              ))}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setItemFormOpen(false)}>Cancel</Button>
            <Button onClick={() => saveItem.mutate()} disabled={!itemForm.item_name.trim() || saveItem.isPending}>
              {saveItem.isPending ? 'Saving...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Confirm dialogs ────────────────────────────────────── */}
      <ConfirmDialog
        open={!!tierDeleteTarget}
        onOpenChange={(o) => !o && setTierDeleteTarget(null)}
        title="Delete tier?"
        description={tierDeleteTarget ? `"${tierDeleteTarget.tier_name}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={removeTier.isPending}
        onConfirm={() => tierDeleteTarget && removeTier.mutate(tierDeleteTarget.tier_id)}
      />
      <ConfirmDialog
        open={!!itemDeleteTarget}
        onOpenChange={(o) => !o && setItemDeleteTarget(null)}
        title="Delete item?"
        description={itemDeleteTarget ? `"${itemDeleteTarget.item_name}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={removeItem.isPending}
        onConfirm={() => itemDeleteTarget && removeItem.mutate(itemDeleteTarget.item_id)}
      />
    </div>
  )
}
