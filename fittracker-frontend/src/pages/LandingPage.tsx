import { useNavigate } from 'react-router-dom'
import { Dumbbell, Apple, Trophy, BarChart3, Users, Brain, ChevronDown } from 'lucide-react'

const features = [
  {
    icon: Dumbbell,
    title: 'Workout Logging',
    description: 'Log sets, reps, and weight for 50+ exercises. Track your strength progress over time.',
    color: 'text-blue-400',
    bg: 'bg-blue-900/30',
  },
  {
    icon: Apple,
    title: 'Nutrition Tracking',
    description: 'Track calories and macros with a database of 200+ foods. Hit your daily nutrition goals.',
    color: 'text-green-400',
    bg: 'bg-green-900/30',
  },
  {
    icon: Trophy,
    title: 'Gamification & XP',
    description: 'Earn XP, level up, and unlock 40 achievements. Stay motivated with streaks and challenges.',
    color: 'text-yellow-400',
    bg: 'bg-yellow-900/30',
  },
  {
    icon: BarChart3,
    title: 'Advanced Analytics',
    description: 'Visualize your progress with charts, PRs, volume trends, and body metric tracking.',
    color: 'text-purple-400',
    bg: 'bg-purple-900/30',
  },
  {
    icon: Users,
    title: 'Social Features',
    description: 'Follow friends, share workouts, and compete in community challenges.',
    color: 'text-pink-400',
    bg: 'bg-pink-900/30',
  },
  {
    icon: Brain,
    title: 'AI Trainer',
    description: 'Get personalized 12-week training programs and real-time coaching from your AI trainer.',
    color: 'text-cyan-400',
    bg: 'bg-cyan-900/30',
  },
]

const stats = [
  { value: '50+', label: 'Exercises' },
  { value: '200+', label: 'Foods' },
  { value: '40', label: 'Achievements' },
  { value: '12-Week', label: 'Programs' },
]

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen" style={{ background: '#020617' }}>
      {/* Navbar */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <Dumbbell className="w-7 h-7 text-violet-500" />
          <span className="text-white font-bold text-xl">FitTracker</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/login')}
            className="px-4 py-2 text-sm text-slate-300 hover:text-white transition"
          >
            Login
          </button>
          <button
            onClick={() => navigate('/register')}
            className="px-4 py-2 text-sm font-semibold text-white rounded-lg transition hover:opacity-90"
            style={{ background: '#7c3aed' }}
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center text-center px-6 pt-20 pb-24 max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-violet-800 bg-violet-950/50 text-violet-300 text-sm font-medium mb-8">
          <Trophy className="w-4 h-4" />
          12-Week Fitness Programs Available
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold text-white leading-tight mb-6">
          Track Your{' '}
          <span style={{ color: '#7c3aed' }}>Fitness</span>{' '}
          Journey
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl mb-10">
          Log workouts, track nutrition, earn achievements, and crush your goals with FitTracker — your all-in-one fitness companion.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4">
          <button
            onClick={() => navigate('/register')}
            className="px-8 py-3.5 text-base font-semibold text-white rounded-xl transition hover:opacity-90 shadow-lg"
            style={{ background: '#7c3aed' }}
          >
            Get Started Free
          </button>
          <a
            href="#features"
            className="flex items-center gap-2 px-8 py-3.5 text-base font-semibold text-slate-300 rounded-xl border border-slate-700 hover:border-slate-500 hover:text-white transition"
          >
            See Features <ChevronDown className="w-4 h-4" />
          </a>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="border-y border-slate-800 py-8 px-6">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {stats.map((s) => (
            <div key={s.label}>
              <div className="text-3xl font-extrabold text-white mb-1">{s.value}</div>
              <div className="text-slate-400 text-sm">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-6 max-w-7xl mx-auto">
        <div className="text-center mb-14">
          <h2 className="text-4xl font-bold text-white mb-4">Everything You Need</h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            FitTracker combines workout logging, nutrition, analytics, and social features in one powerful app.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="rounded-2xl p-6 border border-slate-800 hover:border-violet-700 transition-colors"
              style={{ background: '#0f172a' }}
            >
              <div className={`inline-flex p-3 rounded-xl ${f.bg} mb-4`}>
                <f.icon className={`w-6 h-6 ${f.color}`} />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{f.title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div
          className="max-w-3xl mx-auto rounded-3xl p-12 text-center border border-violet-800"
          style={{ background: 'linear-gradient(135deg, #1e0a3c 0%, #0f172a 100%)' }}
        >
          <h2 className="text-4xl font-bold text-white mb-4">Ready to Start?</h2>
          <p className="text-slate-400 text-lg mb-8">
            Join FitTracker today and take control of your fitness journey.
          </p>
          <button
            onClick={() => navigate('/register')}
            className="px-10 py-4 text-base font-semibold text-white rounded-xl transition hover:opacity-90 shadow-lg"
            style={{ background: '#7c3aed' }}
          >
            Create Free Account
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 px-6 text-center text-slate-500 text-sm">
        © {new Date().getFullYear()} FitTracker. Built with FastAPI + React.
      </footer>
    </div>
  )
}
