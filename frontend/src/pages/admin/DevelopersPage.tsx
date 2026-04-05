import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { MoreHorizontal, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { PageHeader } from '@/components/common/PageHeader'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { createDeveloper, deleteDeveloper, listDevelopers, updateDeveloper } from '@/api/developers'
import type { DeveloperRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const schema = z.object({
  developer_name: z.string().min(1).max(255),
  developer_website: z.string().max(500).optional().or(z.literal('')),
  contact_email: z.string().email().optional().or(z.literal('')),
  notes: z.string().optional().or(z.literal('')),
})
type Values = z.infer<typeof schema>

export default function DevelopersPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<DeveloperRead | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeveloperRead | null>(null)

  const { data, isLoading } = useQuery({ queryKey: ['developers'], queryFn: listDevelopers })

  const form = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: { developer_name: '', developer_website: '', contact_email: '', notes: '' },
  })

  useEffect(() => {
    if (formOpen) {
      form.reset({
        developer_name: editing?.developer_name ?? '',
        developer_website: editing?.developer_website ?? '',
        contact_email: editing?.contact_email ?? '',
        notes: editing?.notes ?? '',
      })
    }
  }, [formOpen, editing, form])

  const save = useMutation({
    mutationFn: async (values: Values) => {
      const payload = {
        developer_name: values.developer_name,
        developer_website: values.developer_website || null,
        contact_email: values.contact_email || null,
        notes: values.notes || null,
      }
      if (editing) return updateDeveloper(editing.developer_id, payload)
      return createDeveloper(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['developers'] })
      toast({ title: editing ? 'Developer updated' : 'Developer created', variant: 'success' })
      setFormOpen(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const remove = useMutation({
    mutationFn: (id: number) => deleteDeveloper(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['developers'] })
      toast({ title: 'Developer deleted', variant: 'success' })
      setDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const openNew = () => {
    setEditing(null)
    setFormOpen(true)
  }
  const openEdit = (dev: DeveloperRead) => {
    setEditing(dev)
    setFormOpen(true)
  }

  return (
    <div>
      <PageHeader
        title="Developers"
        description="Developer master data."
        actions={
          <Button onClick={openNew}>
            <Plus className="h-4 w-4" /> New Developer
          </Button>
        }
      />

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Website</TableHead>
              <TableHead>Contact</TableHead>
              <TableHead className="w-16"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">
                  Loading...
                </TableCell>
              </TableRow>
            ) : data?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">
                  No developers yet.
                </TableCell>
              </TableRow>
            ) : (
              data?.map((d) => (
                <TableRow key={d.developer_id}>
                  <TableCell className="font-medium">{d.developer_name}</TableCell>
                  <TableCell>{d.developer_website ?? '—'}</TableCell>
                  <TableCell>{d.contact_email ?? '—'}</TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => openEdit(d)}>Edit</DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={() => setDeleteTarget(d)}
                        >
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit developer' : 'New developer'}</DialogTitle>
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit((v) => save.mutate(v))} className="space-y-4">
              <FormField
                control={form.control}
                name="developer_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name *</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="developer_website"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Website</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="contact_email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Contact email</FormLabel>
                    <FormControl>
                      <Input type="email" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Notes</FormLabel>
                    <FormControl>
                      <Textarea {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setFormOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={save.isPending}>
                  {save.isPending ? 'Saving...' : 'Save'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete developer?"
        description={deleteTarget ? `"${deleteTarget.developer_name}" will be permanently removed.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={remove.isPending}
        onConfirm={() => deleteTarget && remove.mutate(deleteTarget.developer_id)}
      />
    </div>
  )
}
