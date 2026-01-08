// ============================================================================
// platforms/web/pages/index.js - Main Page
// ============================================================================

import { useAuth } from '../lib/AuthContext'
import Dashboard from '../components/Dashboard'
import AuthForm from '../components/AuthForm'
import { useEffect, useState } from 'react'

export default function Home() {
  const { user, loading } = useAuth()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted || loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  return user ? <Dashboard /> : <AuthForm />
}
