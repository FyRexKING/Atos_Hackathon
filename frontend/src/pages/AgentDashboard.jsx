/**
 * Agent Dashboard Page Component
 * Support agent interface for handling tickets and approvals
 */

import React, { useState, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import TicketForm from '../components/TicketForm'
import TicketResult from '../components/TicketResult'
import QueueList from '../components/QueueList'
import ApprovalPanel from '../components/ApprovalPanel'

const AgentDashboard = () => {
  const { user, token } = useAuth()
  const [currentTicket, setCurrentTicket] = useState(null)
  const [selectedQueueTicket, setSelectedQueueTicket] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  /**
   * Handle ticket submission from form
   */
  const handleTicketSubmit = (result) => {
    setCurrentTicket(result)
    // Trigger queue refresh
    setRefreshKey((prev) => prev + 1)
  }

  /**
   * Handle queue ticket selection
   */
  const handleSelectQueueTicket = (ticket) => {
    setSelectedQueueTicket(ticket)
  }

  /**
   * Handle approval/rejection action completion
   */
  const handleActionComplete = useCallback(() => {
    setSelectedQueueTicket(null)
    // Trigger queue refresh to remove approved/rejected ticket
    setRefreshKey((prev) => prev + 1)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-600 to-green-800 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="text-white">
          <h1 className="text-4xl font-bold mb-2">Agent Dashboard</h1>
          <p className="text-green-100">Support ticket management and approval workflows</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Form */}
        <div className="lg:col-span-1">
          <TicketForm onSubmit={handleTicketSubmit} />
        </div>

        {/* Center Column - Results and Queue */}
        <div className="lg:col-span-1 space-y-6">
          <TicketResult ticket={currentTicket} />
          <QueueList
            onSelectTicket={handleSelectQueueTicket}
            refreshTrigger={refreshKey}
            showAllPending={true} // Agents can see all pending tickets
          />
        </div>

        {/* Right Column - Approval Panel */}
        <div className="lg:col-span-1">
          <ApprovalPanel ticket={selectedQueueTicket} onActionComplete={handleActionComplete} />
        </div>
      </div>

      {/* Agent Stats */}
      <div className="max-w-7xl mx-auto mt-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Agent Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">0</div>
              <div className="text-gray-600">Tickets Handled Today</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">0</div>
              <div className="text-gray-600">Approved This Week</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">0</div>
              <div className="text-gray-600">Pending Review</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto mt-12 text-center text-green-100 text-sm">
        <p>Agent Panel | Backend API: http://localhost:8000 | Welcome, {user.full_name}</p>
      </div>
    </div>
  )
}

export default AgentDashboard