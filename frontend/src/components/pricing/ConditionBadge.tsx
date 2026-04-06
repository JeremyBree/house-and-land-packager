import { Badge } from '@/components/ui/badge'

const CONDITION_LABELS: Record<string, string> = {
  corner_block: 'Corner Block',
  building_crossover: 'Building Crossover',
  is_kdrb: 'KDRB',
  is_10_90_deal: '10/90 Deal',
  developer_land_referrals: 'Developer Land Referrals',
  custom_house_design: 'Custom House Design',
}

const CONDITION_COLORS: Record<string, string> = {
  corner_block: 'bg-amber-100 text-amber-800 border-amber-200',
  building_crossover: 'bg-blue-100 text-blue-800 border-blue-200',
  is_kdrb: 'bg-purple-100 text-purple-800 border-purple-200',
  is_10_90_deal: 'bg-orange-100 text-orange-800 border-orange-200',
  developer_land_referrals: 'bg-teal-100 text-teal-800 border-teal-200',
  custom_house_design: 'bg-pink-100 text-pink-800 border-pink-200',
}

interface ConditionBadgeProps {
  condition: string | null
  conditionValue?: string | null
}

export function ConditionBadge({ condition, conditionValue }: ConditionBadgeProps) {
  if (!condition) {
    return (
      <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-200">
        Always
      </Badge>
    )
  }

  // Keyed conditions (house_type:value, wholesale_group:value)
  if (condition.includes(':')) {
    const [key, value] = condition.split(':')
    const label = key === 'house_type' ? 'House Type' : key === 'wholesale_group' ? 'Wholesale Group' : key
    return (
      <Badge variant="secondary" className="bg-indigo-100 text-indigo-800 border-indigo-200">
        {label}: {value || conditionValue}
      </Badge>
    )
  }

  // Boolean conditions
  const label = CONDITION_LABELS[condition] ?? condition
  const colorClass = CONDITION_COLORS[condition] ?? 'bg-gray-100 text-gray-800 border-gray-200'

  return (
    <Badge variant="secondary" className={colorClass}>
      {label}
    </Badge>
  )
}
