import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { notificationsApi, type NotificationSettings } from '@/api/gamification'

interface ToggleRowProps {
  label: string
  description: string
  checked: boolean
  onChange: (val: boolean) => void
}

function ToggleRow({ label, description, checked, onChange }: ToggleRowProps) {
  return (
    <div className="flex items-center justify-between py-4 border-b border-slate-700 last:border-0">
      <div>
        <p className="text-sm font-medium text-white">{label}</p>
        <p className="text-xs text-slate-400 mt-0.5">{description}</p>
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`relative w-11 h-6 rounded-full transition-colors ${checked ? 'bg-violet-600' : 'bg-slate-600'}`}
      >
        <span
          className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${checked ? 'translate-x-5' : 'translate-x-0'}`}
        />
      </button>
    </div>
  )
}

export default function SettingsPage() {
  const qc = useQueryClient()

  const { data: settings, isLoading } = useQuery({
    queryKey: ['notification-settings'],
    queryFn: notificationsApi.settings,
  })

  const updateSettings = useMutation({
    mutationFn: notificationsApi.updateSettings,
    onSuccess: (updated) => {
      qc.setQueryData(['notification-settings'], updated)
    },
  })

  const handleToggle = (field: keyof NotificationSettings, value: boolean) => {
    updateSettings.mutate({ [field]: value })
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-white mb-6">Settings</h1>

      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-white mb-1">Notification Preferences</h2>
        <p className="text-sm text-slate-400 mb-4">Choose which notifications you want to receive.</p>

        {isLoading ? (
          <div className="py-8 text-center text-slate-500 text-sm">Loading…</div>
        ) : settings ? (
          <div>
            <ToggleRow
              label="Workout Reminders"
              description="Get reminded to complete your scheduled workouts"
              checked={settings.workout_reminders}
              onChange={v => handleToggle('workout_reminders', v)}
            />
            <ToggleRow
              label="Streak Alerts"
              description="Notifications about your workout streak status"
              checked={settings.streak_alerts}
              onChange={v => handleToggle('streak_alerts', v)}
            />
            <ToggleRow
              label="Achievement Alerts"
              description="Celebrate when you unlock new achievements"
              checked={settings.achievement_alerts}
              onChange={v => handleToggle('achievement_alerts', v)}
            />
            <ToggleRow
              label="Social Alerts"
              description="Notifications for follows, likes, and comments"
              checked={settings.social_alerts}
              onChange={v => handleToggle('social_alerts', v)}
            />
            <ToggleRow
              label="Challenge Alerts"
              description="Updates on challenges you've joined"
              checked={settings.challenge_alerts}
              onChange={v => handleToggle('challenge_alerts', v)}
            />
            <ToggleRow
              label="Email Notifications"
              description="Receive important updates via email"
              checked={settings.email_notifications}
              onChange={v => handleToggle('email_notifications', v)}
            />
          </div>
        ) : null}
      </div>
    </div>
  )
}
