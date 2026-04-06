import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronDown, ChevronRight, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { PageHeader } from '@/components/common/PageHeader'
import {
  getValidations,
  listTemplates,
  updateMappings,
  uploadTemplate,
} from '@/api/pricingTemplates'
import type { PricingTemplateRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const BRANDS = [
  { slug: 'hermitage', label: 'Hermitage Homes' },
  { slug: 'kingsbridge', label: 'Kingsbridge Homes' },
] as const

function BrandTemplateCard({ brand, template }: { brand: typeof BRANDS[number]; template?: PricingTemplateRead }) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const fileRef = useRef<HTMLInputElement>(null)
  const [sheetName, setSheetName] = useState(template?.sheet_name ?? '')
  const [dataStartRow, setDataStartRow] = useState(template?.data_start_row ?? 2)
  const [expandedFields, setExpandedFields] = useState<Set<string>>(new Set())

  const { data: validationsData } = useQuery({
    queryKey: ['validations', brand.slug],
    queryFn: () => getValidations(brand.slug),
    enabled: !!template,
  })

  const uploadMut = useMutation({
    mutationFn: (file: File) => uploadTemplate(brand.slug, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pricing-templates'] })
      queryClient.invalidateQueries({ queryKey: ['validations', brand.slug] })
      toast({ title: 'Template uploaded', variant: 'success' })
    },
    onError: (err) => {
      toast({ title: 'Upload failed', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const mappingsMut = useMutation({
    mutationFn: () => {
      if (!template) return Promise.reject(new Error('No template'))
      return updateMappings(template.template_id, {
        sheet_name: sheetName || undefined,
        data_start_row: dataStartRow || undefined,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pricing-templates'] })
      toast({ title: 'Mappings updated', variant: 'success' })
    },
    onError: (err) => {
      toast({ title: 'Update failed', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) uploadMut.mutate(file)
    e.target.value = ''
  }

  function toggleField(field: string) {
    setExpandedFields((prev) => {
      const next = new Set(prev)
      if (next.has(field)) next.delete(field)
      else next.add(field)
      return next
    })
  }

  const validations = validationsData?.validations ?? template?.data_validations ?? {}

  return (
    <Card>
      <CardHeader>
        <CardTitle>{brand.label}</CardTitle>
        <CardDescription>
          {template
            ? `Current file: ${template.file_path.split('/').pop()} (uploaded ${new Date(template.updated_at).toLocaleDateString()})`
            : 'No template uploaded yet'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <input
            ref={fileRef}
            type="file"
            accept=".xlsx,.xlsm"
            className="hidden"
            onChange={handleFileChange}
          />
          <Button
            variant="outline"
            onClick={() => fileRef.current?.click()}
            disabled={uploadMut.isPending}
          >
            <Upload className="mr-2 h-4 w-4" />
            {uploadMut.isPending ? 'Uploading...' : 'Upload Template'}
          </Button>
        </div>

        {template && (
          <>
            <div className="border-t pt-4">
              <h4 className="mb-3 text-sm font-semibold">Cell Mappings</h4>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-xs text-muted-foreground">Sheet Name</label>
                  <Input
                    value={sheetName}
                    onChange={(e) => setSheetName(e.target.value)}
                    placeholder="Sheet1"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs text-muted-foreground">Data Start Row</label>
                  <Input
                    type="number"
                    min={1}
                    value={dataStartRow}
                    onChange={(e) => setDataStartRow(Number(e.target.value))}
                  />
                </div>
              </div>
              <Button
                size="sm"
                className="mt-2"
                onClick={() => mappingsMut.mutate()}
                disabled={mappingsMut.isPending}
              >
                Save Mappings
              </Button>
            </div>

            <div className="border-t pt-4">
              <h4 className="mb-3 text-sm font-semibold">Data Validations</h4>
              {Object.keys(validations).length === 0 ? (
                <p className="text-sm text-muted-foreground">No data validations extracted.</p>
              ) : (
                <div className="space-y-1">
                  {Object.entries(validations).map(([field, values]) => (
                    <div key={field} className="rounded border">
                      <button
                        className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-muted/50"
                        onClick={() => toggleField(field)}
                      >
                        {expandedFields.has(field) ? (
                          <ChevronDown className="h-3 w-3" />
                        ) : (
                          <ChevronRight className="h-3 w-3" />
                        )}
                        <span className="font-medium">{field}</span>
                        <Badge variant="secondary" className="ml-auto text-xs">
                          {values.length} values
                        </Badge>
                      </button>
                      {expandedFields.has(field) && (
                        <div className="border-t px-3 py-2">
                          <div className="flex flex-wrap gap-1">
                            {values.map((v) => (
                              <Badge key={v} variant="outline" className="text-xs">
                                {v}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}

export default function PricingTemplatesPage() {
  const { data: templates, isLoading } = useQuery({
    queryKey: ['pricing-templates'],
    queryFn: listTemplates,
  })

  return (
    <div>
      <PageHeader
        title="Pricing Templates"
        description="Upload and configure Excel pricing templates for each brand."
      />

      {isLoading ? (
        <p className="text-muted-foreground">Loading templates...</p>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {BRANDS.map((brand) => {
            const template = templates?.find(
              (t) => t.brand.toLowerCase().includes(brand.slug),
            )
            return <BrandTemplateCard key={brand.slug} brand={brand} template={template} />
          })}
        </div>
      )}
    </div>
  )
}
