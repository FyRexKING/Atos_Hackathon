/**
 * Dashboard Page Component - Modern Design
 * Client dashboard with ticket form and queue management
 */

import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import TicketForm from '../components/TicketForm'
import QueueList from '../components/QueueList'
import ClientTicketDetail from '../components/ClientTicketDetail'

const Dashboard = () => {
  const { user } = useAuth()
  const [refreshKey, setRefreshKey] = useState(0)
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [ticketRefreshKey, setTicketRefreshKey] = useState(0)

  /**
   * Handle ticket submission from form
   */
  const handleTicketSubmit = (result) => {
    // Trigger queue refresh
    setRefreshKey((prev) => prev + 1)
  }

  /**
   * Handle queue ticket selection
   */
  const handleSelectQueueTicket = (ticket) => {
    setSelectedTicket(ticket)
  }

  /**
   * Refresh selected ticket after admin action (for clients viewing)
   * Called when ticket is updated (rejected, assigned, approved, etc.)
   */
  const handleTicketUpdated = (updatedTicket) => {
    setSelectedTicket(updatedTicket)
    setTicketRefreshKey((prev) => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700 pt-24">
      {/* Hero Header */}
      <div className="px-6 py-12 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 animate-fade-in-down">
            <span className="text-6xl mr-3">🎫</span>Support Portal
          </h1>
          <p className="text-purple-100 text-xl mb-2 animate-fade-in-up">
            Welcome back, <span className="font-bold text-white">{user.full_name}</span>!
          </p>
          <p className="text-purple-100 text-lg animate-fade-in-up animation-delay-2000">
            Create a ticket and let our AI assist you instantly
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Form */}
          <div className="animate-slide-in-right">
            <div className="glass-effect rounded-xl p-1 mb-6">
              <div className="bg-white rounded-lg p-6 lg:p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <span className="text-3xl mr-3">📝</span> Create Ticket
                </h2>
                <TicketForm onSubmit={handleTicketSubmit} />
              </div>
            </div>
          </div>

          {/* Right Column - My Tickets */}
          <div className="animate-fade-in-up animation-delay-2000">
            <div className="glass-effect rounded-xl p-1">
              <div className="bg-white rounded-lg p-6 lg:p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <span className="text-3xl mr-3">📋</span> My Tickets
                </h2>
                <QueueList 
                  onSelectTicket={handleSelectQueueTicket} 
                  refreshTrigger={refreshKey}
                  onTicketUpdated={handleTicketUpdated}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Ticket Detail Modal */}
      {selectedTicket && (
        <ClientTicketDetail
          key={ticketRefreshKey}
          ticket={selectedTicket}
          onClose={() => setSelectedTicket(null)}
        />
      )}

      {/* Footer */}
      <div className="text-center pb-8">
        <p className="text-purple-200 text-sm">
          Powered by AI-driven support | Real-time ticket resolution
        </p>
      </div>
    </div>
  )
}

export default Dashboard
