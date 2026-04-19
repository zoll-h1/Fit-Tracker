import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AppLayout from '@/components/layout/AppLayout'
import PrivateRoute from '@/components/layout/PrivateRoute'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import LandingPage from '@/pages/LandingPage'
import DashboardPage from '@/pages/dashboard/DashboardPage'
import WorkoutsPage from '@/pages/workouts/WorkoutsPage'
import ActiveWorkoutPage from '@/pages/workouts/ActiveWorkoutPage'
import WorkoutDetailPage from '@/pages/workouts/WorkoutDetailPage'
import ExerciseLibraryPage from '@/pages/exercises/ExerciseLibraryPage'
import BodyMetricsPage from '@/pages/body/BodyMetricsPage'
import NutritionPage from '@/pages/nutrition/NutritionPage'
import AnalyticsPage from '@/pages/analytics/AnalyticsPage'
import AchievementsPage from '@/pages/achievements/AchievementsPage'
import TemplatesPage from '@/pages/templates/TemplatesPage'
import SocialFeedPage from '@/pages/social/SocialFeedPage'
import PublicProfilePage from '@/pages/social/PublicProfilePage'
import ChallengesPage from '@/pages/challenges/ChallengesPage'
import ChallengeDetailPage from '@/pages/challenges/ChallengeDetailPage'
import NotificationsPage from '@/pages/notifications/NotificationsPage'
import SettingsPage from '@/pages/settings/SettingsPage'
import TrainerPage from '@/pages/trainer/TrainerPage'
import ProgramDetailPage from '@/pages/trainer/ProgramDetailPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60 * 5,
    },
  },
})

const ComingSoon = ({ name }: { name: string }) => (
  <div className="flex items-center justify-center h-64">
    <div className="text-center">
      <div className="text-4xl mb-4">🚧</div>
      <h2 className="text-xl font-semibold text-white mb-2">{name}</h2>
      <p className="text-slate-400">Coming soon in the next sprint</p>
    </div>
  </div>
)

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/landing" element={<LandingPage />} />
          <Route path="/forgot-password" element={<ComingSoon name="Forgot Password" />} />

          <Route element={<PrivateRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/workouts" element={<WorkoutsPage />} />
              <Route path="/workouts/active" element={<ActiveWorkoutPage />} />
              <Route path="/workouts/:id" element={<WorkoutDetailPage />} />
              <Route path="/exercises" element={<ExerciseLibraryPage />} />
              <Route path="/body-metrics" element={<BodyMetricsPage />} />
              <Route path="/nutrition" element={<NutritionPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/social" element={<SocialFeedPage />} />
              <Route path="/users/:id" element={<PublicProfilePage />} />
              <Route path="/achievements" element={<AchievementsPage />} />
              <Route path="/templates" element={<TemplatesPage />} />
              <Route path="/challenges" element={<ChallengesPage />} />
              <Route path="/challenges/:id" element={<ChallengeDetailPage />} />
              <Route path="/notifications" element={<NotificationsPage />} />
              <Route path="/profile" element={<ComingSoon name="Profile" />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/trainer" element={<TrainerPage />} />
              <Route path="/trainer/programs/:id" element={<ProgramDetailPage />} />
            </Route>
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
