import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { createRegion, deleteRegion, listRegions, updateRegion } from '@/api/regions'
import type { RegionRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

export default function RegionsPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [editing, setEditing] = useState<RegionRead | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [name, setName] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<RegionRead | null>(null)

  const { data, isLoading } = useQuery({ queryKey: ['regions'], queryFn: listRegions })

  const save = useMutation({
    mutationFn: async () => {
      if (editing) return updateRegion(editing.region_id, { name })
      return createRegion({ name })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['regions'] })
      toast({ title: editing ? 'Region updated' : 'Region created', variant: 'success' })
      setFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const remove = useMutation({
    mutationFn: (id: number) => deleteRegion(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['regions'] })
      toast({ title: 'Region deleted', variant: 'success' })
      setDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const openNew = () => {
    setEditing(null)
    setName('')
    setFormOpen(true)
  }

  const openEdit = (region: RegionRead) => {
    setEditing(region)
    setName(region.name)
    setFormOpen(true)
  }

  return (
    <div>
      <PageHeader
        title="Regions"
        description="Region master data used to group estates."
        actions={
          <Button onClick={openNew}>
            <Plus className="h-4 w-4" /> New Region
          </Button>
        }
      />

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead className="w-32 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={2} className="text-center text-sm text-muted-foreground">
                  Loading...
                </TableCell>
              </TableRow>
            ) : data?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={2} className="text-center text-sm text-muted-foreground">
                  No regions yet.
                </TableCell>
              </TableRow>
            ) : (
              data?.map((r) => (
                <TableRow key={r.region_id}>
                  <TableCell className="font-medium">{r.name}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" onClick={() => openEdit(r)}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:text-destructive"
                      onClick={() => setDeleteTarget(r)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit region' : 'New region'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="region-name">Name</Label>
            <Input id="region-name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setFormOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => save.mutate()} disabled={!name.trim() || save.isPending}>
              {save.isPending ? 'Saving...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete region?"
        description={deleteTarget ? `"${deleteTarget.name}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={remove.isPending}
        onConfirm={() => deleteTarget && remove.mutate(deleteTarget.region_id)}
      />
    </div>
  )
}
