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
  listWholesaleGroups,
  createWholesaleGroup,
  updateWholesaleGroup,
  deleteWholesaleGroup,
  listCommissionRates,
  createCommissionRate,
  updateCommissionRate,
  deleteCommissionRate,
  type WholesaleGroupRead,
  type CommissionRateRead,
} from '@/api/commissions'
import { listUsers } from '@/api/users'

const BRANDS = ['Hermitage Homes', 'Kingsbridge Homes'] as const

// ---------------------------------------------------------------------------
// Wholesale Group form
// ---------------------------------------------------------------------------
const wgSchema = z.object({
  group_name: z.string().min(1, 'Name is required'),
  gst_registered: z.boolean(),
  active: z.boolean(),
})
type WgFormValues = z.infer<typeof wgSchema>

// ---------------------------------------------------------------------------
// Commission Rate form
// ---------------------------------------------------------------------------
const crSchema = z.object({
  bdm_profile_id: z.coerce.number().min(1, 'BDM is required'),
  group_id: z.coerce.number().min(1, 'Wholesale Group is required'),
  brand: z.string().min(1, 'Brand is required'),
  commission_fixed: z.coerce.number().nullable().optional(),
  commission_pct: z.coerce.number().nullable().optional(),
})
type CrFormValues = z.infer<typeof crSchema>

export default function CommissionsPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  // ---- Wholesale Groups state ----
  const [wgFormOpen, setWgFormOpen] = useState(false)
  const [wgEditing, setWgEditing] = useState<WholesaleGroupRead | null>(null)
  const [wgDeleteTarget, setWgDeleteTarget] = useState<WholesaleGroupRead | null>(null)

  // ---- Commission Rates state ----
  const [brandFilter, setBrandFilter] = useState<string>(BRANDS[0])
  const [crFormOpen, setCrFormOpen] = useState(false)
  const [crEditing, setCrEditing] = useState<CommissionRateRead | null>(null)
  const [crDeleteTarget, setCrDeleteTarget] = useState<CommissionRateRead | null>(null)

  // ---- Queries ----
  const { data: groups, isLoading: groupsLoading } = useQuery({
    queryKey: ['wholesale-groups', true],
    queryFn: () => listWholesaleGroups(true),
  })

  const { data: rates, isLoading: ratesLoading } = useQuery({
    queryKey: ['commission-rates', brandFilter],
    queryFn: () => listCommissionRates(brandFilter),
  })

  const { data: usersPage } = useQuery({
    queryKey: ['users-all', 1, 200],
    queryFn: () => listUsers({ page: 1, size: 200 }),
  })

  const bdmUsers = usersPage?.items?.filter((u) => u.roles.includes('bdm' as any)) ?? []

  // ---- Wholesale Group form ----
  const wgForm = useForm<WgFormValues>({
    resolver: zodResolver(wgSchema),
    defaultValues: { group_name: '', gst_registered: false, active: true },
  })

  useEffect(() => {
    if (wgFormOpen) {
      wgForm.reset({
        group_name: wgEditing?.group_name ?? '',
        gst_registered: wgEditing?.gst_registered ?? false,
        active: wgEditing?.active ?? true,
      })
    }
  }, [wgFormOpen, wgEditing, wgForm])

  const wgSaveMut = useMutation({
    mutationFn: async (values: WgFormValues) => {
      if (wgEditing) {
        return updateWholesaleGroup(wgEditing.group_id, values)
      }
      return createWholesaleGroup(values)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wholesale-groups'] })
      toast({ title: wgEditing ? 'Group updated' : 'Group created', variant: 'success' })
      setWgFormOpen(false)
      setWgEditing(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const wgDeleteMut = useMutation({
    mutationFn: (id: number) => deleteWholesaleGroup(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wholesale-groups'] })
      toast({ title: 'Group deleted', variant: 'success' })
      setWgDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  // ---- Commission Rate form ----
  const crForm = useForm<CrFormValues>({
    resolver: zodResolver(crSchema),
    defaultValues: { bdm_profile_id: 0, group_id: 0, brand: BRANDS[0], commission_fixed: null, commission_pct: null },
  })

  useEffect(() => {
    if (crFormOpen) {
      crForm.reset({
        bdm_profile_id: crEditing?.bdm_profile_id ?? 0,
        group_id: crEditing?.group_id ?? 0,
        brand: crEditing?.brand ?? brandFilter,
        commission_fixed: crEditing?.commission_fixed ?? null,
        commission_pct: crEditing?.commission_pct ?? null,
      })
    }
  }, [crFormOpen, crEditing, crForm, brandFilter])

  const crSaveMut = useMutation({
    mutationFn: async (values: CrFormValues) => {
      const payload = {
        ...values,
        commission_fixed: values.commission_fixed || null,
        commission_pct: values.commission_pct || null,
      }
      if (crEditing) {
        return updateCommissionRate(crEditing.rate_id, payload)
      }
      return createCommissionRate(payload as any)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['commission-rates'] })
      toast({ title: crEditing ? 'Rate updated' : 'Rate created', variant: 'success' })
      setCrFormOpen(false)
      setCrEditing(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const crDeleteMut = useMutation({
    mutationFn: (id: number) => deleteCommissionRate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['commission-rates'] })
      toast({ title: 'Rate deleted', variant: 'success' })
      setCrDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  return (
    <div className="space-y-10">
      {/* ================================================================
          Wholesale Groups Section
          ================================================================ */}
      <div>
        <PageHeader
          title="Wholesale Groups"
          description="Manage wholesale groups used in BDM commission calculations."
          actions={
            <div className="flex gap-2">
              <CsvImportButton endpoint="/api/wholesale-groups/upload-csv" label="Import Groups" onSuccess={() => queryClient.invalidateQueries({ queryKey: ['wholesale-groups'] })} />
              <Button onClick={() => { setWgEditing(null); setWgFormOpen(true) }}>
                <Plus className="h-4 w-4" /> New Group
              </Button>
            </div>
          }
        />

        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Group Name</TableHead>
                <TableHead>GST Registered</TableHead>
                <TableHead>Active</TableHead>
                <TableHead className="w-24 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {groupsLoading ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : !groups?.length ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">No wholesale groups yet.</TableCell>
                </TableRow>
              ) : (
                groups.map((g) => (
                  <TableRow key={g.group_id}>
                    <TableCell className="font-medium">{g.group_name}</TableCell>
                    <TableCell>{g.gst_registered ? 'Yes' : 'No'}</TableCell>
                    <TableCell>{g.active ? 'Yes' : 'No'}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => { setWgEditing(g); setWgFormOpen(true) }}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => setWgDeleteTarget(g)}>
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

      {/* ================================================================
          Commission Rates Section
          ================================================================ */}
      <div>
        <PageHeader
          title="Commission Rates"
          description="Manage BDM commission rates per wholesale group and brand."
          actions={
            <div className="flex gap-2">
              <CsvImportButton endpoint="/api/commission-rates/upload-csv" label="Import Rates" onSuccess={() => queryClient.invalidateQueries({ queryKey: ['commission-rates'] })} />
              <Button onClick={() => { setCrEditing(null); setCrFormOpen(true) }}>
                <Plus className="h-4 w-4" /> New Rate
              </Button>
            </div>
          }
        />

        <div className="mb-4">
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Brand</label>
          <select
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            value={brandFilter}
            onChange={(e) => setBrandFilter(e.target.value)}
          >
            {BRANDS.map((b) => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>

        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>BDM</TableHead>
                <TableHead>Wholesale Group</TableHead>
                <TableHead className="text-right">Fixed ($)</TableHead>
                <TableHead className="text-right">Percentage (%)</TableHead>
                <TableHead className="w-24 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {ratesLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">Loading...</TableCell>
                </TableRow>
              ) : !rates?.length ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">No commission rates for this brand.</TableCell>
                </TableRow>
              ) : (
                rates.map((r) => (
                  <TableRow key={r.rate_id}>
                    <TableCell className="font-medium">{r.bdm_name ?? `BDM #${r.bdm_profile_id}`}</TableCell>
                    <TableCell>{r.group_name ?? `Group #${r.group_id}`}</TableCell>
                    <TableCell className="text-right">
                      {r.commission_fixed != null ? `$${r.commission_fixed.toLocaleString()}` : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      {r.commission_pct != null ? `${(r.commission_pct * 100).toFixed(2)}%` : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => { setCrEditing(r); setCrFormOpen(true) }}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => setCrDeleteTarget(r)}>
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

      {/* ---- Wholesale Group Dialog ---- */}
      <Dialog open={wgFormOpen} onOpenChange={setWgFormOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{wgEditing ? 'Edit Wholesale Group' : 'New Wholesale Group'}</DialogTitle>
          </DialogHeader>
          <Form {...wgForm}>
            <form onSubmit={wgForm.handleSubmit((v) => wgSaveMut.mutate(v))} className="space-y-4">
              <FormField control={wgForm.control} name="group_name" render={({ field }) => (
                <FormItem>
                  <FormLabel>Group Name *</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <div className="flex gap-6">
                <FormField control={wgForm.control} name="gst_registered" render={({ field }) => (
                  <FormItem className="flex items-center gap-2">
                    <FormControl>
                      <input type="checkbox" checked={field.value} onChange={field.onChange} className="h-4 w-4" />
                    </FormControl>
                    <FormLabel className="!mt-0">GST Registered</FormLabel>
                  </FormItem>
                )} />
                <FormField control={wgForm.control} name="active" render={({ field }) => (
                  <FormItem className="flex items-center gap-2">
                    <FormControl>
                      <input type="checkbox" checked={field.value} onChange={field.onChange} className="h-4 w-4" />
                    </FormControl>
                    <FormLabel className="!mt-0">Active</FormLabel>
                  </FormItem>
                )} />
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setWgFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={wgSaveMut.isPending}>
                  {wgSaveMut.isPending ? 'Saving...' : wgEditing ? 'Save' : 'Create'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* ---- Commission Rate Dialog ---- */}
      <Dialog open={crFormOpen} onOpenChange={setCrFormOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{crEditing ? 'Edit Commission Rate' : 'New Commission Rate'}</DialogTitle>
          </DialogHeader>
          <Form {...crForm}>
            <form onSubmit={crForm.handleSubmit((v) => crSaveMut.mutate(v))} className="space-y-4">
              <FormField control={crForm.control} name="brand" render={({ field }) => (
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
              <FormField control={crForm.control} name="bdm_profile_id" render={({ field }) => (
                <FormItem>
                  <FormLabel>BDM *</FormLabel>
                  <FormControl>
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={field.value || ''}
                      onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : 0)}
                    >
                      <option value="">Select BDM...</option>
                      {bdmUsers.map((u) => (
                        <option key={u.profile_id} value={u.profile_id}>
                          {u.first_name} {u.last_name}
                        </option>
                      ))}
                    </select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={crForm.control} name="group_id" render={({ field }) => (
                <FormItem>
                  <FormLabel>Wholesale Group *</FormLabel>
                  <FormControl>
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={field.value || ''}
                      onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : 0)}
                    >
                      <option value="">Select group...</option>
                      {groups?.filter((g) => g.active).map((g) => (
                        <option key={g.group_id} value={g.group_id}>{g.group_name}</option>
                      ))}
                    </select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <div className="grid grid-cols-2 gap-4">
                <FormField control={crForm.control} name="commission_fixed" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Fixed Amount ($)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        value={field.value ?? ''}
                        onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : null)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={crForm.control} name="commission_pct" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Percentage (decimal)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.0001"
                        value={field.value ?? ''}
                        onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : null)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setCrFormOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={crSaveMut.isPending}>
                  {crSaveMut.isPending ? 'Saving...' : crEditing ? 'Save' : 'Create'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* ---- Delete Confirmations ---- */}
      <ConfirmDialog
        open={!!wgDeleteTarget}
        onOpenChange={(o) => !o && setWgDeleteTarget(null)}
        title="Delete wholesale group?"
        description={wgDeleteTarget ? `"${wgDeleteTarget.group_name}" will be permanently removed.` : ''}
        confirmLabel="Delete"
        variant="destructive"
        loading={wgDeleteMut.isPending}
        onConfirm={() => wgDeleteTarget && wgDeleteMut.mutate(wgDeleteTarget.group_id)}
      />

      <ConfirmDialog
        open={!!crDeleteTarget}
        onOpenChange={(o) => !o && setCrDeleteTarget(null)}
        title="Delete commission rate?"
        description={crDeleteTarget ? `Rate for ${crDeleteTarget.bdm_name ?? 'BDM'} / ${crDeleteTarget.group_name ?? 'Group'} will be removed.` : ''}
        confirmLabel="Delete"
        variant="destructive"
        loading={crDeleteMut.isPending}
        onConfirm={() => crDeleteTarget && crDeleteMut.mutate(crDeleteTarget.rate_id)}
      />
    </div>
  )
}
