import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
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
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { createStage, updateStage } from '@/api/stages'
import { STAGE_STATUSES, type StageInput, type StageRead, type StageStatus } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const schema = z.object({
  name: z.string().min(1, 'Stage name is required').max(255),
  lot_count: z
    .string()
    .optional()
    .or(z.literal(''))
    .refine((v) => !v || /^\d+$/.test(v), 'Must be a whole number'),
  status: z.enum(['Active', 'Upcoming', 'Completed']),
  release_date: z.string().optional().or(z.literal('')),
})

type FormValues = z.infer<typeof schema>

interface StageFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  estateId: number
  stage?: StageRead | null
}

export function StageFormDialog({ open, onOpenChange, estateId, stage }: StageFormDialogProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const isEdit = Boolean(stage)

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: '', lot_count: '', status: 'Upcoming', release_date: '' },
  })

  useEffect(() => {
    if (open) {
      form.reset({
        name: stage?.name ?? '',
        lot_count: stage?.lot_count != null ? String(stage.lot_count) : '',
        status: stage?.status ?? 'Upcoming',
        release_date: stage?.release_date ?? '',
      })
    }
  }, [open, stage, form])

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      const payload: StageInput = {
        name: values.name,
        lot_count: values.lot_count ? Number(values.lot_count) : null,
        status: values.status as StageStatus,
        release_date: values.release_date || null,
      }
      if (isEdit && stage) {
        return updateStage(stage.stage_id, payload)
      }
      return createStage(estateId, payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stages', estateId] })
      if (isEdit && stage) {
        queryClient.invalidateQueries({ queryKey: ['stage', stage.stage_id] })
      }
      toast({ title: isEdit ? 'Stage updated' : 'Stage created', variant: 'success' })
      onOpenChange(false)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Edit stage' : 'New stage'}</DialogTitle>
          <DialogDescription>
            {isEdit ? 'Update the stage details.' : 'Create a new stage for this estate.'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((v) => mutation.mutate(v))} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name *</FormLabel>
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
                name="lot_count"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Lot count</FormLabel>
                    <FormControl>
                      <Input type="number" min="0" {...field} />
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
                    <FormLabel>Status *</FormLabel>
                    <FormControl>
                      <select
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={field.value}
                        onChange={(e) => field.onChange(e.target.value)}
                      >
                        {STAGE_STATUSES.map((s) => (
                          <option key={s} value={s}>
                            {s}
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
              name="release_date"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Release date</FormLabel>
                  <FormControl>
                    <Input type="date" {...field} />
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
                {mutation.isPending ? 'Saving...' : isEdit ? 'Save changes' : 'Create stage'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
