import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ChevronDown, ChevronRight, MoreHorizontal, Plus } from 'lucide-react'
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
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { CsvImportButton } from '@/components/common/CsvImportButton'
import {
  listGuidelineTypes,
  createGuidelineType,
  updateGuidelineType,
  deleteGuidelineType,
} from '@/api/guidelines'
import type { GuidelineTypeRead } from '@/api/guidelines'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const typeSchema = z.object({
  short_name: z.string().min(1).max(100),
  category_code: z.string().max(100).optional().or(z.literal('')),
  category_name: z.string().max(200).optional().or(z.literal('')),
  description: z.string().optional().or(z.literal('')),
  notes: z.string().optional().or(z.literal('')),
  default_price: z.coerce.number().default(0),
  sort_order: z.coerce.number().int().default(0),
})
type TypeValues = z.infer<typeof typeSchema>

function formatPrice(value: number | null | undefined): string {
  if (value === null || value === undefined) return ''
  return `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

/** Group types by category_code for hierarchical display. */
function buildCodeGroups(types: GuidelineTypeRead[]): Map<string, GuidelineTypeRead[]> {
  const map = new Map<string, GuidelineTypeRead[]>()
  for (const t of types) {
    const code = t.category_code || t.short_name
    if (!map.has(code)) map.set(code, [])
    map.get(code)!.push(t)
  }
  return map
}

export default function GuidelineCategoriesPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<GuidelineTypeRead | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<GuidelineTypeRead | null>(null)
  const [collapsedCodes, setCollapsedCodes] = useState<Set<string>>(new Set())

  const { data: types, isLoading } = useQuery({
    queryKey: ['guideline-types'],
    queryFn: () => listGuidelineTypes(),
  })

  const codeGroups = useMemo(() => types ? buildCodeGroups(types) : new Map<string, GuidelineTypeRead[]>(), [types])

  const form = useForm<TypeValues>({
    resolver: zodResolver(typeSchema),
    defaultValues: { short_name: '', category_code: '', category_name: '', description: '', notes: '', default_price: 0, sort_order: 0 },
  })

  useEffect(() => {
    if (formOpen) {
      form.reset({
        short_name: editing?.short_name ?? '',
        category_code: editing?.category_code ?? '',
        category_name: editing?.category_name ?? '',
        description: editing?.description ?? '',
        notes: editing?.notes ?? '',
        default_price: editing?.default_price ?? 0,
        sort_order: editing?.sort_order ?? 0,
      })
    }
  }, [formOpen, editing, form])

  const save = useMutation({
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
      if (editing) return updateGuidelineType(editing.type_id, payload)
      return createGuidelineType(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guideline-types'] })
      toast({ title: editing ? 'Category updated' : 'Category created', variant: 'success' })
      setFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const remove = useMutation({
    mutationFn: (id: number) => deleteGuidelineType(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guideline-types'] })
      toast({ title: 'Category deleted', variant: 'success' })
      setDeleteTarget(null)
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

  return (
    <div>
      <PageHeader
        title="Guideline Categories"
        description="Manage design guideline categories used across all estates. Categories are grouped by Code."
        actions={
          <div className="flex gap-2">
            <CsvImportButton endpoint="/api/guidelines/types/upload-csv" onSuccess={() => queryClient.invalidateQueries({ queryKey: ['guideline-types'] })} />
            <Button onClick={() => { setEditing(null); setFormOpen(true) }}>
              <Plus className="h-4 w-4" /> New Category
            </Button>
          </div>
        }
      />

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Code / Category Name</TableHead>
              <TableHead className="text-right">Default Price</TableHead>
              <TableHead>Description</TableHead>
              <TableHead className="w-20">Order</TableHead>
              <TableHead className="w-16" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
              </TableRow>
            ) : !types?.length ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">No categories yet.</TableCell>
              </TableRow>
            ) : (
              [...codeGroups.entries()].map(([code, items]) => {
                const hasMultiple = items.length > 1
                const isCollapsed = collapsedCodes.has(code)

                if (!hasMultiple) {
                  // Single item — flat row
                  const t = items[0]
                  return (
                    <TableRow key={t.type_id}>
                      <TableCell>
                        <div>
                          <span className="font-mono text-xs text-muted-foreground mr-2">{code}</span>
                          <span className="font-medium">{t.category_name ?? t.short_name}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">{formatPrice(t.default_price)}</TableCell>
                      <TableCell className="max-w-xs truncate text-sm text-muted-foreground">{t.description || '-'}</TableCell>
                      <TableCell>{t.sort_order}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon"><MoreHorizontal className="h-4 w-4" /></Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => { setEditing(t); setFormOpen(true) }}>Edit</DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={() => setDeleteTarget(t)}>Delete</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  )
                }

                // Multiple items — collapsible group
                return (
                  <CodeGroupRows
                    key={code}
                    code={code}
                    items={items}
                    isCollapsed={isCollapsed}
                    onToggle={() => toggleCodeCollapse(code)}
                    onEdit={(t) => { setEditing(t); setFormOpen(true) }}
                    onDelete={(t) => setDeleteTarget(t)}
                  />
                )
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Form dialog */}
      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit Category' : 'New Category'}</DialogTitle>
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit((v) => save.mutate(v))} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <FormField control={form.control} name="short_name" render={({ field }) => (
                  <FormItem><FormLabel>Short Name *</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <FormField control={form.control} name="category_code" render={({ field }) => (
                  <FormItem><FormLabel>Category Code</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
                )} />
              </div>
              <FormField control={form.control} name="category_name" render={({ field }) => (
                <FormItem><FormLabel>Category Name</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="description" render={({ field }) => (
                <FormItem><FormLabel>Description (appears on pricing request)</FormLabel><FormControl><Textarea rows={3} {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="notes" render={({ field }) => (
                <FormItem><FormLabel>Notes (admin only)</FormLabel><FormControl><Textarea rows={2} {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <div className="grid grid-cols-2 gap-4">
                <FormField control={form.control} name="default_price" render={({ field }) => (
                  <FormItem><FormLabel>Default Price</FormLabel><FormControl><Input type="number" step="0.01" {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <FormField control={form.control} name="sort_order" render={({ field }) => (
                  <FormItem><FormLabel>Sort Order</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
                )} />
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={save.isPending}>{save.isPending ? 'Saving...' : 'Save'}</Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete category?"
        description={deleteTarget ? `"${deleteTarget.category_name || deleteTarget.short_name}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={remove.isPending}
        onConfirm={() => deleteTarget && remove.mutate(deleteTarget.type_id)}
      />
    </div>
  )
}

/** Renders a collapsible code group with its child category rows. */
function CodeGroupRows({
  code,
  items,
  isCollapsed,
  onToggle,
  onEdit,
  onDelete,
}: {
  code: string
  items: GuidelineTypeRead[]
  isCollapsed: boolean
  onToggle: () => void
  onEdit: (t: GuidelineTypeRead) => void
  onDelete: (t: GuidelineTypeRead) => void
}) {
  return (
    <>
      <TableRow className="cursor-pointer hover:bg-muted/50" onClick={onToggle}>
        <TableCell colSpan={5} className="font-semibold text-sm">
          <div className="flex items-center gap-1">
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            <span className="font-mono">{code}</span>
            <span className="text-xs text-muted-foreground ml-1">({items.length} categories)</span>
          </div>
        </TableCell>
      </TableRow>
      {!isCollapsed &&
        items.map((t) => (
          <TableRow key={t.type_id} className="bg-muted/20">
            <TableCell className="pl-10 font-medium">{t.category_name ?? t.short_name}</TableCell>
            <TableCell className="text-right">{formatPrice(t.default_price)}</TableCell>
            <TableCell className="max-w-xs truncate text-sm text-muted-foreground">{t.description || '-'}</TableCell>
            <TableCell>{t.sort_order}</TableCell>
            <TableCell>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon"><MoreHorizontal className="h-4 w-4" /></Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => onEdit(t)}>Edit</DropdownMenuItem>
                  <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={() => onDelete(t)}>Delete</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
        ))}
    </>
  )
}
