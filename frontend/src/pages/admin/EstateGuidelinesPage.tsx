import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { MoreHorizontal, Plus } from 'lucide-react'
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
  description: z.string().min(1),
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

export default function EstateGuidelinesPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  // ---- Estate / Stage selection ---------------------------------------------
  const [selectedEstateId, setSelectedEstateId] = useState<number | null>(null)
  const [selectedStageId, setSelectedStageId] = useState<number | null>(null)

  // ---- Type state -----------------------------------------------------------
  const [typeFormOpen, setTypeFormOpen] = useState(false)
  const [editingType, setEditingType] = useState<GuidelineTypeRead | null>(null)
  const [deleteTypeTarget, setDeleteTypeTarget] = useState<GuidelineTypeRead | null>(null)

  // ---- Guideline state ------------------------------------------------------
  const [glFormOpen, setGlFormOpen] = useState(false)
  const [editingGl, setEditingGl] = useState<EstateGuidelineRead | null>(null)
  const [deleteGlTarget, setDeleteGlTarget] = useState<EstateGuidelineRead | null>(null)

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
    queryFn: () => listStages(selectedEstateId!),
    enabled: selectedEstateId !== null,
  })

  const { data: guidelines, isLoading: glLoading } = useQuery({
    queryKey: ['estate-guidelines', selectedEstateId, selectedStageId],
    queryFn: () => listEstateGuidelines(selectedEstateId!, selectedStageId),
    enabled: selectedEstateId !== null,
  })

  // Reset stage when estate changes
  useEffect(() => {
    setSelectedStageId(null)
  }, [selectedEstateId])

  // ---- Type form ------------------------------------------------------------
  const typeForm = useForm<TypeValues>({
    resolver: zodResolver(typeSchema),
    defaultValues: { short_name: '', description: '', sort_order: 0 },
  })

  useEffect(() => {
    if (typeFormOpen) {
      typeForm.reset({
        short_name: editingType?.short_name ?? '',
        description: editingType?.description ?? '',
        sort_order: editingType?.sort_order ?? 0,
      })
    }
  }, [typeFormOpen, editingType, typeForm])

  const saveType = useMutation({
    mutationFn: async (values: TypeValues) => {
      if (editingType) return updateGuidelineType(editingType.type_id, values)
      return createGuidelineType(values)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guideline-types'] })
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
        estate_id: selectedEstateId!,
        stage_id: selectedStageId ?? null,
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

  // ---- Helpers --------------------------------------------------------------
  const openNewType = () => { setEditingType(null); setTypeFormOpen(true) }
  const openEditType = (t: GuidelineTypeRead) => { setEditingType(t); setTypeFormOpen(true) }
  const openNewGl = () => { setEditingGl(null); setGlFormOpen(true) }
  const openEditGl = (g: EstateGuidelineRead) => { setEditingGl(g); setGlFormOpen(true) }

  return (
    <div>
      <PageHeader
        title="Estate Guidelines"
        description="Manage guideline types and per-estate design guideline overrides."
        actions={
          <div className="flex gap-2">
            <CsvImportButton endpoint="/api/guidelines/types/upload-csv" label="Import Types" onSuccess={() => queryClient.invalidateQueries({ queryKey: ['guideline-types'] })} />
            <CsvImportButton endpoint="/api/guidelines/estate/upload-csv" label="Import Guidelines" onSuccess={() => { queryClient.invalidateQueries({ queryKey: ['guideline-types'] }); queryClient.invalidateQueries({ queryKey: ['estate-guidelines'] }) }} />
          </div>
        }
      />

      {/* ---- Guideline Types ---- */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold">Guideline Types</h2>
          <Button size="sm" onClick={openNewType}>
            <Plus className="h-4 w-4" /> New Type
          </Button>
        </div>
        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Short Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead className="w-24">Sort Order</TableHead>
                <TableHead className="w-16"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {typesLoading ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : typesData?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">No guideline types yet.</TableCell>
                </TableRow>
              ) : (
                typesData?.map((t) => (
                  <TableRow key={t.type_id}>
                    <TableCell className="font-medium">{t.short_name}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{t.description}</TableCell>
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

      {/* ---- Estate Guidelines ---- */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold">Estate Design Guidelines</h2>
          <Button size="sm" onClick={openNewGl} disabled={selectedEstateId === null}>
            <Plus className="h-4 w-4" /> New Guideline
          </Button>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-4">
          <Select
            value={selectedEstateId !== null ? String(selectedEstateId) : '__none__'}
            onValueChange={(v) => setSelectedEstateId(v === '__none__' ? null : Number(v))}
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
            value={selectedStageId !== null ? String(selectedStageId) : '__none__'}
            onValueChange={(v) => setSelectedStageId(v === '__none__' ? null : Number(v))}
            disabled={selectedEstateId === null}
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
                <TableHead>Guideline Type</TableHead>
                <TableHead className="w-32">Cost</TableHead>
                <TableHead>Override Text</TableHead>
                <TableHead className="w-16"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {selectedEstateId === null ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">Select an estate to view guidelines.</TableCell>
                </TableRow>
              ) : glLoading ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : guidelines?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">No guidelines for this estate.</TableCell>
                </TableRow>
              ) : (
                guidelines?.map((g) => (
                  <TableRow key={g.guideline_id}>
                    <TableCell className="font-medium">{g.guideline_type_name ?? `Type #${g.type_id}`}</TableCell>
                    <TableCell>
                      {g.cost !== null && g.cost !== undefined
                        ? `$${Number(g.cost).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
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
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* ---- Type dialog ---- */}
      <Dialog open={typeFormOpen} onOpenChange={setTypeFormOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingType ? 'Edit guideline type' : 'New guideline type'}</DialogTitle>
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
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description *</FormLabel>
                    <FormControl><Textarea {...field} /></FormControl>
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
                    <FormLabel>Cost</FormLabel>
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
                    <FormLabel>Override Text</FormLabel>
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

      {/* ---- Confirm dialogs ---- */}
      <ConfirmDialog
        open={!!deleteTypeTarget}
        onOpenChange={(o) => !o && setDeleteTypeTarget(null)}
        title="Delete guideline type?"
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
