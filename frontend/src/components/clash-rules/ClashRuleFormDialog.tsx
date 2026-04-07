import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
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
import { createClashRule, updateClashRule } from '@/api/clashRules'
import { listLots } from '@/api/lots'
import type { ClashRuleRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const schema = z.object({
  lot_number: z.string().min(1, 'Lot number is required'),
})

type FormValues = z.infer<typeof schema>

interface ClashRuleFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  estateId: number
  stageId: number
  rule?: ClashRuleRead | null
}

export function ClashRuleFormDialog({
  open,
  onOpenChange,
  estateId,
  stageId,
  rule,
}: ClashRuleFormDialogProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const isEdit = Boolean(rule)

  const [cannotMatch, setCannotMatch] = useState<string[]>([])
  const [selectedAddLot, setSelectedAddLot] = useState('')

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { lot_number: '' },
  })

  const { data: lotsData } = useQuery({
    queryKey: ['stage-lots', stageId],
    queryFn: () => listLots(stageId, { size: 200 }),
    enabled: open && !!stageId,
  })
  const availableLots = lotsData?.items ?? []

  const watchedLotNumber = form.watch('lot_number')

  // Lots available for "cannot match" (excluding the primary lot and already-added lots)
  const cannotMatchOptions = availableLots.filter(
    (l) => l.lot_number !== watchedLotNumber && !cannotMatch.includes(l.lot_number),
  )

  useEffect(() => {
    if (open) {
      form.reset({ lot_number: rule?.lot_number ?? '' })
      setCannotMatch(rule?.cannot_match ?? [])
      setSelectedAddLot('')
    }
  }, [open, rule, form])

  function addLot() {
    if (selectedAddLot && !cannotMatch.includes(selectedAddLot)) {
      setCannotMatch((prev) => [...prev, selectedAddLot])
      setSelectedAddLot('')
    }
  }

  function removeLot(lot: string) {
    setCannotMatch((prev) => prev.filter((l) => l !== lot))
  }

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      if (isEdit && rule) {
        return updateClashRule(rule.rule_id, {
          lot_number: values.lot_number,
          cannot_match: cannotMatch,
        })
      }
      return createClashRule(estateId, stageId, {
        lot_number: values.lot_number,
        cannot_match: cannotMatch,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clash-rules', stageId] })
      toast({ title: isEdit ? 'Rule updated' : 'Rule created', variant: 'success' })
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
          <DialogTitle>{isEdit ? 'Edit clash rule' : 'New clash rule'}</DialogTitle>
          <DialogDescription>
            {isEdit
              ? 'Update the clash rule.'
              : 'Define which lots cannot share the same design + facade.'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit((v) => mutation.mutate(v))}
            className="space-y-4"
          >
            <FormField
              control={form.control}
              name="lot_number"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Lot number *</FormLabel>
                  <FormControl>
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={field.value}
                      onChange={(e) => {
                        field.onChange(e.target.value)
                        // Remove the newly selected lot from cannot_match if present
                        setCannotMatch((prev) => prev.filter((l) => l !== e.target.value))
                      }}
                    >
                      <option value="">Select lot...</option>
                      {availableLots.map((l) => (
                        <option key={l.lot_id} value={l.lot_number}>
                          {l.lot_number}{l.street_name ? ` — ${l.street_name}` : ''}
                        </option>
                      ))}
                    </select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div>
              <label className="mb-1 block text-sm font-medium">Cannot match with</label>
              <div className="mb-2 flex flex-wrap gap-1.5">
                {cannotMatch.map((lot) => (
                  <span
                    key={lot}
                    className="inline-flex items-center gap-1 rounded-full bg-secondary px-2 py-0.5 text-xs font-medium"
                  >
                    {lot}
                    <button
                      type="button"
                      onClick={() => removeLot(lot)}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
                {cannotMatch.length === 0 && (
                  <span className="text-xs text-muted-foreground">
                    No lots added yet
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={selectedAddLot}
                  onChange={(e) => setSelectedAddLot(e.target.value)}
                  disabled={!watchedLotNumber}
                >
                  <option value="">Select lot to add...</option>
                  {cannotMatchOptions.map((l) => (
                    <option key={l.lot_id} value={l.lot_number}>
                      {l.lot_number}{l.street_name ? ` — ${l.street_name}` : ''}
                    </option>
                  ))}
                </select>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addLot}
                  disabled={!selectedAddLot}
                >
                  Add
                </Button>
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Saving...' : isEdit ? 'Save changes' : 'Create rule'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
