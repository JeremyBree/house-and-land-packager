import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { PageHeader } from '@/components/common/PageHeader'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import { getPricingConfig, updatePricingConfig, type PricingConfigRead } from '@/api/pricingRequests'
import { Pencil, Save, X } from 'lucide-react'

const BRANDS = ['Hermitage Homes', 'Kingsbridge Homes']

const CONFIG_FIELDS: { key: keyof Omit<PricingConfigRead, 'config_id' | 'brand'>; label: string; type: 'decimal' | 'int' }[] = [
  { key: 'landscaping_rate_per_sqm', label: 'Landscaping Rate ($/sqm)', type: 'decimal' },
  { key: 'base_commission', label: 'Base Commission ($)', type: 'decimal' },
  { key: 'pct_commission_divisor', label: 'Pct Commission Divisor', type: 'decimal' },
  { key: 'kdrb_surcharge', label: 'KDRB Surcharge ($)', type: 'decimal' },
  { key: 'holding_cost_rate', label: 'Holding Cost Rate', type: 'decimal' },
  { key: 'small_lot_threshold_sqm', label: 'Small Lot Threshold (sqm)', type: 'decimal' },
  { key: 'small_lot_discount', label: 'Small Lot Discount ($)', type: 'decimal' },
  { key: 'dwellings_discount', label: 'Dwellings Discount ($)', type: 'decimal' },
  { key: 'corner_block_savings', label: 'Corner Block Savings ($)', type: 'decimal' },
  { key: 'build_price_rounding', label: 'Build Price Rounding ($)', type: 'int' },
  { key: 'package_price_rounding', label: 'Package Price Rounding ($)', type: 'int' },
]

function BrandConfigCard({ brand }: { brand: string }) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [editing, setEditing] = useState(false)
  const [formValues, setFormValues] = useState<Record<string, string | number>>({})

  const { data: config, isLoading } = useQuery({
    queryKey: ['pricing-config', brand],
    queryFn: () => getPricingConfig(brand),
  })

  const updateMut = useMutation({
    mutationFn: (updates: Record<string, unknown>) => updatePricingConfig(brand, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pricing-config', brand] })
      toast({ title: 'Config updated' })
      setEditing(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const startEditing = () => {
    if (!config) return
    const vals: Record<string, string | number> = {}
    for (const field of CONFIG_FIELDS) {
      vals[field.key] = config[field.key]
    }
    setFormValues(vals)
    setEditing(true)
  }

  const handleSave = () => {
    const updates: Record<string, unknown> = {}
    for (const field of CONFIG_FIELDS) {
      const val = formValues[field.key]
      if (field.type === 'int') {
        updates[field.key] = Number(val)
      } else {
        updates[field.key] = String(val)
      }
    }
    updateMut.mutate(updates)
  }

  if (isLoading) return <Card><CardContent className="p-6">Loading...</CardContent></Card>

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{brand}</CardTitle>
        {!editing ? (
          <Button variant="outline" size="sm" onClick={startEditing}>
            <Pencil className="mr-2 h-4 w-4" /> Edit
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setEditing(false)}>
              <X className="mr-2 h-4 w-4" /> Cancel
            </Button>
            <Button size="sm" onClick={handleSave} disabled={updateMut.isPending}>
              <Save className="mr-2 h-4 w-4" /> {updateMut.isPending ? 'Saving...' : 'Save'}
            </Button>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {CONFIG_FIELDS.map((field) => (
            <div key={field.key}>
              <Label className="text-xs text-muted-foreground">{field.label}</Label>
              {editing ? (
                <Input
                  type={field.type === 'int' ? 'number' : 'text'}
                  value={formValues[field.key] ?? ''}
                  onChange={(e) =>
                    setFormValues((prev) => ({ ...prev, [field.key]: e.target.value }))
                  }
                />
              ) : (
                <p className="text-sm font-medium">
                  {config ? String(config[field.key]) : '-'}
                </p>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default function PricingConfigPage() {
  return (
    <div className="p-6">
      <PageHeader
        title="Pricing Configuration"
        description="Manage configurable pricing engine constants per brand"
      />
      <div className="grid gap-6">
        {BRANDS.map((brand) => (
          <BrandConfigCard key={brand} brand={brand} />
        ))}
      </div>
    </div>
  )
}
