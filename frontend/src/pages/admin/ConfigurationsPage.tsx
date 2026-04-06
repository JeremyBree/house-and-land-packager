import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { FileText, Globe, Lock, Mail, Plus, Pencil, Trash2 } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { PageHeader } from '@/components/common/PageHeader'
import {
  listConfigurations,
  createConfiguration,
  updateConfiguration,
  deleteConfiguration,
  toggleConfiguration,
  type ConfigurationRead,
  type ConfigurationCreate,
} from '@/api/configurations'
import { extractErrorMessage } from '@/api/client'

const typeIcons: Record<string, typeof Mail> = {
  email_account: Mail,
  website: Globe,
  portal: Lock,
  pdf_folder: FileText,
}

const typeLabels: Record<string, string> = {
  email_account: 'Email',
  website: 'Website',
  portal: 'Portal',
  pdf_folder: 'PDF Folder',
}

const CONFIG_TYPES = ['email_account', 'website', 'portal', 'pdf_folder'] as const

export default function ConfigurationsPage() {
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<ConfigurationCreate>({
    config_type: 'website',
    label: '',
    url_or_path: '',
    enabled: true,
    priority_rank: 0,
  })
  const [error, setError] = useState<string | null>(null)

  const { data: configs = [], isLoading } = useQuery({
    queryKey: ['configurations'],
    queryFn: () => listConfigurations(),
  })

  const createMutation = useMutation({
    mutationFn: (data: ConfigurationCreate) => createConfiguration(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configurations'] })
      setDialogOpen(false)
      resetForm()
    },
    onError: (err) => setError(extractErrorMessage(err)),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ConfigurationCreate> }) =>
      updateConfiguration(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configurations'] })
      setDialogOpen(false)
      resetForm()
    },
    onError: (err) => setError(extractErrorMessage(err)),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteConfiguration(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['configurations'] }),
  })

  const toggleMutation = useMutation({
    mutationFn: (id: number) => toggleConfiguration(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['configurations'] }),
  })

  function resetForm() {
    setFormData({
      config_type: 'website',
      label: '',
      url_or_path: '',
      enabled: true,
      priority_rank: 0,
    })
    setEditingId(null)
    setError(null)
  }

  function openCreate() {
    resetForm()
    setDialogOpen(true)
  }

  function openEdit(cfg: ConfigurationRead) {
    setEditingId(cfg.config_id)
    setFormData({
      config_type: cfg.config_type,
      label: cfg.label,
      url_or_path: cfg.url_or_path,
      credentials_ref: undefined,
      run_schedule: cfg.run_schedule,
      enabled: cfg.enabled,
      priority_rank: cfg.priority_rank,
      notes: cfg.notes,
    })
    setError(null)
    setDialogOpen(true)
  }

  function handleSubmit() {
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  return (
    <div>
      <PageHeader
        title="Ingestion Configurations"
        description="Manage data source configurations for ingestion agents"
        actions={
          <Button onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Add Configuration
          </Button>
        }
      />

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Label</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>URL / Path</TableHead>
                <TableHead>Schedule</TableHead>
                <TableHead>Enabled</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : configs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    No configurations found
                  </TableCell>
                </TableRow>
              ) : (
                configs.map((cfg) => {
                  const Icon = typeIcons[cfg.config_type] ?? Globe
                  return (
                    <TableRow key={cfg.config_id}>
                      <TableCell className="font-medium">{cfg.label}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="gap-1">
                          <Icon className="h-3 w-3" />
                          {typeLabels[cfg.config_type] ?? cfg.config_type}
                        </Badge>
                      </TableCell>
                      <TableCell className="max-w-[200px] truncate text-sm">
                        {cfg.url_or_path}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {cfg.run_schedule ?? '-'}
                      </TableCell>
                      <TableCell>
                        <button
                          className={`h-5 w-9 rounded-full transition-colors ${
                            cfg.enabled ? 'bg-green-500' : 'bg-gray-300'
                          } relative`}
                          onClick={() => toggleMutation.mutate(cfg.config_id)}
                        >
                          <span
                            className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform ${
                              cfg.enabled ? 'left-[18px]' : 'left-0.5'
                            }`}
                          />
                        </button>
                      </TableCell>
                      <TableCell>{cfg.priority_rank}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openEdit(cfg)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              if (confirm('Delete this configuration?')) {
                                deleteMutation.mutate(cfg.config_id)
                              }
                            }}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )
                })
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingId ? 'Edit Configuration' : 'New Configuration'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-2">
            {error && (
              <div className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-600">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label>Type</Label>
              <Select
                value={formData.config_type}
                onValueChange={(v) => setFormData({ ...formData, config_type: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CONFIG_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>
                      {typeLabels[t]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Label</Label>
              <Input
                value={formData.label}
                onChange={(e) => setFormData({ ...formData, label: e.target.value })}
                placeholder="e.g. Stockland Cloverton Scraper"
              />
            </div>

            <div className="space-y-2">
              <Label>URL / Path</Label>
              <Input
                value={formData.url_or_path}
                onChange={(e) => setFormData({ ...formData, url_or_path: e.target.value })}
                placeholder="https://example.com/lots or /data/pdfs/"
              />
            </div>

            <div className="space-y-2">
              <Label>Schedule (cron)</Label>
              <Input
                value={formData.run_schedule ?? ''}
                onChange={(e) =>
                  setFormData({ ...formData, run_schedule: e.target.value || undefined })
                }
                placeholder="e.g. 0 */6 * * *"
              />
            </div>

            <div className="space-y-2">
              <Label>Priority Rank</Label>
              <Input
                type="number"
                value={formData.priority_rank ?? 0}
                onChange={(e) =>
                  setFormData({ ...formData, priority_rank: parseInt(e.target.value) || 0 })
                }
              />
            </div>

            <div className="space-y-2">
              <Label>Notes</Label>
              <Textarea
                value={formData.notes ?? ''}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value || undefined })
                }
                rows={2}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>
              {editingId ? 'Save Changes' : 'Create'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
