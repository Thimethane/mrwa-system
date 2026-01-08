// ============================================================================
// platforms/web/pages/index.js - Main Page
// ============================================================================

import { useEffect, useState } from 'react'
import { useAuth } from '../lib/AuthContext'
import Dashboard from '../components/Dashboard'
import AuthForm from '../components/AuthForm'
import Head from 'next/head'

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

  return (
    <>
      <Head>
        <title>MRWA Dashboard</title>
      </Head>
      {user ? <Dashboard /> : <AuthForm />}
    </>
  )
}
