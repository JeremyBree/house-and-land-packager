import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogDescription,
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
import { createPackage, updatePackage } from '@/api/packages'
import { listEstates } from '@/api/estates'
import { listStages } from '@/api/stages'
import type { PackageRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const schema = z.object({
  estate_id: z.string().min(1, 'Estate is required'),
  stage_id: z.string().min(1, 'Stage is required'),
  lot_number: z.string().min(1, 'Lot number is required').max(50),
  design: z.string().min(1, 'Design is required').max(255),
  facade: z.string().min(1, 'Facade is required').max(255),
  colour_scheme: z.string().optional().or(z.literal('')),
  brand: z.enum(['Hermitage', 'Kingsbridge']),
  source: z.string().optional().or(z.literal('')),
  status: z.string().optional().or(z.literal('')),
})

type FormValues = z.infer<typeof schema>

interface PackageFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  pkg?: PackageRead | null
}

export function PackageFormDialog({ open, onOpenChange, pkg }: PackageFormDialogProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const isEdit = Boolean(pkg)

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      estate_id: '',
      stage_id: '',
      lot_number: '',
      design: '',
      facade: '',
      colour_scheme: '',
      brand: 'Hermitage',
      source: '',
      status: '',
    },
  })

  const watchedEstateId = form.watch('estate_id')
  const selectedEstateId = watchedEstateId ? Number(watchedEstateId) : undefined

  const { data: estatesData } = useQuery({
    queryKey: ['estates', { page: 1, size: 200 }],
    queryFn: () => listEstates({ page: 1, size: 200 }),
    enabled: open,
  })

  const { data: stages } = useQuery({
    queryKey: ['stages', selectedEstateId],
    queryFn: () => listStages(selectedEstateId!),
    enabled: open && !!selectedEstateId,
  })

  useEffect(() => {
    if (open) {
      form.reset({
        estate_id: pkg ? String(pkg.estate_id) : '',
        stage_id: pkg ? String(pkg.stage_id) : '',
        lot_number: pkg?.lot_number ?? '',
        design: pkg?.design ?? '',
        facade: pkg?.facade ?? '',
        colour_scheme: pkg?.colour_scheme ?? '',
        brand: (pkg?.brand as 'Hermitage' | 'Kingsbridge') ?? 'Hermitage',
        source: pkg?.source ?? '',
        status: pkg?.status ?? '',
      })
    }
  }, [open, pkg, form])

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      const payload = {
        estate_id: Number(values.estate_id),
        stage_id: Number(values.stage_id),
        lot_number: values.lot_number,
        design: values.design,
        facade: values.facade,
        colour_scheme: values.colour_scheme || null,
        brand: values.brand,
        source: values.source || null,
        status: values.status || null,
      }
      if (isEdit && pkg) {
        return updatePackage(pkg.package_id, payload)
      }
      return createPackage(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] })
      toast({ title: isEdit ? 'Package updated' : 'Package created', variant: 'success' })
      onOpenChange(false)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Edit package' : 'New package'}</DialogTitle>
          <DialogDescription>
            {isEdit ? 'Update the package details.' : 'Create a new house & land package.'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((v) => mutation.mutate(v))} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="estate_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Estate *</FormLabel>
                    <FormControl>
                      <select
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={field.value}
                        onChange={(e) => {
                          field.onChange(e.target.value)
                          form.setValue('stage_id', '')
                        }}
                      >
                        <option value="">Select estate</option>
                        {estatesData?.items.map((e) => (
                          <option key={e.estate_id} value={String(e.estate_id)}>
                            {e.estate_name}
                          </option>
                        ))}
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="stage_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Stage *</FormLabel>
                    <FormControl>
                      <select
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={field.value}
                        onChange={(e) => field.onChange(e.target.value)}
                        disabled={!selectedEstateId}
                      >
                        <option value="">Select stage</option>
                        {stages?.map((s) => (
                          <option key={s.stage_id} value={String(s.stage_id)}>
                            {s.name}
                          </option>
                        ))}
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="lot_number"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Lot number *</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="design"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Design *</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="facade"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Facade *</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="colour_scheme"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Colour scheme</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="brand"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Brand *</FormLabel>
                    <FormControl>
                      <select
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={field.value}
                        onChange={(e) => field.onChange(e.target.value)}
                      >
                        <option value="Hermitage">Hermitage</option>
                        <option value="Kingsbridge">Kingsbridge</option>
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="source"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Source</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Saving...' : isEdit ? 'Save changes' : 'Create package'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
