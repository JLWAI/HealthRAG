import { useState } from 'react'
import { Scale, Utensils, Dumbbell, TrendingUp, Plus } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { WeightChart } from '@/components/WeightChart'
import { useProfile, useDailyNutrition, useWeightTrend, useLogWeight, useToday } from '@/hooks/useApi'

// Metric Card Component
function MetricCard({
  title,
  value,
  subValue,
  icon: Icon,
  color = 'text-primary',
}: {
  title: string
  value: string | number
  subValue?: string
  icon: React.ElementType
  color?: string
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-4">
        <div className={`rounded-full bg-muted p-3 ${color}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
          {subValue && <p className="text-xs text-muted-foreground">{subValue}</p>}
        </div>
      </CardContent>
    </Card>
  )
}

// Quick Weight Entry Component
function QuickWeightEntry() {
  const [weight, setWeight] = useState('')
  const logWeight = useLogWeight()
  const today = useToday()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!weight) return

    logWeight.mutate(
      { weight_lbs: parseFloat(weight), date: today },
      {
        onSuccess: () => {
          setWeight('')
        },
      }
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Scale className="h-4 w-4" />
          Log Weight
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            type="number"
            step="0.1"
            placeholder="Weight (lbs)"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            className="flex-1"
          />
          <Button type="submit" size="icon" disabled={logWeight.isPending || !weight}>
            <Plus className="h-4 w-4" />
          </Button>
        </form>
        {logWeight.isSuccess && (
          <p className="text-sm text-green-600 mt-2">Weight logged!</p>
        )}
      </CardContent>
    </Card>
  )
}

// Macro Progress Bar
function MacroProgress({
  label,
  current,
  target,
  color,
}: {
  label: string
  current: number
  target: number
  color: string
}) {
  const percentage = Math.min((current / target) * 100, 100)

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span>{label}</span>
        <span>
          {current}g / {target}g
        </span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

// Main Dashboard Component
export function Dashboard() {
  const today = useToday()
  const { data: profile, isLoading: profileLoading } = useProfile()
  const { data: nutrition } = useDailyNutrition(today)
  const { data: weightTrend } = useWeightTrend(7)

  // Get latest weight from trend
  const latestWeight = weightTrend?.[weightTrend.length - 1]

  // Format today's date
  const formattedDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })

  if (profileLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">
          {profile?.name ? `Hi, ${profile.name}!` : 'HealthRAG'}
        </h1>
        <p className="text-muted-foreground">{formattedDate}</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          title="Weight"
          value={latestWeight?.weight_lbs?.toFixed(1) || '--'}
          subValue="lbs"
          icon={Scale}
          color="text-blue-500"
        />
        <MetricCard
          title="Calories"
          value={nutrition?.total_calories || 0}
          subValue={`/ ${profile?.target_calories || 2000} cal`}
          icon={Utensils}
          color="text-orange-500"
        />
        <MetricCard
          title="Protein"
          value={`${nutrition?.total_protein || 0}g`}
          subValue={`/ ${profile?.target_protein || 150}g`}
          icon={Dumbbell}
          color="text-red-500"
        />
        <MetricCard
          title="Trend"
          value={latestWeight?.trend_weight?.toFixed(1) || '--'}
          subValue="7-day avg"
          icon={TrendingUp}
          color="text-green-500"
        />
      </div>

      {/* Quick Actions Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <QuickWeightEntry />

        {/* Macro Progress */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Utensils className="h-4 w-4" />
              Today's Macros
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <MacroProgress
              label="Protein"
              current={nutrition?.total_protein || 0}
              target={profile?.target_protein || 150}
              color="bg-red-500"
            />
            <MacroProgress
              label="Carbs"
              current={nutrition?.total_carbs || 0}
              target={profile?.target_carbs || 200}
              color="bg-yellow-500"
            />
            <MacroProgress
              label="Fat"
              current={nutrition?.total_fat || 0}
              target={profile?.target_fat || 70}
              color="bg-blue-500"
            />
          </CardContent>
        </Card>
      </div>

      {/* Weight Trend Chart */}
      <WeightChart days={30} />

      {/* Quick Add Favorites (placeholder) */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Quick Add</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm">
              🍗 Chicken Breast
            </Button>
            <Button variant="outline" size="sm">
              🥚 Eggs
            </Button>
            <Button variant="outline" size="sm">
              🍚 White Rice
            </Button>
            <Button variant="outline" size="sm">
              🥛 Greek Yogurt
            </Button>
            <Button variant="secondary" size="sm">
              <Plus className="h-4 w-4 mr-1" />
              Search Food
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Today's Workout (placeholder) */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Dumbbell className="h-4 w-4" />
            Today's Workout
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm mb-4">
            No workout scheduled for today
          </p>
          <Button variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-1" />
            Start Workout
          </Button>
        </CardContent>
      </Card>

      {/* External Links */}
      <div className="flex gap-2 pt-4 border-t">
        <Button variant="ghost" size="sm" asChild>
          <a href="http://192.168.0.210:8501" target="_blank" rel="noopener noreferrer">
            🤖 AI Coach
          </a>
        </Button>
        <Button variant="ghost" size="sm" asChild>
          <a href="http://192.168.0.210:3001" target="_blank" rel="noopener noreferrer">
            💬 Open WebUI
          </a>
        </Button>
      </div>
    </div>
  )
}
