import { Bell, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { authApi } from '@/api/auth'

export default function TopBar() {
  const navigate = useNavigate()
  const { user, refreshToken, logout } = useAuthStore()

  const handleLogout = async () => {
    try {
      if (refreshToken) await authApi.logout(refreshToken)
    } catch {
      // ignore
    } finally {
      logout()
      navigate('/login')
    }
  }

  const avatarUrl = user?.avatar_url
    ? user.avatar_url.startsWith('http')
      ? user.avatar_url
      : `${import.meta.env.VITE_API_URL || ''}${user.avatar_url}`
    : null

  return (
    <header
      className="h-14 flex items-center justify-between px-4 md:px-6 border-b border-slate-700 sticky top-0 z-20"
      style={{ background: 'var(--bg-secondary)' }}
    >
      {/* Left: Mobile Logo */}
      <div className="lg:hidden text-white font-bold text-lg">FitTracker</div>
      <div className="hidden lg:block" />

      {/* Right */}
      <div className="flex items-center gap-3">
        {/* Notifications */}
        <button className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-500 rounded-full" />
        </button>

        {/* Avatar */}
        <button
          onClick={() => navigate('/profile')}
          className="flex items-center gap-2 hover:opacity-80 transition"
        >
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt={user?.full_name || user?.username || 'Avatar'}
              className="w-8 h-8 rounded-full object-cover ring-2 ring-slate-600"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-semibold">
              {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
            </div>
          )}
          <span className="hidden md:block text-sm text-slate-300">
            {user?.full_name || user?.username}
          </span>
        </button>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-700 transition"
          title="Logout"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}
