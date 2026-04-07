import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import {
  listTravelSurcharges,
  createTravelSurcharge,
  updateTravelSurcharge,
  deleteTravelSurcharge,
} from '@/api/pricingReference'
import type { TravelSurchargeRead, TravelSurchargeInput } from '@/api/pricingReference'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const emptyForm: TravelSurchargeInput = {
  suburb_name: '',
  postcode: '',
  surcharge_amount: 0,
  region_name: '',
}

export default function TravelSurchargesPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [editing, setEditing] = useState<TravelSurchargeRead | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [form, setForm] = useState<TravelSurchargeInput>(emptyForm)
  const [deleteTarget, setDeleteTarget] = useState<TravelSurchargeRead | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['travel-surcharges'],
    queryFn: listTravelSurcharges,
  })

  const save = useMutation({
    mutationFn: async () => {
      if (editing) return updateTravelSurcharge(editing.surcharge_id, form)
      return createTravelSurcharge(form)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['travel-surcharges'] })
      toast({ title: editing ? 'Surcharge updated' : 'Surcharge created', variant: 'success' })
      setFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const remove = useMutation({
    mutationFn: (id: number) => deleteTravelSurcharge(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['travel-surcharges'] })
      toast({ title: 'Surcharge deleted', variant: 'success' })
      setDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const openNew = () => {
    setEditing(null)
    setForm(emptyForm)
    setFormOpen(true)
  }

  const openEdit = (item: TravelSurchargeRead) => {
    setEditing(item)
    setForm({
      suburb_name: item.suburb_name,
      postcode: item.postcode || '',
      surcharge_amount: item.surcharge_amount,
      region_name: item.region_name || '',
    })
    setFormOpen(true)
  }

  return (
    <div>
      <PageHeader
        title="Travel Surcharges"
        description="Suburb-based travel surcharge amounts."
        actions={
          <Button onClick={openNew}>
            <Plus className="h-4 w-4" /> New Surcharge
          </Button>
        }
      />

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Suburb</TableHead>
              <TableHead>Postcode</TableHead>
              <TableHead>Region</TableHead>
              <TableHead className="text-right">Amount ($)</TableHead>
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
                  No travel surcharges yet.
                </TableCell>
              </TableRow>
            ) : (
              data?.map((s) => (
                <TableRow key={s.surcharge_id}>
                  <TableCell className="font-medium">{s.suburb_name}</TableCell>
                  <TableCell>{s.postcode || '-'}</TableCell>
                  <TableCell>{s.region_name || '-'}</TableCell>
                  <TableCell className="text-right">{s.surcharge_amount.toFixed(2)}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" onClick={() => openEdit(s)}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:text-destructive"
                      onClick={() => setDeleteTarget(s)}
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
            <DialogTitle>{editing ? 'Edit surcharge' : 'New surcharge'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label htmlFor="suburb_name">Suburb name</Label>
              <Input
                id="suburb_name"
                value={form.suburb_name}
                onChange={(e) => setForm({ ...form, suburb_name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="postcode">Postcode</Label>
              <Input
                id="postcode"
                value={form.postcode || ''}
                onChange={(e) => setForm({ ...form, postcode: e.target.value || null })}
              />
            </div>
            <div>
              <Label htmlFor="region_name">Region</Label>
              <Input
                id="region_name"
                value={form.region_name || ''}
                onChange={(e) => setForm({ ...form, region_name: e.target.value || null })}
              />
            </div>
            <div>
              <Label htmlFor="surcharge_amount">Amount ($)</Label>
              <Input
                id="surcharge_amount"
                type="number"
                step="0.01"
                value={form.surcharge_amount}
                onChange={(e) => setForm({ ...form, surcharge_amount: parseFloat(e.target.value) || 0 })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setFormOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => save.mutate()} disabled={!form.suburb_name.trim() || save.isPending}>
              {save.isPending ? 'Saving...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete surcharge?"
        description={deleteTarget ? `"${deleteTarget.suburb_name}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={remove.isPending}
        onConfirm={() => deleteTarget && remove.mutate(deleteTarget.surcharge_id)}
      />
    </div>
  )
}
