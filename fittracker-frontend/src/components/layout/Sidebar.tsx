import { NavLink } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  LayoutDashboard,
  Dumbbell,
  LineChart,
  Scale,
  UtensilsCrossed,
  Users,
  Trophy,
  User,
  Settings,
} from 'lucide-react'
import { gamificationApi } from '@/api/gamification'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/workouts', icon: Dumbbell, label: 'Workouts' },
  { to: '/exercises', icon: Dumbbell, label: 'Exercises' },
  { to: '/body-metrics', icon: Scale, label: 'Body' },
  { to: '/nutrition', icon: UtensilsCrossed, label: 'Nutrition' },
  { to: '/analytics', icon: LineChart, label: 'Analytics' },
  { to: '/social', icon: Users, label: 'Social' },
  { to: '/achievements', icon: Trophy, label: 'Achievements' },
  { to: '/profile', icon: User, label: 'Profile' },
]

export default function Sidebar() {
  const { data: xp } = useQuery({
    queryKey: ['gamification-profile'],
    queryFn: gamificationApi.profile,
    staleTime: 1000 * 60 * 2,
    retry: false,
  })

  return (
    <aside
      className="hidden lg:flex flex-col w-60 min-h-screen border-r border-slate-700 py-4"
      style={{ background: 'var(--bg-secondary)' }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 mb-8">
        <Dumbbell className="w-6 h-6 text-blue-500" />
        <span className="text-lg font-bold text-white">FitTracker</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700'
              }`
            }
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* XP Bar */}
      {xp && (
        <div className="mx-3 mb-3 px-3 py-3 bg-slate-700/50 rounded-xl border border-slate-600">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-violet-600 flex items-center justify-center text-xs font-bold text-white">
                {xp.current_level}
              </div>
              <span className="text-xs font-medium text-white">{xp.level_name}</span>
            </div>
            <span className="text-xs text-slate-400">{xp.total_xp.toLocaleString()} XP</span>
          </div>
          <div className="w-full bg-slate-600 rounded-full h-1.5">
            <div
              className="bg-violet-500 h-1.5 rounded-full transition-all duration-700"
              style={{ width: `${xp.xp_pct}%` }}
            />
          </div>
          {xp.xp_for_next && (
            <p className="text-[10px] text-slate-500 mt-1 text-right">
              {xp.xp_in_level}/{xp.xp_for_next} to Level {xp.current_level + 1}
            </p>
          )}
          {xp.current_streak_days > 0 && (
            <p className="text-[10px] text-amber-400 mt-1">🔥 {xp.current_streak_days} day streak</p>
          )}
        </div>
      )}

      {/* Settings */}
      <div className="px-3 mt-1">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              isActive ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-700'
            }`
          }
        >
          <Settings className="w-5 h-5" />
          Settings
        </NavLink>
      </div>
    </aside>
  )
}
