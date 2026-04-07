import axios from 'axios'

// API base URL - uses proxy in development, direct URL in production
const API_BASE_URL = import.meta.env.VITE_API_URL || ''

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('healthrag_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('healthrag_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth Types
export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest extends LoginRequest {
  name: string
}

export interface Token {
  access_token: string
  token_type: string
  expires_in: number
}

export interface TokenData {
  user_id: string
  email: string
}

// API Types (matching FastAPI schemas)
export interface UserProfile {
  id: string
  name: string
  age: number
  sex: 'male' | 'female'
  height_inches: number
  weight_lbs: number
  activity_level: string
  goal: string
  phase: string
  target_calories: number
  target_protein: number
  target_fat: number
  target_carbs: number
}

export interface WeightEntry {
  id?: number
  date: string
  weight_lbs: number
  notes?: string
}

export interface WeightTrend {
  date: string
  weight_lbs: number
  trend_weight: number
  seven_day_avg?: number
}

export interface DailyNutrition {
  date: string
  total_calories: number
  total_protein: number
  total_fat: number
  total_carbs: number
  meal_count: number
}

export interface FoodItem {
  id: string
  name: string
  brand?: string
  serving_size: string
  calories: number
  protein: number
  fat: number
  carbs: number
  source: 'fdc' | 'off' | 'custom'
}

export interface FoodEntry {
  id?: number
  food_id: string
  food_name: string
  servings: number
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  calories: number
  protein: number
  fat: number
  carbs: number
  logged_at: string
}

export interface TemplateFoodItem {
  food_id: number
  food_name: string
  servings: number
  serving_size: string
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

export interface MealTemplate {
  template_id: number
  name: string
  description?: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  foods: TemplateFoodItem[]
  total_calories: number
  total_protein_g: number
  total_carbs_g: number
  total_fat_g: number
  created_at: string
  last_used?: string
  use_count: number
}

export interface MealTemplateCreate {
  name: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  description?: string
}

// API Functions
export const api = {
  // Health check
  health: () => apiClient.get('/health'),

  // Auth
  login: (data: LoginRequest) => apiClient.post<Token>('/api/auth/login', data),
  signup: (data: SignupRequest) => apiClient.post<Token>('/api/auth/signup', data),
  logout: () => apiClient.post('/api/auth/logout'),
  getMe: () => apiClient.get<TokenData>('/api/auth/me'),

  // Profile
  getProfile: () => apiClient.get<UserProfile>('/api/profile'),
  updateProfile: (data: Partial<UserProfile>) => apiClient.put('/api/profile', data),

  // Weight tracking
  getWeights: (days?: number) =>
    apiClient.get<WeightEntry[]>(`/api/weight/entries${days ? `?days=${days}` : ''}`),
  logWeight: (data: { weight_lbs: number; date?: string; notes?: string }) =>
    apiClient.post<WeightEntry>('/api/weight/entries', data),
  getWeightTrend: (days?: number) =>
    apiClient.get<WeightTrend[]>(`/api/weight/trend${days ? `?days=${days}` : ''}`),

  // Nutrition
  searchFood: (query: string) =>
    apiClient.get<FoodItem[]>(`/api/nutrition/search?q=${encodeURIComponent(query)}`),
  getRecentFoods: (days: number = 14, limit: number = 10) =>
    apiClient.get<FoodItem[]>(`/api/nutrition/recent?days=${days}&limit=${limit}`),
  logFood: (data: Omit<FoodEntry, 'id' | 'logged_at'>) =>
    apiClient.post<FoodEntry>('/api/nutrition/foods', data),
  deleteFood: (id: number) =>
    apiClient.delete(`/api/nutrition/foods/${id}`),
  getDailyNutrition: (date?: string) =>
    apiClient.get<DailyNutrition>(`/api/nutrition/daily-totals${date ? `?date=${date}` : ''}`),
  getFoodLog: (date?: string) =>
    apiClient.get<FoodEntry[]>(`/api/nutrition/foods${date ? `?date=${date}` : ''}`),

  // Meal Templates
  getTemplates: (mealType?: string, sortBy: string = 'recent') =>
    apiClient.get<MealTemplate[]>(`/api/templates?${mealType ? `meal_type=${mealType}&` : ''}sort_by=${sortBy}`),
  getTemplate: (id: number) =>
    apiClient.get<MealTemplate>(`/api/templates/${id}`),
  createTemplate: (data: MealTemplateCreate) =>
    apiClient.post<MealTemplate>('/api/templates', data),
  logTemplate: (id: number, multiplier: number = 1.0, date?: string) =>
    apiClient.post(`/api/templates/${id}/log?multiplier=${multiplier}${date ? `&date=${date}` : ''}`),
  deleteTemplate: (id: number) =>
    apiClient.delete(`/api/templates/${id}`),

  // Workouts (placeholder for Phase C)
  getWorkouts: () => apiClient.get('/api/workouts'),
  logWorkout: (data: unknown) => apiClient.post('/api/workouts', data),
}
