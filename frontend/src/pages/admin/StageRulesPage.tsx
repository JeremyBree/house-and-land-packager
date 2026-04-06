import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { Copy, MoreHorizontal, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
import { listEstates } from '@/api/estates'
import { listStages } from '@/api/stages'
import { listCategories } from '@/api/pricingRules'
import {
  createStageRule,
  deleteStageRule,
  duplicateStageRule,
  listStageRules,
  updateStageRule,
} from '@/api/pricingRules'
import type { GlobalPricingRuleRead, StagePricingRuleRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

export default function StageRulesPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [selectedEstateId, setSelectedEstateId] = useState<number | null>(null)
  const [selectedStageId, setSelectedStageId] = useState<number | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [editRule, setEditRule] = useState<GlobalPricingRuleRead | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<StagePricingRuleRead | null>(null)

  const { data: estatesData } = useQuery({
    queryKey: ['estates-list'],
    queryFn: () => listEstates({ size: 200, active: true }),
  })

  const { data: stages } = useQuery({
    queryKey: ['stages', selectedEstateId],
    queryFn: () => listStages(selectedEstateId!),
    enabled: !!selectedEstateId,
  })

  const { data: rules, isLoading } = useQuery({
    queryKey: ['stage-rules', selectedEstateId, selectedStageId],
    queryFn: () => listStageRules(selectedEstateId!, selectedStageId!),
    enabled: !!selectedEstateId && !!selectedStageId,
  })

  const { data: categories } = useQuery({
    queryKey: ['rule-categories', 'all'],
    queryFn: () => listCategories('Hermitage Homes'),
  })

  const createMut = useMutation({
    mutationFn: createStageRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stage-rules'] })
      toast({ title: 'Stage rule created', variant: 'success' })
      setShowForm(false)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof updateStageRule>[1] }) =>
      updateStageRule(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stage-rules'] })
      toast({ title: 'Stage rule updated', variant: 'success' })
      setShowForm(false)
      setEditRule(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const deleteMut = useMutation({
    mutationFn: deleteStageRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stage-rules'] })
      toast({ title: 'Stage rule deleted', variant: 'success' })
      setDeleteTarget(null)
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const dupMut = useMutation({
    mutationFn: duplicateStageRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stage-rules'] })
      toast({ title: 'Stage rule duplicated', variant: 'success' })
    },
    onError: (err) => toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' }),
  })

  const columns = useMemo<ColumnDef<StagePricingRuleRead>[]>(
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

  const estates = estatesData?.items ?? []

  return (
    <div>
      <PageHeader
        title="Stage Pricing Rules"
        description="Configure pricing rules scoped to a specific estate and stage."
        actions={
          selectedEstateId && selectedStageId ? (
            <Button
              onClick={() => {
                setEditRule(null)
                setShowForm(true)
              }}
            >
              <Plus className="h-4 w-4" />
              Add Stage Rule
            </Button>
          ) : undefined
        }
      />

      <div className="mb-4 flex gap-4">
        <div className="w-64">
          <label className="mb-1 block text-xs text-muted-foreground">Estate</label>
          <Select
            value={selectedEstateId ? String(selectedEstateId) : ''}
            onValueChange={(v) => {
              setSelectedEstateId(Number(v))
              setSelectedStageId(null)
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select estate" />
            </SelectTrigger>
            <SelectContent>
              {estates.map((e) => (
                <SelectItem key={e.estate_id} value={String(e.estate_id)}>
                  {e.estate_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="w-64">
          <label className="mb-1 block text-xs text-muted-foreground">Stage</label>
          <Select
            value={selectedStageId ? String(selectedStageId) : ''}
            onValueChange={(v) => setSelectedStageId(Number(v))}
            disabled={!selectedEstateId}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select stage" />
            </SelectTrigger>
            <SelectContent>
              {(stages ?? []).map((s) => (
                <SelectItem key={s.stage_id} value={String(s.stage_id)}>
                  {s.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {selectedEstateId && selectedStageId ? (
        <DataTable
          data={rules ?? []}
          columns={columns}
          loading={isLoading}
          emptyTitle="No stage pricing rules"
        />
      ) : (
        <p className="text-muted-foreground">Select an estate and stage to view stage-specific pricing rules.</p>
      )}

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
            createMut.mutate({
              ...values,
              brand: 'Hermitage Homes',
              estate_id: selectedEstateId!,
              stage_id: selectedStageId!,
            })
          }
        }}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete stage rule?"
        description={deleteTarget ? `"${deleteTarget.item_name}" will be permanently deleted.` : undefined}
        confirmLabel="Delete"
        variant="destructive"
        loading={deleteMut.isPending}
        onConfirm={() => deleteTarget && deleteMut.mutate(deleteTarget.rule_id)}
      />
    </div>
  )
}
