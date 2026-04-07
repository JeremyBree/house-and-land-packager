import { useCallback, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FileUp, CheckCircle, XCircle, Clock, Trash2, Eye, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import {
  uploadPdf,
  listExtractions,
  approveExtraction,
  rejectExtraction,
  deleteExtraction,
} from '@/api/pdfIngestion'
import type { PendingExtractionRead } from '@/api/pdfIngestion'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import { useAuth } from '@/hooks/useAuth'
import { cn } from '@/lib/utils'

// Types for the AI-extracted data structure
interface ExtractedLot {
  lot_number: string
  street_name: string | null
  frontage: number | null
  depth: number | null
  size_sqm: number | null
  land_price: number | null
  orientation: string | null
  corner_block: boolean
}

interface ExtractedGuideline {
  guideline_type: string
  cost: number | null
  notes: string
}

interface ExtractedEstate {
  estate_name: string
  stage_name: string
  suburb: string | null
  postcode: string | null
  developer_name: string
  contact_name: string | null
  contact_email: string | null
  contact_mobile: string | null
  lots: ExtractedLot[]
  guidelines: ExtractedGuideline[]
}

interface ExtractedData {
  estates: ExtractedEstate[]
  confidence: string
  notes: string
}

const STATUS_OPTIONS = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
]

function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  }
  const icons: Record<string, React.ReactNode> = {
    pending: <Clock className="mr-1 h-3 w-3" />,
    approved: <CheckCircle className="mr-1 h-3 w-3" />,
    rejected: <XCircle className="mr-1 h-3 w-3" />,
  }
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        variants[status] || 'bg-gray-100 text-gray-800',
      )}
    >
      {icons[status]}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

export default function PdfIngestionPage() {
  const { toast } = useToast()
  const { hasRole } = useAuth()
  const isAdmin = hasRole('admin')
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedExtraction, setSelectedExtraction] = useState<PendingExtractionRead | null>(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [reviewNotes, setReviewNotes] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<PendingExtractionRead | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  const filterStatus = statusFilter === 'all' ? undefined : statusFilter
  const { data: extractions = [], isLoading } = useQuery({
    queryKey: ['pdf-extractions', filterStatus],
    queryFn: () => listExtractions(filterStatus),
  })

  const uploadMutation = useMutation({
    mutationFn: uploadPdf,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pdf-extractions'] })
      toast({ title: 'PDF uploaded and extraction started', variant: 'default' })
    },
    onError: (err) => {
      toast({ title: 'Upload failed', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const approveMutation = useMutation({
    mutationFn: ({ id, notes }: { id: number; notes?: string }) => approveExtraction(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pdf-extractions'] })
      setDetailOpen(false)
      setSelectedExtraction(null)
      setReviewNotes('')
      toast({ title: 'Extraction approved and data committed', variant: 'default' })
    },
    onError: (err) => {
      toast({ title: 'Approve failed', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ id, notes }: { id: number; notes?: string }) => rejectExtraction(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pdf-extractions'] })
      setDetailOpen(false)
      setSelectedExtraction(null)
      setReviewNotes('')
      toast({ title: 'Extraction rejected', variant: 'default' })
    },
    onError: (err) => {
      toast({ title: 'Reject failed', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteExtraction(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pdf-extractions'] })
      setDeleteTarget(null)
      toast({ title: 'Extraction deleted', variant: 'default' })
    },
    onError: (err) => {
      toast({ title: 'Delete failed', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const handleFileUpload = useCallback(
    (files: FileList | null) => {
      if (!files || files.length === 0) return
      const file = files[0]
      if (file.type !== 'application/pdf') {
        toast({ title: 'Please upload a PDF file', variant: 'destructive' })
        return
      }
      uploadMutation.mutate(file)
    },
    [uploadMutation, toast],
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      handleFileUpload(e.dataTransfer.files)
    },
    [handleFileUpload],
  )

  const openDetail = (extraction: PendingExtractionRead) => {
    setSelectedExtraction(extraction)
    setReviewNotes('')
    setDetailOpen(true)
  }

  const extractedData = selectedExtraction?.extracted_data as ExtractedData | undefined

  return (
    <div className="space-y-6 p-6">
      <PageHeader
        title="PDF Ingestion"
        description="Upload developer price list PDFs for AI-powered data extraction"
      />

      {/* Upload Section */}
      <div
        className={cn(
          'rounded-lg border-2 border-dashed p-8 text-center transition-colors',
          isDragOver
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-muted-foreground/50',
          uploadMutation.isPending && 'pointer-events-none opacity-60',
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <FileUp className="mx-auto mb-4 h-10 w-10 text-muted-foreground" />
        <p className="mb-2 text-sm text-muted-foreground">
          {uploadMutation.isPending
            ? 'Uploading and extracting data...'
            : 'Drag and drop a PDF file here, or click to select'}
        </p>
        <Input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => handleFileUpload(e.target.files)}
        />
        <Button
          variant="outline"
          disabled={uploadMutation.isPending}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="mr-2 h-4 w-4" />
          {uploadMutation.isPending ? 'Processing...' : 'Select PDF'}
        </Button>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium">Filter by status:</label>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {STATUS_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Extractions Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>File Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Notes</TableHead>
              <TableHead>Uploaded</TableHead>
              <TableHead className="w-[120px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  Loading...
                </TableCell>
              </TableRow>
            ) : extractions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  No extractions found
                </TableCell>
              </TableRow>
            ) : (
              extractions.map((ext) => (
                <TableRow key={ext.extraction_id}>
                  <TableCell className="font-medium">{ext.file_name}</TableCell>
                  <TableCell>
                    <StatusBadge status={ext.status} />
                  </TableCell>
                  <TableCell className="max-w-[300px] truncate text-sm text-muted-foreground">
                    {ext.extraction_notes}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(ext.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        title="View details"
                        onClick={() => openDetail(ext)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {isAdmin && (
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Delete"
                          onClick={() => setDeleteTarget(ext)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Detail Dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-h-[85vh] max-w-3xl overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              Extraction: {selectedExtraction?.file_name}
            </DialogTitle>
          </DialogHeader>

          {selectedExtraction && (
            <div className="space-y-4">
              <div className="flex items-center gap-4 text-sm">
                <StatusBadge status={selectedExtraction.status} />
                <span className="text-muted-foreground">
                  Uploaded {new Date(selectedExtraction.created_at).toLocaleString()}
                </span>
              </div>

              {selectedExtraction.extraction_notes && (
                <div className="rounded-md bg-muted p-3 text-sm">
                  {selectedExtraction.extraction_notes}
                </div>
              )}

              {selectedExtraction.review_notes && (
                <div className="rounded-md bg-blue-50 p-3 text-sm">
                  <strong>Review notes:</strong> {selectedExtraction.review_notes}
                </div>
              )}

              {/* Extracted Data Display */}
              {extractedData?.estates?.map((estate, idx) => (
                <div key={idx} className="rounded-md border p-4 space-y-3">
                  <h3 className="font-semibold">
                    {estate.estate_name}
                    {estate.stage_name && (
                      <span className="ml-2 text-sm font-normal text-muted-foreground">
                        Stage {estate.stage_name}
                      </span>
                    )}
                  </h3>

                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {estate.developer_name && (
                      <div>
                        <span className="text-muted-foreground">Developer:</span>{' '}
                        {estate.developer_name}
                      </div>
                    )}
                    {estate.suburb && (
                      <div>
                        <span className="text-muted-foreground">Suburb:</span>{' '}
                        {estate.suburb}
                      </div>
                    )}
                    {estate.postcode && (
                      <div>
                        <span className="text-muted-foreground">Postcode:</span>{' '}
                        {estate.postcode}
                      </div>
                    )}
                    {estate.contact_name && (
                      <div>
                        <span className="text-muted-foreground">Contact:</span>{' '}
                        {estate.contact_name}
                      </div>
                    )}
                  </div>

                  {/* Lots */}
                  {estate.lots.length > 0 && (
                    <div>
                      <h4 className="mb-1 text-sm font-medium">
                        Lots ({estate.lots.length})
                      </h4>
                      <div className="max-h-60 overflow-y-auto rounded border">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead className="text-xs">Lot</TableHead>
                              <TableHead className="text-xs">Street</TableHead>
                              <TableHead className="text-xs">Frontage</TableHead>
                              <TableHead className="text-xs">Depth</TableHead>
                              <TableHead className="text-xs">Size</TableHead>
                              <TableHead className="text-xs">Price</TableHead>
                              <TableHead className="text-xs">Orient.</TableHead>
                              <TableHead className="text-xs">Corner</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {estate.lots.map((lot, li) => (
                              <TableRow key={li}>
                                <TableCell className="text-xs">
                                  {lot.lot_number}
                                </TableCell>
                                <TableCell className="text-xs">
                                  {lot.street_name || '-'}
                                </TableCell>
                                <TableCell className="text-xs">
                                  {lot.frontage != null ? `${lot.frontage}m` : '-'}
                                </TableCell>
                                <TableCell className="text-xs">
                                  {lot.depth != null ? `${lot.depth}m` : '-'}
                                </TableCell>
                                <TableCell className="text-xs">
                                  {lot.size_sqm != null ? `${lot.size_sqm}m2` : '-'}
                                </TableCell>
                                <TableCell className="text-xs">
                                  {lot.land_price != null
                                    ? `$${Number(lot.land_price).toLocaleString()}`
                                    : '-'}
                                </TableCell>
                                <TableCell className="text-xs">
                                  {lot.orientation || '-'}
                                </TableCell>
                                <TableCell className="text-xs">
                                  {lot.corner_block ? 'Yes' : 'No'}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  )}

                  {/* Guidelines */}
                  {estate.guidelines.length > 0 && (
                    <div>
                      <h4 className="mb-1 text-sm font-medium">
                        Design Guidelines ({estate.guidelines.length})
                      </h4>
                      <div className="max-h-40 overflow-y-auto rounded border">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead className="text-xs">Type</TableHead>
                              <TableHead className="text-xs">Cost</TableHead>
                              <TableHead className="text-xs">Notes</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {estate.guidelines.map((gl, gi) => (
                              <TableRow key={gi}>
                                <TableCell className="text-xs font-medium">
                                  {gl.guideline_type}
                                </TableCell>
                                <TableCell className="text-xs">
                                  {gl.cost != null
                                    ? `$${Number(gl.cost).toLocaleString()}`
                                    : '-'}
                                </TableCell>
                                <TableCell className="max-w-[200px] truncate text-xs">
                                  {gl.notes || '-'}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {/* Approve/Reject actions for admins on pending extractions */}
              {isAdmin && selectedExtraction.status === 'pending' && (
                <div className="space-y-3 border-t pt-4">
                  <div>
                    <label className="mb-1 block text-sm font-medium">
                      Review Notes (optional)
                    </label>
                    <Textarea
                      value={reviewNotes}
                      onChange={(e) => setReviewNotes(e.target.value)}
                      placeholder="Add any review notes..."
                      rows={2}
                    />
                  </div>
                  <DialogFooter>
                    <Button
                      variant="destructive"
                      disabled={rejectMutation.isPending || approveMutation.isPending}
                      onClick={() =>
                        rejectMutation.mutate({
                          id: selectedExtraction.extraction_id,
                          notes: reviewNotes || undefined,
                        })
                      }
                    >
                      <XCircle className="mr-2 h-4 w-4" />
                      {rejectMutation.isPending ? 'Rejecting...' : 'Reject'}
                    </Button>
                    <Button
                      disabled={approveMutation.isPending || rejectMutation.isPending}
                      onClick={() =>
                        approveMutation.mutate({
                          id: selectedExtraction.extraction_id,
                          notes: reviewNotes || undefined,
                        })
                      }
                    >
                      <CheckCircle className="mr-2 h-4 w-4" />
                      {approveMutation.isPending ? 'Approving...' : 'Approve & Import'}
                    </Button>
                  </DialogFooter>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete Extraction"
        description={`Are you sure you want to delete "${deleteTarget?.file_name}"? This action cannot be undone.`}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.extraction_id)}
        loading={deleteMutation.isPending}
      />
    </div>
  )
}
