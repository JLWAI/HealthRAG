import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useWeightTrend, useProfile } from '@/hooks/useApi'
import { TrendingDown, TrendingUp, Minus } from 'lucide-react'

interface WeightChartProps {
  days?: number
}

export function WeightChart({ days = 30 }: WeightChartProps) {
  const { data: weightData, isLoading } = useWeightTrend(days)
  const { data: profile } = useProfile()

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Weight Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] flex items-center justify-center">
            <div className="animate-pulse text-muted-foreground">Loading...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!weightData || weightData.length === 0) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Weight Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            No weight data yet. Log your first weight to see trends!
          </div>
        </CardContent>
      </Card>
    )
  }

  // Format data for chart
  const chartData = weightData.map((entry) => ({
    date: new Date(entry.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
    actual: entry.weight_lbs,
    trend: entry.trend_weight,
    sevenDayAvg: entry.seven_day_avg,
  }))

  // Calculate weight change
  const firstWeight = weightData[0]?.weight_lbs
  const lastWeight = weightData[weightData.length - 1]?.weight_lbs
  const weightChange = lastWeight && firstWeight ? lastWeight - firstWeight : 0
  const percentChange = firstWeight ? ((weightChange / firstWeight) * 100).toFixed(1) : '0.0'

  // Determine trend icon
  const TrendIcon = weightChange > 0.5 ? TrendingUp : weightChange < -0.5 ? TrendingDown : Minus
  const trendColor = weightChange > 0.5 ? 'text-red-500' : weightChange < -0.5 ? 'text-green-500' : 'text-muted-foreground'

  // Calculate Y-axis domain with padding
  const allWeights = weightData.flatMap((d) => [d.weight_lbs, d.trend_weight, d.seven_day_avg].filter((v): v is number => typeof v === 'number'))
  const minWeight = allWeights.length > 0 ? Math.floor(Math.min(...allWeights) - 2) : 100
  const maxWeight = allWeights.length > 0 ? Math.ceil(Math.max(...allWeights) + 2) : 300

  // Goal weight from profile (if set)
  const goalWeight = profile?.weight_lbs // This should be target weight, using current as placeholder

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Weight Trend</CardTitle>
          <div className={`flex items-center gap-1 text-sm ${trendColor}`}>
            <TrendIcon className="h-4 w-4" />
            <span>
              {weightChange > 0 ? '+' : ''}
              {weightChange.toFixed(1)} lbs ({percentChange}%)
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10 }}
                className="text-muted-foreground"
              />
              <YAxis
                domain={[minWeight, maxWeight]}
                tick={{ fontSize: 10 }}
                className="text-muted-foreground"
                tickFormatter={(value) => `${value}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--popover))',
                  borderColor: 'hsl(var(--border))',
                  borderRadius: '6px',
                }}
                labelStyle={{ color: 'hsl(var(--popover-foreground))' }}
              />
              <Legend />

              {/* Goal weight reference line */}
              {goalWeight && (
                <ReferenceLine
                  y={goalWeight}
                  stroke="hsl(var(--primary))"
                  strokeDasharray="5 5"
                  label={{
                    value: 'Goal',
                    position: 'right',
                    fontSize: 10,
                    fill: 'hsl(var(--muted-foreground))',
                  }}
                />
              )}

              {/* Daily weight points */}
              <Line
                type="monotone"
                dataKey="actual"
                name="Daily"
                stroke="hsl(210 100% 60%)"
                strokeWidth={1}
                dot={{ r: 2 }}
                activeDot={{ r: 4 }}
              />

              {/* EWMA trend line */}
              <Line
                type="monotone"
                dataKey="trend"
                name="Trend"
                stroke="hsl(142 76% 36%)"
                strokeWidth={2}
                dot={false}
              />

              {/* 7-day moving average */}
              <Line
                type="monotone"
                dataKey="sevenDayAvg"
                name="7-Day Avg"
                stroke="hsl(47 95% 53%)"
                strokeWidth={1}
                strokeDasharray="3 3"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Stats summary */}
        <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
          <div className="text-center">
            <p className="text-xs text-muted-foreground">Start</p>
            <p className="text-sm font-medium">{firstWeight?.toFixed(1)} lbs</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground">Current</p>
            <p className="text-sm font-medium">{lastWeight?.toFixed(1)} lbs</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground">Change</p>
            <p className={`text-sm font-medium ${trendColor}`}>
              {weightChange > 0 ? '+' : ''}
              {weightChange.toFixed(1)} lbs
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
