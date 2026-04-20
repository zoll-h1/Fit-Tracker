import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { socialApi } from '@/api/social'
import type { FeedItem, Comment } from '@/api/social'
import { formatDistanceToNow } from 'date-fns'

function Avatar({ username, avatarUrl, size = 10 }: { username: string; avatarUrl: string | null; size?: number }) {
  if (avatarUrl) {
    return <img src={avatarUrl} alt={username} className={`w-${size} h-${size} rounded-full object-cover`} />
  }
  return (
    <div className={`w-${size} h-${size} rounded-full bg-violet-600 flex items-center justify-center text-white font-bold text-sm`}>
      {username.charAt(0).toUpperCase()}
    </div>
  )
}

function activityIcon(type: string) {
  if (type === 'workout') return '💪'
  if (type === 'achievement') return '🏆'
  if (type === 'pr') return '📈'
  return '🏋️'
}

function FeedItemCard({ item }: { item: FeedItem }) {
  const queryClient = useQueryClient()
  const [showComments, setShowComments] = useState(false)
  const [commentText, setCommentText] = useState('')

  const likeMutation = useMutation({
    mutationFn: () => socialApi.toggleLike(item.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['social-feed'] }),
  })

  const { data: comments } = useQuery({
    queryKey: ['feed-comments', item.id],
    queryFn: () => socialApi.getComments(item.id),
    enabled: showComments,
  })

  const addCommentMutation = useMutation({
    mutationFn: (content: string) => socialApi.addComment(item.id, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feed-comments', item.id] })
      queryClient.invalidateQueries({ queryKey: ['social-feed'] })
      setCommentText('')
    },
  })

  const handleAddComment = () => {
    if (commentText.trim()) {
      addCommentMutation.mutate(commentText.trim())
    }
  }

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3">
      <div className="flex items-center gap-3">
        <Avatar username={item.username} avatarUrl={item.avatar_url} size={10} />
        <div>
          <p className="font-semibold text-white">{item.username}</p>
          <p className="text-xs text-slate-400">
            {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
          </p>
        </div>
        <span className="ml-auto text-2xl">{activityIcon(item.activity_type)}</span>
      </div>

      <div>
        <p className="font-medium text-white">{item.title}</p>
        {item.body && <p className="text-sm text-slate-400 mt-1">{item.body}</p>}
      </div>

      <div className="flex items-center gap-4 pt-1">
        <button
          onClick={() => likeMutation.mutate()}
          className={`flex items-center gap-1.5 text-sm transition-colors ${item.is_liked_by_me ? 'text-red-400' : 'text-slate-400 hover:text-red-400'}`}
        >
          <span>{item.is_liked_by_me ? '❤️' : '🤍'}</span>
          <span>{item.likes_count}</span>
        </button>
        <button
          onClick={() => setShowComments(v => !v)}
          className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-violet-400 transition-colors"
        >
          <span>💬</span>
          <span>{item.comments_count}</span>
        </button>
      </div>

      {showComments && (
        <div className="border-t border-slate-700 pt-3 space-y-3">
          {comments && comments.length > 0 ? (
            comments.map((c: Comment) => (
              <div key={c.id} className="flex gap-2">
                <div className="w-7 h-7 rounded-full bg-violet-700 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                  {c.username.charAt(0).toUpperCase()}
                </div>
                <div className="bg-slate-700 rounded-lg px-3 py-2 flex-1">
                  <p className="text-xs font-semibold text-violet-400">{c.username}</p>
                  <p className="text-sm text-slate-200">{c.content}</p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-500">No comments yet.</p>
          )}
          <div className="flex gap-2">
            <input
              value={commentText}
              onChange={e => setCommentText(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAddComment()}
              placeholder="Add a comment..."
              className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-violet-500"
            />
            <button
              onClick={handleAddComment}
              disabled={!commentText.trim() || addCommentMutation.isPending}
              className="px-3 py-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Post
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function UserSearchDropdown() {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const queryClient = useQueryClient()

  const debounce = useCallback((value: string) => {
    setQuery(value)
    const timer = setTimeout(() => setDebouncedQuery(value), 400)
    return () => clearTimeout(timer)
  }, [])

  const { data: searchResults } = useQuery({
    queryKey: ['user-search', debouncedQuery],
    queryFn: () => socialApi.searchUsers(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
  })

  const followMutation = useMutation({
    mutationFn: (userId: number) => socialApi.follow(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['social-feed'] })
      queryClient.invalidateQueries({ queryKey: ['user-search', debouncedQuery] })
    },
  })

  return (
    <div className="relative">
      <input
        value={query}
        onChange={e => debounce(e.target.value)}
        placeholder="Search users..."
        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder-slate-400 focus:outline-none focus:border-violet-500"
      />
      {searchResults && searchResults.length > 0 && query.length >= 2 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-slate-800 border border-slate-700 rounded-xl shadow-xl z-10 overflow-hidden">
          {searchResults.map(user => (
            <div key={user.id} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-700 transition-colors">
              <Avatar username={user.username} avatarUrl={user.avatar_url} size={8} />
              <div className="flex-1 min-w-0">
                <p className="font-medium text-white truncate">{user.username}</p>
                {user.full_name && <p className="text-xs text-slate-400 truncate">{user.full_name}</p>}
              </div>
              <button
                onClick={() => followMutation.mutate(user.id)}
                className="px-3 py-1 bg-violet-600 hover:bg-violet-700 text-white text-xs font-medium rounded-lg transition-colors"
              >
                Follow
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function SocialFeedPage() {
  const { data: feed, isLoading } = useQuery({
    queryKey: ['social-feed'],
    queryFn: () => socialApi.feed(),
  })

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Social Feed</h1>
      </div>

      <UserSearchDropdown />

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : feed && feed.length > 0 ? (
        <div className="space-y-4">
          {feed.map(item => (
            <FeedItemCard key={item.id} item={item} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <p className="text-4xl mb-4">🤝</p>
          <h2 className="text-lg font-semibold text-white mb-2">Your feed is empty</h2>
          <p className="text-slate-400">Follow other users to see their activity here</p>
        </div>
      )}
    </div>
  )
}
