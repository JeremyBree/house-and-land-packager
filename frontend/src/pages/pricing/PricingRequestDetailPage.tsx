import { useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, FileUp, RotateCcw, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import {
  getPricingRequest,
  downloadGeneratedSheet,
  downloadCompletedSheet,
  fulfilPricingRequest,
  resubmitPricingRequest,
  deletePricingRequest,
} from '@/api/pricingRequests'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

function statusVariant(status: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'Completed': return 'default'
    case 'In Progress': return 'secondary'
    case 'Pending': return 'outline'
    default: return 'default'
  }
}

export default function PricingRequestDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { hasAnyRole } = useAuth()
  const { toast } = useToast()
  const fileRef = useRef<HTMLInputElement>(null)
  const [showDelete, setShowDelete] = useState(false)

  const canFulfil = hasAnyRole(['admin', 'pricing'])

  const { data: request, isLoading } = useQuery({
    queryKey: ['pricing-request', id],
    queryFn: () => getPricingRequest(Number(id)),
    enabled: !!id,
  })

  const fulfilMut = useMutation({
    mutationFn: (file: File) => fulfilPricingRequest(Number(id), file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pricing-request', id] })
      toast({ title: 'Request fulfilled successfully' })
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const deleteMut = useMutation({
    mutationFn: () => deletePricingRequest(Number(id)),
    onSuccess: () => {
      toast({ title: 'Request deleted' })
      navigate('/pricing-requests')
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const handleDownloadGenerated = async () => {
    try {
      const blob = await downloadGeneratedSheet(Number(id))
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `pricing_request_${id}_generated.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    }
  }

  const handleDownloadCompleted = async () => {
    try {
      const blob = await downloadCompletedSheet(Number(id))
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `pricing_request_${id}_completed.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    }
  }

  const handleResubmit = async () => {
    try {
      const formData = await resubmitPricingRequest(Number(id))
      const params = new URLSearchParams({
        estate_id: String(formData.estate_id),
        stage_id: String(formData.stage_id),
        brand: formData.brand,
      })
      navigate(`/pricing-requests/new?${params.toString()}`)
    } catch (err) {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) fulfilMut.mutate(file)
  }

  if (isLoading) return <div className="p-6">Loading...</div>
  if (!request) return <div className="p-6">Not found</div>

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const formData = request.form_data as Record<string, any>
  const lots = (formData.lots as Array<Record<string, string | boolean | null>>) || []

  return (
    <div className="p-6">
      <PageHeader
        title={`Pricing Request #${request.request_id}`}
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleResubmit}>
              <RotateCcw className="mr-2 h-4 w-4" /> Resubmit
            </Button>
            <Button variant="destructive" size="sm" onClick={() => setShowDelete(true)}>
              <Trash2 className="mr-2 h-4 w-4" /> Delete
            </Button>
          </div>
        }
      />

      {/* Status timeline */}
      <div className="mb-6 flex items-center gap-4">
        <Badge variant={statusVariant(request.status)} className="text-sm px-3 py-1">
          {request.status}
        </Badge>
        {request.submitted_at && (
          <span className="text-sm text-muted-foreground">
            Submitted: {new Date(request.submitted_at).toLocaleString()}
          </span>
        )}
        {request.completed_at && (
          <span className="text-sm text-muted-foreground">
            Completed: {new Date(request.completed_at).toLocaleString()}
          </span>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Overview */}
        <Card>
          <CardHeader><CardTitle>Details</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-muted-foreground">Requester</span><span>{request.requester_name}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Estate</span><span>{request.estate_name}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Stage</span><span>{request.stage_name}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Brand</span><span>{request.brand}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Lots</span><span>{request.lot_numbers.join(', ')}</span></div>
          </CardContent>
        </Card>

        {/* Form data recap */}
        <Card>
          <CardHeader><CardTitle>Submission Data</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-muted-foreground">Land Titled</span><span>{formData.has_land_titled ? 'Yes' : 'No'}</span></div>
            {formData.bdm && <div className="flex justify-between"><span className="text-muted-foreground">BDM</span><span>{String(formData.bdm)}</span></div>}
            {formData.wholesale_group && <div className="flex justify-between"><span className="text-muted-foreground">Wholesale Group</span><span>{String(formData.wholesale_group)}</span></div>}
            {formData.is_kdrb && <div className="flex justify-between"><span className="text-muted-foreground">KDRB</span><span>Yes</span></div>}
            {formData.is_10_90_deal && <div className="flex justify-between"><span className="text-muted-foreground">10/90 Deal</span><span>Yes</span></div>}
            {formData.building_crossover && <div className="flex justify-between"><span className="text-muted-foreground">Building Crossover</span><span>Yes</span></div>}
            {formData.notes && <div className="flex justify-between"><span className="text-muted-foreground">Notes</span><span>{String(formData.notes)}</span></div>}
          </CardContent>
        </Card>
      </div>

      {/* Lot entries */}
      {lots.length > 0 && (
        <Card className="mt-6">
          <CardHeader><CardTitle>Lot Entries</CardTitle></CardHeader>
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="pb-2">Lot</th>
                  <th className="pb-2">House Type</th>
                  <th className="pb-2">Facade</th>
                  {request.brand === 'Hermitage Homes' && <th className="pb-2">Garage</th>}
                  {request.brand === 'Kingsbridge Homes' && <th className="pb-2">Custom</th>}
                </tr>
              </thead>
              <tbody>
                {lots.map((lot, i) => (
                  <tr key={i} className="border-b">
                    <td className="py-2">{String(lot.lot_number)}</td>
                    <td className="py-2">{String(lot.house_type)}</td>
                    <td className="py-2">{String(lot.facade_type)}</td>
                    {request.brand === 'Hermitage Homes' && <td className="py-2">{String(lot.garage_side || '-')}</td>}
                    {request.brand === 'Kingsbridge Homes' && <td className="py-2">{lot.custom_house_design ? 'Yes' : 'No'}</td>}
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <Card className="mt-6">
        <CardHeader><CardTitle>Actions</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          {request.generated_file_path && (
            <Button variant="outline" onClick={handleDownloadGenerated}>
              <Download className="mr-2 h-4 w-4" /> Download Generated Sheet
            </Button>
          )}

          {canFulfil && request.status !== 'Completed' && (
            <>
              <Button onClick={() => fileRef.current?.click()} disabled={fulfilMut.isPending}>
                <FileUp className="mr-2 h-4 w-4" />
                {fulfilMut.isPending ? 'Uploading...' : 'Upload Completed Sheet'}
              </Button>
              <input
                ref={fileRef}
                type="file"
                accept=".xlsx,.xlsm"
                className="hidden"
                onChange={handleFileChange}
              />
            </>
          )}

          {request.completed_file_path && (
            <Button variant="outline" onClick={handleDownloadCompleted}>
              <Download className="mr-2 h-4 w-4" /> Download Completed Sheet
            </Button>
          )}
        </CardContent>
      </Card>

      <ConfirmDialog
        open={showDelete}
        title="Delete Pricing Request"
        description={`Are you sure you want to delete request #${request.request_id}?`}
        onOpenChange={() => setShowDelete(false)}
        onConfirm={() => deleteMut.mutate()}
      />
    </div>
  )
}
