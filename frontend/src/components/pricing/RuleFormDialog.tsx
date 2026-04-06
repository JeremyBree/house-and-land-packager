import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { GlobalPricingRuleRead, PricingRuleCategoryRead } from '@/api/types'

const CONDITIONS = [
  { value: '', label: 'Always (no condition)' },
  { value: 'corner_block', label: 'Corner Block' },
  { value: 'building_crossover', label: 'Building Crossover' },
  { value: 'is_kdrb', label: 'KDRB' },
  { value: 'is_10_90_deal', label: '10/90 Deal' },
  { value: 'developer_land_referrals', label: 'Developer Land Referrals' },
  { value: 'custom_house_design', label: 'Custom House Design' },
  { value: 'house_type', label: 'House Type (keyed)' },
  { value: 'wholesale_group', label: 'Wholesale Group (keyed)' },
] as const

const ruleSchema = z.object({
  item_name: z.string().min(1, 'Item name is required').max(255),
  cost: z.string().min(1, 'Cost is required'),
  condition: z.string().optional(),
  condition_value: z.string().optional(),
  cell_row: z.coerce.number().int().min(1),
  cell_col: z.coerce.number().int().min(1),
  cost_cell_row: z.coerce.number().int().min(1),
  cost_cell_col: z.coerce.number().int().min(1),
  category_id: z.string().optional(),
  sort_order: z.coerce.number().int().min(0).default(0),
})

type RuleFormValues = z.infer<typeof ruleSchema>

interface RuleFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  rule?: GlobalPricingRuleRead | null
  categories: PricingRuleCategoryRead[]
  loading?: boolean
  onSubmit: (values: {
    item_name: string
    cost: string
    condition: string | null
    condition_value: string | null
    cell_row: number
    cell_col: number
    cost_cell_row: number
    cost_cell_col: number
    category_id: number | null
    sort_order: number
  }) => void
}

export function RuleFormDialog({
  open,
  onOpenChange,
  rule,
  categories,
  loading,
  onSubmit,
}: RuleFormDialogProps) {
  const isEdit = !!rule
  const form = useForm<RuleFormValues>({
    resolver: zodResolver(ruleSchema),
    defaultValues: {
      item_name: '',
      cost: '',
      condition: '',
      condition_value: '',
      cell_row: 1,
      cell_col: 1,
      cost_cell_row: 1,
      cost_cell_col: 1,
      category_id: '',
      sort_order: 0,
    },
  })

  const selectedCondition = form.watch('condition')
  const isKeyedCondition = selectedCondition === 'house_type' || selectedCondition === 'wholesale_group'

  useEffect(() => {
    if (open && rule) {
      let conditionBase = rule.condition ?? ''
      let conditionVal = rule.condition_value ?? ''
      if (conditionBase.includes(':')) {
        const [key, val] = conditionBase.split(':')
        conditionBase = key
        conditionVal = val || conditionVal
      }
      form.reset({
        item_name: rule.item_name,
        cost: String(rule.cost),
        condition: conditionBase,
        condition_value: conditionVal,
        cell_row: rule.cell_row,
        cell_col: rule.cell_col,
        cost_cell_row: rule.cost_cell_row,
        cost_cell_col: rule.cost_cell_col,
        category_id: rule.category_id ? String(rule.category_id) : '',
        sort_order: rule.sort_order,
      })
    } else if (open) {
      form.reset({
        item_name: '',
        cost: '',
        condition: '',
        condition_value: '',
        cell_row: 1,
        cell_col: 1,
        cost_cell_row: 1,
        cost_cell_col: 1,
        category_id: '',
        sort_order: 0,
      })
    }
  }, [open, rule, form])

  function handleSubmit(values: RuleFormValues) {
    let condition: string | null = values.condition || null
    const conditionValue = values.condition_value || null
    if (condition && isKeyedCondition && conditionValue) {
      condition = `${condition}:${conditionValue}`
    }
    onSubmit({
      item_name: values.item_name,
      cost: values.cost,
      condition,
      condition_value: isKeyedCondition ? conditionValue : null,
      cell_row: values.cell_row,
      cell_col: values.cell_col,
      cost_cell_row: values.cost_cell_row,
      cost_cell_col: values.cost_cell_col,
      category_id: values.category_id ? Number(values.category_id) : null,
      sort_order: values.sort_order,
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Edit Rule' : 'Add Rule'}</DialogTitle>
          <DialogDescription>
            {isEdit
              ? 'Update the pricing rule details below.'
              : 'Fill in the details to create a new pricing rule.'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="item_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Item Name</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="cost"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Cost</FormLabel>
                  <FormControl>
                    <Input {...field} type="number" step="0.01" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="condition"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Condition</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Always (no condition)" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {CONDITIONS.map((c) => (
                          <SelectItem key={c.value || '__none'} value={c.value || '__none'}>
                            {c.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {isKeyedCondition && (
                <FormField
                  control={form.control}
                  name="condition_value"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Condition Value</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="e.g. Access 18" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="cell_row"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cell Row</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" min={1} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="cell_col"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cell Col</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" min={1} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="cost_cell_row"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cost Cell Row</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" min={1} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="cost_cell_col"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cost Cell Col</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" min={1} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="category_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="No category" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="__none">No category</SelectItem>
                        {categories.map((cat) => (
                          <SelectItem key={cat.category_id} value={String(cat.category_id)}>
                            {cat.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="sort_order"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Sort Order</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" min={0} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {isEdit ? 'Save Changes' : 'Create Rule'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
