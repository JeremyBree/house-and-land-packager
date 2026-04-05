import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { Copy, Edit, MoreHorizontal, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { DataTable } from '@/components/common/DataTable'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { ClashRuleFormDialog } from './ClashRuleFormDialog'
import { ClashRuleCopyDialog } from './ClashRuleCopyDialog'
import { listClashRulesByStage, deleteClashRule } from '@/api/clashRules'
import type { ClashRuleRead } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

interface ClashRuleEditorProps {
  estateId: number
  stageId: number
  isAdmin: boolean
}

export function ClashRuleEditor({ estateId, stageId, isAdmin }: ClashRuleEditorProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [showNew, setShowNew] = useState(false)
  const [editRule, setEditRule] = useState<ClashRuleRead | null>(null)
  const [deleteRule, setDeleteRule] = useState<ClashRuleRead | null>(null)
  const [showCopy, setShowCopy] = useState(false)

  const { data: rules, isLoading } = useQuery({
    queryKey: ['clash-rules', stageId],
    queryFn: () => listClashRulesByStage(stageId),
    enabled: Number.isFinite(stageId),
  })

  const deleteMutation = useMutation({
    mutationFn: (ruleId: number) => deleteClashRule(ruleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clash-rules', stageId] })
      toast({ title: 'Rule deleted', variant: 'success' })
      setDeleteRule(null)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const columns = useMemo<ColumnDef<ClashRuleRead>[]>(
    () => [
      {
        accessorKey: 'lot_number',
        header: 'Lot #',
        cell: ({ row }) => <span className="font-medium">{row.original.lot_number}</span>,
      },
      {
        accessorKey: 'cannot_match',
        header: 'Cannot Match',
        cell: ({ row }) => (
          <div className="flex flex-wrap gap-1">
            {row.original.cannot_match.map((lot) => (
              <span
                key={lot}
                className="inline-flex rounded-full bg-secondary px-2 py-0.5 text-xs font-medium"
              >
                {lot}
              </span>
            ))}
          </div>
        ),
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => {
          if (!isAdmin) return null
          const rule = row.original
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" onClick={(e) => e.stopPropagation()}>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setEditRule(rule)}>
                  <Edit className="h-4 w-4" /> Edit
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => setDeleteRule(rule)}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="h-4 w-4" /> Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )
        },
      },
    ],
    [isAdmin],
  )

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Clash Rules</CardTitle>
          {isAdmin && (
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => setShowCopy(true)}>
                <Copy className="h-4 w-4" /> Copy Rules
              </Button>
              <Button size="sm" onClick={() => setShowNew(true)}>
                <Plus className="h-4 w-4" /> Add Rule
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <DataTable
          data={rules ?? []}
          columns={columns}
          loading={isLoading}
          emptyTitle="No clash rules"
          emptyDescription={
            isAdmin
              ? 'Add clash rules to prevent design+facade duplication between lots.'
              : 'No clash rules have been defined for this stage.'
          }
        />
      </CardContent>

      <ClashRuleFormDialog
        open={showNew}
        onOpenChange={setShowNew}
        estateId={estateId}
        stageId={stageId}
      />
      <ClashRuleFormDialog
        open={!!editRule}
        onOpenChange={(open) => !open && setEditRule(null)}
        estateId={estateId}
        stageId={stageId}
        rule={editRule}
      />
      <ClashRuleCopyDialog
        open={showCopy}
        onOpenChange={setShowCopy}
        sourceStageId={stageId}
      />
      <ConfirmDialog
        open={!!deleteRule}
        onOpenChange={(open) => !open && setDeleteRule(null)}
        title="Delete clash rule?"
        description={
          deleteRule
            ? `The rule for lot ${deleteRule.lot_number} will be permanently removed.`
            : ''
        }
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={() => deleteRule && deleteMutation.mutate(deleteRule.rule_id)}
        loading={deleteMutation.isPending}
      />
    </Card>
  )
}
