import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { Pencil, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { CsvImportButton } from '@/components/common/CsvImportButton'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import {
  listHouseDesigns,
  listEnergyRatings,
  createEnergyRating,
  updateEnergyRating,
  deleteEnergyRating,
  type EnergyRatingRead,
} from '@/api/houseDesigns'

const BRANDS = ['Hermitage Homes', 'Kingsbridge Homes'] as const

const schema = z.object({
  garage_side: z.string().min(1),
  orientation: z.string().min(1).max(5),
  star_rating: z.coerce.number().min(0),
  best_worst: z.string().min(1).max(1),
  compliance_cost: z.coerce.number().min(0),
})
type FormValues = z.infer<typeof schema>

export default function EnergyRatingsPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [brandFilter, setBrandFilter] = useState<string>(BRANDS[0])
  const [selectedDesignId, setSelectedDesignId] = useState<number | ''>('')
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<EnergyRatingRead | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<EnergyRatingRead | null>(null)

  const { data: designs } = useQuery({
    queryKey: ['house-designs', brandFilter, true],
    queryFn: () => listHouseDesigns(brandFilter, true),
  })

  const { data: ratings, isLoading } = useQuery({
    queryKey: ['energy-ratings', selectedDesignId],
    queryFn: () => listEnergyRatings(selectedDesignId as number),
    enabled: !!selectedDesignId,
  })

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { garage_side: 'LHS', orientation: 'N', star_rating: 0, best_worst: 'B', compliance_cost: 0 },
  })

  useEffect(() => {
    if (formOpen) {
      form.reset({
        garage_side: editing?.garage_side ?? 'LHS',
        orientation: editing?.orientation ?? 'N',
        star_rating: editing?.star_rating ?? 0,
        best_worst: editing?.best_worst ?? 'B',
        compliance_cost: editing?.compliance_cost ?? 0,
      })
    }
  }, [formOpen, editing, form])

  const saveMut = useMutation({
    mutationFn: async (values: FormValues) => {
      if (editing) {
        return updateEnergyRating(selectedDesignId as number, editing.rating_id, values)
      }
      return createEnergyRating(selectedDesignId as number, values)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['energy-ratings', selectedDesignId] })
      toast({ title: editing ? 'Rating updated' : 'Rating created', variant: 'success' })
      setFormOpen(false)
      setEditing(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteEnergyRating(selectedDesignId as number, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['energy-ratings', selectedDesignId] })
      toast({ title: 'Rating deleted', variant: 'success' })
      setDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })



  return (
    <div>
      <PageHeader
        title="Energy Ratings"
        description="Manage energy compliance cost matrix per house design."
        actions={
          <div className="flex gap-2">
            <CsvImportButton endpoint="/api/house-designs/energy-ratings/upload-csv" onSuccess={() => queryClient.invalidateQueries({ queryKey: ['energy-ratings'] })} />
            {selectedDesignId ? (
              <Button onClick={() => { setEditing(null); setFormOpen(true) }}>
                <Plus className="h-4 w-4" /> New Rating
              </Button>
            ) : null}
          </div>
        }
      />

      <div className="mb-4 flex gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Brand</label>
          <select
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            value={brandFilter}
            onChange={(e) => { setBrandFilter(e.target.value); setSelectedDesignId('') }}
          >
            {BRANDS.map((b) => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">House Design</label>
          <select
            className="h-10 min-w-[200px] rounded-md border border-input bg-background px-3 text-sm"
            value={selectedDesignId}
            onChange={(e) => setSelectedDesignId(e.target.value ? Number(e.target.value) : '')}
          >
            <option value="">Select design...</option>
            {designs?.map((d) => (
              <option key={d.design_id} value={d.design_id}>{d.house_name}</option>
            ))}
          </select>
        </div>
      </div>

      {!selectedDesignId ? (
        <p className="text-sm text-muted-foreground">Select a house design to manage energy ratings.</p>
      ) : (
        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Garage Side</TableHead>
                <TableHead>Orientation</TableHead>
                <TableHead className="text-right">Star Rating</TableHead>
                <TableHead>Best/Worst</TableHead>
                <TableHead className="text-right">Compliance Cost</TableHead>
                <TableHead className="w-24 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : !ratings?.length ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-sm text-muted-foreground">No energy ratings yet.</TableCell>
                </TableRow>
              ) : (
                ratings.map((r) => (
                  <TableRow key={r.rating_id}>
                    <TableCell className="font-medium">{r.garage_side}</TableCell>
                    <TableCell>{r.orientation}</TableCell>
                    <TableCell className="text-right">{r.star_rating}</TableCell>
                    <TableCell>{r.best_worst === 'B' ? 'Best' : 'Worst'}</TableCell>
                    <TableCell className="text-right">${r.compliance_cost.toLocaleString()}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => { setEditing(r); setFormOpen(true) }}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(r)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      )}

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit Energy Rating' : 'New Energy Rating'}</DialogTitle>
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit((v) => saveMut.mutate(v))} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <FormField control={form.control} name="garage_side" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Garage Side *</FormLabel>
                    <FormControl>
                      <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...field}>
                        <option value="LHS">LHS</option>
                        <option value="RHS">RHS</option>
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={form.control} name="orientation" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Orientation *</FormLabel>
                    <FormControl>
                      <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...field}>
                        {['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'].map((o) => (
                          <option key={o} value={o}>{o}</option>
                        ))}
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <FormField control={form.control} name="star_rating" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Star Rating</FormLabel>
                    <FormControl><Input type="number" step="0.1" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={form.control} name="best_worst" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Best/Worst</FormLabel>
                    <FormControl>
                      <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...field}>
                        <option value="B">Best</option>
                        <option value="W">Worst</option>
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={form.control} name="compliance_cost" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Compliance Cost</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={saveMut.isPending}>
                  {saveMut.isPending ? 'Saving...' : editing ? 'Save' : 'Create'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete energy rating?"
        description={deleteTarget ? `Rating for ${deleteTarget.garage_side} / ${deleteTarget.orientation} will be removed.` : ''}
        confirmLabel="Delete"
        variant="destructive"
        loading={deleteMut.isPending}
        onConfirm={() => deleteTarget && deleteMut.mutate(deleteTarget.rating_id)}
      />
    </div>
  )
}
