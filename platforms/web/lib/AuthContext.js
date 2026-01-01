// ============================================================================
// platforms/web/lib/AuthContext.js - Authentication Context
// ============================================================================

import React, { createContext, useState, useEffect, useContext } from 'react'
import { apiClient } from './api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const profile = await apiClient.getProfile()
        setUser(profile)
      } catch (error) {
        console.error('Auth check failed:', error)
        localStorage.clear()
      }
    }
    setLoading(false)
  }

  const login = async (email, password) => {
    const data = await apiClient.login(email, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    setUser(data.user)
    return data
  }

  const signup = async (email, password, name) => {
    const data = await apiClient.signup(email, password, name)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    setUser(data.user)
    return data
  }

  const logout = async () => {
    await apiClient.logout()
    localStorage.clear()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}
