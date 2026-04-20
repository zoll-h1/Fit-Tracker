import { useState, useRef, useEffect } from 'react'
import { Bell, LogOut, X, CheckCheck, Sun, Moon } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import { authApi } from '@/api/auth'
import { notificationsApi } from '@/api/gamification'
import { useThemeStore } from '@/store/themeStore'
import { useTranslation } from 'react-i18next'

export default function TopBar() {
  const navigate = useNavigate()
  const { user, refreshToken, logout } = useAuthStore()
  const [notifOpen, setNotifOpen] = useState(false)
  const notifRef = useRef<HTMLDivElement>(null)
  const qc = useQueryClient()
  const { theme, toggleTheme } = useThemeStore()
  const { i18n } = useTranslation()

  const toggleLang = () => {
    const next = i18n.language === 'en' ? 'ru' : 'en'
    i18n.changeLanguage(next)
    localStorage.setItem('fittracker-lang', next)
  }

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotifOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const { data: unreadCount = 0 } = useQuery({
    queryKey: ['notif-unread-count'],
    queryFn: notificationsApi.unreadCount,
    refetchInterval: 60_000,
    retry: false,
  })

  const { data: notifications = [] } = useQuery({
    queryKey: ['notif-dropdown'],
    queryFn: () => notificationsApi.list(false),
    enabled: notifOpen,
    retry: false,
  })

  const markRead = useMutation({
    mutationFn: notificationsApi.markRead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notif-unread-count'] })
      qc.invalidateQueries({ queryKey: ['notif-dropdown'] })
    },
  })

  const markAllRead = useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notif-unread-count'] })
      qc.invalidateQueries({ queryKey: ['notif-dropdown'] })
    },
  })

  const handleLogout = async () => {
    try { if (refreshToken) await authApi.logout(refreshToken) } catch {}
    finally { logout(); navigate('/login') }
  }

  const avatarUrl = user?.avatar_url
    ? user.avatar_url.startsWith('http') ? user.avatar_url : `${import.meta.env.VITE_API_URL || ''}${user.avatar_url}`
    : null

  const typeIcon = (type: string) => {
    if (type.includes('achievement')) return '🏆'
    if (type.includes('streak')) return '🔥'
    if (type.includes('level')) return '⬆️'
    if (type.includes('pr')) return '💪'
    if (type.includes('social') || type.includes('follow')) return '👥'
    if (type.includes('challenge')) return '🎯'
    return '🔔'
  }

  return (
    <header className="h-14 flex items-center justify-between px-4 md:px-6 border-b border-slate-700 sticky top-0 z-20" style={{ background: 'var(--bg-secondary)' }}>
      <div className="lg:hidden text-white font-bold text-lg">FitTracker</div>
      <div className="hidden lg:block" />
      <div className="flex items-center gap-3">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition"
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        {/* Language Toggle */}
        <button
          onClick={toggleLang}
          className="px-2 py-1 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-700 transition"
          title="Toggle language"
        >
          {i18n.language === 'en' ? 'EN' : 'RU'}
        </button>

        {/* Notification Bell */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setNotifOpen(v => !v)}
            className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] bg-red-500 rounded-full text-[10px] text-white font-bold flex items-center justify-center px-1">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </button>

          {notifOpen && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-slate-800 border border-slate-700 rounded-2xl shadow-2xl z-50">
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
                <span className="text-white font-semibold text-sm">Notifications</span>
                {unreadCount > 0 && (
                  <button
                    onClick={() => markAllRead.mutate()}
                    className="flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300"
                  >
                    <CheckCheck className="w-3 h-3" />
                    Mark all read
                  </button>
                )}
              </div>
              {/* List */}
              <div className="max-h-80 overflow-y-auto">
                {notifications.slice(0, 10).map(n => (
                  <div
                    key={n.id}
                    className={`flex items-start gap-3 px-4 py-3 border-b border-slate-700/50 hover:bg-slate-700/40 cursor-pointer ${!n.is_read ? 'bg-violet-950/20' : ''}`}
                    onClick={() => {
                      if (!n.is_read) markRead.mutate(n.id)
                      if (n.action_url) navigate(n.action_url)
                      setNotifOpen(false)
                    }}
                  >
                    <span className="text-lg mt-0.5 flex-shrink-0">{typeIcon(n.notification_type)}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white font-medium truncate">{n.title}</p>
                      <p className="text-xs text-slate-400 truncate">{n.body}</p>
                      <p className="text-[10px] text-slate-600 mt-0.5">{new Date(n.created_at).toLocaleString()}</p>
                    </div>
                    {!n.is_read && (
                      <div className="w-2 h-2 bg-violet-500 rounded-full flex-shrink-0 mt-1.5" />
                    )}
                  </div>
                ))}
                {notifications.length === 0 && (
                  <div className="text-center py-8 text-slate-500 text-sm">No notifications yet</div>
                )}
              </div>
              {/* Footer */}
              <div className="px-4 py-2 border-t border-slate-700">
                <button
                  onClick={() => { navigate('/notifications'); setNotifOpen(false) }}
                  className="text-xs text-violet-400 hover:text-violet-300 w-full text-center"
                >
                  View all notifications →
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Avatar */}
        <button onClick={() => navigate('/profile')} className="flex items-center gap-2 hover:opacity-80 transition">
          {avatarUrl ? (
            <img src={avatarUrl} alt={user?.full_name || user?.username || 'Avatar'} className="w-8 h-8 rounded-full object-cover ring-2 ring-slate-600" />
          ) : (
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-semibold">
              {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
            </div>
          )}
          <span className="hidden md:block text-sm text-slate-300">{user?.full_name || user?.username}</span>
        </button>

        {/* Logout */}
        <button onClick={handleLogout} className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-700 transition" title="Logout">
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}
