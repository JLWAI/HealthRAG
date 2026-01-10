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
      const { data } = await api.getProfile()
      return data
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
      return data
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
      return data
    },
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  })
}

export function useLogFood() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: Omit<FoodEntry, 'id' | 'logged_at'>) => {
      const response = await api.logFood(data)
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
