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
  listUpgradeCategories,
  createUpgradeCategory,
  updateUpgradeCategory,
  deleteUpgradeCategory,
  listUpgradeItems,
  createUpgradeItem,
  updateUpgradeItem,
  deleteUpgradeItem,
} from '@/api/upgrades'
import type { UpgradeCategoryRead, UpgradeItemRead } from '@/api/upgrades'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const BRANDS = ['Hermitage Homes', 'Kingsbridge Homes']

// ---- Category schemas -------------------------------------------------------

const categorySchema = z.object({
  brand: z.string().min(1),
  name: z.string().min(1).max(100),
  sort_order: z.coerce.number().int().default(0),
})
type CategoryValues = z.infer<typeof categorySchema>

// ---- Item schemas -----------------------------------------------------------

const itemSchema = z.object({
  brand: z.string().min(1),
  category_id: z.coerce.number().int().optional().nullable(),
  description: z.string().min(1),
  price: z.coerce.number().min(0),
  date_added: z.string().optional().or(z.literal('')),
  notes: z.string().optional().or(z.literal('')),
  sort_order: z.coerce.number().int().default(0),
})
type ItemValues = z.infer<typeof itemSchema>

export default function UpgradesPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [brand, setBrand] = useState(BRANDS[0])
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null)

  // ---- Category state -------------------------------------------------------
  const [catFormOpen, setCatFormOpen] = useState(false)
  const [editingCat, setEditingCat] = useState<UpgradeCategoryRead | null>(null)
  const [deleteCatTarget, setDeleteCatTarget] = useState<UpgradeCategoryRead | null>(null)

  // ---- Item state -----------------------------------------------------------
  const [itemFormOpen, setItemFormOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<UpgradeItemRead | null>(null)
  const [deleteItemTarget, setDeleteItemTarget] = useState<UpgradeItemRead | null>(null)

  // ---- Queries --------------------------------------------------------------
  const { data: categories, isLoading: catsLoading } = useQuery({
    queryKey: ['upgrade-categories', brand],
    queryFn: () => listUpgradeCategories(brand),
  })

  const { data: items, isLoading: itemsLoading } = useQuery({
    queryKey: ['upgrade-items', brand, selectedCategoryId],
    queryFn: () => listUpgradeItems(brand, selectedCategoryId ?? undefined),
  })

  // Reset selected category when brand changes
  useEffect(() => {
    setSelectedCategoryId(null)
  }, [brand])

  // ---- Category form --------------------------------------------------------
  const catForm = useForm<CategoryValues>({
    resolver: zodResolver(categorySchema),
    defaultValues: { brand: BRANDS[0], name: '', sort_order: 0 },
  })

  useEffect(() => {
    if (catFormOpen) {
      catForm.reset({
        brand: editingCat?.brand ?? brand,
        name: editingCat?.name ?? '',
        sort_order: editingCat?.sort_order ?? 0,
      })
    }
  }, [catFormOpen, editingCat, catForm, brand])

  const saveCat = useMutation({
    mutationFn: async (values: CategoryValues) => {
      if (editingCat) return updateUpgradeCategory(editingCat.category_id, values)
      return createUpgradeCategory(values)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['upgrade-categories'] })
      toast({ title: editingCat ? 'Category updated' : 'Category created', variant: 'success' })
      setCatFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const removeCat = useMutation({
    mutationFn: (id: number) => deleteUpgradeCategory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['upgrade-categories'] })
      queryClient.invalidateQueries({ queryKey: ['upgrade-items'] })
      toast({ title: 'Category deleted', variant: 'success' })
      setDeleteCatTarget(null)
      if (deleteCatTarget && selectedCategoryId === deleteCatTarget.category_id) {
        setSelectedCategoryId(null)
      }
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  // ---- Item form ------------------------------------------------------------
  const itemForm = useForm<ItemValues>({
    resolver: zodResolver(itemSchema),
    defaultValues: { brand: BRANDS[0], category_id: null, description: '', price: 0, date_added: '', notes: '', sort_order: 0 },
  })

  useEffect(() => {
    if (itemFormOpen) {
      itemForm.reset({
        brand: editingItem?.brand ?? brand,
        category_id: editingItem?.category_id ?? selectedCategoryId ?? null,
        description: editingItem?.description ?? '',
        price: editingItem?.price ?? 0,
        date_added: editingItem?.date_added ?? '',
        notes: editingItem?.notes ?? '',
        sort_order: editingItem?.sort_order ?? 0,
      })
    }
  }, [itemFormOpen, editingItem, itemForm, brand, selectedCategoryId])

  const saveItem = useMutation({
    mutationFn: async (values: ItemValues) => {
      const payload = {
        brand: values.brand,
        category_id: values.category_id || null,
        description: values.description,
        price: values.price,
        date_added: values.date_added || null,
        notes: values.notes || null,
        sort_order: values.sort_order,
      }
      if (editingItem) return updateUpgradeItem(editingItem.upgrade_id, payload)
      return createUpgradeItem(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['upgrade-items'] })
      toast({ title: editingItem ? 'Item updated' : 'Item created', variant: 'success' })
      setItemFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const removeItem = useMutation({
    mutationFn: (id: number) => deleteUpgradeItem(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['upgrade-items'] })
      toast({ title: 'Item deleted', variant: 'success' })
      setDeleteItemTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  // ---- Helpers --------------------------------------------------------------
  const openNewCat = () => { setEditingCat(null); setCatFormOpen(true) }
  const openEditCat = (c: UpgradeCategoryRead) => { setEditingCat(c); setCatFormOpen(true) }
  const openNewItem = () => { setEditingItem(null); setItemFormOpen(true) }
  const openEditItem = (i: UpgradeItemRead) => { setEditingItem(i); setItemFormOpen(true) }

  return (
    <div>
      <PageHeader
        title="Upgrades"
        description="Manage upgrade categories and items per brand."
        actions={
          <div className="flex gap-2">
            <CsvImportButton endpoint="/api/upgrades/categories/upload-csv" label="Import Categories" onSuccess={() => { queryClient.invalidateQueries({ queryKey: ['upgrade-categories'] }); queryClient.invalidateQueries({ queryKey: ['upgrade-items'] }) }} />
            <CsvImportButton endpoint="/api/upgrades/items/upload-csv" label="Import Items" onSuccess={() => { queryClient.invalidateQueries({ queryKey: ['upgrade-categories'] }); queryClient.invalidateQueries({ queryKey: ['upgrade-items'] }) }} />
            <Select value={brand} onValueChange={setBrand}>
              <SelectTrigger className="w-[220px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {BRANDS.map((b) => (
                  <SelectItem key={b} value={b}>{b}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        }
      />

      {/* ---- Categories ---- */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold">Categories</h2>
          <Button size="sm" onClick={openNewCat}>
            <Plus className="h-4 w-4" /> New Category
          </Button>
        </div>
        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead className="w-24">Sort Order</TableHead>
                <TableHead className="w-16"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {catsLoading ? (
                <TableRow>
                  <TableCell colSpan={3} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : categories?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} className="text-center text-sm text-muted-foreground">No categories yet.</TableCell>
                </TableRow>
              ) : (
                categories?.map((c) => (
                  <TableRow
                    key={c.category_id}
                    className={selectedCategoryId === c.category_id ? 'bg-muted/50' : 'cursor-pointer hover:bg-muted/30'}
                    onClick={() => setSelectedCategoryId(selectedCategoryId === c.category_id ? null : c.category_id)}
                  >
                    <TableCell className="font-medium">{c.name}</TableCell>
                    <TableCell>{c.sort_order}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" onClick={(e) => e.stopPropagation()}>
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={(e) => { e.stopPropagation(); openEditCat(c) }}>Edit</DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive focus:text-destructive"
                            onClick={(e) => { e.stopPropagation(); setDeleteCatTarget(c) }}
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

      {/* ---- Items ---- */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold">
            Items{selectedCategoryId ? ` — ${categories?.find((c) => c.category_id === selectedCategoryId)?.name}` : ' (all categories)'}
          </h2>
          <Button size="sm" onClick={openNewItem}>
            <Plus className="h-4 w-4" /> New Item
          </Button>
        </div>
        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Description</TableHead>
                <TableHead>Category</TableHead>
                <TableHead className="w-28">Price</TableHead>
                <TableHead className="w-24">Sort</TableHead>
                <TableHead className="w-16"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {itemsLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : items?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">No items yet.</TableCell>
                </TableRow>
              ) : (
                items?.map((item) => (
                  <TableRow key={item.upgrade_id}>
                    <TableCell className="font-medium">{item.description}</TableCell>
                    <TableCell>{item.category_name ?? '—'}</TableCell>
                    <TableCell>${item.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</TableCell>
                    <TableCell>{item.sort_order}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => openEditItem(item)}>Edit</DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive focus:text-destructive"
                            onClick={() => setDeleteItemTarget(item)}
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

      {/* ---- Category dialog ---- */}
      <Dialog open={catFormOpen} onOpenChange={setCatFormOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingCat ? 'Edit category' : 'New category'}</DialogTitle>
          </DialogHeader>
          <Form {...catForm}>
            <form onSubmit={catForm.handleSubmit((v) => saveCat.mutate(v))} className="space-y-4">
              <FormField
                control={catForm.control}
                name="brand"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Brand *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {BRANDS.map((b) => (
                          <SelectItem key={b} value={b}>{b}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={catForm.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name *</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={catForm.control}
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
                <Button type="button" variant="outline" onClick={() => setCatFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={saveCat.isPending}>
                  {saveCat.isPending ? 'Saving...' : 'Save'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* ---- Item dialog ---- */}
      <Dialog open={itemFormOpen} onOpenChange={setItemFormOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingItem ? 'Edit item' : 'New item'}</DialogTitle>
          </DialogHeader>
          <Form {...itemForm}>
            <form onSubmit={itemForm.handleSubmit((v) => saveItem.mutate(v))} className="space-y-4">
              <FormField
                control={itemForm.control}
                name="brand"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Brand *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {BRANDS.map((b) => (
                          <SelectItem key={b} value={b}>{b}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={itemForm.control}
                name="category_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category</FormLabel>
                    <Select
                      onValueChange={(v) => field.onChange(v === '__none__' ? null : Number(v))}
                      value={field.value ? String(field.value) : '__none__'}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="__none__">None</SelectItem>
                        {categories?.map((c) => (
                          <SelectItem key={c.category_id} value={String(c.category_id)}>{c.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={itemForm.control}
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
                control={itemForm.control}
                name="price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Price *</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={itemForm.control}
                name="date_added"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Date Added</FormLabel>
                    <FormControl><Input type="date" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={itemForm.control}
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
                control={itemForm.control}
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
                <Button type="button" variant="outline" onClick={() => setItemFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={saveItem.isPending}>
                  {saveItem.isPending ? 'Saving...' : 'Save'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* ---- Confirm dialogs ---- */}
      <ConfirmDialog
        open={!!deleteCatTarget}
        onOpenChange={(o) => !o && setDeleteCatTarget(null)}
        title="Delete category?"
        description={deleteCatTarget ? `"${deleteCatTarget.name}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={removeCat.isPending}
        onConfirm={() => deleteCatTarget && removeCat.mutate(deleteCatTarget.category_id)}
      />

      <ConfirmDialog
        open={!!deleteItemTarget}
        onOpenChange={(o) => !o && setDeleteItemTarget(null)}
        title="Delete item?"
        description={deleteItemTarget ? `"${deleteItemTarget.description}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={removeItem.isPending}
        onConfirm={() => deleteItemTarget && removeItem.mutate(deleteItemTarget.upgrade_id)}
      />
    </div>
  )
}
