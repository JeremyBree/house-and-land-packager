import { useEffect, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
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
import { uploadDocument } from '@/api/documents'
import type { StageRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const MAX_SIZE_BYTES = 10 * 1024 * 1024
const ACCEPTED_EXT = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg']

interface DocumentUploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  estateId: number
  stages?: StageRead[]
}

export function DocumentUploadDialog({
  open,
  onOpenChange,
  estateId,
  stages,
}: DocumentUploadDialogProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [file, setFile] = useState<File | null>(null)
  const [stageId, setStageId] = useState<string>('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (open) {
      setFile(null)
      setStageId('')
      setDescription('')
      setError(null)
    }
  }, [open])

  const validateFile = (f: File): string | null => {
    if (f.size > MAX_SIZE_BYTES) return 'File exceeds 10MB limit'
    const name = f.name.toLowerCase()
    if (!ACCEPTED_EXT.some((ext) => name.endsWith(ext))) {
      return `File type not allowed. Accepted: ${ACCEPTED_EXT.join(', ')}`
    }
    return null
  }

  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file selected')
      return uploadDocument(estateId, {
        file,
        stageId: stageId ? Number(stageId) : null,
        description: description || null,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', estateId] })
      toast({ title: 'Document uploaded', variant: 'success' })
      onOpenChange(false)
    },
    onError: (err) => {
      toast({ title: 'Upload failed', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Upload document</DialogTitle>
          <DialogDescription>
            PDF, Word, or image files (max 10MB). Optionally link to a specific stage.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">File *</label>
            <input
              type="file"
              accept={ACCEPTED_EXT.join(',')}
              onChange={(e) => {
                const f = e.target.files?.[0] ?? null
                if (f) {
                  const msg = validateFile(f)
                  setError(msg)
                  setFile(msg ? null : f)
                } else {
                  setFile(null)
                  setError(null)
                }
              }}
              className="block w-full text-sm file:mr-3 file:rounded-md file:border file:border-input file:bg-background file:px-3 file:py-1.5 file:text-sm file:font-medium hover:file:bg-accent"
            />
            {file && (
              <div className="mt-1 text-xs text-muted-foreground">
                {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </div>
            )}
            {error && <div className="mt-1 text-xs text-destructive">{error}</div>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Stage (optional)</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={stageId}
              onChange={(e) => setStageId(e.target.value)}
            >
              <option value="">Estate-wide (no stage)</option>
              {stages?.map((s) => (
                <option key={s.stage_id} value={s.stage_id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Description (optional)</label>
            <Textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={500}
            />
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            type="button"
            onClick={() => mutation.mutate()}
            disabled={!file || !!error || mutation.isPending}
          >
            {mutation.isPending ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
