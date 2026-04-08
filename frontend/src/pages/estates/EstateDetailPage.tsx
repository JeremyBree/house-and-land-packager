import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, BookOpen, Download, Edit, FileText, Plus, Trash2, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { StageStatusBadge } from '@/components/common/StageStatusBadge'
import { EstateFormDialog } from './EstateFormDialog'
import { StageFormDialog } from '@/components/stages/StageFormDialog'
import { DocumentUploadDialog } from '@/components/documents/DocumentUploadDialog'
import { deleteEstate, getEstate } from '@/api/estates'
import { listStages } from '@/api/stages'
import { deleteDocument, downloadDocument, listDocuments } from '@/api/documents'
import type { DocumentRead } from '@/api/types'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

export default function EstateDetailPage() {
  const { id } = useParams<{ id: string }>()
  const estateId = Number(id)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { hasRole } = useAuth()
  const { toast } = useToast()
  const isAdmin = hasRole('admin')

  const [showEdit, setShowEdit] = useState(false)
  const [showDelete, setShowDelete] = useState(false)
  const [showNewStage, setShowNewStage] = useState(false)
  const [showUploadDoc, setShowUploadDoc] = useState(false)
  const [docToDelete, setDocToDelete] = useState<DocumentRead | null>(null)

  const { data: estate, isLoading, error } = useQuery({
    queryKey: ['estate', estateId],
    queryFn: () => getEstate(estateId),
    enabled: Number.isFinite(estateId),
  })

  const { data: stages } = useQuery({
    queryKey: ['stages', estateId],
    queryFn: () => listStages(estateId),
    enabled: Number.isFinite(estateId),
  })

  const { data: documents } = useQuery({
    queryKey: ['documents', estateId],
    queryFn: () => listDocuments(estateId),
    enabled: Number.isFinite(estateId),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteEstate(estateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estates'] })
      toast({ title: 'Estate deleted', variant: 'success' })
      navigate('/estates')
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const deleteDocMutation = useMutation({
    mutationFn: (docId: number) => deleteDocument(docId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', estateId] })
      toast({ title: 'Document deleted', variant: 'success' })
      setDocToDelete(null)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const handleDownload = async (doc: DocumentRead) => {
    try {
      const url = await downloadDocument(doc.document_id)
      const a = document.createElement('a')
      a.href = url
      a.download = doc.file_name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (err) {
      toast({ title: 'Download failed', description: extractErrorMessage(err), variant: 'destructive' })
    }
  }

  if (isLoading) {
    return <div className="text-sm text-muted-foreground">Loading...</div>
  }

  if (error || !estate) {
    return (
      <div>
        <Button variant="outline" size="sm" asChild>
          <Link to="/estates">
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>
        </Button>
        <div className="mt-6 text-sm text-muted-foreground">Estate not found.</div>
      </div>
    )
  }

  return (
    <div>
      <Button variant="ghost" size="sm" asChild className="mb-4 -ml-2">
        <Link to="/estates">
          <ArrowLeft className="h-4 w-4" /> Back to estates
        </Link>
      </Button>

      <PageHeader
        title={estate.estate_name}
        description={`${estate.developer.developer_name}${estate.region ? ' · ' + estate.region.name : ''}`}
        actions={
          isAdmin && (
            <>
              <Button variant="outline" onClick={() => setShowEdit(true)}>
                <Edit className="h-4 w-4" /> Edit
              </Button>
              <Button variant="destructive" onClick={() => setShowDelete(true)}>
                <Trash2 className="h-4 w-4" /> Delete
              </Button>
            </>
          )
        }
      />

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Location</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <DetailRow label="Suburb" value={estate.suburb} />
            <DetailRow label="State" value={estate.state} />
            <DetailRow label="Postcode" value={estate.postcode} />
            <DetailRow label="Region" value={estate.region?.name ?? null} />
            <DetailRow
              label="Status"
              value={estate.active ? <Badge variant="success">Active</Badge> : <Badge variant="secondary">Inactive</Badge>}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Contact</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <DetailRow label="Name" value={estate.contact_name} />
            <DetailRow label="Mobile" value={estate.contact_mobile} />
            <DetailRow label="Email" value={estate.contact_email} />
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Developer</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <DetailRow label="Name" value={estate.developer.developer_name} />
            <DetailRow label="Website" value={estate.developer.developer_website} />
            <DetailRow label="Contact" value={estate.developer.contact_email} />
          </CardContent>
        </Card>

        {estate.description && (
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-base">Description</CardTitle>
            </CardHeader>
            <CardContent className="whitespace-pre-wrap text-sm">{estate.description}</CardContent>
          </Card>
        )}

        {estate.notes && (
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-base">Notes</CardTitle>
            </CardHeader>
            <CardContent className="whitespace-pre-wrap text-sm">{estate.notes}</CardContent>
          </Card>
        )}

        <Card className="md:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-base">Stages</CardTitle>
            {isAdmin && (
              <Button size="sm" onClick={() => setShowNewStage(true)}>
                <Plus className="h-4 w-4" /> New Stage
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {!stages || stages.length === 0 ? (
              <div className="text-sm text-muted-foreground">No stages yet.</div>
            ) : (
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {stages.map((stage) => (
                  <button
                    key={stage.stage_id}
                    type="button"
                    onClick={() => navigate(`/estates/${estateId}/stages/${stage.stage_id}`)}
                    className="flex flex-col items-start gap-2 rounded-md border bg-card p-3 text-left transition-colors hover:bg-accent"
                  >
                    <div className="flex w-full items-center justify-between gap-2">
                      <span className="font-medium">{stage.name}</span>
                      <StageStatusBadge status={stage.status} />
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {stage.lot_count != null ? `${stage.lot_count} lots planned` : 'Lot count not set'}
                      {stage.release_date && ` · Release ${new Date(stage.release_date).toLocaleDateString()}`}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-base">Documents</CardTitle>
            {isAdmin && (
              <Button size="sm" onClick={() => setShowUploadDoc(true)}>
                <Upload className="h-4 w-4" /> Upload Document
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {!documents || documents.length === 0 ? (
              <div className="text-sm text-muted-foreground">No documents yet.</div>
            ) : (
              <ul className="divide-y">
                {documents.map((doc) => (
                  <li
                    key={doc.document_id}
                    className="flex items-center justify-between gap-3 py-2.5 text-sm"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                      <div className="min-w-0">
                        <div className="truncate font-medium">{doc.file_name}</div>
                        <div className="truncate text-xs text-muted-foreground">
                          {(doc.file_size / 1024).toFixed(1)} KB
                          {doc.description && ` · ${doc.description}`}
                          {doc.stage_id &&
                            stages &&
                            ` · ${stages.find((s) => s.stage_id === doc.stage_id)?.name ?? 'Stage'}`}
                        </div>
                      </div>
                    </div>
                    <div className="flex shrink-0 items-center gap-1">
                      <Button variant="ghost" size="sm" onClick={() => handleDownload(doc)}>
                        <Download className="h-4 w-4" />
                      </Button>
                      {isAdmin && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDocToDelete(doc)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Design Guidelines
              </CardTitle>
              <Link to={`/admin/estate-guidelines?estate_id=${estateId}`}>
                <Button variant="outline" size="sm">Manage Guidelines</Button>
              </Link>
            </div>
          </CardHeader>
        </Card>
      </div>

      <EstateFormDialog open={showEdit} onOpenChange={setShowEdit} estate={estate} />
      <StageFormDialog
        open={showNewStage}
        onOpenChange={setShowNewStage}
        estateId={estateId}
      />
      <DocumentUploadDialog
        open={showUploadDoc}
        onOpenChange={setShowUploadDoc}
        estateId={estateId}
        stages={stages}
      />
      <ConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        title="Delete estate?"
        description={`"${estate.estate_name}" will be marked inactive. This can be reversed by an admin.`}
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={() => deleteMutation.mutate()}
        loading={deleteMutation.isPending}
      />
      <ConfirmDialog
        open={!!docToDelete}
        onOpenChange={(open) => !open && setDocToDelete(null)}
        title="Delete document?"
        description={docToDelete ? `"${docToDelete.file_name}" will be permanently removed.` : ''}
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={() => docToDelete && deleteDocMutation.mutate(docToDelete.document_id)}
        loading={deleteDocMutation.isPending}
      />
    </div>
  )
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-24 shrink-0 text-muted-foreground">{label}</div>
      <div className="flex-1">{value || <span className="text-muted-foreground">—</span>}</div>
    </div>
  )
}
