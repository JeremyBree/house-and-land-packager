import { useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import { uploadCsv } from '@/api/csvImport'

interface CsvImportButtonProps {
  endpoint: string
  label?: string
  onSuccess?: () => void
}

export function CsvImportButton({
  endpoint,
  label = 'Import CSV',
  onSuccess,
}: CsvImportButtonProps) {
  const { toast } = useToast()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const mutation = useMutation({
    mutationFn: (file: File) => uploadCsv(endpoint, file),
    onSuccess: (result) => {
      const parts: string[] = []
      if (result.created > 0) parts.push(`${result.created} created`)
      if (result.skipped > 0) parts.push(`${result.skipped} skipped`)
      if (result.errors.length > 0) parts.push(`${result.errors.length} errors`)

      toast({
        title: 'CSV import complete',
        description: parts.join(', ') || 'No records processed',
        variant: result.errors.length > 0 ? 'destructive' : 'success',
      })

      onSuccess?.()
    },
    onError: (err) => {
      toast({
        title: 'CSV import failed',
        description: extractErrorMessage(err),
        variant: 'destructive',
      })
    },
    onSettled: () => {
      // Reset file input so the same file can be re-selected
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      mutation.mutate(file)
    }
  }

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={handleFileChange}
      />
      <Button
        variant="outline"
        disabled={mutation.isPending}
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload className="h-4 w-4" />
        {mutation.isPending ? 'Importing...' : label}
      </Button>
    </>
  )
}
