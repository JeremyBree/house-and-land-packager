import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, Plus, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable } from '@/components/common/DataTable'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { UserFormDialog } from './UserFormDialog'
import { deleteUser, listUsers } from '@/api/users'
import type { UserRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const PAGE_SIZE = 20

export default function UsersPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [editUser, setEditUser] = useState<UserRead | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<UserRead | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['users', { search, page }],
    queryFn: () => listUsers({ page, size: PAGE_SIZE, search: search || undefined }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast({ title: 'User deleted', variant: 'success' })
      setDeleteTarget(null)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const columns = useMemo<ColumnDef<UserRead>[]>(
    () => [
      {
        accessorKey: 'last_name',
        header: 'Name',
        cell: ({ row }) => (
          <span className="font-medium">
            {row.original.first_name} {row.original.last_name}
          </span>
        ),
      },
      { accessorKey: 'email', header: 'Email' },
      { accessorKey: 'job_title', header: 'Title', cell: ({ row }) => row.original.job_title ?? '—' },
      {
        accessorKey: 'roles',
        header: 'Roles',
        cell: ({ row }) => (
          <div className="flex flex-wrap gap-1">
            {row.original.roles.map((r) => (
              <Badge key={r} variant="secondary">
                {r}
              </Badge>
            ))}
          </div>
        ),
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" onClick={(e) => e.stopPropagation()}>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation()
                  setEditUser(row.original)
                  setShowForm(true)
                }}
              >
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-destructive focus:text-destructive"
                onClick={(e) => {
                  e.stopPropagation()
                  setDeleteTarget(row.original)
                }}
              >
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    [],
  )

  return (
    <div>
      <PageHeader
        title="Users"
        description="Manage user accounts and role assignments."
        actions={
          <Button
            onClick={() => {
              setEditUser(null)
              setShowForm(true)
            }}
          >
            <Plus className="h-4 w-4" />
            New User
          </Button>
        }
      />

      <div className="mb-4 flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search users..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            className="pl-9"
          />
        </div>
      </div>

      <DataTable
        data={data?.items ?? []}
        columns={columns}
        loading={isLoading}
        emptyTitle="No users found"
        pagination={{
          page: data?.page ?? 1,
          size: data?.size ?? PAGE_SIZE,
          total: data?.total ?? 0,
          pages: data?.pages ?? 1,
          onPageChange: setPage,
        }}
      />

      <UserFormDialog open={showForm} onOpenChange={setShowForm} user={editUser} />
      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete user?"
        description={
          deleteTarget
            ? `${deleteTarget.first_name} ${deleteTarget.last_name} (${deleteTarget.email}) will be removed.`
            : undefined
        }
        confirmLabel="Delete"
        variant="destructive"
        loading={deleteMutation.isPending}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.profile_id)}
      />
    </div>
  )
}
