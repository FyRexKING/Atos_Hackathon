/**
 * QueueList Component
 * Displays list of pending tickets awaiting human review (for admins)
 * or user's own tickets (for clients)
 */

import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { getPendingTickets, getMyTickets } from '../api/ticketApi'

const QueueList = ({ onSelectTicket, refreshTrigger, showAllPending = false }) => {
  const { user, hasRole } = useAuth()
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedId, setSelectedId] = useState(null)

  /**
   * Load tickets from backend based on user role
   */
  const loadTickets = async () => {
    setLoading(true)
    setError('')

    let result
    if (hasRole('client') && !showAllPending) {
      // Clients see their own tickets
      result = await getMyTickets()
    } else {
      // Admins see pending tickets
      result = await getPendingTickets()
    }

    setLoading(false)

    if (result.success) {
      setTickets(result.data)
    } else {
      setError(result.error)
    }
  }

  // Load tickets on component mount and when refreshTrigger changes
  useEffect(() => {
    loadTickets()
  }, [refreshTrigger, user])

  /**
   * Handle ticket selection
   */
  const handleSelectTicket = (ticket) => {
    setSelectedId(ticket.id)
    onSelectTicket(ticket)
  }

  /**
   * Get priority badge color
   */
  const getPriorityColor = (priority) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-green-100 text-green-800'
    }
  }

  /**
   * Get confidence badge color
   */
  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800'
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  /**
   * Get status badge color
   */
  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved':
        return 'bg-green-100 text-green-800'
      case 'pending_review':
        return 'bg-orange-100 text-orange-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const queueTitle = hasRole('client') && !showAllPending ? 'My Tickets' : 'Human Review Queue'
  const emptyMessage = hasRole('client') && !showAllPending ? 'You have no tickets yet' : 'No pending tickets'

  if (loading && tickets.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">{queueTitle}</h2>
        <div className="flex justify-center items-center py-8">
          <svg className="animate-spin h-6 w-6 text-blue-600" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">{queueTitle}</h2>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">{queueTitle}</h2>
        <button
          onClick={loadTickets}
          className="text-blue-600 hover:text-blue-800 text-sm font-semibold transition"
        >
          Refresh
        </button>
      </div>

      {/* Count Badge */}
      <div className="mb-4 inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
        {tickets.length} {hasRole('client') && !showAllPending ? 'tickets' : 'pending'}
      </div>

      {/* Tickets List */}
      {tickets.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <svg className="w-12 h-12 mx-auto mb-3 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p>{emptyMessage}</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {tickets.map((ticket) => (
            <button
              key={ticket.id}
              onClick={() => handleSelectTicket(ticket)}
              className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                selectedId === ticket.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 bg-gray-50 hover:border-blue-300 hover:bg-blue-25'
              }`}
            >
              {/* Ticket Title */}
              <div className="flex justify-between items-start mb-2">
                <p className="font-semibold text-gray-800 flex-1">#{ticket.id}: {ticket.title}</p>
                <div className="flex gap-1 ml-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold whitespace-nowrap ${getPriorityColor(ticket.priority)}`}>
                    {ticket.priority}
                  </span>
                  {hasRole('client') && !showAllPending && (
                    <span className={`px-2 py-1 rounded text-xs font-semibold whitespace-nowrap ${getStatusColor(ticket.status)}`}>
                      {ticket.status.replace('_', ' ')}
                    </span>
                  )}
                </div>
              </div>

              {/* Category and Confidence */}
              <div className="flex gap-2 items-center text-sm">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                  {ticket.category}
                </span>
                {(!hasRole('client') || showAllPending) && (
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getConfidenceColor(ticket.confidence_score)}`}>
                    Confidence: {(ticket.confidence_score * 100).toFixed(0)}%
                  </span>
                )}
              </div>

              {/* Created timestamp */}
              <p className="text-xs text-gray-500 mt-2">
                {new Date(ticket.created_at).toLocaleString()}
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default QueueList
