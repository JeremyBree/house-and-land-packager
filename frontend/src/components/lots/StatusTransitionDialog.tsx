import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { transitionStatus } from '@/api/lots'
import { LOT_STATUSES, type LotRead, type LotStatus } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const schema = z.object({
  new_status: z.enum(['Available', 'Unavailable', 'Hold', 'Deposit Taken', 'Sold']),
  reason: z
    .string()
    .min(3, 'Reason must be at least 3 characters')
    .max(500, 'Reason must be 500 characters or fewer'),
})

type FormValues = z.infer<typeof schema>

interface StatusTransitionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  lot: LotRead | null
}

export function StatusTransitionDialog({ open, onOpenChange, lot }: StatusTransitionDialogProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { new_status: 'Available', reason: '' },
  })

  useEffect(() => {
    if (open && lot) {
      form.reset({ new_status: lot.status, reason: '' })
    }
  }, [open, lot, form])

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      if (!lot) throw new Error('No lot selected')
      return transitionStatus(lot.lot_id, {
        new_status: values.new_status as LotStatus,
        reason: values.reason,
      })
    },
    onSuccess: () => {
      if (lot) {
        queryClient.invalidateQueries({ queryKey: ['lots', lot.stage_id] })
        queryClient.invalidateQueries({ queryKey: ['stage', lot.stage_id] })
        queryClient.invalidateQueries({ queryKey: ['status-history', lot.lot_id] })
      }
      toast({ title: 'Status updated', variant: 'success' })
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
          <DialogTitle>Change lot status</DialogTitle>
          <DialogDescription>
            {lot
              ? `Lot ${lot.lot_number} — currently ${lot.status}`
              : 'Select a new status and provide a reason.'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((v) => mutation.mutate(v))} className="space-y-4">
            <FormField
              control={form.control}
              name="new_status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>New status *</FormLabel>
                  <FormControl>
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={field.value}
                      onChange={(e) => field.onChange(e.target.value)}
                    >
                      {LOT_STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s}
                          {lot && s === lot.status ? ' (current)' : ''}
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
              name="reason"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Reason *</FormLabel>
                  <FormControl>
                    <Textarea rows={3} {...field} />
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
                {mutation.isPending ? 'Saving...' : 'Update status'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
