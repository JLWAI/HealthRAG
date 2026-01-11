import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { FoodEntry } from '@/api/client'

// Query keys for cache management
export const queryKeys = {
  profile: ['profile'] as const,
  weights: (days?: number) => ['weights', days] as const,
  weightTrend: (days?: number) => ['weightTrend', days] as const,
  dailyNutrition: (date?: string) => ['dailyNutrition', date] as const,
  foodLog: (date?: string) => ['foodLog', date] as const,
  foodSearch: (query: string) => ['foodSearch', query] as const,
  workouts: ['workouts'] as const,
}

// Profile hooks
export function useProfile() {
  return useQuery({
    queryKey: queryKeys.profile,
    queryFn: async () => {
      try {
        const { data } = await api.getProfile()
        return data
      } catch (error) {
        // Return null for 404 (profile not found) - not an error state
        if ((error as { response?: { status?: number } })?.response?.status === 404) {
          return null
        }
        throw error
      }
    },
  })
}

// Weight tracking hooks
export function useWeights(days?: number) {
  return useQuery({
    queryKey: queryKeys.weights(days),
    queryFn: async () => {
      const { data } = await api.getWeights(days)
      return data
    },
  })
}

export function useWeightTrend(days?: number) {
  return useQuery({
    queryKey: queryKeys.weightTrend(days),
    queryFn: async () => {
      const { data } = await api.getWeightTrend(days)
      // API returns { entries: [...], ewma_alpha, latest_trend, ... }
      // Transform to array format expected by frontend
      const entries = (data as { entries?: Array<{ date: string; weight_lbs: number; trend_weight_lbs: number }> })?.entries || []
      return entries.map(entry => ({
        date: entry.date,
        weight_lbs: entry.weight_lbs,
        trend_weight: entry.trend_weight_lbs,
      }))
    },
  })
}

export function useLogWeight() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: { weight_lbs: number; date?: string; notes?: string }) => {
      const response = await api.logWeight(data)
      return response.data
    },
    onSuccess: () => {
      // Invalidate weight queries to refetch
      queryClient.invalidateQueries({ queryKey: ['weights'] })
      queryClient.invalidateQueries({ queryKey: ['weightTrend'] })
    },
  })
}

// Nutrition hooks
export function useDailyNutrition(date?: string) {
  return useQuery({
    queryKey: queryKeys.dailyNutrition(date),
    queryFn: async () => {
      const { data } = await api.getDailyNutrition(date)
      return data
    },
  })
}

export function useFoodLog(date?: string) {
  return useQuery({
    queryKey: queryKeys.foodLog(date),
    queryFn: async () => {
      const { data } = await api.getFoodLog(date)
      return data
    },
  })
}

export function useFoodSearch(query: string) {
  return useQuery({
    queryKey: queryKeys.foodSearch(query),
    queryFn: async () => {
      if (!query || query.length < 2) return []
      const { data } = await api.searchFood(query)
      // Transform API response to frontend format
      return (data as Array<{
        food_name: string
        serving_size: string
        calories: number
        protein_g: number
        carbs_g: number
        fat_g: number
        source: string
        external_id: string
      }>).map(item => ({
        id: item.external_id || item.food_name,
        name: item.food_name,
        serving_size: item.serving_size,
        calories: item.calories,
        protein: item.protein_g,
        carbs: item.carbs_g,
        fat: item.fat_g,
        source: item.source as 'fdc' | 'off' | 'custom',
      }))
    },
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  })
}

export function useLogFood() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: Omit<FoodEntry, 'id' | 'logged_at'>) => {
      // Transform frontend format to backend format
      const backendData = {
        date: new Date().toISOString().split('T')[0],
        meal_type: data.meal_type,
        food_name: data.food_name,
        serving_size: '1 serving',
        serving_quantity: data.servings,
        calories: data.calories,
        protein_g: data.protein,
        carbs_g: data.carbs,
        fat_g: data.fat,
      }
      const response = await api.logFood(backendData as unknown as Omit<FoodEntry, 'id' | 'logged_at'>)
      return response.data
    },
    onSuccess: () => {
      // Invalidate nutrition queries to refetch
      queryClient.invalidateQueries({ queryKey: ['dailyNutrition'] })
      queryClient.invalidateQueries({ queryKey: ['foodLog'] })
    },
  })
}

// Utility hook for today's date
export function useToday() {
  return new Date().toISOString().split('T')[0]
}
