import { Plus, History } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useRecentFoods, useLogFood } from '@/hooks/useApi'
import type { FoodItem } from '@/api/client'

// Auto-detect meal type from time of day
function getMealType(): 'breakfast' | 'lunch' | 'dinner' | 'snack' {
  const hour = new Date().getHours()
  if (hour < 11) return 'breakfast'
  if (hour < 15) return 'lunch'
  if (hour < 20) return 'dinner'
  return 'snack'
}

interface RecentFoodsProps {
  onFoodLogged?: () => void
}

export function RecentFoods({ onFoodLogged }: RecentFoodsProps) {
  const { data: recentFoods, isLoading } = useRecentFoods(14, 10)
  const logFood = useLogFood()

  const handleQuickAdd = (food: FoodItem) => {
    logFood.mutate(
      {
        food_id: food.id,
        food_name: food.name,
        servings: 1,
        meal_type: getMealType(),
        calories: food.calories,
        protein: food.protein,
        fat: food.fat,
        carbs: food.carbs,
      },
      {
        onSuccess: () => {
          onFoodLogged?.()
        },
      }
    )
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <History className="h-4 w-4" />
            Recent Foods
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse text-muted-foreground text-sm">Loading...</div>
        </CardContent>
      </Card>
    )
  }

  if (!recentFoods || recentFoods.length === 0) {
    return null // Don't show if no recent foods
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <History className="h-4 w-4" />
          Recent Foods
        </CardTitle>
        <p className="text-xs text-muted-foreground">
          Most frequently logged in past 2 weeks
        </p>
      </CardHeader>
      <CardContent>
        {/* Horizontal scrollable carousel */}
        <div className="flex gap-2 overflow-x-auto pb-2 -mx-6 px-6">
          {recentFoods.map((food) => (
            <div
              key={food.id}
              className="flex-shrink-0 w-36 bg-muted/50 rounded-lg p-3 space-y-2"
            >
              <div className="flex items-start justify-between gap-1">
                <p className="text-sm font-medium line-clamp-2 flex-1">{food.name}</p>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 shrink-0"
                  onClick={() => handleQuickAdd(food)}
                  disabled={logFood.isPending}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="text-xs text-muted-foreground space-y-0.5">
                <div>{food.calories} cal</div>
                <div>{food.protein}g protein</div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
