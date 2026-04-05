import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { X } from 'lucide-react'
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
import { createClashRule, updateClashRule } from '@/api/clashRules'
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
  const [newLot, setNewLot] = useState('')

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { lot_number: '' },
  })

  useEffect(() => {
    if (open) {
      form.reset({ lot_number: rule?.lot_number ?? '' })
      setCannotMatch(rule?.cannot_match ?? [])
      setNewLot('')
    }
  }, [open, rule, form])

  function addLots() {
    const lots = newLot
      .split(',')
      .map((l) => l.trim())
      .filter((l) => l && !cannotMatch.includes(l))
    if (lots.length > 0) {
      setCannotMatch((prev) => [...prev, ...lots])
      setNewLot('')
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
                    <Input {...field} placeholder="e.g. 101" />
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
                <Input
                  placeholder="Lot numbers (comma-separated)"
                  value={newLot}
                  onChange={(e) => setNewLot(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addLots()
                    }
                  }}
                />
                <Button type="button" variant="outline" size="sm" onClick={addLots}>
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
