/**
 * Admin Dashboard Page Component - Modern Professional Design
 * Administrative interface with metrics, filters, and ticket management
 */

import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import TicketDetails from '../components/TicketDetails'
import ApprovalPanel from '../components/ApprovalPanel'
import RecommendationPanel from '../components/RecommendationPanel'

const AdminDashboard = () => {
  const { user, token } = useAuth()
  const [stats, setStats] = useState({
    totalTickets: 0,
    pendingTickets: 0,
    autoResolved: 0,
    assignedTickets: 0,
    rejectedTickets: 0,
    resolvedTickets: 0
  })
  const [tickets, setTickets] = useState([])
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filterStatus, setFilterStatus] = useState('pending')

  useEffect(() => {
    if (token) {
      fetchDashboardData()
    } else {
      setLoading(false)
      setError('Not authenticated. Please log in first.')
    }
  }, [token])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError('')

      const ticketsResponse = await fetch('http://localhost:8000/api/admin/tickets', {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!ticketsResponse.ok) {
        throw new Error(`Tickets fetch failed: ${ticketsResponse.statusText}`)
      }

      const ticketsData = await ticketsResponse.json()
      const allTickets = ticketsData.tickets || []
      setTickets(allTickets)

      setStats({
        totalTickets: allTickets.length,
        pendingTickets: allTickets.filter(t => t.status === 'pending_review').length || 0,
        autoResolved: allTickets.filter(t => t.decision === 'auto_resolve' && t.status === 'resolved').length || 0,
        assignedTickets: allTickets.filter(t => t.status === 'assigned').length || 0,
        rejectedTickets: allTickets.filter(t => t.status === 'rejected').length || 0,
        resolvedTickets: allTickets.filter(t => t.status === 'resolved').length || 0
      })
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      setError(error.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleActionComplete = () => {
    fetchDashboardData()
  }

  // Filter tickets based on selected filter
  const getFilteredTickets = () => {
    switch(filterStatus) {
      case 'pending':
        return tickets.filter(t => t.status === 'pending_review')
      case 'auto_resolved':
        return tickets.filter(t => t.decision === 'auto_resolve' && t.status === 'resolved')
      case 'assigned':
        return tickets.filter(t => t.status === 'assigned')
      case 'resolved':
        return tickets.filter(t => t.status === 'resolved')
      default:
        return tickets
    }
  }

  const filteredTickets = getFilteredTickets()

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center pt-24">
        <div className="text-center">
          <div className="inline-block">
            <div className="w-12 h-12 border-4 border-purple-400 border-t-purple-600 rounded-full animate-spin"></div>
          </div>
          <p className="text-white mt-4 text-lg font-medium">Loading Admin Dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-purple-900 flex items-center justify-center p-6 pt-24">
        <div className="bg-white rounded-lg p-6 max-w-md text-center card-shadow">
          <h2 className="text-xl font-bold text-red-800 mb-2">⚠️ Error</h2>
          <p className="text-red-700 mb-4">{error}</p>
          <button 
            onClick={fetchDashboardData}
            className="btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-24 pb-12">
      {/* Header */}
      <div className="px-6 py-12 text-center">
        <h1 className="text-5xl font-bold text-white mb-2 animate-fade-in-down">
          <span className="text-6xl mr-3">⚙️</span>Admin Dashboard
        </h1>
        <p className="text-purple-200 text-lg animate-fade-in-up">Monitor and manage support tickets</p>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-6 mb-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
          {/* Total */}
          <div className="glass-dark rounded-xl p-6 text-center transform hover:scale-105 transition-transform">
            <div className="text-3xl font-bold text-white mb-2">{stats.totalTickets}</div>
            <p className="text-purple-200 font-semibold">Total</p>
            <div className="text-2xl mt-2">📊</div>
          </div>

          {/* Pending */}
          <div className="glass-dark rounded-xl p-6 text-center transform hover:scale-105 transition-transform">
            <div className="text-3xl font-bold text-yellow-400 mb-2">{stats.pendingTickets}</div>
            <p className="text-purple-200 font-semibold">Pending</p>
            <div className="text-2xl mt-2">⏳</div>
          </div>

          {/* Auto-Resolved */}
          <div className="glass-dark rounded-xl p-6 text-center transform hover:scale-105 transition-transform">
            <div className="text-3xl font-bold text-green-400 mb-2">{stats.autoResolved}</div>
            <p className="text-purple-200 font-semibold">Auto-Resolved</p>
            <div className="text-2xl mt-2">✨</div>
          </div>

          {/* Assigned */}
          <div className="glass-dark rounded-xl p-6 text-center transform hover:scale-105 transition-transform">
            <div className="text-3xl font-bold text-blue-400 mb-2">{stats.assignedTickets}</div>
            <p className="text-purple-200 font-semibold">Assigned</p>
            <div className="text-2xl mt-2">👤</div>
          </div>

          {/* Resolved */}
          <div className="glass-dark rounded-xl p-6 text-center transform hover:scale-105 transition-transform">
            <div className="text-3xl font-bold text-cyan-400 mb-2">{stats.resolvedTickets}</div>
            <p className="text-purple-200 font-semibold">Resolved</p>
            <div className="text-2xl mt-2">✅</div>
          </div>

          {/* Rejected */}
          <div className="glass-dark rounded-xl p-6 text-center transform hover:scale-105 transition-transform">
            <div className="text-3xl font-bold text-red-400 mb-2">{stats.rejectedTickets}</div>
            <p className="text-purple-200 font-semibold">Rejected</p>
            <div className="text-2xl mt-2">❌</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Ticket List */}
          <div className="glass-effect rounded-xl p-1">
            <div className="bg-white rounded-lg p-6 h-screen overflow-hidden flex flex-col">
              <h2 className="text-xl font-bold text-gray-800 mb-4">🎫 Tickets</h2>
              
              {/* Filter Tabs */}
              <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
                {[
                  { key: 'pending', label: 'Pending'},
                  { key: 'auto_resolved', label: 'Auto-Resolved'},
                  { key: 'assigned', label: 'Assigned'},
                  { key: 'resolved', label: 'Resolved'}
                ].map(filter => (
                  <button
                    key={filter.key}
                    onClick={() => setFilterStatus(filter.key)}
                    className={`px-3 py-1 rounded-full text-sm font-semibold transition-all whitespace-nowrap ${
                      filterStatus === filter.key 
                        ? 'bg-gradient-primary text-white' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>

              {/* Ticket List */}
              <div className="space-y-2 overflow-y-auto flex-1">
                {filteredTickets.length > 0 ? (
                  filteredTickets.map((ticket) => (
                    <button
                      key={ticket.id}
                      onClick={() => setSelectedTicket(ticket)}
                      className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                        selectedTicket?.id === ticket.id 
                          ? 'border-purple-500 bg-purple-50' 
                          : 'border-gray-200 bg-gray-50 hover:border-purple-300'
                      }`}
                    >
                      <div className="font-semibold text-gray-800 truncate text-sm">
                        #{ticket.id}: {ticket.title}
                      </div>
                      <div className="text-xs text-gray-600 mt-1 space-y-1">
                        {ticket.created_by && (
                          <div className="text-purple-700 font-medium">
                            {ticket.created_by.full_name}
                          </div>
                        )}
                        <div className="flex gap-2 items-center">
                          <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${
                            ticket.priority === 'high' ? 'bg-red-100 text-red-800' 
                            : ticket.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' 
                            : 'bg-green-100 text-green-800'
                          }`}>
                            {ticket.priority}
                          </span>
                          <span className="text-gray-600 text-xs">
                            {(ticket.confidence_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="text-gray-400 text-center py-8">No tickets found</div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Details & Actions */}
          <div className="lg:col-span-2 space-y-6">
            {selectedTicket ? (
              <>
                {/* Details */}
                <div className="glass-effect rounded-xl p-1">
                  <div className="bg-white rounded-lg p-6">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">📋 Details</h2>
                    <TicketDetails ticket={selectedTicket} />
                  </div>
                </div>

                {/* AI Recommendations Panel */}
                <RecommendationPanel ticket={selectedTicket} onActionComplete={handleActionComplete} />

                {/* Legacy Approval Panel (for backwards compatibility) */}
                <ApprovalPanel ticket={selectedTicket} onActionComplete={handleActionComplete} />
              </>
            ) : (
              <div className="glass-effect rounded-xl p-1">
                <div className="bg-white rounded-lg p-6 text-center py-12">
                  <div className="text-6xl mb-4">👈</div>
                  <p className="text-gray-500 font-semibold">Select a ticket to view details and take action</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard