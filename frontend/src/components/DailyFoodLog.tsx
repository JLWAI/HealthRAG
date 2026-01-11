import { Utensils, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useFoodLog, useDailyNutrition, useToday } from '@/hooks/useApi'
import type { FoodEntry } from '@/api/client'

interface MealSectionProps {
  title: string
  entries: FoodEntry[]
  onDelete?: (id: number) => void
}

function MealSection({ title, entries, onDelete }: MealSectionProps) {
  if (entries.length === 0) return null

  const totalCalories = entries.reduce((sum, e) => sum + e.calories, 0)

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <h4 className="font-medium capitalize">{title}</h4>
        <span className="text-sm text-muted-foreground">{totalCalories} cal</span>
      </div>
      <div className="space-y-1">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="flex items-center justify-between py-2 px-3 bg-muted/50 rounded text-sm"
          >
            <div className="flex-1 min-w-0">
              <span className="truncate">{entry.food_name}</span>
              {entry.servings !== 1 && (
                <span className="text-muted-foreground ml-1">x{entry.servings}</span>
              )}
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <span className="text-muted-foreground">{entry.calories} cal</span>
              <span className="text-muted-foreground text-xs">{entry.protein}g P</span>
              {onDelete && entry.id && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 text-muted-foreground hover:text-destructive"
                  onClick={() => onDelete(entry.id!)}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function DailyFoodLog() {
  const today = useToday()
  const { data: foodLog, isLoading } = useFoodLog(today)
  const { data: nutrition } = useDailyNutrition(today)

  // Group entries by meal type
  const mealGroups = {
    breakfast: foodLog?.filter((e) => e.meal_type === 'breakfast') || [],
    lunch: foodLog?.filter((e) => e.meal_type === 'lunch') || [],
    dinner: foodLog?.filter((e) => e.meal_type === 'dinner') || [],
    snack: foodLog?.filter((e) => e.meal_type === 'snack') || [],
  }

  const handleDelete = (id: number) => {
    // TODO: Implement delete mutation
    console.log('Delete food entry:', id)
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Utensils className="h-4 w-4" />
            Today's Food
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse text-muted-foreground">Loading...</div>
        </CardContent>
      </Card>
    )
  }

  const hasFood = foodLog && foodLog.length > 0

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Utensils className="h-4 w-4" />
            Today's Food
          </CardTitle>
          {nutrition && (
            <div className="text-sm text-muted-foreground">
              {nutrition.total_calories} cal total
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {!hasFood ? (
          <p className="text-muted-foreground text-sm">
            No food logged today. Use the search above to add your meals.
          </p>
        ) : (
          <>
            <MealSection title="Breakfast" entries={mealGroups.breakfast} onDelete={handleDelete} />
            <MealSection title="Lunch" entries={mealGroups.lunch} onDelete={handleDelete} />
            <MealSection title="Dinner" entries={mealGroups.dinner} onDelete={handleDelete} />
            <MealSection title="Snacks" entries={mealGroups.snack} onDelete={handleDelete} />
          </>
        )}

        {/* Daily Totals */}
        {hasFood && nutrition && (
          <div className="border-t pt-3">
            <div className="grid grid-cols-4 gap-2 text-center text-sm">
              <div>
                <p className="text-muted-foreground">Calories</p>
                <p className="font-medium">{nutrition.total_calories}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Protein</p>
                <p className="font-medium">{nutrition.total_protein}g</p>
              </div>
              <div>
                <p className="text-muted-foreground">Carbs</p>
                <p className="font-medium">{nutrition.total_carbs}g</p>
              </div>
              <div>
                <p className="text-muted-foreground">Fat</p>
                <p className="font-medium">{nutrition.total_fat}g</p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
