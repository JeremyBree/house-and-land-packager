import { useEffect, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { uploadCsv } from '@/api/lots'
import type { CsvUploadResult } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const EXPECTED_COLUMNS = [
  'lot_number',
  'frontage',
  'depth',
  'size_sqm',
  'corner_block',
  'orientation',
  'street_name',
  'land_price',
  'build_price',
  'package_price',
  'title_date',
]

interface BulkUploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  stageId: number
}

export function BulkUploadDialog({ open, onOpenChange, stageId }: BulkUploadDialogProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<CsvUploadResult | null>(null)

  useEffect(() => {
    if (open) {
      setFile(null)
      setResult(null)
    }
  }, [open])

  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file selected')
      return uploadCsv(stageId, file)
    },
    onSuccess: (data) => {
      setResult(data)
      queryClient.invalidateQueries({ queryKey: ['lots', stageId] })
      queryClient.invalidateQueries({ queryKey: ['stage', stageId] })
      toast({
        title: 'CSV processed',
        description: `${data.created} created, ${data.skipped} skipped`,
        variant: data.errors.length > 0 ? 'default' : 'success',
      })
    },
    onError: (err) => {
      toast({ title: 'Upload failed', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const handleClose = () => {
    queryClient.invalidateQueries({ queryKey: ['lots', stageId] })
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Bulk upload lots (CSV)</DialogTitle>
          <DialogDescription>
            Upload a CSV file with lot data. Existing lot numbers will be skipped.
          </DialogDescription>
        </DialogHeader>

        {!result ? (
          <div className="space-y-4">
            <div className="rounded-md border bg-muted/30 p-3 text-xs">
              <div className="mb-1 font-medium">Expected columns:</div>
              <div className="flex flex-wrap gap-1">
                {EXPECTED_COLUMNS.map((col) => (
                  <code
                    key={col}
                    className="rounded bg-background px-1.5 py-0.5 font-mono text-[11px]"
                  >
                    {col}
                  </code>
                ))}
              </div>
              <div className="mt-2 text-muted-foreground">
                <code>lot_number</code> is required; other columns are optional. Booleans accept
                true/false, 1/0, yes/no. Dates use YYYY-MM-DD.
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">CSV file *</label>
              <input
                type="file"
                accept=".csv,text/csv"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="block w-full text-sm file:mr-3 file:rounded-md file:border file:border-input file:bg-background file:px-3 file:py-1.5 file:text-sm file:font-medium hover:file:bg-accent"
              />
              {file && (
                <div className="mt-1 text-xs text-muted-foreground">
                  {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </div>
              )}
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button
                type="button"
                onClick={() => mutation.mutate()}
                disabled={!file || mutation.isPending}
              >
                {mutation.isPending ? 'Uploading...' : 'Upload CSV'}
              </Button>
            </DialogFooter>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-md bg-green-50 p-3 text-center">
                <div className="text-2xl font-semibold text-green-700">{result.created}</div>
                <div className="text-xs text-green-700">Created</div>
              </div>
              <div className="rounded-md bg-amber-50 p-3 text-center">
                <div className="text-2xl font-semibold text-amber-700">{result.skipped}</div>
                <div className="text-xs text-amber-700">Skipped</div>
              </div>
              <div className="rounded-md bg-red-50 p-3 text-center">
                <div className="text-2xl font-semibold text-red-700">{result.errors.length}</div>
                <div className="text-xs text-red-700">Errors</div>
              </div>
            </div>

            {result.errors.length > 0 && (
              <div className="max-h-64 overflow-y-auto rounded-md border">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50 text-xs font-medium">
                    <tr>
                      <th className="px-3 py-2 text-left">Row</th>
                      <th className="px-3 py-2 text-left">Error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.errors.map((err, idx) => (
                      <tr key={idx} className="border-t">
                        <td className="px-3 py-2 font-mono text-xs">{err.row}</td>
                        <td className="px-3 py-2 text-xs">{err.error}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <DialogFooter>
              <Button type="button" onClick={handleClose}>
                Close
              </Button>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
