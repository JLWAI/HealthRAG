import { Utensils } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FoodSearch } from '@/components/FoodSearch'
import { DailyFoodLog } from '@/components/DailyFoodLog'
import { useProfile, useDailyNutrition, useToday } from '@/hooks/useApi'

// Macro Progress Bar
function MacroProgress({
  label,
  current,
  target,
  color,
  unit = 'g',
}: {
  label: string
  current: number
  target: number
  color: string
  unit?: string
}) {
  const percentage = Math.min((current / target) * 100, 100)
  const isOver = current > target

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span>{label}</span>
        <span className={isOver ? 'text-red-500' : ''}>
          {current}{unit} / {target}{unit}
        </span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div
          className={`h-full rounded-full ${isOver ? 'bg-red-500' : color}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  )
}

export function NutritionPage() {
  const today = useToday()
  const { data: profile } = useProfile()
  const { data: nutrition, refetch: refetchNutrition } = useDailyNutrition(today)

  // Get targets from profile or use defaults
  const targets = {
    calories: profile?.target_calories || 2000,
    protein: profile?.target_protein || 150,
    carbs: profile?.target_carbs || 200,
    fat: profile?.target_fat || 70,
  }

  // Current values from daily nutrition
  const current = {
    calories: nutrition?.total_calories || 0,
    protein: nutrition?.total_protein || 0,
    carbs: nutrition?.total_carbs || 0,
    fat: nutrition?.total_fat || 0,
  }

  const handleFoodLogged = () => {
    refetchNutrition()
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Utensils className="h-6 w-6" />
          Nutrition
        </h1>
        <p className="text-muted-foreground">Track your daily meals and macros</p>
      </div>

      {/* Daily Progress */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Daily Progress</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <MacroProgress
            label="Calories"
            current={current.calories}
            target={targets.calories}
            color="bg-orange-500"
            unit=" cal"
          />
          <MacroProgress
            label="Protein"
            current={current.protein}
            target={targets.protein}
            color="bg-red-500"
          />
          <MacroProgress
            label="Carbs"
            current={current.carbs}
            target={targets.carbs}
            color="bg-yellow-500"
          />
          <MacroProgress
            label="Fat"
            current={current.fat}
            target={targets.fat}
            color="bg-blue-500"
          />
        </CardContent>
      </Card>

      {/* Food Search */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Log Food</CardTitle>
        </CardHeader>
        <CardContent>
          <FoodSearch onFoodLogged={handleFoodLogged} />
        </CardContent>
      </Card>

      {/* Today's Food Log */}
      <DailyFoodLog />
    </div>
  )
}
