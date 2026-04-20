import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Dumbbell, Activity, Scale, TrendingUp, Clock, BarChart3, ChevronRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { workoutsApi } from '@/api/workouts'
import { gamificationApi } from '@/api/gamification'
import { formatDistanceToNow, subDays } from 'date-fns'

function formatDuration(seconds: number | null): string {
  if (!seconds) return '—'
  const m = Math.floor(seconds / 60)
  const h = Math.floor(m / 60)
  if (h > 0) return `${h}h ${m % 60}m`
  return `${m}m`
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()

  const { data: workoutsData } = useQuery({
    queryKey: ['dashboard-workouts'],
    queryFn: () => workoutsApi.list(1, 5, 'finished'),
  })

  const { data: profile } = useQuery({
    queryKey: ['gamification-profile'],
    queryFn: () => gamificationApi.profile(),
  })

  const workouts = workoutsData?.items ?? []
  const sevenDaysAgo = subDays(new Date(), 7)
  const thisWeekCount = workouts.filter(
    (w) => new Date(w.started_at) >= sevenDaysAgo,
  ).length
  const totalVolume = workouts.length
    ? workouts.reduce((sum, w) => sum + (w.total_volume_kg ?? 0), 0)
    : null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">{t('dashboard.title')}</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Welcome back! Here's your fitness overview.</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: t('dashboard.thisWeek'), value: String(thisWeekCount), sub: 'workouts', icon: Dumbbell, color: 'text-blue-400', bg: 'bg-blue-900/30' },
          { label: t('dashboard.totalVolume'), value: totalVolume != null ? `${Math.round(totalVolume)} kg` : '—', sub: 'all time', icon: Activity, color: 'text-orange-400', bg: 'bg-orange-900/30' },
          { label: t('dashboard.streak'), value: String(profile?.current_streak_days ?? 0), sub: t('common.days'), icon: TrendingUp, color: 'text-green-400', bg: 'bg-green-900/30' },
          { label: t('dashboard.goalsMet'), value: '0%', sub: 'this month', icon: Scale, color: 'text-purple-400', bg: 'bg-purple-900/30' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl p-4 border border-slate-700"
            style={{ background: 'var(--bg-secondary)' }}
          >
            <div className={`inline-flex p-2 rounded-lg ${stat.bg} mb-3`}>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <div className="text-2xl font-bold text-white">{stat.value}</div>
            <div className="text-sm text-slate-400">{stat.label}</div>
            <div className="text-xs text-slate-500">{stat.sub}</div>
          </div>
        ))}
      </div>

      {/* Recent Workouts */}
      <div className="rounded-xl p-5 border border-slate-700" style={{ background: 'var(--bg-secondary)' }}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">{t('dashboard.recentWorkouts')}</h2>
          {workouts.length > 0 && (
            <button
              onClick={() => navigate('/workouts')}
              className="text-sm text-violet-400 hover:text-violet-300 transition-colors"
            >
              {t('dashboard.viewAll')}
            </button>
          )}
        </div>
        {workouts.length === 0 ? (
          <div className="text-center py-8">
            <Dumbbell className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400">{t('dashboard.noWorkouts')}</p>
            <p className="text-sm text-slate-500 mt-1">{t('dashboard.startFirst')}</p>
            <button
              onClick={() => navigate('/workouts')}
              className="mt-4 px-4 py-2 rounded-lg text-sm font-medium text-white transition hover:opacity-90"
              style={{ background: 'var(--primary)' }}
            >
              {t('dashboard.startWorkout')}
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {workouts.map((session) => (
              <button
                key={session.id}
                onClick={() => navigate(`/workouts/${session.id}`)}
                className="w-full bg-slate-800/60 border border-slate-700 hover:border-violet-500 rounded-xl p-4 flex items-center gap-4 text-left transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                  <Dumbbell className="w-5 h-5 text-violet-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-white truncate">{session.name}</p>
                  <p className="text-slate-400 text-sm mt-0.5">
                    {formatDistanceToNow(new Date(session.started_at), { addSuffix: true })}
                  </p>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="flex items-center gap-3 text-slate-400 text-sm">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {formatDuration(session.duration_seconds)}
                    </span>
                    <span className="flex items-center gap-1">
                      <BarChart3 className="w-3.5 h-3.5" />
                      {Math.round(session.total_volume_kg)}kg
                    </span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-600" />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Progress Charts placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-xl p-5 border border-slate-700" style={{ background: 'var(--bg-secondary)' }}>
          <h2 className="text-lg font-semibold text-white mb-4">Strength Progress</h2>
          <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
            Chart coming soon (Phase 3)
          </div>
        </div>
        <div className="rounded-xl p-5 border border-slate-700" style={{ background: 'var(--bg-secondary)' }}>
          <h2 className="text-lg font-semibold text-white mb-4">Muscle Groups This Week</h2>
          <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
            Heatmap coming soon (Phase 3)
          </div>
        </div>
      </div>
    </div>
  )
}
