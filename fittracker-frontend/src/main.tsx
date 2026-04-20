import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './i18n'
import App from './App'
import { initSentry } from './lib/sentry'

initSentry()

const savedTheme = localStorage.getItem('fittracker-theme')
const theme = savedTheme ? JSON.parse(savedTheme)?.state?.theme : 'dark'
document.documentElement.classList.add(theme === 'light' ? 'light' : 'dark')

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
