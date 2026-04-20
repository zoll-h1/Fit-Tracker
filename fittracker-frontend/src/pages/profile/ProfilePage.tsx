import { useRef, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Camera, Edit2, Save, X, Dumbbell, Flame, Trophy, Activity } from 'lucide-react';
import { authApi } from '@/api/auth';
import { gamificationApi } from '@/api/gamification';
import { workoutsApi } from '@/api/workouts';
import { useAuthStore } from '@/stores/authStore';

const GENDER_LABELS: Record<string, string> = { male: 'Male', female: 'Female', other: 'Other' };

export default function ProfilePage() {
  const qc = useQueryClient();
  const { updateUser } = useAuthStore();
  const [editing, setEditing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [avatarUploading, setAvatarUploading] = useState(false);

  const { data: me, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: () => authApi.me(),
  });

  const { data: xp } = useQuery({
    queryKey: ['gamification-profile'],
    queryFn: () => gamificationApi.profile(),
  });

  const { data: workoutsData } = useQuery({
    queryKey: ['workouts', 1],
    queryFn: () => workoutsApi.list(1, 100, 'finished'),
  });

  const totalWorkouts = workoutsData?.total ?? 0;
  const totalVolume = (workoutsData?.items ?? []).reduce((s, w) => s + (w.total_volume_kg ?? 0), 0);

  const [form, setForm] = useState({
    full_name: '',
    bio: '',
    height_cm: '',
    weight_kg: '',
    gender: '',
    date_of_birth: '',
    unit_system: 'metric',
  });

  const startEdit = () => {
    if (!me) return;
    setForm({
      full_name: me.full_name ?? '',
      bio: me.bio ?? '',
      height_cm: me.height_cm ? String(me.height_cm) : '',
      weight_kg: me.weight_kg ? String(me.weight_kg) : '',
      gender: me.gender ?? '',
      date_of_birth: me.date_of_birth ?? '',
      unit_system: me.unit_system ?? 'metric',
    });
    setEditing(true);
  };

  const updateMutation = useMutation({
    mutationFn: () =>
      authApi.updateMe({
        full_name: form.full_name || undefined,
        bio: form.bio || undefined,
        height_cm: form.height_cm ? parseFloat(form.height_cm) : undefined,
        weight_kg: form.weight_kg ? parseFloat(form.weight_kg) : undefined,
        gender: (form.gender || undefined) as any,
        date_of_birth: form.date_of_birth || undefined,
        unit_system: form.unit_system as any,
      }),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ['me'] });
      updateUser(updated);
      setEditing(false);
    },
  });

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarUploading(true);
    try {
      const updated = await authApi.uploadAvatar(file);
      updateUser(updated);
      qc.invalidateQueries({ queryKey: ['me'] });
    } finally {
      setAvatarUploading(false);
      e.target.value = '';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const user = me;
  if (!user) return null;

  const initials = (user.full_name || user.username)
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="p-6 space-y-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-white">Profile</h1>

      {/* Avatar + name card */}
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 flex items-center gap-5">
        <div className="relative flex-shrink-0">
          <div className="w-20 h-20 rounded-full bg-violet-700 flex items-center justify-center text-2xl font-bold text-white">
            {user.avatar_url ? (
              <img src={user.avatar_url} alt={user.username} className="w-full h-full rounded-full object-cover" />
            ) : (
              initials
            )}
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={avatarUploading}
            className="absolute bottom-0 right-0 w-7 h-7 bg-violet-600 hover:bg-violet-500 rounded-full flex items-center justify-center border-2 border-slate-800 transition-colors disabled:opacity-50"
            title="Change profile photo"
          >
            <Camera className="w-3.5 h-3.5 text-white" />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={handleAvatarChange}
          />
        </div>
        <div className="flex-1 min-w-0">
          <h2 className="text-xl font-bold text-white truncate">{user.full_name || user.username}</h2>
          <p className="text-slate-400 text-sm">@{user.username}</p>
          {user.bio && <p className="text-slate-300 text-sm mt-1">{user.bio}</p>}
          <div className="flex items-center gap-2 mt-2">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              user.role === 'admin' ? 'bg-red-900/50 text-red-300' :
              user.role === 'trainer' ? 'bg-blue-900/50 text-blue-300' :
              'bg-violet-900/50 text-violet-300'
            }`}>
              {user.role}
            </span>
            <span className="text-xs text-slate-500">Joined {new Date(user.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        {!editing && (
          <button
            onClick={startEdit}
            className="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors flex-shrink-0"
          >
            <Edit2 className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Dumbbell, label: 'Workouts', value: String(totalWorkouts), color: 'text-blue-400', bg: 'bg-blue-900/30' },
          { icon: Activity, label: 'Total Volume', value: totalVolume ? `${Math.round(totalVolume)} kg` : '—', color: 'text-orange-400', bg: 'bg-orange-900/30' },
          { icon: Flame, label: 'Streak', value: `${xp?.current_streak_days ?? 0}d`, color: 'text-red-400', bg: 'bg-red-900/30' },
          { icon: Trophy, label: 'Level', value: `${xp?.current_level ?? 1}`, color: 'text-amber-400', bg: 'bg-amber-900/30' },
        ].map(({ icon: Icon, label, value, color, bg }) => (
          <div key={label} className={`rounded-xl p-4 border border-slate-700 bg-slate-800`}>
            <div className={`w-8 h-8 rounded-lg ${bg} flex items-center justify-center mb-2`}>
              <Icon className={`w-4 h-4 ${color}`} />
            </div>
            <p className="text-2xl font-bold text-white">{value}</p>
            <p className="text-slate-500 text-xs mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* XP bar */}
      {xp && (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-white">Level {xp.current_level}</span>
            <span className="text-xs text-slate-400">{xp.xp_in_level} / {xp.xp_for_next ?? '?'} XP to next level</span>
          </div>
          <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-violet-500 rounded-full transition-all"
              style={{ width: `${Math.min(100, (xp.xp_pct))}%` }}
            />
          </div>
        </div>
      )}

      {/* Edit form */}
      {editing && (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 space-y-4">
          <h3 className="text-lg font-semibold text-white">Edit Profile</h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Full Name</label>
              <input
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                placeholder="Your full name"
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Date of Birth</label>
              <input
                type="date"
                value={form.date_of_birth}
                onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Height (cm)</label>
              <input
                type="number"
                value={form.height_cm}
                onChange={(e) => setForm({ ...form, height_cm: e.target.value })}
                placeholder="175"
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Weight (kg)</label>
              <input
                type="number"
                value={form.weight_kg}
                onChange={(e) => setForm({ ...form, weight_kg: e.target.value })}
                placeholder="70"
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Gender</label>
              <select
                value={form.gender}
                onChange={(e) => setForm({ ...form, gender: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
              >
                <option value="">Prefer not to say</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Unit System</label>
              <select
                value={form.unit_system}
                onChange={(e) => setForm({ ...form, unit_system: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
              >
                <option value="metric">Metric (kg, cm)</option>
                <option value="imperial">Imperial (lb, in)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Bio</label>
            <textarea
              value={form.bio}
              onChange={(e) => setForm({ ...form, bio: e.target.value })}
              placeholder="Tell us about yourself..."
              rows={3}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500 resize-none"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              onClick={() => setEditing(false)}
              className="flex-1 py-2.5 border border-slate-600 rounded-xl text-slate-300 hover:text-white transition-colors flex items-center justify-center gap-2"
            >
              <X className="w-4 h-4" />
              Cancel
            </button>
            <button
              onClick={() => updateMutation.mutate()}
              disabled={updateMutation.isPending}
              className="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 text-white rounded-xl font-semibold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Save className="w-4 h-4" />
              {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      )}

      {/* Body stats (read-only) */}
      {!editing && (user.height_cm || user.weight_kg || user.gender || user.date_of_birth) && (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Body Stats</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {user.height_cm && (
              <div className="bg-slate-700/50 rounded-xl p-3 text-center">
                <p className="text-white font-semibold">{user.height_cm} cm</p>
                <p className="text-slate-500 text-xs mt-0.5">Height</p>
              </div>
            )}
            {user.weight_kg && (
              <div className="bg-slate-700/50 rounded-xl p-3 text-center">
                <p className="text-white font-semibold">{user.weight_kg} kg</p>
                <p className="text-slate-500 text-xs mt-0.5">Weight</p>
              </div>
            )}
            {user.gender && (
              <div className="bg-slate-700/50 rounded-xl p-3 text-center">
                <p className="text-white font-semibold capitalize">{GENDER_LABELS[user.gender] ?? user.gender}</p>
                <p className="text-slate-500 text-xs mt-0.5">Gender</p>
              </div>
            )}
            {user.date_of_birth && (
              <div className="bg-slate-700/50 rounded-xl p-3 text-center">
                <p className="text-white font-semibold">
                  {new Date().getFullYear() - new Date(user.date_of_birth).getFullYear()} yrs
                </p>
                <p className="text-slate-500 text-xs mt-0.5">Age</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
