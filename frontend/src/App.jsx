/**
 * Main App Component - Modern Design
 * Entry point with professional navigation and role-based routing
 */

import React, { useState } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './components/Login'
import Register from './components/Register'
import Dashboard from './pages/Dashboard'
import AdminDashboard from './pages/AdminDashboard'

const AppContent = () => {
  const { isAuthenticated, user, loading, logout } = useAuth()
  const [showRegister, setShowRegister] = useState(false)

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block">
            <div className="w-12 h-12 border-4 border-purple-400 border-t-purple-600 rounded-full animate-spin"></div>
          </div>
          <p className="text-white mt-4 text-lg font-medium">Initializing System...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated()) {
    return showRegister ? (
      <Register onSwitchToLogin={() => setShowRegister(false)} />
    ) : (
      <Login onSwitchToRegister={() => setShowRegister(true)} />
    )
  }

  // Role-based dashboard rendering
  const renderDashboard = () => {
    switch (user.role) {
      case 'admin':
        return <AdminDashboard />
      case 'client':
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="relative min-h-screen">
      {/* Logout button - Modern Floating Header */}
      <div className="fixed top-0 right-0 z-50 p-6">
        <div className="flex items-center space-x-6 bg-white/80 backdrop-blur-md rounded-full px-6 py-3 shadow-lg">
          <div className="text-center">
            <p className="text-sm font-semibold text-gray-800">{user.full_name}</p>
            <p className="text-xs text-gray-500 capitalize">{user.role}</p>
          </div>
          <div className="w-px h-6 bg-gray-300"></div>
          <button
            onClick={logout}
            className="px-5 py-2 bg-gradient-secondary text-white rounded-full font-semibold text-sm hover:shadow-lg transition-smooth hover:scale-105 active:scale-95"
          >
            Logout
          </button>
        </div>
      </div>

      {renderDashboard()}
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
