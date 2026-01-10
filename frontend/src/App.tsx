import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import { Dashboard } from '@/components/Dashboard'
import './index.css'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

// App content component that uses auth
function AppContent() {
  const { isLoading, isAuthenticated, user } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="flex items-center gap-2 font-semibold">
            <span className="text-xl">💪</span>
            <span>HealthRAG</span>
          </div>
          <div className="flex-1" />
          <nav className="flex items-center gap-2">
            <a
              href="#"
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              Today
            </a>
            <a
              href="#"
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              Progress
            </a>
            <a
              href="#"
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              Settings
            </a>
            {isAuthenticated && user && (
              <span className="text-xs text-muted-foreground ml-2">
                {user.email}
              </span>
            )}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-6">
        <Dashboard />
      </main>

      {/* Bottom Navigation (Mobile) */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background md:hidden">
        <div className="grid grid-cols-4 h-16">
          <a
            href="#"
            className="flex flex-col items-center justify-center text-xs font-medium text-primary"
          >
            <span className="text-lg mb-1">📊</span>
            Today
          </a>
          <a
            href="#"
            className="flex flex-col items-center justify-center text-xs font-medium text-muted-foreground"
          >
            <span className="text-lg mb-1">🍽️</span>
            Food
          </a>
          <a
            href="#"
            className="flex flex-col items-center justify-center text-xs font-medium text-muted-foreground"
          >
            <span className="text-lg mb-1">🏋️</span>
            Workout
          </a>
          <a
            href="#"
            className="flex flex-col items-center justify-center text-xs font-medium text-muted-foreground"
          >
            <span className="text-lg mb-1">📈</span>
            Progress
          </a>
        </div>
      </nav>

      {/* Add padding for mobile nav */}
      <div className="h-16 md:hidden" />
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
      {/* React Query Devtools (only in development) */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

export default App
