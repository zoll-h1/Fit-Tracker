import { Link, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { challengesApi, type LeaderboardEntry } from '@/api/challenges'
import { format, formatDistanceToNow } from 'date-fns'

const TYPE_ICONS: Record<string, string> = {
  total_workouts: '💪',
  total_volume: '📦',
  streak: '🔥',
}

const TYPE_LABELS: Record<string, string> = {
  total_workouts: 'Total Workouts',
  total_volume: 'Total Volume',
  streak: 'Streak',
}

const TYPE_UNITS: Record<string, string> = {
  total_workouts: 'workouts',
  total_volume: 'kg',
  streak: 'days',
}

function ProgressBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0
  return (
    <div className="w-full bg-slate-700 rounded-full h-3">
      <div
        className="bg-violet-500 h-3 rounded-full transition-all"
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

function RankBadge({ rank }: { rank: number }) {
  if (rank === 1) return <span className="text-xl">🥇</span>
  if (rank === 2) return <span className="text-xl">🥈</span>
  if (rank === 3) return <span className="text-xl">🥉</span>
  return <span className="text-sm font-bold text-slate-400">#{rank}</span>
}

export default function ChallengeDetailPage() {
  const { id } = useParams<{ id: string }>()
  const challengeId = Number(id)
  const queryClient = useQueryClient()

  const { data: challenge, isLoading } = useQuery({
    queryKey: ['challenge', challengeId],
    queryFn: () => challengesApi.get(challengeId),
    enabled: !isNaN(challengeId),
  })

  const { data: leaderboard } = useQuery({
    queryKey: ['challenge-leaderboard', challengeId],
    queryFn: () => challengesApi.leaderboard(challengeId),
    enabled: !isNaN(challengeId),
  })

  const joinMutation = useMutation({
    mutationFn: () => challengesApi.join(challengeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['challenge', challengeId] })
      queryClient.invalidateQueries({ queryKey: ['challenge-leaderboard', challengeId] })
      queryClient.invalidateQueries({ queryKey: ['challenges'] })
    },
  })

  const leaveMutation = useMutation({
    mutationFn: () => challengesApi.leave(challengeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['challenge', challengeId] })
      queryClient.invalidateQueries({ queryKey: ['challenge-leaderboard', challengeId] })
      queryClient.invalidateQueries({ queryKey: ['challenges'] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!challenge) {
    return (
      <div className="text-center py-16">
        <p className="text-slate-400">Challenge not found.</p>
        <Link to="/challenges" className="text-violet-400 hover:text-violet-300 mt-2 inline-block">
          ← Back to Challenges
        </Link>
      </div>
    )
  }

  const unit = TYPE_UNITS[challenge.challenge_type]

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Link to="/challenges" className="text-sm text-violet-400 hover:text-violet-300 flex items-center gap-1">
        ← Back to Challenges
      </Link>

      {/* Header card */}
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{TYPE_ICONS[challenge.challenge_type]}</span>
            <div>
              <h1 className="text-xl font-bold text-white">{challenge.title}</h1>
              <p className="text-sm text-slate-400">{TYPE_LABELS[challenge.challenge_type]}</p>
            </div>
          </div>
          <span className={`text-xs font-semibold px-3 py-1 rounded-full ${
            challenge.status === 'active'
              ? 'bg-green-900/50 text-green-400'
              : challenge.status === 'completed'
              ? 'bg-violet-900/50 text-violet-400'
              : 'bg-slate-700 text-slate-400'
          }`}>
            {challenge.status}
          </span>
        </div>

        {challenge.description && (
          <p className="text-slate-300">{challenge.description}</p>
        )}

        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="bg-slate-700/50 rounded-xl p-3">
            <p className="text-lg font-bold text-white">{challenge.target_value}</p>
            <p className="text-xs text-slate-400">{unit} target</p>
          </div>
          <div className="bg-slate-700/50 rounded-xl p-3">
            <p className="text-lg font-bold text-white">{challenge.participant_count}</p>
            <p className="text-xs text-slate-400">participants</p>
          </div>
          <div className="bg-slate-700/50 rounded-xl p-3">
            <p className="text-sm font-bold text-white">{format(new Date(challenge.end_date), 'MMM d')}</p>
            <p className="text-xs text-slate-400">end date</p>
          </div>
        </div>

        <div className="text-xs text-slate-400">
          {format(new Date(challenge.start_date), 'MMM d, yyyy')} → {format(new Date(challenge.end_date), 'MMM d, yyyy')}
        </div>

        {challenge.status === 'active' && (
          <div>
            {challenge.is_joined ? (
              <button
                onClick={() => leaveMutation.mutate()}
                disabled={leaveMutation.isPending}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                {leaveMutation.isPending ? 'Leaving…' : 'Leave Challenge'}
              </button>
            ) : (
              <button
                onClick={() => joinMutation.mutate()}
                disabled={joinMutation.isPending}
                className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                {joinMutation.isPending ? 'Joining…' : 'Join Challenge'}
              </button>
            )}
          </div>
        )}
      </div>

      {/* My progress card */}
      {challenge.is_joined && challenge.my_progress !== null && (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5 space-y-3">
          <h2 className="font-semibold text-white">My Progress</h2>
          <div className="flex justify-between text-sm text-slate-300">
            <span>{challenge.my_progress} {unit}</span>
            <span>{challenge.target_value} {unit}</span>
          </div>
          <ProgressBar value={challenge.my_progress} max={challenge.target_value} />
          {challenge.my_rank && (
            <p className="text-sm text-violet-400 font-medium">
              Current rank: #{challenge.my_rank} of {challenge.participant_count}
            </p>
          )}
        </div>
      )}

      {/* Leaderboard */}
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-5 space-y-4">
        <h2 className="font-semibold text-white">Leaderboard</h2>
        {leaderboard && leaderboard.length > 0 ? (
          <div className="space-y-2">
            {leaderboard.map((entry: LeaderboardEntry, idx: number) => (
              <div
                key={entry.user_id}
                className="flex items-center gap-3 p-3 bg-slate-700/50 rounded-xl"
              >
                <div className="w-8 flex justify-center">
                  <RankBadge rank={idx + 1} />
                </div>
                <div className="w-8 h-8 rounded-full bg-violet-700 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                  {entry.username.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-white truncate">{entry.username}</p>
                  <p className="text-xs text-slate-400">
                    Joined {formatDistanceToNow(new Date(entry.joined_at), { addSuffix: true })}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-white">{entry.current_progress}</p>
                  <p className="text-xs text-slate-400">{unit}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-400 text-sm">No participants yet.</p>
        )}
      </div>
    </div>
  )
}
