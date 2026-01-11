import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import { api } from '@/api/client'
import type { TokenData, LoginRequest, SignupRequest } from '@/api/client'

interface AuthContextType {
  user: TokenData | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (data: LoginRequest) => Promise<void>
  signup: (data: SignupRequest) => Promise<void>
  logout: () => Promise<void>
  error: string | null
}

const AuthContext = createContext<AuthContextType | null>(null)

const TOKEN_KEY = 'healthrag_token'

// Dev mode token for local testing (backend returns dev user when Supabase not configured)
const DEV_TOKEN = 'dev-mode-token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<TokenData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Check for existing token and validate on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem(TOKEN_KEY)

      if (token) {
        try {
          // Validate token by fetching user info
          const { data } = await api.getMe()
          setUser(data)
        } catch {
          // Token invalid, clear it
          localStorage.removeItem(TOKEN_KEY)
        }
      } else {
        // In dev mode, auto-authenticate with dev token
        // The backend will return a dev user when Supabase isn't configured
        try {
          localStorage.setItem(TOKEN_KEY, DEV_TOKEN)
          const { data } = await api.getMe()
          setUser(data)
        } catch {
          // Backend might require real auth, clear dev token
          localStorage.removeItem(TOKEN_KEY)
        }
      }

      setIsLoading(false)
    }

    initAuth()
  }, [])

  const login = useCallback(async (data: LoginRequest) => {
    setError(null)
    try {
      const { data: tokenResponse } = await api.login(data)
      localStorage.setItem(TOKEN_KEY, tokenResponse.access_token)

      // Fetch user info
      const { data: userData } = await api.getMe()
      setUser(userData)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed'
      setError(message)
      throw err
    }
  }, [])

  const signup = useCallback(async (data: SignupRequest) => {
    setError(null)
    try {
      const { data: tokenResponse } = await api.signup(data)
      localStorage.setItem(TOKEN_KEY, tokenResponse.access_token)

      // Fetch user info
      const { data: userData } = await api.getMe()
      setUser(userData)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Signup failed'
      setError(message)
      throw err
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await api.logout()
    } catch {
      // Ignore logout errors (token might already be invalid)
    } finally {
      localStorage.removeItem(TOKEN_KEY)
      setUser(null)
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
        error,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
