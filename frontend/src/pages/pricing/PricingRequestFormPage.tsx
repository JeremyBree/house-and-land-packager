import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { AlertTriangle, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageHeader } from '@/components/common/PageHeader'
import {
  createPricingRequest,
  type PricingRequestCreateInput,
  type LotEntry,
  type ClashViolationResponse,
} from '@/api/pricingRequests'
import { listEstates } from '@/api/estates'
import { listStages } from '@/api/stages'
import { listLots } from '@/api/lots'
import { listHouseDesigns } from '@/api/houseDesigns'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import axios from 'axios'

const BRANDS = ['Hermitage Homes', 'Kingsbridge Homes'] as const

interface LotEntryForm extends LotEntry {
  ad_hoc_lot: boolean
}

const emptyLot = (): LotEntryForm => ({
  lot_number: '',
  house_type: '',
  facade_type: '',
  garage_side: null,
  custom_house_design: false,
  ad_hoc_lot: false,
})

export default function PricingRequestFormPage() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [searchParams] = useSearchParams()

  const [estateId, setEstateId] = useState<number | ''>(
    searchParams.get('estate_id') ? Number(searchParams.get('estate_id')) : '',
  )
  const [stageId, setStageId] = useState<number | ''>(
    searchParams.get('stage_id') ? Number(searchParams.get('stage_id')) : '',
  )
  const [brand, setBrand] = useState<string>(searchParams.get('brand') || '')
  const [hasLandTitled, setHasLandTitled] = useState(true)
  const [titlingWhen, setTitlingWhen] = useState('')
  const [isKdrb, setIsKdrb] = useState(false)
  const [is1090Deal, setIs1090Deal] = useState(false)
  const [devLandReferrals, setDevLandReferrals] = useState(false)
  const [buildingCrossover, setBuildingCrossover] = useState(false)
  const [sharedCrossovers, setSharedCrossovers] = useState(false)
  const [sideEasement, setSideEasement] = useState('')
  const [rearEasement, setRearEasement] = useState('')
  const [bdm, setBdm] = useState('')
  const [wholesaleGroup, setWholesaleGroup] = useState('')
  const [lots, setLots] = useState<LotEntryForm[]>([emptyLot()])
  const [notes, setNotes] = useState('')
  const [clashErrors, setClashErrors] = useState<ClashViolationResponse | null>(null)

  const { data: estatesData } = useQuery({
    queryKey: ['estates', { page: 1, size: 200 }],
    queryFn: () => listEstates({ page: 1, size: 200 }),
  })

  const selectedEstateId = estateId || undefined
  const { data: stagesData } = useQuery({
    queryKey: ['stages', selectedEstateId],
    queryFn: () => listStages(selectedEstateId!),
    enabled: !!selectedEstateId,
  })

  // Fetch available lots for the selected stage
  const { data: lotsData } = useQuery({
    queryKey: ['stage-lots', stageId],
    queryFn: () => listLots(stageId as number, { size: 200 }),
    enabled: !!stageId,
  })
  const availableLots = lotsData?.items ?? []

  // Fetch house designs for the selected brand
  const { data: houseDesigns } = useQuery({
    queryKey: ['house-designs', brand],
    queryFn: () => listHouseDesigns(brand),
    enabled: !!brand,
  })

  const isHermitage = brand === 'Hermitage Homes'
  const isKingsbridge = brand === 'Kingsbridge Homes'

  const submitMut = useMutation({
    mutationFn: (payload: PricingRequestCreateInput) => createPricingRequest(payload),
    onSuccess: () => {
      toast({ title: 'Pricing request submitted successfully' })
      navigate('/pricing-requests')
    },
    onError: (err) => {
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        const data = err.response.data as ClashViolationResponse
        if (data.violations) {
          setClashErrors(data)
          return
        }
      }
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const addLot = () => setLots([...lots, emptyLot()])
  const removeLot = (idx: number) => {
    if (lots.length <= 1) return
    setLots(lots.filter((_, i) => i !== idx))
  }
  const updateLot = (idx: number, field: keyof LotEntryForm, value: string | boolean | null) => {
    const updated = [...lots]
    updated[idx] = { ...updated[idx], [field]: value }
    // Reset facade when house type changes
    if (field === 'house_type') {
      updated[idx].facade_type = ''
    }
    setLots(updated)
  }

  // Get facades for a specific lot entry's selected house design
  const getFacadesForLot = (lot: LotEntryForm) => {
    if (!lot.house_type || !houseDesigns) return []
    const design = houseDesigns.find((d) => d.house_name === lot.house_type)
    return design?.facades ?? []
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setClashErrors(null)

    // Strip the ad_hoc_lot field before sending
    const cleanLots: LotEntry[] = lots.map(({ ad_hoc_lot: _, ...rest }) => rest)

    const payload: PricingRequestCreateInput = {
      estate_id: estateId as number,
      stage_id: stageId as number,
      brand,
      has_land_titled: hasLandTitled,
      titling_when: !hasLandTitled && titlingWhen ? titlingWhen : null,
      is_kdrb: isKdrb,
      is_10_90_deal: is1090Deal,
      developer_land_referrals: devLandReferrals,
      building_crossover: buildingCrossover,
      shared_crossovers: sharedCrossovers,
      side_easement: sideEasement || null,
      rear_easement: rearEasement || null,
      bdm: isHermitage ? bdm : null,
      wholesale_group: isHermitage ? wholesaleGroup : null,
      lots: cleanLots,
      notes: notes || null,
    }

    submitMut.mutate(payload)
  }

  return (
    <div className="p-6">
      <PageHeader title="New Pricing Request" description="Submit a pricing request for house & land packages" />

      {clashErrors && (
        <Card className="mb-6 border-destructive">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Clash Violations Detected
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {clashErrors.violations.map((v, i) => (
                <li key={i} className="rounded border border-destructive/30 bg-destructive/5 p-3 text-sm">
                  <strong>Lots {v.lot_numbers.join(' & ')}</strong> — same design &quot;{v.design}&quot; + facade &quot;{v.facade}&quot;
                  <span className="ml-2 text-xs text-muted-foreground">({v.violation_type.replace('_', ' ')})</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Estate & Stage */}
        <Card>
          <CardHeader><CardTitle>Location</CardTitle></CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <div>
              <Label>Estate</Label>
              <select
                className="mt-1 w-full rounded-md border px-3 py-2 text-sm"
                value={estateId}
                onChange={(e) => { setEstateId(e.target.value ? Number(e.target.value) : ''); setStageId(''); setLots([emptyLot()]) }}
                required
              >
                <option value="">Select estate...</option>
                {estatesData?.items.map((e) => (
                  <option key={e.estate_id} value={e.estate_id}>{e.estate_name}</option>
                ))}
              </select>
            </div>
            <div>
              <Label>Stage</Label>
              <select
                className="mt-1 w-full rounded-md border px-3 py-2 text-sm"
                value={stageId}
                onChange={(e) => { setStageId(e.target.value ? Number(e.target.value) : ''); setLots([emptyLot()]) }}
                required
                disabled={!estateId}
              >
                <option value="">Select stage...</option>
                {stagesData?.map((s) => (
                  <option key={s.stage_id} value={s.stage_id}>{s.name}</option>
                ))}
              </select>
            </div>
            <div>
              <Label>Brand</Label>
              <select
                className="mt-1 w-full rounded-md border px-3 py-2 text-sm"
                value={brand}
                onChange={(e) => {
                  setBrand(e.target.value)
                  // Reset house/facade selections when brand changes
                  setLots(lots.map((l) => ({ ...l, house_type: '', facade_type: '' })))
                }}
                required
              >
                <option value="">Select brand...</option>
                {BRANDS.map((b) => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>
          </CardContent>
        </Card>

        {/* General Toggles */}
        <Card>
          <CardHeader><CardTitle>General Options</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={hasLandTitled} onChange={(e) => setHasLandTitled(e.target.checked)} className="h-4 w-4 rounded border" />
                Land Titled
              </label>
              {!hasLandTitled && (
                <div>
                  <Label>Titling When</Label>
                  <Input type="date" value={titlingWhen} onChange={(e) => setTitlingWhen(e.target.value)} />
                </div>
              )}
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={isKdrb} onChange={(e) => setIsKdrb(e.target.checked)} className="h-4 w-4 rounded border" />
                KDRB
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={is1090Deal} onChange={(e) => setIs1090Deal(e.target.checked)} className="h-4 w-4 rounded border" />
                10/90 Deal
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={devLandReferrals} onChange={(e) => setDevLandReferrals(e.target.checked)} className="h-4 w-4 rounded border" />
                Developer Land Referrals
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={buildingCrossover} onChange={(e) => setBuildingCrossover(e.target.checked)} className="h-4 w-4 rounded border" />
                Building Crossover
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={sharedCrossovers} onChange={(e) => setSharedCrossovers(e.target.checked)} className="h-4 w-4 rounded border" />
                Shared Crossovers
              </label>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <Label>Side Easement</Label>
                <Input type="number" step="0.01" value={sideEasement} onChange={(e) => setSideEasement(e.target.value)} placeholder="Optional" />
              </div>
              <div>
                <Label>Rear Easement</Label>
                <Input type="number" step="0.01" value={rearEasement} onChange={(e) => setRearEasement(e.target.value)} placeholder="Optional" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Brand-specific fields */}
        {isHermitage && (
          <Card>
            <CardHeader><CardTitle>Hermitage Homes</CardTitle></CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div>
                <Label>BDM *</Label>
                <Input value={bdm} onChange={(e) => setBdm(e.target.value)} required />
              </div>
              <div>
                <Label>Wholesale Group *</Label>
                <Input value={wholesaleGroup} onChange={(e) => setWholesaleGroup(e.target.value)} required />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Lots */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Lot Entries</CardTitle>
              <Button type="button" variant="outline" size="sm" onClick={addLot}>
                <Plus className="mr-1 h-4 w-4" /> Add Lot
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {lots.map((lot, idx) => {
              const facades = getFacadesForLot(lot)
              return (
                <div key={idx} className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-medium">Lot {idx + 1}</span>
                    {lots.length > 1 && (
                      <Button type="button" variant="ghost" size="sm" onClick={() => removeLot(idx)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    )}
                  </div>
                  <div className="grid gap-3 md:grid-cols-4">
                    {/* Lot Number - dropdown or ad-hoc */}
                    <div>
                      <Label>Lot Number *</Label>
                      {lot.ad_hoc_lot ? (
                        <Input
                          value={lot.lot_number}
                          onChange={(e) => updateLot(idx, 'lot_number', e.target.value)}
                          placeholder="Enter lot number..."
                          required
                        />
                      ) : (
                        <select
                          className="mt-1 w-full rounded-md border px-3 py-2 text-sm"
                          value={lot.lot_number}
                          onChange={(e) => updateLot(idx, 'lot_number', e.target.value)}
                          required
                          disabled={!stageId}
                        >
                          <option value="">Select lot...</option>
                          {availableLots.map((l) => (
                            <option key={l.lot_id} value={l.lot_number}>
                              {l.lot_number}{l.street_name ? ` — ${l.street_name}` : ''}
                            </option>
                          ))}
                        </select>
                      )}
                      <label className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
                        <input
                          type="checkbox"
                          checked={lot.ad_hoc_lot}
                          onChange={(e) => {
                            updateLot(idx, 'ad_hoc_lot', e.target.checked)
                            if (e.target.checked) updateLot(idx, 'lot_number', '')
                            else updateLot(idx, 'lot_number', '')
                          }}
                          className="h-3 w-3 rounded border"
                        />
                        Ad hoc lot
                      </label>
                    </div>

                    {/* House Type - dropdown from house catalog */}
                    <div>
                      <Label>House Type *</Label>
                      <select
                        className="mt-1 w-full rounded-md border px-3 py-2 text-sm"
                        value={lot.house_type}
                        onChange={(e) => updateLot(idx, 'house_type', e.target.value)}
                        required
                        disabled={!brand}
                      >
                        <option value="">Select house...</option>
                        {houseDesigns?.filter((d) => d.active).map((d) => (
                          <option key={d.design_id} value={d.house_name}>
                            {d.house_name}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Facade Type - dropdown filtered by selected house */}
                    <div>
                      <Label>Facade Type *</Label>
                      <select
                        className="mt-1 w-full rounded-md border px-3 py-2 text-sm"
                        value={lot.facade_type}
                        onChange={(e) => updateLot(idx, 'facade_type', e.target.value)}
                        required
                        disabled={!lot.house_type}
                      >
                        <option value="">Select facade...</option>
                        {facades.map((f) => (
                          <option key={f.facade_id} value={f.facade_name}>
                            {f.facade_name}
                          </option>
                        ))}
                      </select>
                    </div>

                    {isHermitage && (
                      <div>
                        <Label>Garage Side</Label>
                        <select
                          className="mt-1 w-full rounded-md border px-3 py-2 text-sm"
                          value={lot.garage_side ?? ''}
                          onChange={(e) => updateLot(idx, 'garage_side', e.target.value || null)}
                        >
                          <option value="">-</option>
                          <option value="Left">Left</option>
                          <option value="Right">Right</option>
                        </select>
                      </div>
                    )}
                    {isKingsbridge && (
                      <label className="flex items-end gap-2 pb-2 text-sm">
                        <input
                          type="checkbox"
                          checked={!!lot.custom_house_design}
                          onChange={(e) => updateLot(idx, 'custom_house_design', e.target.checked)}
                          className="h-4 w-4 rounded border"
                        />
                        Custom Design
                      </label>
                    )}
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>

        {/* Notes */}
        <Card>
          <CardHeader><CardTitle>Notes</CardTitle></CardHeader>
          <CardContent>
            <textarea
              className="w-full rounded-md border px-3 py-2 text-sm"
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Optional notes..."
            />
          </CardContent>
        </Card>

        <div className="flex gap-3">
          <Button type="submit" disabled={submitMut.isPending}>
            {submitMut.isPending ? 'Submitting...' : 'Submit Request'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/pricing-requests')}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
