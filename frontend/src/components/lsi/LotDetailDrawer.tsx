import { useNavigate } from 'react-router-dom'
import { X, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { LotStatusBadge } from '@/components/common/LotStatusBadge'
import { cn } from '@/lib/utils'
import { getStage } from '@/api/stages'
import type { LotSearchResult } from '@/api/types'

interface LotDetailDrawerProps {
  lot: LotSearchResult | null
  open: boolean
  onClose: () => void
}

interface FieldProps {
  label: string
  value: React.ReactNode
}

function Field({ label, value }: FieldProps) {
  return (
    <div className="flex justify-between gap-4 py-1.5 text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="text-right font-medium text-slate-900">{value ?? '—'}</span>
    </div>
  )
}

interface SectionProps {
  title: string
  children: React.ReactNode
}

function Section({ title, children }: SectionProps) {
  return (
    <div className="border-t border-slate-200 px-6 py-4">
      <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-700">
        {title}
      </div>
      <div className="divide-y divide-slate-100">{children}</div>
    </div>
  )
}

function formatCurrency(v: string | null | undefined): string {
  if (v == null || v === '') return '—'
  const n = Number(v)
  if (Number.isNaN(n)) return v
  return n.toLocaleString(undefined, { style: 'currency', currency: 'AUD', maximumFractionDigits: 0 })
}

function formatDate(v: string | null | undefined): string {
  if (!v) return '—'
  return v.slice(0, 10)
}

export function LotDetailDrawer({ lot, open, onClose }: LotDetailDrawerProps) {
  const navigate = useNavigate()

  return (
    <>
      <div
        className={cn(
          'fixed inset-0 z-[60] bg-black/40 transition-opacity',
          open ? 'opacity-100' : 'pointer-events-none opacity-0',
        )}
        onClick={onClose}
      />
      <div
        className={cn(
          'fixed right-0 top-0 z-[61] h-full w-[480px] max-w-full transform bg-white shadow-xl transition-transform duration-300',
          open ? 'translate-x-0' : 'translate-x-full',
        )}
      >
        {lot && (
          <div className="flex h-full flex-col">
            <div className="flex items-start justify-between border-b border-slate-200 px-6 py-4">
              <div>
                <div className="text-xs uppercase tracking-wide text-slate-500">
                  Lot {lot.lot_number}
                </div>
                <div className="mt-1 text-lg font-semibold text-slate-900">{lot.estate_name}</div>
                <div className="text-sm text-slate-600">{lot.stage_name}</div>
              </div>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="flex-1 overflow-y-auto">
              <Section title="Overview">
                <Field label="Estate" value={lot.estate_name} />
                <Field label="Developer" value={lot.developer_name} />
                <Field label="Region" value={lot.region_name ?? '—'} />
                <Field label="Stage" value={lot.stage_name} />
                <Field label="Suburb" value={lot.estate_suburb ?? '—'} />
                <Field label="State" value={lot.estate_state ?? '—'} />
                <Field label="Status" value={<LotStatusBadge status={lot.status} />} />
              </Section>

              <Section title="Dimensions">
                <Field label="Frontage" value={lot.frontage ? `${lot.frontage} m` : '—'} />
                <Field label="Depth" value={lot.depth ? `${lot.depth} m` : '—'} />
                <Field label="Size" value={lot.size_sqm ? `${lot.size_sqm} m²` : '—'} />
                <Field label="Corner block" value={lot.corner_block ? 'Yes' : 'No'} />
                <Field label="Orientation" value={lot.orientation ?? '—'} />
                <Field label="Side easement" value={lot.side_easement ?? '—'} />
                <Field label="Rear easement" value={lot.rear_easement ?? '—'} />
                <Field label="Substation" value={lot.substation ? 'Yes' : 'No'} />
              </Section>

              <Section title="Pricing">
                <Field label="Land price" value={formatCurrency(lot.land_price)} />
                <Field label="Build price" value={formatCurrency(lot.build_price)} />
                <Field label="Package price" value={formatCurrency(lot.package_price)} />
                <Field label="Title date" value={formatDate(lot.title_date)} />
              </Section>

              <Section title="Source">
                <Field label="Source" value={lot.source ?? '—'} />
                <Field label="Source detail" value={lot.source_detail ?? '—'} />
                <Field label="Last confirmed" value={formatDate(lot.last_confirmed_date)} />
              </Section>
            </div>

            <div className="border-t border-slate-200 px-6 py-4">
              <Button
                variant="outline"
                className="w-full"
                onClick={async () => {
                  try {
                    const stage = await getStage(lot.stage_id)
                    navigate(`/estates/${stage.estate_id}/stages/${stage.stage_id}`)
                    onClose()
                  } catch {
                    navigate('/estates')
                    onClose()
                  }
                }}
              >
                <ExternalLink className="h-4 w-4" /> View Stage
              </Button>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
