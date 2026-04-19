import { NavLink } from 'react-router-dom'
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

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/workouts', icon: Dumbbell, label: 'Workouts' },
  { to: '/body-metrics', icon: Scale, label: 'Body' },
  { to: '/nutrition', icon: UtensilsCrossed, label: 'Nutrition' },
  { to: '/analytics', icon: LineChart, label: 'Analytics' },
  { to: '/social', icon: Users, label: 'Social' },
  { to: '/achievements', icon: Trophy, label: 'Achievements' },
  { to: '/profile', icon: User, label: 'Profile' },
]

export default function Sidebar() {
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

      {/* Settings */}
      <div className="px-3 mt-4">
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
