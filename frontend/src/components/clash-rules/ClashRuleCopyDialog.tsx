import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { copyClashRules } from '@/api/clashRules'
import { listEstates } from '@/api/estates'
import { listStages } from '@/api/stages'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

interface ClashRuleCopyDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  sourceStageId: number
}

export function ClashRuleCopyDialog({
  open,
  onOpenChange,
  sourceStageId,
}: ClashRuleCopyDialogProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [targetEstateId, setTargetEstateId] = useState<number | ''>('')
  const [targetStageId, setTargetStageId] = useState<number | ''>('')

  const { data: estatesData } = useQuery({
    queryKey: ['estates', { page: 1, size: 200 }],
    queryFn: () => listEstates({ page: 1, size: 200 }),
    enabled: open,
  })

  const { data: stages } = useQuery({
    queryKey: ['stages', targetEstateId],
    queryFn: () => listStages(targetEstateId as number),
    enabled: open && typeof targetEstateId === 'number',
  })

  const mutation = useMutation({
    mutationFn: () =>
      copyClashRules(sourceStageId, {
        target_estate_id: targetEstateId as number,
        target_stage_id: targetStageId as number,
      }),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['clash-rules'] })
      toast({
        title: 'Rules copied',
        description: `${result.copied} rules copied successfully.`,
        variant: 'success',
      })
      onOpenChange(false)
      setTargetEstateId('')
      setTargetStageId('')
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Copy clash rules</DialogTitle>
          <DialogDescription>
            Copy all clash rules from this stage to another estate and stage.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Target estate *</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={targetEstateId}
              onChange={(e) => {
                setTargetEstateId(e.target.value ? Number(e.target.value) : '')
                setTargetStageId('')
              }}
            >
              <option value="">Select estate</option>
              {estatesData?.items.map((e) => (
                <option key={e.estate_id} value={e.estate_id}>
                  {e.estate_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Target stage *</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={targetStageId}
              onChange={(e) => setTargetStageId(e.target.value ? Number(e.target.value) : '')}
              disabled={!targetEstateId}
            >
              <option value="">Select stage</option>
              {stages?.map((s) => (
                <option key={s.stage_id} value={s.stage_id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => mutation.mutate()}
            disabled={!targetEstateId || !targetStageId || mutation.isPending}
          >
            {mutation.isPending ? 'Copying...' : 'Copy rules'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
