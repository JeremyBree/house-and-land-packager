import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft, ChevronDown, ChevronRight, Copy, MoreHorizontal, Plus } from 'lucide-react'
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
  listEstateGuidelines,
  createEstateGuideline,
  updateEstateGuideline,
  deleteEstateGuideline,
  copyGuidelines,
} from '@/api/guidelines'
import type { EstateGuidelineRead, GuidelineTypeRead } from '@/api/guidelines'
import { getEstate } from '@/api/estates'
import { listEstates } from '@/api/estates'
import { listStages } from '@/api/stages'
import type { StageRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const guidelineSchema = z.object({
  type_id: z.coerce.number().int().min(1, 'Required'),
  cost: z.coerce.number().optional().or(z.literal('')),
  override_text: z.string().optional().or(z.literal('')),
})
type GuidelineValues = z.infer<typeof guidelineSchema>

const copySchema = z.object({
  target_estate_id: z.coerce.number().int().min(1, 'Required'),
  target_stage_id: z.coerce.number().int().optional().or(z.literal('')),
})
type CopyValues = z.infer<typeof copySchema>

function formatPrice(value: number | null | undefined): string {
  if (value === null || value === undefined) return ''
  return `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

/** Build a map of category_code -> GuidelineTypeRead[] for the hierarchical picker. */
function buildCodeGroups(types: GuidelineTypeRead[]): Map<string, GuidelineTypeRead[]> {
  const map = new Map<string, GuidelineTypeRead[]>()
  for (const t of types) {
    const code = t.category_code || t.short_name
    if (!map.has(code)) map.set(code, [])
    map.get(code)!.push(t)
  }
  return map
}

/** Group guidelines by category_code for table display. */
function groupByCode(guidelines: EstateGuidelineRead[]): Map<string, EstateGuidelineRead[]> {
  const map = new Map<string, EstateGuidelineRead[]>()
  for (const g of guidelines) {
    const code = g.category_code || g.guideline_type_name || `type-${g.type_id}`
    if (!map.has(code)) map.set(code, [])
    map.get(code)!.push(g)
  }
  return map
}

export default function EstateGuidelinesPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [searchParams] = useSearchParams()

  const estateId = searchParams.get('estate_id') ? Number(searchParams.get('estate_id')) : null
  const stageId = searchParams.get('stage_id') ? Number(searchParams.get('stage_id')) : null

  const [glFormOpen, setGlFormOpen] = useState(false)
  const [editingGl, setEditingGl] = useState<EstateGuidelineRead | null>(null)
  const [deleteGlTarget, setDeleteGlTarget] = useState<EstateGuidelineRead | null>(null)
  const [copyDialogOpen, setCopyDialogOpen] = useState(false)
  const [copyTargetEstateId, setCopyTargetEstateId] = useState<number | ''>('')

  // Hierarchical picker state
  const [selectedCode, setSelectedCode] = useState<string>('')

  // Collapsed code groups in table
  const [collapsedCodes, setCollapsedCodes] = useState<Set<string>>(new Set())

  // Fetch estate details for the header
  const { data: estate } = useQuery({
    queryKey: ['estate', estateId],
    queryFn: () => getEstate(estateId!),
    enabled: !!estateId,
  })

  // Fetch stages for this estate to find stage name
  const { data: stages } = useQuery({
    queryKey: ['stages', estateId],
    queryFn: () => listStages(estateId!),
    enabled: !!estateId,
  })
  const selectedStage = stages?.find((s) => s.stage_id === stageId)

  // Fetch guideline types for the add dialog
  const { data: typesData } = useQuery({
    queryKey: ['guideline-types'],
    queryFn: () => listGuidelineTypes(),
  })

  // Fetch guidelines for this estate/stage
  const { data: guidelines, isLoading } = useQuery({
    queryKey: ['estate-guidelines', estateId, stageId],
    queryFn: () => listEstateGuidelines(estateId!, stageId),
    enabled: !!estateId,
  })

  // Build code groups for the hierarchical picker
  const codeGroups = useMemo(() => typesData ? buildCodeGroups(typesData) : new Map<string, GuidelineTypeRead[]>(), [typesData])
  const sortedCodes = useMemo(() => [...codeGroups.keys()].sort(), [codeGroups])

  // Get category names for the selected code
  const categoryNamesForCode = useMemo(
    () => (selectedCode ? codeGroups.get(selectedCode) || [] : []),
    [selectedCode, codeGroups],
  )

  // Group guidelines by code for table display
  const groupedGuidelines = useMemo(() => guidelines ? groupByCode(guidelines) : new Map(), [guidelines])

  // Copy dialog: estates and stages for target
  const { data: estatesData } = useQuery({
    queryKey: ['estates', { page: 1, size: 200 }],
    queryFn: () => listEstates({ page: 1, size: 200 }),
    enabled: copyDialogOpen,
  })
  const { data: copyTargetStages } = useQuery({
    queryKey: ['stages', copyTargetEstateId],
    queryFn: () => listStages(copyTargetEstateId as number),
    enabled: copyTargetEstateId !== '',
  })

  // Guideline form
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
      // Set the code picker to match editing item
      if (editingGl) {
        const matchingType = typesData?.find((t) => t.type_id === editingGl.type_id)
        setSelectedCode(matchingType?.category_code || matchingType?.short_name || '')
      } else {
        setSelectedCode('')
      }
    }
  }, [glFormOpen, editingGl, glForm, typesData])

  const saveGl = useMutation({
    mutationFn: async (values: GuidelineValues) => {
      const payload = {
        estate_id: estateId!,
        stage_id: stageId,
        type_id: values.type_id,
        cost: values.cost !== '' && values.cost !== undefined ? Number(values.cost) : null,
        override_text: values.override_text || null,
      }
      if (editingGl) return updateEstateGuideline(editingGl.guideline_id, payload)
      return createEstateGuideline(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estate-guidelines'] })
      toast({ title: editingGl ? 'Guideline updated' : 'Guideline added', variant: 'success' })
      setGlFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const removeGl = useMutation({
    mutationFn: (id: number) => deleteEstateGuideline(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estate-guidelines'] })
      toast({ title: 'Guideline removed', variant: 'success' })
      setDeleteGlTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  // Copy form
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
        source_estate_id: estateId!,
        source_stage_id: stageId,
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

  const toggleCodeCollapse = (code: string) => {
    setCollapsedCodes((prev) => {
      const next = new Set(prev)
      if (next.has(code)) next.delete(code)
      else next.add(code)
      return next
    })
  }

  // No estate selected — show instructions
  if (!estateId) {
    return (
      <div>
        <PageHeader title="Estate Guidelines" description="Configure design guidelines per estate and stage." />
        <div className="rounded-lg border bg-card p-8 text-center">
          <p className="text-muted-foreground mb-4">
            Navigate to an estate or stage from the <strong>Estates</strong> section, then click <strong>Manage Guidelines</strong> to configure guidelines.
          </p>
          <Link to="/estates">
            <Button variant="outline">Go to Estates</Button>
          </Link>
        </div>
      </div>
    )
  }

  const title = estate
    ? `${estate.estate_name}${selectedStage ? ` — ${selectedStage.name}` : ''}`
    : 'Estate Guidelines'

  return (
    <div>
      <PageHeader
        title={title}
        description="Configure which design guideline categories apply to this estate/stage and set override pricing."
        actions={
          <div className="flex gap-2">
            <CsvImportButton endpoint="/api/guidelines/estate/upload-csv" label="Import CSV" onSuccess={() => queryClient.invalidateQueries({ queryKey: ['estate-guidelines'] })} />
            <Button variant="outline" size="sm" onClick={() => setCopyDialogOpen(true)}>
              <Copy className="h-4 w-4" /> Copy From...
            </Button>
            <Button onClick={() => { setEditingGl(null); setGlFormOpen(true) }}>
              <Plus className="h-4 w-4" /> Add Guideline
            </Button>
          </div>
        }
      />

      <div className="mb-4">
        <Link to={estateId ? `/estates/${estateId}` : '/estates'} className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> Back to {estate?.estate_name ?? 'Estate'}
        </Link>
      </div>

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Code / Category</TableHead>
              <TableHead className="text-right w-36">Default Price</TableHead>
              <TableHead className="text-right w-36">Override Price</TableHead>
              <TableHead>Override Description</TableHead>
              <TableHead className="w-16" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
              </TableRow>
            ) : !guidelines?.length ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">No guidelines configured for this estate/stage yet.</TableCell>
              </TableRow>
            ) : (
              [...groupedGuidelines.entries()].map(([code, items]) => {
                const isCollapsed = collapsedCodes.has(code)
                const hasMultiple = items.length > 1
                return (
                  <TableGroupRows
                    key={code}
                    code={code}
                    items={items}
                    isCollapsed={isCollapsed}
                    hasMultiple={hasMultiple}
                    onToggle={() => toggleCodeCollapse(code)}
                    onEdit={(g) => { setEditingGl(g); setGlFormOpen(true) }}
                    onDelete={(g) => setDeleteGlTarget(g)}
                  />
                )
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Add/Edit Guideline dialog */}
      <Dialog open={glFormOpen} onOpenChange={setGlFormOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingGl ? 'Edit Guideline' : 'Add Guideline'}</DialogTitle>
          </DialogHeader>
          <Form {...glForm}>
            <form onSubmit={glForm.handleSubmit((v) => saveGl.mutate(v))} className="space-y-4">
              {/* Step 1: Select Code */}
              <FormItem>
                <FormLabel>Code *</FormLabel>
                <Select
                  value={selectedCode}
                  onValueChange={(v) => {
                    setSelectedCode(v)
                    // Clear type_id when code changes (unless single child)
                    const children = codeGroups.get(v) || []
                    if (children.length === 1) {
                      glForm.setValue('type_id', children[0].type_id)
                    } else {
                      glForm.setValue('type_id', 0)
                    }
                  }}
                >
                  <FormControl>
                    <SelectTrigger><SelectValue placeholder="Select code..." /></SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {sortedCodes.map((code) => (
                      <SelectItem key={code} value={code}>{code}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormItem>

              {/* Step 2: Select Category Name (filtered by code) */}
              <FormField control={glForm.control} name="type_id" render={({ field }) => (
                <FormItem>
                  <FormLabel>Category Name *</FormLabel>
                  <Select
                    onValueChange={(v) => field.onChange(Number(v))}
                    value={field.value ? String(field.value) : ''}
                    disabled={!selectedCode}
                  >
                    <FormControl>
                      <SelectTrigger><SelectValue placeholder={selectedCode ? 'Select category...' : 'Select a code first'} /></SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {categoryNamesForCode.map((t) => (
                        <SelectItem key={t.type_id} value={String(t.type_id)}>
                          {t.category_name || t.short_name}{t.default_price ? ` ($${t.default_price})` : ''}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={glForm.control} name="cost" render={({ field }) => (
                <FormItem>
                  <FormLabel>Override Price (leave blank to use default)</FormLabel>
                  <FormControl><Input type="number" step="0.01" placeholder="Use default price" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={glForm.control} name="override_text" render={({ field }) => (
                <FormItem>
                  <FormLabel>Override Description (optional)</FormLabel>
                  <FormControl><Textarea placeholder="Override the category description..." {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setGlFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={saveGl.isPending}>{saveGl.isPending ? 'Saving...' : 'Save'}</Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* Copy dialog */}
      <Dialog open={copyDialogOpen} onOpenChange={setCopyDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Copy Guidelines From Another Estate</DialogTitle>
          </DialogHeader>
          <Form {...copyForm}>
            <form onSubmit={copyForm.handleSubmit((v) => copyMutation.mutate(v))} className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Copy all guidelines from a source estate/stage into {estate?.estate_name ?? 'this estate'}{selectedStage ? ` — ${selectedStage.name}` : ''}. Existing guidelines won't be duplicated.
              </p>
              <FormField control={copyForm.control} name="target_estate_id" render={({ field }) => (
                <FormItem>
                  <FormLabel>Source Estate *</FormLabel>
                  <Select onValueChange={(v) => { field.onChange(Number(v)); setCopyTargetEstateId(Number(v)); copyForm.setValue('target_stage_id', '') }} value={field.value ? String(field.value) : ''}>
                    <FormControl><SelectTrigger><SelectValue placeholder="Select estate..." /></SelectTrigger></FormControl>
                    <SelectContent>
                      {estatesData?.items.map((e) => (
                        <SelectItem key={e.estate_id} value={String(e.estate_id)}>{e.estate_name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={copyForm.control} name="target_stage_id" render={({ field }) => (
                <FormItem>
                  <FormLabel>Source Stage (optional)</FormLabel>
                  <Select onValueChange={(v) => field.onChange(v === '__none__' ? '' : Number(v))} value={field.value ? String(field.value) : '__none__'} disabled={copyTargetEstateId === ''}>
                    <FormControl><SelectTrigger><SelectValue placeholder="All stages" /></SelectTrigger></FormControl>
                    <SelectContent>
                      <SelectItem value="__none__">-- No stage --</SelectItem>
                      {copyTargetStages?.map((s: StageRead) => (
                        <SelectItem key={s.stage_id} value={String(s.stage_id)}>{s.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )} />
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setCopyDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={copyMutation.isPending}>{copyMutation.isPending ? 'Copying...' : 'Copy Guidelines'}</Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* Confirm delete */}
      <ConfirmDialog
        open={!!deleteGlTarget}
        onOpenChange={(o) => !o && setDeleteGlTarget(null)}
        title="Remove guideline?"
        description={deleteGlTarget ? `"${deleteGlTarget.guideline_type_name}" will be removed from this estate configuration.` : undefined}
        confirmLabel="Remove"
        variant="destructive"
        loading={removeGl.isPending}
        onConfirm={() => deleteGlTarget && removeGl.mutate(deleteGlTarget.guideline_id)}
      />
    </div>
  )
}

/** Renders a code group header row + child rows for the grouped table. */
function TableGroupRows({
  code,
  items,
  isCollapsed,
  hasMultiple,
  onToggle,
  onEdit,
  onDelete,
}: {
  code: string
  items: EstateGuidelineRead[]
  isCollapsed: boolean
  hasMultiple: boolean
  onToggle: () => void
  onEdit: (g: EstateGuidelineRead) => void
  onDelete: (g: EstateGuidelineRead) => void
}) {
  // Single item under this code — render as a flat row
  if (!hasMultiple) {
    const g = items[0]
    const hasOverride = g.cost !== null && g.cost !== undefined
    return (
      <TableRow>
        <TableCell className="font-medium">
          <span className="text-xs text-muted-foreground mr-2">{code}</span>
          {g.category_description || g.guideline_type_name || `Type #${g.type_id}`}
        </TableCell>
        <TableCell className="text-right text-sm text-muted-foreground">
          {g.default_price != null ? formatPrice(g.default_price) : '-'}
        </TableCell>
        <TableCell className="text-right">
          {hasOverride ? (
            <span className="font-medium">{formatPrice(g.cost)}</span>
          ) : (
            <span className="text-muted-foreground">{g.default_price != null ? formatPrice(g.default_price) : '-'}</span>
          )}
        </TableCell>
        <TableCell className="text-sm text-muted-foreground max-w-xs truncate">{g.override_text ?? '-'}</TableCell>
        <TableCell>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon"><MoreHorizontal className="h-4 w-4" /></Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onEdit(g)}>Edit</DropdownMenuItem>
              <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={() => onDelete(g)}>Remove</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </TableCell>
      </TableRow>
    )
  }

  // Multiple items — render collapsible group
  return (
    <>
      <TableRow
        className="cursor-pointer hover:bg-muted/50"
        onClick={onToggle}
      >
        <TableCell colSpan={5} className="font-semibold text-sm">
          <div className="flex items-center gap-1">
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            {code}
            <span className="text-xs text-muted-foreground ml-1">({items.length})</span>
          </div>
        </TableCell>
      </TableRow>
      {!isCollapsed &&
        items.map((g) => {
          const hasOverride = g.cost !== null && g.cost !== undefined
          return (
            <TableRow key={g.guideline_id} className="bg-muted/20">
              <TableCell className="pl-10 font-medium">
                {g.category_description || g.guideline_type_name || `Type #${g.type_id}`}
              </TableCell>
              <TableCell className="text-right text-sm text-muted-foreground">
                {g.default_price != null ? formatPrice(g.default_price) : '-'}
              </TableCell>
              <TableCell className="text-right">
                {hasOverride ? (
                  <span className="font-medium">{formatPrice(g.cost)}</span>
                ) : (
                  <span className="text-muted-foreground">{g.default_price != null ? formatPrice(g.default_price) : '-'}</span>
                )}
              </TableCell>
              <TableCell className="text-sm text-muted-foreground max-w-xs truncate">{g.override_text ?? '-'}</TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon"><MoreHorizontal className="h-4 w-4" /></Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => onEdit(g)}>Edit</DropdownMenuItem>
                    <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={() => onDelete(g)}>Remove</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          )
        })}
    </>
  )
}
