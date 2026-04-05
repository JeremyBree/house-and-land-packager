import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { createLot, updateLot } from '@/api/lots'
import { LOT_ORIENTATIONS, type LotInput, type LotRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const decimalRegex = /^\d+(\.\d{1,2})?$/

const decimalField = z
  .string()
  .optional()
  .or(z.literal(''))
  .refine((v) => !v || decimalRegex.test(v), 'Must be a number (up to 2 decimals)')

const schema = z.object({
  lot_number: z.string().min(1, 'Lot number is required').max(50),
  frontage: decimalField,
  depth: decimalField,
  size_sqm: decimalField,
  corner_block: z.boolean(),
  orientation: z.string().optional().or(z.literal('')),
  side_easement: z.string().max(100).optional().or(z.literal('')),
  rear_easement: z.string().max(100).optional().or(z.literal('')),
  street_name: z.string().max(255).optional().or(z.literal('')),
  land_price: decimalField,
  build_price: decimalField,
  package_price: decimalField,
  substation: z.boolean(),
  title_date: z.string().optional().or(z.literal('')),
})

type FormValues = z.infer<typeof schema>

interface LotFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  stageId: number
  lot?: LotRead | null
}

export function LotFormDialog({ open, onOpenChange, stageId, lot }: LotFormDialogProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const isEdit = Boolean(lot)

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      lot_number: '',
      frontage: '',
      depth: '',
      size_sqm: '',
      corner_block: false,
      orientation: '',
      side_easement: '',
      rear_easement: '',
      street_name: '',
      land_price: '',
      build_price: '',
      package_price: '',
      substation: false,
      title_date: '',
    },
  })

  useEffect(() => {
    if (open) {
      form.reset({
        lot_number: lot?.lot_number ?? '',
        frontage: lot?.frontage ?? '',
        depth: lot?.depth ?? '',
        size_sqm: lot?.size_sqm ?? '',
        corner_block: lot?.corner_block ?? false,
        orientation: lot?.orientation ?? '',
        side_easement: lot?.side_easement ?? '',
        rear_easement: lot?.rear_easement ?? '',
        street_name: lot?.street_name ?? '',
        land_price: lot?.land_price ?? '',
        build_price: lot?.build_price ?? '',
        package_price: lot?.package_price ?? '',
        substation: lot?.substation ?? false,
        title_date: lot?.title_date ?? '',
      })
    }
  }, [open, lot, form])

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      const payload: LotInput = {
        lot_number: values.lot_number,
        frontage: values.frontage || null,
        depth: values.depth || null,
        size_sqm: values.size_sqm || null,
        corner_block: values.corner_block,
        orientation: values.orientation || null,
        side_easement: values.side_easement || null,
        rear_easement: values.rear_easement || null,
        street_name: values.street_name || null,
        land_price: values.land_price || null,
        build_price: values.build_price || null,
        package_price: values.package_price || null,
        substation: values.substation,
        title_date: values.title_date || null,
      }
      if (isEdit && lot) {
        return updateLot(lot.lot_id, payload)
      }
      return createLot(stageId, payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lots', stageId] })
      queryClient.invalidateQueries({ queryKey: ['stage', stageId] })
      toast({ title: isEdit ? 'Lot updated' : 'Lot created', variant: 'success' })
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
          <DialogTitle>{isEdit ? 'Edit lot' : 'New lot'}</DialogTitle>
          <DialogDescription>
            {isEdit ? 'Update the lot details.' : 'Create a new lot in this stage.'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((v) => mutation.mutate(v))} className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
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
              <FormField
                control={form.control}
                name="street_name"
                render={({ field }) => (
                  <FormItem className="col-span-2">
                    <FormLabel>Street name</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="frontage"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Frontage (m)</FormLabel>
                    <FormControl>
                      <Input inputMode="decimal" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="depth"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Depth (m)</FormLabel>
                    <FormControl>
                      <Input inputMode="decimal" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="size_sqm"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Size (sqm)</FormLabel>
                    <FormControl>
                      <Input inputMode="decimal" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="orientation"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Orientation</FormLabel>
                    <FormControl>
                      <select
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={field.value ?? ''}
                        onChange={(e) => field.onChange(e.target.value)}
                      >
                        <option value="">—</option>
                        {LOT_ORIENTATIONS.map((o) => (
                          <option key={o} value={o}>
                            {o}
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
                name="side_easement"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Side easement</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="rear_easement"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Rear easement</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="land_price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Land price ($)</FormLabel>
                    <FormControl>
                      <Input inputMode="decimal" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="build_price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Build price ($)</FormLabel>
                    <FormControl>
                      <Input inputMode="decimal" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="package_price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Package price ($)</FormLabel>
                    <FormControl>
                      <Input inputMode="decimal" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-3 items-end gap-4">
              <FormField
                control={form.control}
                name="title_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Title date</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="corner_block"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Checkbox
                        label="Corner block"
                        checked={field.value}
                        onChange={(e) => field.onChange(e.target.checked)}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="substation"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Checkbox
                        label="Substation"
                        checked={field.value}
                        onChange={(e) => field.onChange(e.target.checked)}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Saving...' : isEdit ? 'Save changes' : 'Create lot'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
