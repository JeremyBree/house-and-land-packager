import { useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { CheckCircle2, FileSpreadsheet, Upload, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { PageHeader } from '@/components/common/PageHeader'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import { importPricingWorkbook, type ImportResult } from '@/api/importData'

const BRANDS = ['Hermitage Homes', 'Kingsbridge Homes'] as const

export default function ImportDataPage() {
  const { toast } = useToast()
  const fileRef = useRef<HTMLInputElement>(null)
  const [brand, setBrand] = useState<string>(BRANDS[0])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [dragOver, setDragOver] = useState(false)

  const importMut = useMutation({
    mutationFn: () => importPricingWorkbook(selectedFile!, brand),
    onSuccess: (data) => {
      setResult(data)
      const totalCreated =
        data.houses_created +
        data.facades_created +
        data.energy_ratings_created +
        data.upgrades_created +
        data.upgrade_categories_created +
        data.wholesale_groups_created +
        data.commission_rates_created +
        data.travel_surcharges_created +
        data.postcode_costs_created +
        data.guideline_types_created +
        data.estate_guidelines_created +
        data.fbc_bands_created +
        data.site_cost_tiers_created +
        data.site_cost_items_created
      toast({
        title: 'Import complete',
        description: `${totalCreated} records created, ${data.skipped} skipped.`,
        variant: 'success',
      })
    },
    onError: (err) => {
      toast({ title: 'Import failed', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  function handleFile(file: File) {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext !== 'xlsx' && ext !== 'xlsm') {
      toast({ title: 'Invalid file', description: 'Please select an .xlsx or .xlsm file.', variant: 'destructive' })
      return
    }
    setSelectedFile(file)
    setResult(null)
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const resultRows: { label: string; value: number }[] = result
    ? [
        { label: 'House Designs', value: result.houses_created },
        { label: 'Facades', value: result.facades_created },
        { label: 'Energy Ratings', value: result.energy_ratings_created },
        { label: 'Upgrade Categories', value: result.upgrade_categories_created },
        { label: 'Upgrade Items', value: result.upgrades_created },
        { label: 'Wholesale Groups', value: result.wholesale_groups_created },
        { label: 'Commission Rates', value: result.commission_rates_created },
        { label: 'Travel Surcharges', value: result.travel_surcharges_created },
        { label: 'Postcode Costs', value: result.postcode_costs_created },
        { label: 'Guideline Types', value: result.guideline_types_created },
        { label: 'Estate Guidelines', value: result.estate_guidelines_created },
        { label: 'FBC Escalation Bands', value: result.fbc_bands_created },
        { label: 'Site Cost Tiers', value: result.site_cost_tiers_created },
        { label: 'Site Cost Items', value: result.site_cost_items_created },
      ]
    : []

  return (
    <div>
      <PageHeader
        title="Import Pricing Data"
        description="Upload a pricing workbook (.xlsx / .xlsm) to import house designs, facades, energy ratings, upgrades, commissions, site costs, and guidelines. Existing records are skipped (idempotent)."
      />

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Upload Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5" />
              Upload Workbook
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Brand</Label>
              <select
                className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
              >
                {BRANDS.map((b) => (
                  <option key={b} value={b}>
                    {b}
                  </option>
                ))}
              </select>
            </div>

            <div
              className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors ${
                dragOver
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/25 hover:border-primary/50'
              }`}
              onClick={() => fileRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault()
                setDragOver(true)
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
            >
              <Upload className="mb-2 h-8 w-8 text-muted-foreground" />
              <p className="text-sm font-medium">
                {selectedFile ? selectedFile.name : 'Drop workbook here or click to browse'}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">.xlsx or .xlsm files</p>
            </div>

            <input
              ref={fileRef}
              type="file"
              className="hidden"
              accept=".xlsx,.xlsm"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleFile(file)
                e.target.value = ''
              }}
            />

            <Button
              className="w-full"
              onClick={() => importMut.mutate()}
              disabled={!selectedFile || importMut.isPending}
            >
              {importMut.isPending ? 'Importing...' : 'Import Data'}
            </Button>
          </CardContent>
        </Card>

        {/* Results Card */}
        {result && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {result.errors.length === 0 ? (
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                ) : (
                  <XCircle className="h-5 w-5 text-amber-500" />
                )}
                Import Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {resultRows.map((row) => (
                  <div key={row.label} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{row.label}</span>
                    <span className={row.value > 0 ? 'font-medium text-green-600' : 'text-muted-foreground'}>
                      {row.value > 0 ? `+${row.value}` : '0'}
                    </span>
                  </div>
                ))}
                <div className="mt-2 flex items-center justify-between border-t pt-2 text-sm">
                  <span className="font-medium">Skipped (existing)</span>
                  <span className="text-muted-foreground">{result.skipped}</span>
                </div>
              </div>

              {result.errors.length > 0 && (
                <div className="mt-4">
                  <p className="mb-1 text-sm font-medium text-destructive">
                    Errors ({result.errors.length})
                  </p>
                  <ul className="max-h-40 space-y-1 overflow-y-auto">
                    {result.errors.map((err, i) => (
                      <li
                        key={i}
                        className="rounded border border-destructive/20 bg-destructive/5 px-2 py-1 text-xs"
                      >
                        {err}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
