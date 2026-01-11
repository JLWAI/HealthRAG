import { useState, useRef, useEffect } from 'react'
import { Search, Plus, Loader2 } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useFoodSearch, useLogFood, useToday } from '@/hooks/useApi'
import type { FoodItem } from '@/api/client'

type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack'

interface FoodSearchProps {
  mealType?: MealType
  onFoodLogged?: () => void
}

// Auto-detect meal type from time of day
function getDefaultMealType(): MealType {
  const hour = new Date().getHours()
  if (hour < 11) return 'breakfast'
  if (hour < 15) return 'lunch'
  if (hour < 20) return 'dinner'
  return 'snack'
}

export function FoodSearch({ mealType, onFoodLogged }: FoodSearchProps) {
  const [query, setQuery] = useState('')
  const [selectedFood, setSelectedFood] = useState<FoodItem | null>(null)
  const [servings, setServings] = useState('1')
  const [showResults, setShowResults] = useState(false)
  const [activeMealType, setActiveMealType] = useState<MealType>(mealType || getDefaultMealType())
  const inputRef = useRef<HTMLInputElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  const today = useToday()
  const { data: searchResults, isLoading: isSearching } = useFoodSearch(query)
  const logFood = useLogFood()

  // Close results when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        resultsRef.current &&
        !resultsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowResults(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelectFood = (food: FoodItem) => {
    setSelectedFood(food)
    setQuery(food.name)
    setShowResults(false)
    setServings('1')
  }

  const handleLogFood = () => {
    if (!selectedFood) return

    const servingsNum = parseFloat(servings) || 1

    logFood.mutate(
      {
        food_id: selectedFood.id,
        food_name: selectedFood.name,
        servings: servingsNum,
        meal_type: activeMealType,
        calories: Math.round(selectedFood.calories * servingsNum),
        protein: Math.round(selectedFood.protein * servingsNum),
        fat: Math.round(selectedFood.fat * servingsNum),
        carbs: Math.round(selectedFood.carbs * servingsNum),
      },
      {
        onSuccess: () => {
          setQuery('')
          setSelectedFood(null)
          setServings('1')
          onFoodLogged?.()
        },
      }
    )
  }

  const handleQuickAdd = (food: FoodItem) => {
    logFood.mutate(
      {
        food_id: food.id,
        food_name: food.name,
        servings: 1,
        meal_type: activeMealType,
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

  return (
    <div className="space-y-4">
      {/* Meal Type Selector */}
      <div className="flex gap-1">
        {(['breakfast', 'lunch', 'dinner', 'snack'] as const).map((type) => (
          <Button
            key={type}
            variant={activeMealType === type ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveMealType(type)}
            className="capitalize flex-1"
          >
            {type}
          </Button>
        ))}
      </div>

      {/* Search Input */}
      <div className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            ref={inputRef}
            type="text"
            placeholder="Search foods..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setSelectedFood(null)
              setShowResults(true)
            }}
            onFocus={() => setShowResults(true)}
            className="pl-10"
          />
          {isSearching && (
            <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
          )}
        </div>

        {/* Search Results Dropdown */}
        {showResults && searchResults && searchResults.length > 0 && !selectedFood && (
          <Card ref={resultsRef} className="absolute z-50 w-full mt-1 max-h-64 overflow-y-auto">
            <CardContent className="p-1">
              {searchResults.map((food) => (
                <div
                  key={food.id}
                  className="flex items-center justify-between p-2 hover:bg-muted rounded cursor-pointer"
                  onClick={() => handleSelectFood(food)}
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{food.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {food.serving_size} • {food.calories} cal • {food.protein}g protein
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 shrink-0"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleQuickAdd(food)
                    }}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {showResults && query.length >= 2 && searchResults?.length === 0 && !isSearching && (
          <Card ref={resultsRef} className="absolute z-50 w-full mt-1">
            <CardContent className="p-4 text-center text-muted-foreground">
              No foods found for "{query}"
            </CardContent>
          </Card>
        )}
      </div>

      {/* Selected Food Details */}
      {selectedFood && (
        <Card>
          <CardContent className="p-4 space-y-4">
            <div>
              <p className="font-medium">{selectedFood.name}</p>
              <p className="text-sm text-muted-foreground">{selectedFood.serving_size}</p>
            </div>

            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <label className="text-sm text-muted-foreground">Servings</label>
                <Input
                  type="number"
                  step="0.5"
                  min="0.25"
                  value={servings}
                  onChange={(e) => setServings(e.target.value)}
                  className="mt-1"
                />
              </div>
              <Button onClick={handleLogFood} disabled={logFood.isPending}>
                {logFood.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Plus className="h-4 w-4 mr-2" />
                )}
                Add to {activeMealType}
              </Button>
            </div>

            {/* Nutrition Preview */}
            <div className="grid grid-cols-4 gap-2 text-center text-sm border-t pt-3">
              <div>
                <p className="text-muted-foreground">Calories</p>
                <p className="font-medium">
                  {Math.round(selectedFood.calories * (parseFloat(servings) || 1))}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Protein</p>
                <p className="font-medium">
                  {Math.round(selectedFood.protein * (parseFloat(servings) || 1))}g
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Carbs</p>
                <p className="font-medium">
                  {Math.round(selectedFood.carbs * (parseFloat(servings) || 1))}g
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Fat</p>
                <p className="font-medium">
                  {Math.round(selectedFood.fat * (parseFloat(servings) || 1))}g
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {logFood.isSuccess && !selectedFood && (
        <p className="text-sm text-green-600">Food logged to {activeMealType}!</p>
      )}
    </div>
  )
}
