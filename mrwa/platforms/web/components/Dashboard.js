// ============================================================================
// platforms/web/components/Dashboard.js - Main Dashboard
// ============================================================================


import React, { useState, useEffect, useRef } from 'react';
import { Upload, Play, CheckCircle, XCircle, AlertCircle, Loader, FileText, Code, Link2, Video, User, LogOut, Menu, X } from 'lucide-react';

// API Configuration
const API_URL = 'http://localhost:8000';

// Authentication Context
const AuthContext = React.createContext(null);

const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

// API Client
class APIClient {
  static async request(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
    };

    const response = await fetch(`${API_URL}${endpoint}`, config);
    
    if (response.status === 401) {
      // Try to refresh token
      const refreshed = await this.refreshToken();
      if (refreshed) {
        // Retry request
        return this.request(endpoint, options);
      } else {
        // Logout user
        localStorage.clear();
        window.location.reload();
      }
    }

    return response;
  }

  static async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }
    
    return false;
  }

  static async signup(email, password, name) {
    const response = await this.request('/api/v1/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
    return response.json();
  }

  static async login(email, password) {
    const response = await this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return response.json();
  }

  static async logout() {
    await this.request('/api/v1/auth/logout', { method: 'POST' });
    localStorage.clear();
  }

  static async getProfile() {
    const response = await this.request('/api/v1/user/profile');
    return response.json();
  }

  static async createExecution(data) {
    const response = await this.request('/api/v1/executions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response.json();
  }

  static async listExecutions(page = 1) {
    const response = await this.request(`/api/v1/executions?page=${page}&limit=20`);
    return response.json();
  }

  static async getExecution(id) {
    const response = await this.request(`/api/v1/executions/${id}`);
    return response.json();
  }
}

// Auth Provider Component
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const profile = await APIClient.getProfile();
        setUser(profile);
      } catch (error) {
        localStorage.clear();
      }
    }
    setLoading(false);
  };

  const login = async (email, password) => {
    const data = await APIClient.login(email, password);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    setUser(data.user);
    return data;
  };

  const signup = async (email, password, name) => {
    const data = await APIClient.signup(email, password, name);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    await APIClient.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Login/Signup Component
const AuthForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, signup } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await signup(email, password, name);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">MRWA</h1>
          <p className="text-gray-400">Marathon Research & Workflow Agent</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-8 border border-gray-700">
          <h2 className="text-2xl font-bold text-white mb-6">
            {isLogin ? 'Sign In' : 'Create Account'}
          </h2>

          {error && (
            <div className="bg-red-900/30 border border-red-600 rounded-lg p-3 mb-4 text-red-200 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                  required={!isLogin}
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                required
                minLength={8}
              />
              {!isLogin && (
                <p className="text-xs text-gray-400 mt-1">
                  At least 8 characters with uppercase, lowercase, and number
                </p>
              )}
            </div>

            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 rounded-lg font-medium"
            >
              {loading ? 'Please wait...' : isLogin ? 'Sign In' : 'Create Account'}
            </button>
          </div>

          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
              }}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('upload');
  const [inputType, setInputType] = useState(null);
  const [inputValue, setInputValue] = useState('');
  const [currentExecution, setCurrentExecution] = useState(null);
  const [executionHistory, setExecutionHistory] = useState([]);
  const [showMenu, setShowMenu] = useState(false);

  useEffect(() => {
    loadExecutionHistory();
  }, []);

  const loadExecutionHistory = async () => {
    try {
      const data = await APIClient.listExecutions();
      setExecutionHistory(data.executions);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const handleFileUpload = async (e, type) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setInputType(type);
    setInputValue(file.name);
  };

  const handleUrlInput = (type) => {
    if (!inputValue.trim()) return;
    setInputType(type);
  };

  const startExecution = async () => {
    if (!inputType) return;

    try {
      const execution = await APIClient.createExecution({
        input_type: inputType,
        input_value: inputValue,
        auto_correct: true,
        max_retries: 3
      });

      setCurrentExecution(execution);
      setActiveTab('execution');
      
      // Poll for updates
      pollExecutionStatus(execution.execution_id);
    } catch (error) {
      console.error('Execution failed:', error);
    }
  };

  const pollExecutionStatus = async (executionId) => {
    const interval = setInterval(async () => {
      try {
        const data = await APIClient.getExecution(executionId);
        setCurrentExecution(data);
        
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(interval);
          setActiveTab('results');
          loadExecutionHistory();
        }
      } catch (error) {
        clearInterval(interval);
      }
    }, 2000);
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'running': return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      default: return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">MRWA</h1>
            <p className="text-sm text-gray-400">Autonomous Research Agent</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium">{user?.name || user?.email}</p>
              <p className="text-xs text-gray-400">
                {user?.statistics?.total_executions || 0} executions
              </p>
            </div>
            <button
              onClick={logout}
              className="flex items-center space-x-2 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-700">
          {['upload', 'execution', 'results', 'history'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-4 capitalize ${
                activeTab === tab
                  ? 'border-b-2 border-blue-500 text-blue-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              {/* PDF Upload */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <FileText className="w-8 h-8 mb-3 text-blue-400" />
                <h3 className="text-lg font-semibold mb-2">PDF Document</h3>
                <p className="text-sm text-gray-400 mb-4">Upload research papers or documents</p>
                <label className="block">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => handleFileUpload(e, 'pdf')}
                    className="hidden"
                  />
                  <div className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded text-center">
                    Select PDF
                  </div>
                </label>
              </div>

              {/* Code Upload */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <Code className="w-8 h-8 mb-3 text-green-400" />
                <h3 className="text-lg font-semibold mb-2">Code Files</h3>
                <p className="text-sm text-gray-400 mb-4">Analyze source code repositories</p>
                <label className="block">
                  <input
                    type="file"
                    accept=".py,.js,.java,.cpp,.ts"
                    onChange={(e) => handleFileUpload(e, 'code')}
                    className="hidden"
                  />
                  <div className="cursor-pointer bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded text-center">
                    Select Code
                  </div>
                </label>
              </div>

              {/* URL Input */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <Link2 className="w-8 h-8 mb-3 text-purple-400" />
                <h3 className="text-lg font-semibold mb-2">Web URL</h3>
                <p className="text-sm text-gray-400 mb-4">Scrape and analyze websites</p>
                <input
                  type="text"
                  placeholder="https://example.com"
                  value={inputType === 'url' ? inputValue : ''}
                  onChange={(e) => setInputValue(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 mb-2"
                />
                <button
                  onClick={() => handleUrlInput('url')}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded"
                >
                  Add URL
                </button>
              </div>

              {/* YouTube Input */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <Video className="w-8 h-8 mb-3 text-red-400" />
                <h3 className="text-lg font-semibold mb-2">YouTube Video</h3>
                <p className="text-sm text-gray-400 mb-4">Process video transcripts</p>
                <input
                  type="text"
                  placeholder="https://youtube.com/watch?v=..."
                  value={inputType === 'youtube' ? inputValue : ''}
                  onChange={(e) => setInputValue(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 mb-2"
                />
                <button
                  onClick={() => handleUrlInput('youtube')}
                  className="w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded"
                >
                  Add Video
                </button>
              </div>
            </div>

            {inputType && (
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Ready to process:</p>
                    <p className="text-lg font-semibold">{inputValue}</p>
                  </div>
                  <button
                    onClick={startExecution}
                    className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg"
                  >
                    <Play className="w-5 h-5" />
                    <span>Start Execution</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Execution Tab */}
        {activeTab === 'execution' && currentExecution && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h2 className="text-xl font-bold mb-4">Execution Plan</h2>
              <div className="space-y-3">
                {currentExecution.plan?.map((step, idx) => (
                  <div
                    key={step.id}
                    className={`flex items-center space-x-3 p-3 rounded ${
                      idx === currentExecution.current_step 
                        ? 'bg-blue-900/30 border border-blue-700' 
                        : 'bg-gray-700'
                    }`}
                  >
                    {getStatusIcon(step.status)}
                    <div className="flex-1">
                      <p className="font-medium">{step.name}</p>
                      <p className="text-xs text-gray-400">
                        Step {idx + 1} of {currentExecution.plan.length}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h2 className="text-xl font-bold mb-4">Status</h2>
              <div className="flex items-center space-x-3">
                {getStatusIcon(currentExecution.status)}
                <span className="text-lg capitalize">{currentExecution.status}</span>
              </div>
            </div>
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && currentExecution?.status === 'completed' && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold mb-4">Execution Complete</h2>
            <div className="space-y-4">
              <div className="flex items-center space-x-3 text-green-400">
                <CheckCircle className="w-6 h-6" />
                <span className="text-lg">All steps completed successfully</span>
              </div>
              <div className="bg-gray-700 rounded p-4">
                <p className="text-sm text-gray-300">
                  Processed {currentExecution.input_type} input with {currentExecution.plan?.length || 0} steps
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  Execution ID: {currentExecution.id}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold">Execution History</h2>
            {executionHistory.length === 0 ? (
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 text-center text-gray-400">
                No executions yet. Start one from the Upload tab!
              </div>
            ) : (
              <div className="space-y-3">
                {executionHistory.map((exec) => (
                  <div key={exec.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{exec.input_value.substring(0, 50)}...</p>
                        <p className="text-sm text-gray-400">
                          {exec.input_type} • {new Date(exec.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(exec.status)}
                        <span className="text-sm capitalize">{exec.status}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <Loader className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  return user ? <Dashboard /> : <AuthForm />;
};

// Root Component with Provider
export default function Root() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}
