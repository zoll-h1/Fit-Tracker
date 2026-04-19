import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { gamificationApi, type Achievement } from '@/api/gamification';

const RARITY_COLORS: Record<string, string> = {
  common: 'border-slate-600 bg-slate-800',
  rare: 'border-blue-500/40 bg-blue-950/40',
  epic: 'border-violet-500/50 bg-violet-950/40',
  legendary: 'border-amber-400/60 bg-amber-950/30',
};

const RARITY_BADGE: Record<string, string> = {
  common: 'text-slate-400 bg-slate-700',
  rare: 'text-blue-300 bg-blue-900/60',
  epic: 'text-violet-300 bg-violet-900/60',
  legendary: 'text-amber-300 bg-amber-900/60',
};

const CATEGORIES = ['all', 'workout', 'strength', 'consistency', 'nutrition', 'body'];

export default function AchievementsPage() {
  const [category, setCategory] = useState('all');
  const [showEarned, setShowEarned] = useState(false);

  const { data: achievements, isLoading } = useQuery({
    queryKey: ['achievements-all'],
    queryFn: gamificationApi.allAchievements,
  });

  const { data: profile } = useQuery({
    queryKey: ['gamification-profile'],
    queryFn: gamificationApi.profile,
  });

  const filtered = (achievements ?? []).filter((a) => {
    if (category !== 'all' && a.category !== category) return false;
    if (showEarned && !a.earned) return false;
    return true;
  });

  const earnedCount = (achievements ?? []).filter(a => a.earned).length;
  const totalCount = (achievements ?? []).length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Achievements</h1>
        <p className="text-slate-400 text-sm mt-1">
          {earnedCount} / {totalCount} unlocked
          {profile && ` · Level ${profile.current_level} ${profile.level_name}`}
        </p>
      </div>

      {/* XP Progress */}
      {profile && (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-violet-600 flex items-center justify-center text-xl font-bold text-white">
                {profile.current_level}
              </div>
              <div>
                <p className="font-bold text-white">{profile.level_name}</p>
                <p className="text-slate-400 text-xs">{profile.total_xp.toLocaleString()} Total XP</p>
              </div>
            </div>
            <div className="text-right text-sm">
              <p className="text-white font-medium">{profile.weekly_xp} XP this week</p>
              <p className="text-slate-400 text-xs">{profile.monthly_xp} this month</p>
            </div>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2.5">
            <div
              className="bg-violet-500 h-2.5 rounded-full transition-all duration-700"
              style={{ width: `${profile.xp_pct}%` }}
            />
          </div>
          {profile.xp_for_next && (
            <p className="text-xs text-slate-500 mt-1.5 text-right">
              {profile.xp_in_level}/{profile.xp_for_next} XP to Level {profile.current_level + 1}
            </p>
          )}
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors capitalize ${
              category === cat
                ? 'bg-violet-600 text-white'
                : 'bg-slate-700 text-slate-400 hover:text-white'
            }`}
          >
            {cat}
          </button>
        ))}
        <button
          onClick={() => setShowEarned(!showEarned)}
          className={`ml-auto px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
            showEarned ? 'bg-emerald-600 text-white' : 'bg-slate-700 text-slate-400 hover:text-white'
          }`}
        >
          {showEarned ? '✓ Earned only' : 'Show earned only'}
        </button>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {filtered.map(achievement => (
            <AchievementCard key={achievement.id} achievement={achievement} />
          ))}
        </div>
      )}

      {filtered.length === 0 && !isLoading && (
        <div className="text-center py-12 text-slate-500">
          No achievements match this filter
        </div>
      )}
    </div>
  );
}

function AchievementCard({ achievement: a }: { achievement: Achievement }) {
  const colorClass = RARITY_COLORS[a.rarity] ?? RARITY_COLORS.common;
  const badgeClass = RARITY_BADGE[a.rarity] ?? RARITY_BADGE.common;
  const locked = !a.earned;

  return (
    <div
      className={`border rounded-2xl p-4 transition-all duration-200 ${colorClass} ${
        locked ? 'opacity-50 grayscale' : 'hover:scale-[1.01]'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Icon circle */}
        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0 ${
          locked ? 'bg-slate-700' : 'bg-slate-700'
        }`}>
          {locked ? '🔒' : getIcon(a.category)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <p className="font-semibold text-white text-sm truncate">{a.name}</p>
            <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium capitalize flex-shrink-0 ${badgeClass}`}>
              {a.rarity}
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-0.5 line-clamp-2">{a.description}</p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-violet-400 font-medium">+{a.xp_reward} XP</span>
            {a.earned && a.earned_at && (
              <span className="text-[10px] text-emerald-400">
                ✓ {new Date(a.earned_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function getIcon(category: string): string {
  switch (category) {
    case 'workout': return '💪';
    case 'strength': return '🏋️';
    case 'consistency': return '🔥';
    case 'nutrition': return '🥗';
    case 'body': return '⚖️';
    default: return '🏆';
  }
}
