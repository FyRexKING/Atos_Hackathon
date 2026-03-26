/**
 * Authentication Context
 * Manages user authentication state and provides auth functions
 */

import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('token')
      if (storedToken) {
        try {
          const response = await fetch('http://localhost:8000/api/auth/me', {
            headers: {
              'Authorization': `Bearer ${storedToken}`
            }
          })
          if (response.ok) {
            const userData = await response.json()
            setUser(userData)
            setToken(storedToken)
          } else {
            // Token invalid, remove it
            localStorage.removeItem('token')
            setToken(null)
          }
        } catch (error) {
          console.error('Auth check failed:', error)
          localStorage.removeItem('token')
          setToken(null)
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (email, password) => {
    try {
      const payload = new URLSearchParams()
      payload.append('username', email)
      payload.append('password', password)

      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: payload.toString()
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }

      const data = await response.json()
      const { access_token, user: userData } = data

      localStorage.setItem('token', access_token)
      setToken(access_token)
      setUser(userData)

      return userData
    } catch (error) {
      throw error
    }
  }

  const register = async (email, password, fullName) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, username: email, full_name: fullName, password })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
      }

      const data = await response.json()
      const { access_token, user: userData } = data

      localStorage.setItem('token', access_token)
      setToken(access_token)
      setUser(userData)

      return userData
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  const isAuthenticated = () => {
    return !!user && !!token
  }

  const hasRole = (role) => {
    return user && user.role === role
  }

  const hasPermission = (permission) => {
    if (!user) return false

    // Define permissions based on role
    const rolePermissions = {
      admin: ['create_ticket', 'view_all_tickets', 'approve_tickets', 'manage_users'],
      client: ['create_ticket', 'view_own_tickets']
    }

    return rolePermissions[user.role]?.includes(permission) || false
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated,
    hasRole,
    hasPermission
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}