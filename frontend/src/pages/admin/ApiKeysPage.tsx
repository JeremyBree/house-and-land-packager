import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Copy, Plus, Pencil, ShieldOff, Trash2 } from 'lucide-react'
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
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'
import {
  listApiKeys,
  createApiKey,
  updateApiKey,
  deleteApiKey,
  revokeApiKey,
  type ApiKeyRead,
  type ApiKeyCreateInput,
  type ApiKeyCreateResponse,
} from '@/api/apiKeys'

const AGENT_TYPES = ['email', 'scraper', 'portal', 'pdf', 'other'] as const
const AVAILABLE_SCOPES = ['estates:write', 'lots:write', 'guidelines:write'] as const

export default function ApiKeysPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [createOpen, setCreateOpen] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [editingKey, setEditingKey] = useState<ApiKeyRead | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<ApiKeyRead | null>(null)
  const [createdKey, setCreatedKey] = useState<ApiKeyCreateResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Create form state
  const [agentName, setAgentName] = useState('')
  const [agentType, setAgentType] = useState<string>('scraper')
  const [selectedScopes, setSelectedScopes] = useState<string[]>(['estates:write', 'lots:write'])
  const [expiresAt, setExpiresAt] = useState('')
  const [notes, setNotes] = useState('')

  // Edit form state
  const [editName, setEditName] = useState('')
  const [editType, setEditType] = useState('')
  const [editScopes, setEditScopes] = useState<string[]>([])
  const [editNotes, setEditNotes] = useState('')

  const { data: keys = [], isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: listApiKeys,
  })

  const createMutation = useMutation({
    mutationFn: (data: ApiKeyCreateInput) => createApiKey(data),
    onSuccess: (resp) => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      setCreateOpen(false)
      setCreatedKey(resp)
      resetCreateForm()
    },
    onError: (err) => setError(extractErrorMessage(err)),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof updateApiKey>[1] }) =>
      updateApiKey(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      setEditOpen(false)
      setEditingKey(null)
      toast({ title: 'API key updated' })
    },
    onError: (err) => setError(extractErrorMessage(err)),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteApiKey(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      setDeleteTarget(null)
      toast({ title: 'API key deleted' })
    },
  })

  const revokeMutation = useMutation({
    mutationFn: (id: number) => revokeApiKey(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      toast({ title: 'API key revoked' })
    },
  })

  function resetCreateForm() {
    setAgentName('')
    setAgentType('scraper')
    setSelectedScopes(['estates:write', 'lots:write'])
    setExpiresAt('')
    setNotes('')
    setError(null)
  }

  function openCreate() {
    resetCreateForm()
    setCreateOpen(true)
  }

  function openEdit(key: ApiKeyRead) {
    setEditingKey(key)
    setEditName(key.agent_name)
    setEditType(key.agent_type)
    setEditScopes(key.scopes ? key.scopes.split(',').filter(Boolean) : [])
    setEditNotes(key.notes ?? '')
    setError(null)
    setEditOpen(true)
  }

  function handleCreate() {
    createMutation.mutate({
      agent_name: agentName,
      agent_type: agentType,
      scopes: selectedScopes.join(','),
      expires_at: expiresAt || undefined,
      notes: notes || undefined,
    })
  }

  function handleUpdate() {
    if (!editingKey) return
    updateMutation.mutate({
      id: editingKey.key_id,
      data: {
        agent_name: editName,
        agent_type: editType,
        scopes: editScopes.join(','),
        notes: editNotes || undefined,
      },
    })
  }

  function toggleScope(scope: string, current: string[], setter: (v: string[]) => void) {
    if (current.includes(scope)) {
      setter(current.filter((s) => s !== scope))
    } else {
      setter([...current, scope])
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text)
    toast({ title: 'Copied to clipboard' })
  }

  function formatDate(d: string | null) {
    if (!d) return '-'
    return new Date(d).toLocaleString()
  }

  return (
    <div>
      <PageHeader
        title="API Keys"
        description="Manage API keys for external ingestion agents"
        actions={
          <Button onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Create API Key
          </Button>
        }
      />

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Agent Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Key Prefix</TableHead>
                <TableHead>Scopes</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Used</TableHead>
                <TableHead>Expires</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : keys.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    No API keys found
                  </TableCell>
                </TableRow>
              ) : (
                keys.map((k) => (
                  <TableRow key={k.key_id} className={!k.is_active ? 'opacity-50' : ''}>
                    <TableCell className="font-medium">{k.agent_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{k.agent_type}</Badge>
                    </TableCell>
                    <TableCell>
                      <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
                        {k.key_prefix}...
                      </code>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {k.scopes
                          ? k.scopes.split(',').map((s) => (
                              <Badge key={s} variant="secondary" className="text-xs">
                                {s}
                              </Badge>
                            ))
                          : '-'}
                      </div>
                    </TableCell>
                    <TableCell>
                      {k.is_active ? (
                        <Badge className="bg-green-100 text-green-800">Active</Badge>
                      ) : (
                        <Badge variant="destructive">Revoked</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(k.last_used_at)}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(k.expires_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="sm" onClick={() => openEdit(k)}>
                          <Pencil className="h-4 w-4" />
                        </Button>
                        {k.is_active && (
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Revoke"
                            onClick={() => {
                              if (confirm(`Revoke API key "${k.agent_name}"?`)) {
                                revokeMutation.mutate(k.key_id)
                              }
                            }}
                          >
                            <ShieldOff className="h-4 w-4 text-orange-500" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeleteTarget(k)}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Create Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create API Key</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            {error && (
              <div className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-600">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <Label>Agent Name</Label>
              <Input
                value={agentName}
                onChange={(e) => setAgentName(e.target.value)}
                placeholder="e.g. Stockland Scraper Agent"
              />
            </div>
            <div className="space-y-2">
              <Label>Agent Type</Label>
              <Select value={agentType} onValueChange={setAgentType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {AGENT_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Scopes</Label>
              <div className="flex flex-wrap gap-2">
                {AVAILABLE_SCOPES.map((scope) => (
                  <label key={scope} className="flex items-center gap-1.5 text-sm">
                    <input
                      type="checkbox"
                      checked={selectedScopes.includes(scope)}
                      onChange={() => toggleScope(scope, selectedScopes, setSelectedScopes)}
                      className="rounded"
                    />
                    {scope}
                  </label>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <Label>Expires At (optional)</Label>
              <Input
                type="datetime-local"
                value={expiresAt}
                onChange={(e) => setExpiresAt(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Notes</Label>
              <Textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                placeholder="Optional notes about this key"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={!agentName || createMutation.isPending}>
              Create Key
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit API Key</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            {error && (
              <div className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-600">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <Label>Agent Name</Label>
              <Input value={editName} onChange={(e) => setEditName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Agent Type</Label>
              <Select value={editType} onValueChange={setEditType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {AGENT_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Scopes</Label>
              <div className="flex flex-wrap gap-2">
                {AVAILABLE_SCOPES.map((scope) => (
                  <label key={scope} className="flex items-center gap-1.5 text-sm">
                    <input
                      type="checkbox"
                      checked={editScopes.includes(scope)}
                      onChange={() => toggleScope(scope, editScopes, setEditScopes)}
                      className="rounded"
                    />
                    {scope}
                  </label>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <Label>Notes</Label>
              <Textarea
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={!editName || updateMutation.isPending}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Key Created Modal */}
      <Dialog open={!!createdKey} onOpenChange={() => setCreatedKey(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>API Key Created</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
              Copy this API key now. It will not be shown again.
            </div>
            <div className="space-y-1">
              <Label>Agent</Label>
              <p className="text-sm font-medium">{createdKey?.agent_name}</p>
            </div>
            <div className="space-y-1">
              <Label>API Key</Label>
              <div className="flex items-center gap-2">
                <code className="flex-1 rounded bg-muted p-2 text-xs break-all">
                  {createdKey?.raw_key}
                </code>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => createdKey && copyToClipboard(createdKey.raw_key)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button onClick={() => setCreatedKey(null)}>Done</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => { if (!open) setDeleteTarget(null) }}
        title="Delete API Key"
        description={`Permanently delete the API key "${deleteTarget?.agent_name}"? This cannot be undone.`}
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.key_id)}
      />
    </div>
  )
}
