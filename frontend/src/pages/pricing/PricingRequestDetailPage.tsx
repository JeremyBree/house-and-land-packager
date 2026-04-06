import { useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, FileUp, RotateCcw, Trash2, UserPlus, Calculator } from 'lucide-react'
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
  assignEstimator,
  submitEstimate,
  type PriceBreakdownItem,
  type LotSiteCostInput,
} from '@/api/pricingRequests'
import { listUsers } from '@/api/users'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

function statusVariant(status: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'Completed': return 'default'
    case 'Priced': return 'default'
    case 'In Progress': return 'secondary'
    case 'Estimating': return 'secondary'
    case 'Pending': return 'outline'
    default: return 'default'
  }
}

function statusColor(status: string): string {
  switch (status) {
    case 'Estimating': return 'bg-blue-100 text-blue-800 border-blue-200'
    case 'Priced': return 'bg-purple-100 text-purple-800 border-purple-200'
    default: return ''
  }
}

export default function PricingRequestDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { hasAnyRole, user } = useAuth()
  const { toast } = useToast()
  const fileRef = useRef<HTMLInputElement>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [showAssignDialog, setShowAssignDialog] = useState(false)
  const [selectedEstimatorId, setSelectedEstimatorId] = useState<number | null>(null)
  const [siteCostInputs, setSiteCostInputs] = useState<Record<string, LotSiteCostInput>>({})

  const canFulfil = hasAnyRole(['admin', 'pricing'])
  const isAdminOrPricing = hasAnyRole(['admin', 'pricing'])

  const { data: request, isLoading } = useQuery({
    queryKey: ['pricing-request', id],
    queryFn: () => getPricingRequest(Number(id)),
    enabled: !!id,
  })

  const { data: usersData } = useQuery({
    queryKey: ['users-for-estimator'],
    queryFn: () => listUsers({ size: 200 }),
    enabled: showAssignDialog,
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

  const assignMut = useMutation({
    mutationFn: (estimatorId: number) => assignEstimator(Number(id), { estimator_id: estimatorId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pricing-request', id] })
      toast({ title: 'Estimator assigned' })
      setShowAssignDialog(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const estimateMut = useMutation({
    mutationFn: (inputs: LotSiteCostInput[]) => submitEstimate(Number(id), { lot_inputs: inputs }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pricing-request', id] })
      toast({ title: 'Estimate submitted and prices calculated' })
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

  const initSiteCostInputs = () => {
    if (!request) return
    const lots = (request.form_data.lots as Array<Record<string, string | boolean | null>>) || []
    const inputs: Record<string, LotSiteCostInput> = {}
    for (const lot of lots) {
      const lotNum = String(lot.lot_number)
      inputs[lotNum] = {
        lot_number: lotNum,
        fall_mm: 0,
        fill_trees: false,
        easement_proximity_lhs: false,
        easement_proximity_rhs: false,
        retaining_lhs: false,
        retaining_rhs: false,
        rock_removal: false,
        rear_setback_m: '0',
        existing_neighbours: false,
        notes: null,
      }
    }
    setSiteCostInputs(inputs)
  }

  const handleSubmitEstimate = () => {
    const inputs = Object.values(siteCostInputs)
    if (inputs.length === 0) {
      initSiteCostInputs()
      return
    }
    estimateMut.mutate(inputs)
  }

  const updateSiteCost = (lotNumber: string, field: string, value: unknown) => {
    setSiteCostInputs((prev) => ({
      ...prev,
      [lotNumber]: { ...prev[lotNumber], [field]: value },
    }))
  }

  if (isLoading) return <div className="p-6">Loading...</div>
  if (!request) return <div className="p-6">Not found</div>

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const formData = request.form_data as Record<string, any>
  const lots = (formData.lots as Array<Record<string, string | boolean | null>>) || []
  const isAssignedEstimator = request.estimator_id === user?.profile_id
  const canSubmitEstimate = request.status === 'Estimating' && (isAssignedEstimator || hasAnyRole(['admin']))
  const showBreakdown = request.price_breakdown && request.price_breakdown.length > 0

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
        <Badge
          variant={statusVariant(request.status)}
          className={`text-sm px-3 py-1 ${statusColor(request.status)}`}
        >
          {request.status}
        </Badge>
        {request.submitted_at && (
          <span className="text-sm text-muted-foreground">
            Submitted: {new Date(request.submitted_at).toLocaleString()}
          </span>
        )}
        {request.estimated_at && (
          <span className="text-sm text-muted-foreground">
            Estimated: {new Date(request.estimated_at).toLocaleString()}
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
            {request.estimator_name && (
              <div className="flex justify-between"><span className="text-muted-foreground">Estimator</span><span>{request.estimator_name}</span></div>
            )}
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

      {/* Assign Estimator (visible for admin/pricing when Pending) */}
      {isAdminOrPricing && request.status === 'Pending' && (
        <Card className="mt-6">
          <CardHeader><CardTitle>Estimator Assignment</CardTitle></CardHeader>
          <CardContent>
            <Button onClick={() => { setShowAssignDialog(true) }}>
              <UserPlus className="mr-2 h-4 w-4" /> Assign Estimator
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Site Cost Input Form (visible when Estimating and user is assigned estimator or admin) */}
      {canSubmitEstimate && (
        <Card className="mt-6">
          <CardHeader><CardTitle>Site Cost Inputs</CardTitle></CardHeader>
          <CardContent>
            {Object.keys(siteCostInputs).length === 0 ? (
              <Button onClick={initSiteCostInputs}>
                <Calculator className="mr-2 h-4 w-4" /> Start Site Cost Entry
              </Button>
            ) : (
              <div className="space-y-4">
                {Object.entries(siteCostInputs).map(([lotNum, input]) => (
                  <Card key={lotNum} className="border">
                    <CardHeader className="py-3">
                      <CardTitle className="text-sm">Lot {lotNum}</CardTitle>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-3 md:grid-cols-4 text-sm">
                      <div>
                        <Label>Fall (mm)</Label>
                        <Input
                          type="number"
                          value={input.fall_mm}
                          onChange={(e) => updateSiteCost(lotNum, 'fall_mm', Number(e.target.value))}
                        />
                      </div>
                      <div className="flex items-center gap-2">
                        <input type="checkbox" checked={input.fill_trees} onChange={(e) => updateSiteCost(lotNum, 'fill_trees', e.target.checked)} />
                        <Label>Fill/Trees</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <input type="checkbox" checked={input.retaining_lhs} onChange={(e) => updateSiteCost(lotNum, 'retaining_lhs', e.target.checked)} />
                        <Label>Retaining LHS</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <input type="checkbox" checked={input.retaining_rhs} onChange={(e) => updateSiteCost(lotNum, 'retaining_rhs', e.target.checked)} />
                        <Label>Retaining RHS</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <input type="checkbox" checked={input.easement_proximity_lhs} onChange={(e) => updateSiteCost(lotNum, 'easement_proximity_lhs', e.target.checked)} />
                        <Label>Easement LHS</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <input type="checkbox" checked={input.easement_proximity_rhs} onChange={(e) => updateSiteCost(lotNum, 'easement_proximity_rhs', e.target.checked)} />
                        <Label>Easement RHS</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <input type="checkbox" checked={input.rock_removal} onChange={(e) => updateSiteCost(lotNum, 'rock_removal', e.target.checked)} />
                        <Label>Rock Removal</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <input type="checkbox" checked={input.existing_neighbours} onChange={(e) => updateSiteCost(lotNum, 'existing_neighbours', e.target.checked)} />
                        <Label>Existing Neighbours</Label>
                      </div>
                      <div className="col-span-2">
                        <Label>Notes</Label>
                        <Input
                          value={input.notes || ''}
                          onChange={(e) => updateSiteCost(lotNum, 'notes', e.target.value || null)}
                          placeholder="Optional notes..."
                        />
                      </div>
                    </CardContent>
                  </Card>
                ))}
                <Button onClick={handleSubmitEstimate} disabled={estimateMut.isPending}>
                  <Calculator className="mr-2 h-4 w-4" />
                  {estimateMut.isPending ? 'Calculating...' : 'Calculate & Generate'}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Price Breakdown (visible when Priced or later) */}
      {showBreakdown && (
        <Card className="mt-6">
          <CardHeader><CardTitle>Price Breakdown</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="pb-2 pr-4">Lot</th>
                    <th className="pb-2 pr-4">House</th>
                    <th className="pb-2 pr-4">Facade</th>
                    <th className="pb-2 pr-4 text-right">House Price</th>
                    <th className="pb-2 pr-4 text-right">Facade</th>
                    <th className="pb-2 pr-4 text-right">Site Costs</th>
                    <th className="pb-2 pr-4 text-right">Guidelines</th>
                    <th className="pb-2 pr-4 text-right">Landscaping</th>
                    <th className="pb-2 pr-4 text-right">Upgrades</th>
                    <th className="pb-2 pr-4 text-right">Discount</th>
                    <th className="pb-2 pr-4 text-right font-semibold">Build</th>
                    <th className="pb-2 text-right font-semibold">Package</th>
                  </tr>
                </thead>
                <tbody>
                  {(request.price_breakdown as PriceBreakdownItem[]).map((bd) => (
                    <tr key={bd.lot_number} className="border-b">
                      <td className="py-2 pr-4">{bd.lot_number}</td>
                      <td className="py-2 pr-4">{bd.house_name}</td>
                      <td className="py-2 pr-4">{bd.facade_name}</td>
                      <td className="py-2 pr-4 text-right">${Number(bd.house_price).toLocaleString()}</td>
                      <td className="py-2 pr-4 text-right">${Number(bd.facade_price).toLocaleString()}</td>
                      <td className="py-2 pr-4 text-right">${Number(bd.site_costs_total).toLocaleString()}</td>
                      <td className="py-2 pr-4 text-right">${Number(bd.design_guidelines_total).toLocaleString()}</td>
                      <td className="py-2 pr-4 text-right">${Number(bd.extra_landscaping).toLocaleString()}</td>
                      <td className="py-2 pr-4 text-right">${Number(bd.upgrades_total).toLocaleString()}</td>
                      <td className="py-2 pr-4 text-right">${Number(bd.discount).toLocaleString()}</td>
                      <td className="py-2 pr-4 text-right font-semibold">${Number(bd.total_build_price).toLocaleString()}</td>
                      <td className="py-2 text-right font-semibold">${Number(bd.total_package_price).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {/* Line item details expandable */}
            <details className="mt-4">
              <summary className="cursor-pointer text-sm text-muted-foreground">
                View line item details
              </summary>
              <div className="mt-2 space-y-4">
                {(request.price_breakdown as PriceBreakdownItem[]).map((bd) => (
                  <div key={bd.lot_number} className="rounded border p-3">
                    <h4 className="font-medium text-sm mb-2">Lot {bd.lot_number} - {bd.house_name} ({bd.facade_name})</h4>
                    {!bd.house_fits && (
                      <p className="text-sm text-destructive mb-2">House does not fit: {bd.house_fits_reason}</p>
                    )}
                    {bd.warnings.length > 0 && (
                      <div className="mb-2">
                        {bd.warnings.map((w, i) => (
                          <p key={i} className="text-sm text-yellow-600">{w}</p>
                        ))}
                      </div>
                    )}
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left pb-1">Item</th>
                          <th className="text-right pb-1">Amount</th>
                          <th className="text-left pb-1 pl-3">Category</th>
                          <th className="text-left pb-1 pl-3">Detail</th>
                        </tr>
                      </thead>
                      <tbody>
                        {bd.line_items.map((li, i) => (
                          <tr key={i} className="border-b border-dashed">
                            <td className="py-1">{li.name}</td>
                            <td className="py-1 text-right">${Number(li.amount).toLocaleString()}</td>
                            <td className="py-1 pl-3 text-muted-foreground">{li.category}</td>
                            <td className="py-1 pl-3 text-muted-foreground">{li.detail || ''}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ))}
              </div>
            </details>
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

          {canFulfil && !['Completed', 'Pending', 'Estimating'].includes(request.status) && (
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

      {/* Assign Estimator Dialog */}
      {showAssignDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-background p-6 shadow-lg">
            <h3 className="text-lg font-semibold mb-4">Assign Estimator</h3>
            <p className="text-sm text-muted-foreground mb-4">Select a user with pricing role to estimate site costs.</p>
            <select
              className="w-full rounded-md border px-3 py-2 text-sm mb-4"
              value={selectedEstimatorId || ''}
              onChange={(e) => setSelectedEstimatorId(Number(e.target.value) || null)}
            >
              <option value="">Select estimator...</option>
              {usersData?.items
                ?.filter((u) => u.roles?.some((r: string) => r === 'pricing' || r === 'admin'))
                .map((u) => (
                  <option key={u.profile_id} value={u.profile_id}>
                    {u.first_name} {u.last_name} ({u.email})
                  </option>
                ))}
            </select>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowAssignDialog(false)}>Cancel</Button>
              <Button
                disabled={!selectedEstimatorId || assignMut.isPending}
                onClick={() => selectedEstimatorId && assignMut.mutate(selectedEstimatorId)}
              >
                {assignMut.isPending ? 'Assigning...' : 'Assign'}
              </Button>
            </div>
          </div>
        </div>
      )}

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
