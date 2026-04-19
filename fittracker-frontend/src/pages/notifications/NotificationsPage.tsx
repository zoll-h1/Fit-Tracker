import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Trash2 } from 'lucide-react'
import { notificationsApi, type Notification } from '@/api/gamification'

const typeIcon = (type: string) => {
  if (type.includes('achievement')) return '🏆'
  if (type.includes('streak')) return '🔥'
  if (type.includes('level')) return '⬆️'
  if (type.includes('pr')) return '💪'
  if (type.includes('social') || type.includes('follow')) return '👥'
  if (type.includes('challenge')) return '🎯'
  return '🔔'
}

export default function NotificationsPage() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [unreadOnly, setUnreadOnly] = useState(false)

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ['notifications', unreadOnly],
    queryFn: () => notificationsApi.list(unreadOnly),
  })

  const markRead = useMutation({
    mutationFn: notificationsApi.markRead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] })
      qc.invalidateQueries({ queryKey: ['notif-unread-count'] })
    },
  })

  const markAllRead = useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] })
      qc.invalidateQueries({ queryKey: ['notif-unread-count'] })
    },
  })

  const deleteNotif = useMutation({
    mutationFn: notificationsApi.delete,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] })
      qc.invalidateQueries({ queryKey: ['notif-unread-count'] })
    },
  })

  const handleClick = (n: Notification) => {
    if (!n.is_read) markRead.mutate(n.id)
    if (n.action_url) navigate(n.action_url)
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Notifications</h1>
        <button
          onClick={() => markAllRead.mutate()}
          className="text-sm text-violet-400 hover:text-violet-300 transition"
        >
          Mark all read
        </button>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setUnreadOnly(false)}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
            !unreadOnly ? 'bg-violet-600 text-white' : 'bg-slate-700 text-slate-400 hover:text-white'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setUnreadOnly(true)}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
            unreadOnly ? 'bg-violet-600 text-white' : 'bg-slate-700 text-slate-400 hover:text-white'
          }`}
        >
          Unread
        </button>
      </div>

      {/* List */}
      {isLoading ? (
        <div className="text-center py-16 text-slate-500">Loading…</div>
      ) : notifications.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-4xl mb-3">🔔</div>
          <p className="text-slate-400">No notifications yet</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map(n => (
            <div
              key={n.id}
              className={`flex items-start gap-4 p-4 rounded-xl border transition cursor-pointer group ${
                !n.is_read
                  ? 'bg-violet-950/20 border-violet-800/40 border-l-2 border-l-violet-500'
                  : 'bg-slate-800 border-slate-700 hover:border-slate-600'
              }`}
              onClick={() => handleClick(n)}
            >
              <span className="text-2xl flex-shrink-0 mt-0.5">{typeIcon(n.notification_type)}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-white">{n.title}</p>
                <p className="text-sm text-slate-400 mt-0.5">{n.body}</p>
                <p className="text-xs text-slate-600 mt-1">{new Date(n.created_at).toLocaleString()}</p>
              </div>
              <button
                onClick={e => { e.stopPropagation(); deleteNotif.mutate(n.id) }}
                className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-slate-700 transition"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
