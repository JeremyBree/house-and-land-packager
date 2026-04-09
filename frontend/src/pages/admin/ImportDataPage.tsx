import { useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { CheckCircle2, Database, FileSpreadsheet, Loader2, Upload, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { PageHeader } from '@/components/common/PageHeader'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import {
  importPricingWorkbook,
  seedEstatesStages,
  seedEstateGuidelines,
  uploadEstatesStagesCsv,
  type ImportResult,
  type SeedEstatesResult,
  type SeedGuidelinesResult,
} from '@/api/importData'

const BRANDS = ['Hermitage Homes', 'Kingsbridge Homes'] as const

export default function ImportDataPage() {
  const { toast } = useToast()
  const fileRef = useRef<HTMLInputElement>(null)
  const csvRef = useRef<HTMLInputElement>(null)
  const [brand, setBrand] = useState<string>(BRANDS[0])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [importError, setImportError] = useState<string | null>(null)
  const [dragOver, setDragOver] = useState(false)

  // Seed results
  const [seedEstatesResult, setSeedEstatesResult] = useState<SeedEstatesResult | null>(null)
  const [seedGuidelinesResult, setSeedGuidelinesResult] = useState<SeedGuidelinesResult | null>(null)

  const importMut = useMutation({
    mutationFn: () => importPricingWorkbook(selectedFile!, brand),
    onSuccess: (data) => {
      setResult(data)
      setImportError(null)
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
      const msg = extractErrorMessage(err)
      setImportError(msg)
      toast({ title: 'Import failed', description: msg, variant: 'destructive' })
    },
  })

  const seedEstatesMut = useMutation({
    mutationFn: () => seedEstatesStages(),
    onSuccess: (data) => {
      setSeedEstatesResult(data)
      toast({
        title: 'Estates seeded',
        description: `${data.estates_created} estates, ${data.stages_created} stages created.`,
        variant: 'success',
      })
    },
    onError: (err) => toast({ title: 'Seed failed', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const seedGuidelinesMut = useMutation({
    mutationFn: () => seedEstateGuidelines(),
    onSuccess: (data) => {
      setSeedGuidelinesResult(data)
      toast({
        title: 'Guidelines seeded',
        description: `${data.created} guidelines created, ${data.skipped} skipped.`,
        variant: 'success',
      })
    },
    onError: (err) => toast({ title: 'Seed failed', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const uploadCsvMut = useMutation({
    mutationFn: (file: File) => uploadEstatesStagesCsv(file),
    onSuccess: (data) => {
      setSeedEstatesResult(data)
      toast({
        title: 'CSV imported',
        description: `${data.estates_created} estates, ${data.stages_created} stages created.`,
        variant: 'success',
      })
    },
    onError: (err) => toast({ title: 'Upload failed', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  function handleFile(file: File) {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext !== 'xlsx' && ext !== 'xlsm') {
      toast({ title: 'Invalid file', description: 'Please select an .xlsx or .xlsm file.', variant: 'destructive' })
      return
    }
    setSelectedFile(file)
    setResult(null)
    setImportError(null)
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  function handleCsvFile(file: File) {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext !== 'csv') {
      toast({ title: 'Invalid file', description: 'Please select a .csv file.', variant: 'destructive' })
      return
    }
    uploadCsvMut.mutate(file)
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

  const isSeedRunning = seedEstatesMut.isPending || seedGuidelinesMut.isPending || uploadCsvMut.isPending

  return (
    <div>
      <PageHeader
        title="Import Data"
        description="Import pricing workbooks, seed estates and stages, and bulk-load estate guidelines."
      />

      <div className="space-y-6">
        {/* Bulk Seed Card — shown first since estates must exist before workbook import */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Bulk Seed Data
            </CardTitle>
            <CardDescription>
              Load estates, stages, and estate guidelines from server-side seed files or CSV upload. Run in order: Estates first, then Workbook import, then Guidelines.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Step 1: Seed Estates */}
              <div className="rounded-lg border p-4 space-y-3">
                <p className="text-sm font-medium">Step 1: Seed Estates & Stages</p>
                <p className="text-xs text-muted-foreground">
                  Creates 874 estates and ~4000 stages from the seed file. Must be done before workbook import so estate guidelines can be linked.
                </p>
                <Button
                  className="w-full"
                  size="sm"
                  onClick={() => seedEstatesMut.mutate()}
                  disabled={isSeedRunning}
                >
                  {seedEstatesMut.isPending ? (
                    <><Loader2 className="mr-1 h-4 w-4 animate-spin" /> Seeding...</>
                  ) : (
                    'Seed Estates'
                  )}
                </Button>
                {seedEstatesResult && (
                  <SeedResultSummary
                    rows={[
                      { label: 'Estates created', value: seedEstatesResult.estates_created },
                      { label: 'Stages created', value: seedEstatesResult.stages_created },
                      { label: 'Skipped', value: seedEstatesResult.skipped },
                    ]}
                    errors={seedEstatesResult.errors}
                  />
                )}
              </div>

              {/* Step 2: Workbook import (visual cue) */}
              <div className="rounded-lg border border-dashed p-4 space-y-3">
                <p className="text-sm font-medium">Step 2: Import Pricing Workbook</p>
                <p className="text-xs text-muted-foreground">
                  Upload the .xlsm workbook below to import house designs, facades, upgrades, commissions, guideline types, and estate guidelines.
                </p>
              </div>

              {/* Step 3: Seed Guidelines */}
              <div className="rounded-lg border p-4 space-y-3">
                <p className="text-sm font-medium">Step 3: Seed Estate Guidelines</p>
                <p className="text-xs text-muted-foreground">
                  Bulk-loads ~86k guideline assignments from the seed CSV. Requires estates, stages, and guideline types to exist first.
                </p>
                <Button
                  className="w-full"
                  size="sm"
                  onClick={() => seedGuidelinesMut.mutate()}
                  disabled={isSeedRunning}
                >
                  {seedGuidelinesMut.isPending ? (
                    <><Loader2 className="mr-1 h-4 w-4 animate-spin" /> Seeding...</>
                  ) : (
                    'Seed Guidelines'
                  )}
                </Button>
                {seedGuidelinesResult && (
                  <SeedResultSummary
                    rows={[
                      { label: 'Guidelines created', value: seedGuidelinesResult.created },
                      { label: 'Skipped', value: seedGuidelinesResult.skipped },
                    ]}
                    errors={seedGuidelinesResult.errors}
                  />
                )}
              </div>
            </div>

            {/* CSV Upload for estates/stages */}
            <div className="rounded-lg border p-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Upload Estates CSV</p>
                <p className="text-xs text-muted-foreground">
                  Upload a custom CSV with columns: estate_name, stage_name
                </p>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => csvRef.current?.click()}
                disabled={uploadCsvMut.isPending}
              >
                {uploadCsvMut.isPending ? (
                  <><Loader2 className="mr-1 h-4 w-4 animate-spin" /> Uploading...</>
                ) : (
                  <><Upload className="mr-1 h-4 w-4" /> Upload CSV</>
                )}
              </Button>
              <input
                ref={csvRef}
                type="file"
                className="hidden"
                accept=".csv"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleCsvFile(file)
                  e.target.value = ''
                }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Upload Workbook Card */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileSpreadsheet className="h-5 w-5" />
                Upload Pricing Workbook
              </CardTitle>
              <CardDescription>
                Upload an .xlsx/.xlsm file to import house designs, facades, energy ratings, upgrades, commissions, site costs, and guideline types. Estates must be seeded first for estate guidelines to link correctly.
              </CardDescription>
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
          {(result || importError) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {importError ? (
                    <XCircle className="h-5 w-5 text-destructive" />
                  ) : result && result.errors.length === 0 ? (
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-amber-500" />
                  )}
                  Import Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                {importError && (
                  <div className="rounded border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
                    {importError}
                  </div>
                )}
                {result && (
                  <>
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
                  </>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

function SeedResultSummary({
  rows,
  errors,
}: {
  rows: { label: string; value: number }[]
  errors: { row: number; error: string }[]
}) {
  return (
    <div className="rounded bg-muted/50 p-3 space-y-1">
      {rows.map((r) => (
        <div key={r.label} className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">{r.label}</span>
          <span className={r.value > 0 ? 'font-medium text-green-600' : 'text-muted-foreground'}>
            {r.value > 0 ? `+${r.value}` : '0'}
          </span>
        </div>
      ))}
      {errors.length > 0 && (
        <div className="mt-2">
          <p className="text-xs font-medium text-destructive">
            Errors ({errors.length}{errors.length >= 50 ? '+' : ''})
          </p>
          <ul className="max-h-32 space-y-1 overflow-y-auto mt-1">
            {errors.map((err, i) => (
              <li key={i} className="rounded border border-destructive/20 bg-destructive/5 px-2 py-1 text-xs">
                Row {err.row}: {err.error}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
