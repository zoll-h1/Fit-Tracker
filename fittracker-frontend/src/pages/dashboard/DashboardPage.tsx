import { Dumbbell, Activity, Scale, TrendingUp } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function DashboardPage() {
  const navigate = useNavigate()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Welcome back! Here's your fitness overview.</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'This Week', value: '0', sub: 'workouts', icon: Dumbbell, color: 'text-blue-400', bg: 'bg-blue-900/30' },
          { label: 'Total Volume', value: '0 kg', sub: 'all time', icon: Activity, color: 'text-orange-400', bg: 'bg-orange-900/30' },
          { label: 'Streak', value: '0', sub: 'days', icon: TrendingUp, color: 'text-green-400', bg: 'bg-green-900/30' },
          { label: 'Goals Met', value: '0%', sub: 'this month', icon: Scale, color: 'text-purple-400', bg: 'bg-purple-900/30' },
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

      {/* Recent Workouts placeholder */}
      <div className="rounded-xl p-5 border border-slate-700" style={{ background: 'var(--bg-secondary)' }}>
        <h2 className="text-lg font-semibold text-white mb-4">Recent Workouts</h2>
        <div className="text-center py-8">
          <Dumbbell className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No workouts yet</p>
          <p className="text-sm text-slate-500 mt-1">Start your first workout to see it here</p>
          <button
            onClick={() => navigate('/workouts')}
            className="mt-4 px-4 py-2 rounded-lg text-sm font-medium text-white transition hover:opacity-90"
            style={{ background: 'var(--primary)' }}
          >
            Start Workout
          </button>
        </div>
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
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Welcome back! Here's your fitness overview.</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'This Week', value: '0', sub: 'workouts', icon: Dumbbell, color: 'text-blue-400', bg: 'bg-blue-900/30' },
          { label: 'Total Volume', value: '0 kg', sub: 'all time', icon: Activity, color: 'text-orange-400', bg: 'bg-orange-900/30' },
          { label: 'Streak', value: '0', sub: 'days', icon: TrendingUp, color: 'text-green-400', bg: 'bg-green-900/30' },
          { label: 'Goals Met', value: '0%', sub: 'this month', icon: Scale, color: 'text-purple-400', bg: 'bg-purple-900/30' },
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

      {/* Recent Workouts placeholder */}
      <div className="rounded-xl p-5 border border-slate-700" style={{ background: 'var(--bg-secondary)' }}>
        <h2 className="text-lg font-semibold text-white mb-4">Recent Workouts</h2>
        <div className="text-center py-8">
          <Dumbbell className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No workouts yet</p>
          <p className="text-sm text-slate-500 mt-1">Start your first workout to see it here</p>
          <button
            className="mt-4 px-4 py-2 rounded-lg text-sm font-medium text-white transition hover:opacity-90"
            style={{ background: 'var(--primary)' }}
          >
            Start Workout
          </button>
        </div>
      </div>

      {/* Progress Charts placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-xl p-5 border border-slate-700" style={{ background: 'var(--bg-secondary)' }}>
          <h2 className="text-lg font-semibold text-white mb-4">Strength Progress</h2>
          <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
            Chart coming soon (Week 4)
          </div>
        </div>
        <div className="rounded-xl p-5 border border-slate-700" style={{ background: 'var(--bg-secondary)' }}>
          <h2 className="text-lg font-semibold text-white mb-4">Muscle Groups This Week</h2>
          <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
            Heatmap coming soon (Week 4)
          </div>
        </div>
      </div>
    </div>
  )
}
