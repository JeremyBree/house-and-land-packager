import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Copy, MoreHorizontal, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { CsvImportButton } from '@/components/common/CsvImportButton'
import {
  listGuidelineTypes,
  createGuidelineType,
  updateGuidelineType,
  deleteGuidelineType,
  listEstateGuidelines,
  createEstateGuideline,
  updateEstateGuideline,
  deleteEstateGuideline,
  copyGuidelines,
} from '@/api/guidelines'
import type { GuidelineTypeRead, EstateGuidelineRead } from '@/api/guidelines'
import { listEstates } from '@/api/estates'
import { listStages } from '@/api/stages'
import type { EstateRead, StageRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

// ---- Type schemas -----------------------------------------------------------

const typeSchema = z.object({
  short_name: z.string().min(1).max(100),
  category_code: z.string().max(20).optional().or(z.literal('')),
  category_name: z.string().max(200).optional().or(z.literal('')),
  description: z.string().optional().or(z.literal('')),
  notes: z.string().optional().or(z.literal('')),
  default_price: z.coerce.number().default(0),
  sort_order: z.coerce.number().int().default(0),
})
type TypeValues = z.infer<typeof typeSchema>

// ---- Guideline schemas ------------------------------------------------------

const guidelineSchema = z.object({
  type_id: z.coerce.number().int().min(1, 'Required'),
  cost: z.coerce.number().optional().or(z.literal('')),
  override_text: z.string().optional().or(z.literal('')),
})
type GuidelineValues = z.infer<typeof guidelineSchema>

// ---- Copy schema ------------------------------------------------------------

const copySchema = z.object({
  target_estate_id: z.coerce.number().int().min(1, 'Required'),
  target_stage_id: z.coerce.number().int().optional().or(z.literal('')),
})
type CopyValues = z.infer<typeof copySchema>

function formatPrice(value: number | null | undefined): string {
  if (value === null || value === undefined) return ''
  return `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export default function EstateGuidelinesPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [searchParams] = useSearchParams()

  // ---- Estate / Stage selection ---------------------------------------------
  const [selectedEstateId, setSelectedEstateId] = useState<number | ''>(
    searchParams.get('estate_id') ? Number(searchParams.get('estate_id')) : ''
  )
  const [selectedStageId, setSelectedStageId] = useState<number | ''>(
    searchParams.get('stage_id') ? Number(searchParams.get('stage_id')) : ''
  )

  // ---- Type state -----------------------------------------------------------
  const [typeFormOpen, setTypeFormOpen] = useState(false)
  const [editingType, setEditingType] = useState<GuidelineTypeRead | null>(null)
  const [deleteTypeTarget, setDeleteTypeTarget] = useState<GuidelineTypeRead | null>(null)

  // ---- Guideline state ------------------------------------------------------
  const [glFormOpen, setGlFormOpen] = useState(false)
  const [editingGl, setEditingGl] = useState<EstateGuidelineRead | null>(null)
  const [deleteGlTarget, setDeleteGlTarget] = useState<EstateGuidelineRead | null>(null)

  // ---- Copy state -----------------------------------------------------------
  const [copyDialogOpen, setCopyDialogOpen] = useState(false)

  // ---- Queries --------------------------------------------------------------
  const { data: typesData, isLoading: typesLoading } = useQuery({
    queryKey: ['guideline-types'],
    queryFn: () => listGuidelineTypes(),
  })

  const { data: estatesData } = useQuery({
    queryKey: ['estates-all'],
    queryFn: () => listEstates({ size: 1000 }),
  })
  const estates: EstateRead[] = estatesData?.items ?? []

  const { data: stages } = useQuery({
    queryKey: ['stages', selectedEstateId],
    queryFn: () => listStages(selectedEstateId as number),
    enabled: selectedEstateId !== '',
  })

  const { data: guidelines, isLoading: glLoading } = useQuery({
    queryKey: ['estate-guidelines', selectedEstateId, selectedStageId],
    queryFn: () =>
      listEstateGuidelines(
        selectedEstateId as number,
        selectedStageId !== '' ? (selectedStageId as number) : null,
      ),
    enabled: selectedEstateId !== '',
  })

  // Reset stage when estate changes (but not on initial mount from URL params)
  const [initialMount, setInitialMount] = useState(true)
  useEffect(() => {
    if (initialMount) {
      setInitialMount(false)
      return
    }
    setSelectedStageId('')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedEstateId])

  // ---- Copy form targets: separate estate/stage queries ---------------------
  const [copyTargetEstateId, setCopyTargetEstateId] = useState<number | ''>('' )
  const { data: copyTargetStages } = useQuery({
    queryKey: ['stages', copyTargetEstateId],
    queryFn: () => listStages(copyTargetEstateId as number),
    enabled: copyTargetEstateId !== '',
  })

  // ---- Type form ------------------------------------------------------------
  const typeForm = useForm<TypeValues>({
    resolver: zodResolver(typeSchema),
    defaultValues: { short_name: '', category_code: '', category_name: '', description: '', notes: '', default_price: 0, sort_order: 0 },
  })

  useEffect(() => {
    if (typeFormOpen) {
      typeForm.reset({
        short_name: editingType?.short_name ?? '',
        category_code: editingType?.category_code ?? '',
        category_name: editingType?.category_name ?? '',
        description: editingType?.description ?? '',
        notes: editingType?.notes ?? '',
        default_price: editingType?.default_price ?? 0,
        sort_order: editingType?.sort_order ?? 0,
      })
    }
  }, [typeFormOpen, editingType, typeForm])

  const saveType = useMutation({
    mutationFn: async (values: TypeValues) => {
      const payload = {
        short_name: values.short_name,
        category_code: values.category_code || null,
        category_name: values.category_name || null,
        description: values.description || '',
        notes: values.notes || null,
        default_price: values.default_price,
        sort_order: values.sort_order,
      }
      if (editingType) return updateGuidelineType(editingType.type_id, payload)
      return createGuidelineType(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guideline-types'] })
      queryClient.invalidateQueries({ queryKey: ['estate-guidelines'] })
      toast({ title: editingType ? 'Type updated' : 'Type created', variant: 'success' })
      setTypeFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const removeType = useMutation({
    mutationFn: (id: number) => deleteGuidelineType(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guideline-types'] })
      queryClient.invalidateQueries({ queryKey: ['estate-guidelines'] })
      toast({ title: 'Type deleted', variant: 'success' })
      setDeleteTypeTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  // ---- Guideline form -------------------------------------------------------
  const glForm = useForm<GuidelineValues>({
    resolver: zodResolver(guidelineSchema),
    defaultValues: { type_id: 0, cost: '', override_text: '' },
  })

  useEffect(() => {
    if (glFormOpen) {
      glForm.reset({
        type_id: editingGl?.type_id ?? 0,
        cost: editingGl?.cost ?? '',
        override_text: editingGl?.override_text ?? '',
      })
    }
  }, [glFormOpen, editingGl, glForm])

  const saveGl = useMutation({
    mutationFn: async (values: GuidelineValues) => {
      const payload = {
        estate_id: selectedEstateId as number,
        stage_id: selectedStageId !== '' ? (selectedStageId as number) : null,
        type_id: values.type_id,
        cost: values.cost !== '' && values.cost !== undefined ? Number(values.cost) : null,
        override_text: values.override_text || null,
      }
      if (editingGl) return updateEstateGuideline(editingGl.guideline_id, payload)
      return createEstateGuideline(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estate-guidelines'] })
      toast({ title: editingGl ? 'Guideline updated' : 'Guideline created', variant: 'success' })
      setGlFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const removeGl = useMutation({
    mutationFn: (id: number) => deleteEstateGuideline(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estate-guidelines'] })
      toast({ title: 'Guideline deleted', variant: 'success' })
      setDeleteGlTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  // ---- Copy mutation --------------------------------------------------------
  const copyForm = useForm<CopyValues>({
    resolver: zodResolver(copySchema),
    defaultValues: { target_estate_id: '' as unknown as number, target_stage_id: '' },
  })

  useEffect(() => {
    if (copyDialogOpen) {
      copyForm.reset({ target_estate_id: '' as unknown as number, target_stage_id: '' })
      setCopyTargetEstateId('')
    }
  }, [copyDialogOpen, copyForm])

  const copyMutation = useMutation({
    mutationFn: async (values: CopyValues) => {
      return copyGuidelines({
        source_estate_id: selectedEstateId as number,
        source_stage_id: selectedStageId !== '' ? (selectedStageId as number) : null,
        target_estate_id: values.target_estate_id,
        target_stage_id: values.target_stage_id !== '' && values.target_stage_id !== undefined ? Number(values.target_stage_id) : null,
      })
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['estate-guidelines'] })
      toast({ title: `Copied ${result.copied} guideline(s)`, variant: 'success' })
      setCopyDialogOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  // ---- Helpers --------------------------------------------------------------
  const openNewType = () => { setEditingType(null); setTypeFormOpen(true) }
  const openEditType = (t: GuidelineTypeRead) => { setEditingType(t); setTypeFormOpen(true) }
  const openNewGl = () => { setEditingGl(null); setGlFormOpen(true) }
  const openEditGl = (g: EstateGuidelineRead) => { setEditingGl(g); setGlFormOpen(true) }

  return (
    <div>
      <PageHeader
        title="Design Guidelines"
        description="Manage guideline categories and per-estate design guideline overrides."
        actions={
          <div className="flex gap-2">
            <CsvImportButton endpoint="/api/guidelines/types/upload-csv" label="Import Types" onSuccess={() => queryClient.invalidateQueries({ queryKey: ['guideline-types'] })} />
            <CsvImportButton endpoint="/api/guidelines/estate/upload-csv" label="Import Guidelines" onSuccess={() => { queryClient.invalidateQueries({ queryKey: ['guideline-types'] }); queryClient.invalidateQueries({ queryKey: ['estate-guidelines'] }) }} />
          </div>
        }
      />

      {/* ---- Section 1: Guideline Categories ---- */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold">Guideline Categories</h2>
          <Button size="sm" onClick={openNewType}>
            <Plus className="h-4 w-4" /> New Category
          </Button>
        </div>
        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Category Code</TableHead>
                <TableHead>Category Name</TableHead>
                <TableHead className="w-32">Default Price ($)</TableHead>
                <TableHead>Description</TableHead>
                <TableHead className="w-24">Sort Order</TableHead>
                <TableHead className="w-16"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {typesLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : typesData?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-sm text-muted-foreground">No guideline categories yet.</TableCell>
                </TableRow>
              ) : (
                typesData?.map((t) => (
                  <TableRow key={t.type_id}>
                    <TableCell className="font-medium">{t.category_code ?? '—'}</TableCell>
                    <TableCell>{t.category_name ?? t.short_name}</TableCell>
                    <TableCell>{formatPrice(t.default_price)}</TableCell>
                    <TableCell className="text-sm text-muted-foreground max-w-xs truncate">{t.description || '—'}</TableCell>
                    <TableCell>{t.sort_order}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => openEditType(t)}>Edit</DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive focus:text-destructive"
                            onClick={() => setDeleteTypeTarget(t)}
                          >
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* ---- Section 2: Estate Design Guidelines ---- */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold">Estate Design Guidelines</h2>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setCopyDialogOpen(true)}
              disabled={selectedEstateId === ''}
            >
              <Copy className="h-4 w-4" /> Copy Guidelines
            </Button>
            <Button size="sm" onClick={openNewGl} disabled={selectedEstateId === ''}>
              <Plus className="h-4 w-4" /> New Guideline
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-4">
          <Select
            value={selectedEstateId !== '' ? String(selectedEstateId) : '__none__'}
            onValueChange={(v) => setSelectedEstateId(v === '__none__' ? '' : Number(v))}
          >
            <SelectTrigger className="w-[280px]">
              <SelectValue placeholder="Select estate..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__none__">-- Select Estate --</SelectItem>
              {estates.map((e) => (
                <SelectItem key={e.estate_id} value={String(e.estate_id)}>{e.estate_name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={selectedStageId !== '' ? String(selectedStageId) : '__none__'}
            onValueChange={(v) => setSelectedStageId(v === '__none__' ? '' : Number(v))}
            disabled={selectedEstateId === ''}
          >
            <SelectTrigger className="w-[220px]">
              <SelectValue placeholder="All stages" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__none__">All Stages</SelectItem>
              {stages?.map((s: StageRead) => (
                <SelectItem key={s.stage_id} value={String(s.stage_id)}>{s.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Category Name</TableHead>
                <TableHead className="w-36">Default Price</TableHead>
                <TableHead className="w-36">Override Price</TableHead>
                <TableHead>Override Description</TableHead>
                <TableHead className="w-16"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {selectedEstateId === '' ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">Select an estate to view guidelines.</TableCell>
                </TableRow>
              ) : glLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : guidelines?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">No guidelines for this estate.</TableCell>
                </TableRow>
              ) : (
                guidelines?.map((g) => {
                  const hasOverridePrice = g.cost !== null && g.cost !== undefined
                  return (
                    <TableRow key={g.guideline_id}>
                      <TableCell className="font-medium">{g.guideline_type_name ?? `Type #${g.type_id}`}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {g.default_price !== null && g.default_price !== undefined
                          ? formatPrice(g.default_price)
                          : '—'}
                      </TableCell>
                      <TableCell>
                        {hasOverridePrice
                          ? formatPrice(g.cost)
                          : g.default_price !== null && g.default_price !== undefined
                            ? <span className="text-muted-foreground">{formatPrice(g.default_price)}</span>
                            : '—'}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">{g.override_text ?? '—'}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => openEditGl(g)}>Edit</DropdownMenuItem>
                            <DropdownMenuItem
                              className="text-destructive focus:text-destructive"
                              onClick={() => setDeleteGlTarget(g)}
                            >
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  )
                })
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* ---- Type dialog ---- */}
      <Dialog open={typeFormOpen} onOpenChange={setTypeFormOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingType ? 'Edit guideline category' : 'New guideline category'}</DialogTitle>
          </DialogHeader>
          <Form {...typeForm}>
            <form onSubmit={typeForm.handleSubmit((v) => saveType.mutate(v))} className="space-y-4">
              <FormField
                control={typeForm.control}
                name="short_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Short Name *</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={typeForm.control}
                name="category_code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category Code</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={typeForm.control}
                name="category_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category Name</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={typeForm.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl><Textarea {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={typeForm.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Notes</FormLabel>
                    <FormControl><Textarea {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={typeForm.control}
                name="default_price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Default Price</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={typeForm.control}
                name="sort_order"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Sort Order</FormLabel>
                    <FormControl><Input type="number" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setTypeFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={saveType.isPending}>
                  {saveType.isPending ? 'Saving...' : 'Save'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* ---- Guideline dialog ---- */}
      <Dialog open={glFormOpen} onOpenChange={setGlFormOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingGl ? 'Edit guideline' : 'New guideline'}</DialogTitle>
          </DialogHeader>
          <Form {...glForm}>
            <form onSubmit={glForm.handleSubmit((v) => saveGl.mutate(v))} className="space-y-4">
              <FormField
                control={glForm.control}
                name="type_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Guideline Type *</FormLabel>
                    <Select
                      onValueChange={(v) => field.onChange(Number(v))}
                      value={field.value ? String(field.value) : ''}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type..." />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {typesData?.map((t) => (
                          <SelectItem key={t.type_id} value={String(t.type_id)}>{t.short_name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={glForm.control}
                name="cost"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Override Price</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={glForm.control}
                name="override_text"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Override Description</FormLabel>
                    <FormControl><Textarea {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setGlFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={saveGl.isPending}>
                  {saveGl.isPending ? 'Saving...' : 'Save'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* ---- Copy dialog ---- */}
      <Dialog open={copyDialogOpen} onOpenChange={setCopyDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Copy Guidelines</DialogTitle>
          </DialogHeader>
          <Form {...copyForm}>
            <form
              onSubmit={copyForm.handleSubmit((v) => copyMutation.mutate(v))}
              className="space-y-4"
            >
              <div className="text-sm text-muted-foreground">
                Copy all guidelines from the currently selected estate
                {selectedStageId !== '' ? ' and stage' : ''} to a target estate/stage.
              </div>
              <FormField
                control={copyForm.control}
                name="target_estate_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Target Estate *</FormLabel>
                    <Select
                      onValueChange={(v) => {
                        field.onChange(Number(v))
                        setCopyTargetEstateId(Number(v))
                        copyForm.setValue('target_stage_id', '')
                      }}
                      value={field.value ? String(field.value) : ''}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select estate..." />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {estates.map((e) => (
                          <SelectItem key={e.estate_id} value={String(e.estate_id)}>{e.estate_name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={copyForm.control}
                name="target_stage_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Target Stage (optional)</FormLabel>
                    <Select
                      onValueChange={(v) => field.onChange(v === '__none__' ? '' : Number(v))}
                      value={field.value ? String(field.value) : '__none__'}
                      disabled={copyTargetEstateId === ''}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="All stages" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="__none__">-- No stage --</SelectItem>
                        {copyTargetStages?.map((s: StageRead) => (
                          <SelectItem key={s.stage_id} value={String(s.stage_id)}>{s.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setCopyDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={copyMutation.isPending}>
                  {copyMutation.isPending ? 'Copying...' : 'Copy'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* ---- Confirm dialogs ---- */}
      <ConfirmDialog
        open={!!deleteTypeTarget}
        onOpenChange={(o) => !o && setDeleteTypeTarget(null)}
        title="Delete guideline category?"
        description={deleteTypeTarget ? `"${deleteTypeTarget.short_name}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={removeType.isPending}
        onConfirm={() => deleteTypeTarget && removeType.mutate(deleteTypeTarget.type_id)}
      />

      <ConfirmDialog
        open={!!deleteGlTarget}
        onOpenChange={(o) => !o && setDeleteGlTarget(null)}
        title="Delete guideline?"
        description={deleteGlTarget ? `Guideline "${deleteGlTarget.guideline_type_name}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={removeGl.isPending}
        onConfirm={() => deleteGlTarget && removeGl.mutate(deleteGlTarget.guideline_id)}
      />
    </div>
  )
}
