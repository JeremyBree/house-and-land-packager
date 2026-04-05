import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { listDevelopers } from '@/api/developers'
import { listRegions } from '@/api/regions'
import { createEstate, updateEstate } from '@/api/estates'
import type { EstateDetailRead, EstateInput } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const estateSchema = z.object({
  estate_name: z.string().min(1, 'Estate name is required').max(255),
  developer_id: z.coerce.number().int().positive('Developer is required'),
  region_id: z.coerce.number().int().nullable().optional(),
  suburb: z.string().max(255).optional().or(z.literal('')),
  state: z.string().max(10).optional().or(z.literal('')),
  postcode: z.string().max(10).optional().or(z.literal('')),
  contact_name: z.string().max(255).optional().or(z.literal('')),
  contact_mobile: z.string().max(50).optional().or(z.literal('')),
  contact_email: z.string().email('Invalid email').optional().or(z.literal('')),
  description: z.string().optional().or(z.literal('')),
  notes: z.string().optional().or(z.literal('')),
})

type EstateFormValues = z.infer<typeof estateSchema>

interface EstateFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  estate?: EstateDetailRead | null
}

export function EstateFormDialog({ open, onOpenChange, estate }: EstateFormDialogProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const isEdit = Boolean(estate)

  const { data: developers } = useQuery({ queryKey: ['developers'], queryFn: listDevelopers, enabled: open })
  const { data: regions } = useQuery({ queryKey: ['regions'], queryFn: listRegions, enabled: open })

  const form = useForm<EstateFormValues>({
    resolver: zodResolver(estateSchema),
    defaultValues: {
      estate_name: '',
      developer_id: 0,
      region_id: null,
      suburb: '',
      state: '',
      postcode: '',
      contact_name: '',
      contact_mobile: '',
      contact_email: '',
      description: '',
      notes: '',
    },
  })

  useEffect(() => {
    if (open) {
      form.reset({
        estate_name: estate?.estate_name ?? '',
        developer_id: estate?.developer_id ?? 0,
        region_id: estate?.region_id ?? null,
        suburb: estate?.suburb ?? '',
        state: estate?.state ?? '',
        postcode: estate?.postcode ?? '',
        contact_name: estate?.contact_name ?? '',
        contact_mobile: estate?.contact_mobile ?? '',
        contact_email: estate?.contact_email ?? '',
        description: estate?.description ?? '',
        notes: estate?.notes ?? '',
      })
    }
  }, [open, estate, form])

  const mutation = useMutation({
    mutationFn: async (values: EstateFormValues) => {
      const payload: EstateInput = {
        estate_name: values.estate_name,
        developer_id: Number(values.developer_id),
        region_id: values.region_id ? Number(values.region_id) : null,
        suburb: values.suburb || null,
        state: values.state || null,
        postcode: values.postcode || null,
        contact_name: values.contact_name || null,
        contact_mobile: values.contact_mobile || null,
        contact_email: values.contact_email || null,
        description: values.description || null,
        notes: values.notes || null,
      }
      if (isEdit && estate) {
        return updateEstate(estate.estate_id, payload)
      }
      return createEstate(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estates'] })
      if (isEdit && estate) {
        queryClient.invalidateQueries({ queryKey: ['estate', estate.estate_id] })
      }
      toast({ title: isEdit ? 'Estate updated' : 'Estate created', variant: 'success' })
      onOpenChange(false)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Edit estate' : 'New estate'}</DialogTitle>
          <DialogDescription>
            {isEdit ? 'Update the estate details.' : 'Create a new estate record.'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((v) => mutation.mutate(v))} className="space-y-4">
            <FormField
              control={form.control}
              name="estate_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Estate name *</FormLabel>
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
                name="developer_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Developer *</FormLabel>
                    <FormControl>
                      <select
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={field.value || ''}
                        onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : 0)}
                      >
                        <option value="">Select developer...</option>
                        {developers?.map((d) => (
                          <option key={d.developer_id} value={d.developer_id}>
                            {d.developer_name}
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
                name="region_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Region</FormLabel>
                    <FormControl>
                      <select
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={field.value ?? ''}
                        onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : null)}
                      >
                        <option value="">No region</option>
                        {regions?.map((r) => (
                          <option key={r.region_id} value={r.region_id}>
                            {r.name}
                          </option>
                        ))}
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="suburb"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Suburb</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="state"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>State</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="postcode"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Postcode</FormLabel>
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
                name="contact_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Contact name</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="contact_mobile"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Contact mobile</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="contact_email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Contact email</FormLabel>
                  <FormControl>
                    <Input type="email" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes</FormLabel>
                  <FormControl>
                    <Textarea {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Saving...' : isEdit ? 'Save changes' : 'Create estate'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
