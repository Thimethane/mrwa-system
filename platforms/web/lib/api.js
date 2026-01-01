// ============================================================================
// platforms/web/lib/api.js - API Client
// ============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIClient {
  async request(endpoint, options = {}) {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    
    const config = {
      ...options,
      headers: {
        ...(options.body && !(options.body instanceof FormData) && { 'Content-Type': 'application/json' }),
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
    }

    const response = await fetch(`${API_URL}${endpoint}`, config)
    
    if (response.status === 401) {
      const refreshed = await this.refreshToken()
      if (refreshed) {
        return this.request(endpoint, options)
      } else {
        if (typeof window !== 'undefined') {
          localStorage.clear()
          window.location.reload()
        }
        throw new Error('Authentication failed')
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || 'Request failed')
    }

    return response.json()
  }

  async refreshToken() {
    const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null
    if (!refreshToken) return false

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        return true
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
    }
    
    return false
  }

  async signup(email, password, name) {
    return this.request('/api/v1/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    })
  }

  async login(email, password) {
    return this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  }

  async logout() {
    return this.request('/api/v1/auth/logout', { method: 'POST' })
  }

  async getProfile() {
    return this.request('/api/v1/user/profile')
  }

  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    return this.request('/api/v1/upload', {
      method: 'POST',
      body: formData,
    })
  }

  async createExecutionWithFile(file, inputType, autoCorrect = true, maxRetries = 3) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('input_type', inputType)
    formData.append('auto_correct', autoCorrect)
    formData.append('max_retries', maxRetries)
    
    return this.request('/api/v1/executions/with-file', {
      method: 'POST',
      body: formData,
    })
  }

  async createExecutionFromUrl(url, inputType, autoCorrect = true, maxRetries = 3) {
    return this.request(
      `/api/v1/executions/from-url?url=${encodeURIComponent(url)}&input_type=${inputType}&auto_correct=${autoCorrect}&max_retries=${maxRetries}`,
      { method: 'POST' }
    )
  }

  async listExecutions(page = 1) {
    return this.request(`/api/v1/executions?page=${page}&limit=20`)
  }

  async getExecution(id) {
    return this.request(`/api/v1/executions/${id}`)
  }
}

export const apiClient = new APIClient()
