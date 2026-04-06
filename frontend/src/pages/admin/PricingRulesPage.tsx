import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { Copy, MoreHorizontal, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
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
import { RuleFormDialog } from '@/components/pricing/RuleFormDialog'
import { ConditionBadge } from '@/components/pricing/ConditionBadge'
import { CellReference } from '@/components/pricing/CellReference'
import {
  createGlobalRule,
  deleteGlobalRule,
  duplicateGlobalRule,
  listCategories,
  listGlobalRules,
  updateGlobalRule,
} from '@/api/pricingRules'
import type { GlobalPricingRuleRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const BRANDS = [
  { slug: 'hermitage', full: 'Hermitage Homes' },
  { slug: 'kingsbridge', full: 'Kingsbridge Homes' },
] as const

export default function PricingRulesPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [activeBrand, setActiveBrand] = useState<typeof BRANDS[number]>(BRANDS[0])
  const [showForm, setShowForm] = useState(false)
  const [editRule, setEditRule] = useState<GlobalPricingRuleRead | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<GlobalPricingRuleRead | null>(null)

  const { data: rules, isLoading } = useQuery({
    queryKey: ['global-rules', activeBrand.full],
    queryFn: () => listGlobalRules(activeBrand.full),
  })

  const { data: categories } = useQuery({
    queryKey: ['rule-categories', activeBrand.full],
    queryFn: () => listCategories(activeBrand.full),
  })

  const createMut = useMutation({
    mutationFn: createGlobalRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['global-rules'] })
      toast({ title: 'Rule created', variant: 'success' })
      setShowForm(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof updateGlobalRule>[1] }) =>
      updateGlobalRule(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['global-rules'] })
      toast({ title: 'Rule updated', variant: 'success' })
      setShowForm(false)
      setEditRule(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const deleteMut = useMutation({
    mutationFn: deleteGlobalRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['global-rules'] })
      toast({ title: 'Rule deleted', variant: 'success' })
      setDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const dupMut = useMutation({
    mutationFn: duplicateGlobalRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['global-rules'] })
      toast({ title: 'Rule duplicated', variant: 'success' })
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const columns = useMemo<ColumnDef<GlobalPricingRuleRead>[]>(
    () => [
      { accessorKey: 'item_name', header: 'Item Name' },
      {
        accessorKey: 'cost',
        header: 'Cost',
        cell: ({ row }) => `$${Number(row.original.cost).toLocaleString('en-AU', { minimumFractionDigits: 2 })}`,
      },
      {
        accessorKey: 'condition',
        header: 'Condition',
        cell: ({ row }) => (
          <ConditionBadge
            condition={row.original.condition}
            conditionValue={row.original.condition_value}
          />
        ),
      },
      {
        id: 'cell_ref',
        header: 'Cell',
        cell: ({ row }) => <CellReference row={row.original.cell_row} col={row.original.cell_col} />,
      },
      {
        id: 'cost_cell_ref',
        header: 'Cost Cell',
        cell: ({ row }) => <CellReference row={row.original.cost_cell_row} col={row.original.cost_cell_col} />,
      },
      {
        accessorKey: 'category_name',
        header: 'Category',
        cell: ({ row }) => row.original.category_name ?? <span className="text-muted-foreground">--</span>,
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
                  setEditRule(row.original)
                  setShowForm(true)
                }}
              >
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation()
                  dupMut.mutate(row.original.rule_id)
                }}
              >
                <Copy className="mr-2 h-3 w-3" />
                Duplicate
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
    [dupMut],
  )

  return (
    <div>
      <PageHeader
        title="Global Pricing Rules"
        description="Configure brand-wide pricing rules applied to all pricing requests."
        actions={
          <Button
            onClick={() => {
              setEditRule(null)
              setShowForm(true)
            }}
          >
            <Plus className="h-4 w-4" />
            Add Rule
          </Button>
        }
      />

      <div className="mb-4 flex gap-2">
        {BRANDS.map((b) => (
          <Button
            key={b.slug}
            variant={activeBrand.slug === b.slug ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveBrand(b)}
          >
            {b.full}
          </Button>
        ))}
      </div>

      {categories && categories.length > 0 && (
        <div className="mb-4 flex flex-wrap gap-1">
          <span className="mr-2 text-xs text-muted-foreground">Categories:</span>
          {categories.map((c) => (
            <Badge key={c.category_id} variant="secondary" className="text-xs">
              {c.name}
            </Badge>
          ))}
        </div>
      )}

      <DataTable
        data={rules ?? []}
        columns={columns}
        loading={isLoading}
        emptyTitle="No pricing rules"
      />

      <RuleFormDialog
        open={showForm}
        onOpenChange={(o) => {
          setShowForm(o)
          if (!o) setEditRule(null)
        }}
        rule={editRule}
        categories={categories ?? []}
        loading={createMut.isPending || updateMut.isPending}
        onSubmit={(values) => {
          if (editRule) {
            updateMut.mutate({ id: editRule.rule_id, data: values })
          } else {
            createMut.mutate({ ...values, brand: activeBrand.full })
          }
        }}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete rule?"
        description={deleteTarget ? `"${deleteTarget.item_name}" will be permanently deleted.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={deleteMut.isPending}
        onConfirm={() => deleteTarget && deleteMut.mutate(deleteTarget.rule_id)}
      />
    </div>
  )
}
