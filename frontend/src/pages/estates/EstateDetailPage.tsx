import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Edit, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { EstateFormDialog } from './EstateFormDialog'
import { deleteEstate, getEstate } from '@/api/estates'
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

  const { data: estate, isLoading, error } = useQuery({
    queryKey: ['estate', estateId],
    queryFn: () => getEstate(estateId),
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

        <Card className="md:col-span-2 border-dashed">
          <CardHeader>
            <CardTitle className="text-base">Stages</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Stages, lots, and clash rules will be available in Sprint 2.
          </CardContent>
        </Card>
      </div>

      <EstateFormDialog open={showEdit} onOpenChange={setShowEdit} estate={estate} />
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
