import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { ChevronDown, ChevronRight, MoreHorizontal, Pencil, Plus, Trash2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
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
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import {
  listHouseDesigns,
  createHouseDesign,
  updateHouseDesign,
  deleteHouseDesign,
  createFacade,
  updateFacade,
  deleteFacade,
  type HouseDesignRead,
  type HouseFacadeRead,
} from '@/api/houseDesigns'

const BRANDS = ['Hermitage Homes', 'Kingsbridge Homes'] as const

// --- Design form schema ---
const designSchema = z.object({
  brand: z.string().min(1),
  house_name: z.string().min(1).max(100),
  base_price: z.coerce.number().min(0),
  storey: z.string().min(1).max(10),
  frontage: z.coerce.number().min(0),
  depth: z.coerce.number().min(0),
  gf_sqm: z.coerce.number().min(0),
  total_sqm: z.coerce.number().min(0),
  lot_total_sqm: z.coerce.number().min(0),
  squares: z.coerce.number().int().min(0),
  details: z.string().optional().or(z.literal('')),
  effective_date: z.string().optional().or(z.literal('')),
  active: z.boolean(),
})
type DesignFormValues = z.infer<typeof designSchema>

// --- Facade form schema ---
const facadeSchema = z.object({
  facade_name: z.string().min(1).max(100),
  facade_price: z.coerce.number().min(0),
  facade_details: z.string().optional().or(z.literal('')),
  is_included: z.boolean(),
})
type FacadeFormValues = z.infer<typeof facadeSchema>

export default function HouseDesignsPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [brandFilter, setBrandFilter] = useState<string>(BRANDS[0])
  const [expandedDesign, setExpandedDesign] = useState<number | null>(null)

  // Design dialog state
  const [designFormOpen, setDesignFormOpen] = useState(false)
  const [editingDesign, setEditingDesign] = useState<HouseDesignRead | null>(null)
  const [deleteDesign, setDeleteDesign] = useState<HouseDesignRead | null>(null)

  // Facade dialog state
  const [facadeFormOpen, setFacadeFormOpen] = useState(false)
  const [facadeDesignId, setFacadeDesignId] = useState<number | null>(null)
  const [editingFacade, setEditingFacade] = useState<HouseFacadeRead | null>(null)
  const [deleteFacadeTarget, setDeleteFacadeTarget] = useState<{ designId: number; facade: HouseFacadeRead } | null>(null)

  const { data: designs, isLoading } = useQuery({
    queryKey: ['house-designs', brandFilter, true],
    queryFn: () => listHouseDesigns(brandFilter, true),
  })

  // --- Design form ---
  const designForm = useForm<DesignFormValues>({
    resolver: zodResolver(designSchema),
    defaultValues: {
      brand: brandFilter,
      house_name: '',
      base_price: 0,
      storey: 'Single',
      frontage: 0,
      depth: 0,
      gf_sqm: 0,
      total_sqm: 0,
      lot_total_sqm: 0,
      squares: 0,
      details: '',
      effective_date: '',
      active: true,
    },
  })

  useEffect(() => {
    if (designFormOpen) {
      designForm.reset({
        brand: editingDesign?.brand ?? brandFilter,
        house_name: editingDesign?.house_name ?? '',
        base_price: editingDesign?.base_price ?? 0,
        storey: editingDesign?.storey ?? 'Single',
        frontage: editingDesign?.frontage ?? 0,
        depth: editingDesign?.depth ?? 0,
        gf_sqm: editingDesign?.gf_sqm ?? 0,
        total_sqm: editingDesign?.total_sqm ?? 0,
        lot_total_sqm: editingDesign?.lot_total_sqm ?? 0,
        squares: editingDesign?.squares ?? 0,
        details: editingDesign?.details ?? '',
        effective_date: editingDesign?.effective_date ?? '',
        active: editingDesign?.active ?? true,
      })
    }
  }, [designFormOpen, editingDesign, brandFilter, designForm])

  const designMutation = useMutation({
    mutationFn: async (values: DesignFormValues) => {
      const input = {
        ...values,
        details: values.details || null,
        effective_date: values.effective_date || null,
      }
      if (editingDesign) {
        return updateHouseDesign(editingDesign.design_id, input)
      }
      return createHouseDesign(input)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['house-designs'] })
      toast({ title: editingDesign ? 'Design updated' : 'Design created', variant: 'success' })
      setDesignFormOpen(false)
      setEditingDesign(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const designDeleteMut = useMutation({
    mutationFn: (id: number) => deleteHouseDesign(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['house-designs'] })
      toast({ title: 'Design deleted', variant: 'success' })
      setDeleteDesign(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  // --- Facade form ---
  const facadeForm = useForm<FacadeFormValues>({
    resolver: zodResolver(facadeSchema),
    defaultValues: { facade_name: '', facade_price: 0, facade_details: '', is_included: false },
  })

  useEffect(() => {
    if (facadeFormOpen) {
      facadeForm.reset({
        facade_name: editingFacade?.facade_name ?? '',
        facade_price: editingFacade?.facade_price ?? 0,
        facade_details: editingFacade?.facade_details ?? '',
        is_included: editingFacade?.is_included ?? false,
      })
    }
  }, [facadeFormOpen, editingFacade, facadeForm])

  const facadeMutation = useMutation({
    mutationFn: async (values: FacadeFormValues) => {
      const input = { ...values, facade_details: values.facade_details || null }
      if (editingFacade && facadeDesignId) {
        return updateFacade(facadeDesignId, editingFacade.facade_id, input)
      }
      if (facadeDesignId) {
        return createFacade(facadeDesignId, input)
      }
      throw new Error('No design selected')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['house-designs'] })
      toast({ title: editingFacade ? 'Facade updated' : 'Facade created', variant: 'success' })
      setFacadeFormOpen(false)
      setEditingFacade(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const facadeDeleteMut = useMutation({
    mutationFn: ({ designId, facadeId }: { designId: number; facadeId: number }) =>
      deleteFacade(designId, facadeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['house-designs'] })
      toast({ title: 'Facade deleted', variant: 'success' })
      setDeleteFacadeTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  function openNewDesign() {
    setEditingDesign(null)
    setDesignFormOpen(true)
  }

  function openEditDesign(d: HouseDesignRead) {
    setEditingDesign(d)
    setDesignFormOpen(true)
  }

  function openNewFacade(designId: number) {
    setFacadeDesignId(designId)
    setEditingFacade(null)
    setFacadeFormOpen(true)
  }

  function openEditFacade(designId: number, f: HouseFacadeRead) {
    setFacadeDesignId(designId)
    setEditingFacade(f)
    setFacadeFormOpen(true)
  }

  return (
    <div>
      <PageHeader
        title="House Designs"
        description="Manage house design catalog and facades."
        actions={
          <Button onClick={openNewDesign}>
            <Plus className="h-4 w-4" /> New Design
          </Button>
        }
      />

      <div className="mb-4 flex gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Brand</label>
          <select
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            value={brandFilter}
            onChange={(e) => { setBrandFilter(e.target.value); setExpandedDesign(null) }}
          >
            {BRANDS.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-8" />
              <TableHead>House Name</TableHead>
              <TableHead>Storey</TableHead>
              <TableHead className="text-right">Base Price</TableHead>
              <TableHead className="text-right">Frontage</TableHead>
              <TableHead className="text-right">Squares</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Facades</TableHead>
              <TableHead className="w-16" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
              </TableRow>
            ) : !designs?.length ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center text-sm text-muted-foreground">No designs found.</TableCell>
              </TableRow>
            ) : (
              designs.map((d) => {
                const isExpanded = expandedDesign === d.design_id
                return (
                  <>
                    <TableRow
                      key={d.design_id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => setExpandedDesign(isExpanded ? null : d.design_id)}
                    >
                      <TableCell>
                        {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                      </TableCell>
                      <TableCell className="font-medium">{d.house_name}</TableCell>
                      <TableCell>{d.storey}</TableCell>
                      <TableCell className="text-right">${d.base_price.toLocaleString()}</TableCell>
                      <TableCell className="text-right">{d.frontage}m</TableCell>
                      <TableCell className="text-right">{d.squares}</TableCell>
                      <TableCell>
                        <Badge variant={d.active ? 'default' : 'secondary'}>
                          {d.active ? 'Active' : 'Inactive'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">{d.facades.length}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" onClick={(e) => e.stopPropagation()}>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => openEditDesign(d)}>Edit</DropdownMenuItem>
                            <DropdownMenuItem
                              className="text-destructive focus:text-destructive"
                              onClick={() => setDeleteDesign(d)}
                            >
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                    {isExpanded && (
                      <TableRow key={`${d.design_id}-facades`}>
                        <TableCell colSpan={9} className="bg-muted/30 p-4">
                          <div className="mb-2 flex items-center justify-between">
                            <span className="text-sm font-medium">Facades</span>
                            <Button variant="outline" size="sm" onClick={() => openNewFacade(d.design_id)}>
                              <Plus className="mr-1 h-3 w-3" /> Add Facade
                            </Button>
                          </div>
                          {d.facades.length === 0 ? (
                            <p className="text-sm text-muted-foreground">No facades yet.</p>
                          ) : (
                            <Table>
                              <TableHeader>
                                <TableRow>
                                  <TableHead>Name</TableHead>
                                  <TableHead className="text-right">Price</TableHead>
                                  <TableHead>Included</TableHead>
                                  <TableHead>Details</TableHead>
                                  <TableHead className="w-16" />
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {d.facades.map((f) => (
                                  <TableRow key={f.facade_id}>
                                    <TableCell className="font-medium">{f.facade_name}</TableCell>
                                    <TableCell className="text-right">${f.facade_price.toLocaleString()}</TableCell>
                                    <TableCell>
                                      <Badge variant={f.is_included ? 'default' : 'outline'}>
                                        {f.is_included ? 'Yes' : 'No'}
                                      </Badge>
                                    </TableCell>
                                    <TableCell className="max-w-[200px] truncate text-sm text-muted-foreground">
                                      {f.facade_details ?? '-'}
                                    </TableCell>
                                    <TableCell>
                                      <div className="flex gap-1">
                                        <Button variant="ghost" size="icon" onClick={() => openEditFacade(d.design_id, f)}>
                                          <Pencil className="h-3 w-3" />
                                        </Button>
                                        <Button
                                          variant="ghost"
                                          size="icon"
                                          onClick={() => setDeleteFacadeTarget({ designId: d.design_id, facade: f })}
                                        >
                                          <Trash2 className="h-3 w-3" />
                                        </Button>
                                      </div>
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          )}
                        </TableCell>
                      </TableRow>
                    )}
                  </>
                )
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Design Form Dialog */}
      <Dialog open={designFormOpen} onOpenChange={setDesignFormOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingDesign ? 'Edit House Design' : 'New House Design'}</DialogTitle>
          </DialogHeader>
          <Form {...designForm}>
            <form onSubmit={designForm.handleSubmit((v) => designMutation.mutate(v))} className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <FormField control={designForm.control} name="brand" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Brand *</FormLabel>
                    <FormControl>
                      <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...field}>
                        {BRANDS.map((b) => <option key={b} value={b}>{b}</option>)}
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={designForm.control} name="house_name" render={({ field }) => (
                  <FormItem>
                    <FormLabel>House Name *</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={designForm.control} name="storey" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Storey *</FormLabel>
                    <FormControl>
                      <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" {...field}>
                        <option value="Single">Single</option>
                        <option value="Double">Double</option>
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
              </div>
              <div className="grid grid-cols-4 gap-4">
                <FormField control={designForm.control} name="base_price" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Base Price *</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={designForm.control} name="frontage" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Frontage (m) *</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={designForm.control} name="depth" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Depth (m) *</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={designForm.control} name="squares" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Squares *</FormLabel>
                    <FormControl><Input type="number" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
              </div>
              <div className="grid grid-cols-4 gap-4">
                <FormField control={designForm.control} name="gf_sqm" render={({ field }) => (
                  <FormItem>
                    <FormLabel>GF sqm</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={designForm.control} name="total_sqm" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Total sqm</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={designForm.control} name="lot_total_sqm" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Lot Total sqm</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={designForm.control} name="effective_date" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Effective Date</FormLabel>
                    <FormControl><Input type="date" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <FormField control={designForm.control} name="details" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Details</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={designForm.control} name="active" render={({ field }) => (
                  <FormItem className="flex items-end gap-2 pb-2">
                    <FormControl>
                      <input type="checkbox" checked={field.value} onChange={field.onChange} className="h-4 w-4 rounded border" />
                    </FormControl>
                    <FormLabel>Active</FormLabel>
                  </FormItem>
                )} />
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setDesignFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={designMutation.isPending}>
                  {designMutation.isPending ? 'Saving...' : editingDesign ? 'Save' : 'Create'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* Facade Form Dialog */}
      <Dialog open={facadeFormOpen} onOpenChange={setFacadeFormOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{editingFacade ? 'Edit Facade' : 'New Facade'}</DialogTitle>
          </DialogHeader>
          <Form {...facadeForm}>
            <form onSubmit={facadeForm.handleSubmit((v) => facadeMutation.mutate(v))} className="space-y-4">
              <FormField control={facadeForm.control} name="facade_name" render={({ field }) => (
                <FormItem>
                  <FormLabel>Facade Name *</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={facadeForm.control} name="facade_price" render={({ field }) => (
                <FormItem>
                  <FormLabel>Facade Price</FormLabel>
                  <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={facadeForm.control} name="facade_details" render={({ field }) => (
                <FormItem>
                  <FormLabel>Details</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={facadeForm.control} name="is_included" render={({ field }) => (
                <FormItem className="flex items-center gap-2">
                  <FormControl>
                    <input type="checkbox" checked={field.value} onChange={field.onChange} className="h-4 w-4 rounded border" />
                  </FormControl>
                  <FormLabel>Included in base price</FormLabel>
                </FormItem>
              )} />
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setFacadeFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={facadeMutation.isPending}>
                  {facadeMutation.isPending ? 'Saving...' : editingFacade ? 'Save' : 'Create'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmations */}
      <ConfirmDialog
        open={!!deleteDesign}
        onOpenChange={(o) => !o && setDeleteDesign(null)}
        title="Delete house design?"
        description={deleteDesign ? `"${deleteDesign.house_name}" and all its facades will be permanently removed.` : ''}
        confirmLabel="Delete"
        variant="destructive"
        loading={designDeleteMut.isPending}
        onConfirm={() => deleteDesign && designDeleteMut.mutate(deleteDesign.design_id)}
      />
      <ConfirmDialog
        open={!!deleteFacadeTarget}
        onOpenChange={(o) => !o && setDeleteFacadeTarget(null)}
        title="Delete facade?"
        description={deleteFacadeTarget ? `"${deleteFacadeTarget.facade.facade_name}" will be permanently removed.` : ''}
        confirmLabel="Delete"
        variant="destructive"
        loading={facadeDeleteMut.isPending}
        onConfirm={() =>
          deleteFacadeTarget &&
          facadeDeleteMut.mutate({ designId: deleteFacadeTarget.designId, facadeId: deleteFacadeTarget.facade.facade_id })
        }
      />
    </div>
  )
}
