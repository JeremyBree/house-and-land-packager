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
import {
  listPostcodeCosts,
  createPostcodeCost,
  updatePostcodeCost,
  deletePostcodeCost,
} from '@/api/pricingReference'
import type { PostcodeSiteCostRead } from '@/api/pricingReference'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

export default function PostcodeCostsPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [editing, setEditing] = useState<PostcodeSiteCostRead | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [postcode, setPostcode] = useState('')
  const [cost, setCost] = useState(0)
  const [deleteTarget, setDeleteTarget] = useState<PostcodeSiteCostRead | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['postcode-costs'],
    queryFn: listPostcodeCosts,
  })

  const save = useMutation({
    mutationFn: async () => {
      if (editing) return updatePostcodeCost(editing.postcode, { rock_removal_cost: cost })
      return createPostcodeCost({ postcode, rock_removal_cost: cost })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['postcode-costs'] })
      toast({ title: editing ? 'Postcode cost updated' : 'Postcode cost created', variant: 'success' })
      setFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const remove = useMutation({
    mutationFn: (pc: string) => deletePostcodeCost(pc),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['postcode-costs'] })
      toast({ title: 'Postcode cost deleted', variant: 'success' })
      setDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const openNew = () => {
    setEditing(null)
    setPostcode('')
    setCost(0)
    setFormOpen(true)
  }

  const openEdit = (item: PostcodeSiteCostRead) => {
    setEditing(item)
    setPostcode(item.postcode)
    setCost(item.rock_removal_cost)
    setFormOpen(true)
  }

  return (
    <div>
      <PageHeader
        title="Postcode Site Costs"
        description="Rock removal costs by postcode."
        actions={
          <Button onClick={openNew}>
            <Plus className="h-4 w-4" /> New Postcode Cost
          </Button>
        }
      />

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Postcode</TableHead>
              <TableHead className="text-right">Rock Removal Cost ($)</TableHead>
              <TableHead className="w-32 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={3} className="text-center text-sm text-muted-foreground">
                  Loading...
                </TableCell>
              </TableRow>
            ) : data?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} className="text-center text-sm text-muted-foreground">
                  No postcode costs yet.
                </TableCell>
              </TableRow>
            ) : (
              data?.map((p) => (
                <TableRow key={p.postcode}>
                  <TableCell className="font-medium">{p.postcode}</TableCell>
                  <TableCell className="text-right">{p.rock_removal_cost.toFixed(2)}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" onClick={() => openEdit(p)}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:text-destructive"
                      onClick={() => setDeleteTarget(p)}
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
            <DialogTitle>{editing ? 'Edit postcode cost' : 'New postcode cost'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label htmlFor="postcode">Postcode</Label>
              <Input
                id="postcode"
                value={postcode}
                onChange={(e) => setPostcode(e.target.value)}
                disabled={!!editing}
              />
            </div>
            <div>
              <Label htmlFor="rock_cost">Rock removal cost ($)</Label>
              <Input
                id="rock_cost"
                type="number"
                step="0.01"
                value={cost}
                onChange={(e) => setCost(parseFloat(e.target.value) || 0)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setFormOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => save.mutate()} disabled={!postcode.trim() || save.isPending}>
              {save.isPending ? 'Saving...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete postcode cost?"
        description={deleteTarget ? `Postcode "${deleteTarget.postcode}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={remove.isPending}
        onConfirm={() => deleteTarget && remove.mutate(deleteTarget.postcode)}
      />
    </div>
  )
}
