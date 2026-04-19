import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Dumbbell, Loader2 } from 'lucide-react'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/authStore'

const registerSchema = z
  .object({
    full_name: z.string().min(1, 'Full name is required').max(200),
    username: z
      .string()
      .min(3, 'Username must be at least 3 characters')
      .max(50)
      .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers and underscores'),
    email: z.string().email('Invalid email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/\d/, 'Password must contain at least one number'),
    confirm_password: z.string(),
    date_of_birth: z.string().optional(),
    gender: z.enum(['male', 'female', 'other']).optional(),
    unit_system: z.enum(['metric', 'imperial']),
    terms: z.boolean().refine((v) => v === true, { message: 'You must accept the terms' }),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })

type RegisterFormData = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { unit_system: 'metric' },
  })

  const unitSystem = watch('unit_system')

  const onSubmit = async (data: RegisterFormData) => {
    setServerError(null)
    try {
      const payload = {
        username: data.username,
        email: data.email,
        password: data.password,
        full_name: data.full_name,
        date_of_birth: data.date_of_birth || undefined,
        gender: data.gender,
        unit_system: data.unit_system,
      }
      const response = await authApi.register(payload)
      setAuth(response.user, response.access_token, response.refresh_token)
      navigate('/dashboard')
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Registration failed. Please try again.'
      setServerError(msg)
    }
  }

  const inputClass = (hasError: boolean) =>
    `w-full px-3 py-2.5 rounded-lg border text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition`

  const inputStyle = (hasError: boolean) => ({
    background: 'var(--bg-tertiary)',
    borderColor: hasError ? '#ef4444' : '#475569',
  })

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8" style={{ background: 'var(--bg-primary)' }}>
      <div className="w-full max-w-lg">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Dumbbell className="w-8 h-8 text-blue-500" />
            <span className="text-2xl font-bold text-white">FitTracker</span>
          </div>
          <p style={{ color: 'var(--text-secondary)' }}>Start your fitness journey today</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl p-8 border border-slate-700" style={{ background: 'var(--bg-secondary)' }}>
          <h1 className="text-xl font-semibold text-white mb-6">Create your account</h1>

          {serverError && (
            <div className="mb-4 p-3 rounded-lg bg-red-900/40 border border-red-700 text-red-300 text-sm">
              {serverError}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Full Name</label>
              <input
                {...register('full_name')}
                type="text"
                placeholder="John Doe"
                className={inputClass(!!errors.full_name)}
                style={inputStyle(!!errors.full_name)}
              />
              {errors.full_name && <p className="mt-1 text-xs text-red-400">{errors.full_name.message}</p>}
            </div>

            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Username</label>
              <input
                {...register('username')}
                type="text"
                placeholder="strongjohn"
                autoComplete="username"
                className={inputClass(!!errors.username)}
                style={inputStyle(!!errors.username)}
              />
              {errors.username && <p className="mt-1 text-xs text-red-400">{errors.username.message}</p>}
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
              <input
                {...register('email')}
                type="email"
                placeholder="john@example.com"
                autoComplete="email"
                className={inputClass(!!errors.email)}
                style={inputStyle(!!errors.email)}
              />
              {errors.email && <p className="mt-1 text-xs text-red-400">{errors.email.message}</p>}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  autoComplete="new-password"
                  className={`${inputClass(!!errors.password)} pr-10`}
                  style={inputStyle(!!errors.password)}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="mt-1 text-xs text-red-400">{errors.password.message}</p>}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Confirm Password</label>
              <div className="relative">
                <input
                  {...register('confirm_password')}
                  type={showConfirm ? 'text' : 'password'}
                  placeholder="••••••••"
                  autoComplete="new-password"
                  className={`${inputClass(!!errors.confirm_password)} pr-10`}
                  style={inputStyle(!!errors.confirm_password)}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300"
                >
                  {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.confirm_password && (
                <p className="mt-1 text-xs text-red-400">{errors.confirm_password.message}</p>
              )}
            </div>

            {/* Date of Birth + Gender row */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Date of Birth</label>
                <input
                  {...register('date_of_birth')}
                  type="date"
                  className={inputClass(false)}
                  style={inputStyle(false)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Gender</label>
                <select
                  {...register('gender')}
                  className={inputClass(false)}
                  style={inputStyle(false)}
                >
                  <option value="">Select...</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            {/* Unit System */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Unit System</label>
              <div className="flex gap-2">
                {(['metric', 'imperial'] as const).map((unit) => (
                  <label
                    key={unit}
                    className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg border cursor-pointer transition"
                    style={{
                      background: unitSystem === unit ? '#1D4ED8' : 'var(--bg-tertiary)',
                      borderColor: unitSystem === unit ? '#3B82F6' : '#475569',
                      color: unitSystem === unit ? 'white' : '#94A3B8',
                    }}
                  >
                    <input {...register('unit_system')} type="radio" value={unit} className="hidden" />
                    {unit === 'metric' ? '🌍 Metric (kg/cm)' : '🇺🇸 Imperial (lb/in)'}
                  </label>
                ))}
              </div>
            </div>

            {/* Terms */}
            <div>
              <label className="flex items-start gap-2 text-sm text-slate-400 cursor-pointer">
                <input {...register('terms')} type="checkbox" className="mt-0.5 rounded" />
                <span>
                  I agree to the{' '}
                  <a href="#" className="text-blue-400 hover:text-blue-300">Terms of Service</a>
                  {' '}and{' '}
                  <a href="#" className="text-blue-400 hover:text-blue-300">Privacy Policy</a>
                </span>
              </label>
              {errors.terms && <p className="mt-1 text-xs text-red-400">{errors.terms.message}</p>}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-2.5 rounded-lg font-semibold text-white flex items-center justify-center gap-2 transition disabled:opacity-60 disabled:cursor-not-allowed mt-2"
              style={{ background: isSubmitting ? '#2563EB80' : 'var(--primary)' }}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-400">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
