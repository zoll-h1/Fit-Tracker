import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { socialApi } from '@/api/social'
import { useAuthStore } from '@/stores/authStore'

export default function PublicProfilePage() {
  const { id } = useParams<{ id: string }>()
  const userId = Number(id)
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const currentUser = useAuthStore(s => s.user)

  const { data: profile, isLoading } = useQuery({
    queryKey: ['public-profile', userId],
    queryFn: () => socialApi.publicProfile(userId),
    enabled: !!userId,
  })

  const followMutation = useMutation({
    mutationFn: () => socialApi.follow(userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['public-profile', userId] }),
  })

  const unfollowMutation = useMutation({
    mutationFn: () => socialApi.unfollow(userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['public-profile', userId] }),
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="text-center py-16">
        <p className="text-slate-400">User not found</p>
      </div>
    )
  }

  const isOwnProfile = currentUser?.id === userId

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="text-slate-400 hover:text-white text-sm transition-colors"
      >
        ← Back
      </button>

      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
        <div className="flex items-start gap-5">
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt={profile.username} className="w-20 h-20 rounded-full object-cover" />
          ) : (
            <div className="w-20 h-20 rounded-full bg-violet-600 flex items-center justify-center text-white text-3xl font-bold">
              {profile.username.charAt(0).toUpperCase()}
            </div>
          )}

          <div className="flex-1">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-2xl font-bold text-white">{profile.username}</h1>
                {profile.full_name && <p className="text-slate-400">{profile.full_name}</p>}
              </div>
              {!isOwnProfile && (
                <button
                  onClick={() => profile.is_following ? unfollowMutation.mutate() : followMutation.mutate()}
                  disabled={followMutation.isPending || unfollowMutation.isPending}
                  className={`px-5 py-2 rounded-lg font-medium text-sm transition-colors disabled:opacity-50 ${
                    profile.is_following
                      ? 'bg-slate-700 hover:bg-slate-600 text-white border border-slate-600'
                      : 'bg-violet-600 hover:bg-violet-700 text-white'
                  }`}
                >
                  {profile.is_following ? 'Following' : 'Follow'}
                </button>
              )}
            </div>

            <div className="flex gap-6 mt-4">
              <div className="text-center">
                <p className="text-xl font-bold text-white">{profile.followers_count}</p>
                <p className="text-xs text-slate-400">Followers</p>
              </div>
              <div className="text-center">
                <p className="text-xl font-bold text-white">{profile.following_count}</p>
                <p className="text-xs text-slate-400">Following</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
        <h2 className="font-semibold text-white mb-3">Recent Activity</h2>
        <p className="text-slate-400 text-sm">
          See {isOwnProfile ? 'your' : `${profile.username}'s`} activity on the{' '}
          <button onClick={() => navigate('/social')} className="text-violet-400 hover:underline">
            social feed
          </button>
          .
        </p>
      </div>
    </div>
  )
}
