/**
 * ClientTicketDetail Component
 * Shows ticket details and resolution/solution to clients
 */

import React from 'react'

const ClientTicketDetail = ({ ticket, onClose }) => {
  if (!ticket) return null

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

  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved':
        return 'bg-green-100 text-green-800'
      case 'pending_review':
        return 'bg-orange-100 text-orange-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      case 'assigned':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getCategoryColor = (category) => {
    const colors = {
      auth: 'bg-blue-100 text-blue-800',
      billing: 'bg-green-100 text-green-800',
      infra: 'bg-purple-100 text-purple-800',
      ui: 'bg-pink-100 text-pink-800',
      api: 'bg-indigo-100 text-indigo-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-96 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6 flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold">Ticket #{ticket.id}</h2>
            <p className="text-blue-100 text-sm">{new Date(ticket.created_at).toLocaleString()}</p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-blue-700 p-2 rounded-lg transition"
          >
            ✕
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Title */}
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">{ticket.title}</h3>
            <p className="text-gray-600 whitespace-pre-wrap">{ticket.description}</p>
          </div>

          {/* Status Badges */}
          <div className="flex flex-wrap gap-3">
            <span className={`px-4 py-2 rounded-full text-sm font-semibold ${getStatusColor(ticket.status)}`}>
              {ticket.status.replace('_', ' ').toUpperCase()}
            </span>
            <span className={`px-4 py-2 rounded-full text-sm font-semibold ${getPriorityColor(ticket.priority)}`}>
              Priority: {ticket.priority.toUpperCase()}
            </span>
            <span className={`px-4 py-2 rounded-full text-sm font-semibold ${getCategoryColor(ticket.category)}`}>
              {ticket.category.toUpperCase()}
            </span>
          </div>

          {/* RESOLUTION SECTION - For Auto-Resolved Tickets */}
          {ticket.status === 'resolved' && ticket.decision === 'auto_resolve' && ticket.resolution && (
            <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="text-3xl">✓</div>
                <h4 className="text-xl font-bold text-green-800">Your Ticket Has Been Resolved</h4>
              </div>
              <div className="bg-white rounded-lg p-4 border border-green-100">
                <p className="text-green-900 leading-relaxed">{ticket.resolution}</p>
              </div>
              {ticket.confidence_score && (
                <p className="text-sm text-green-700 mt-3">
                  ✓ AI Confidence: {(ticket.confidence_score * 100).toFixed(0)}%
                </p>
              )}
            </div>
          )}

          {/* ASSIGNED SECTION */}
          {ticket.status === 'assigned' && ticket.assigned_team && (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="text-3xl">👥</div>
                <h4 className="text-xl font-bold text-blue-800">Your Ticket Has Been Assigned</h4>
              </div>
              <div className="bg-white rounded-lg p-4 border border-blue-100">
                <p className="text-blue-900 font-semibold mb-2">Assigned to: {ticket.assigned_team}</p>
                <p className="text-blue-800 text-sm">Our {ticket.assigned_team} team will investigate and respond shortly.</p>
              </div>
            </div>
          )}

          {/* REJECTION SECTION */}
          {ticket.status === 'rejected' && ticket.rejection_message && (
            <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="text-3xl">✕</div>
                <h4 className="text-xl font-bold text-red-800">Ticket Status Update</h4>
              </div>
              <div className="bg-white rounded-lg p-4 border border-red-100">
                <p className="text-red-900 leading-relaxed">{ticket.rejection_message}</p>
              </div>
            </div>
          )}

          {/* PENDING SECTION */}
          {ticket.status === 'pending_review' && (
            <div className="bg-orange-50 border-2 border-orange-200 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="text-3xl">⏳</div>
                <h4 className="text-xl font-bold text-orange-800">Ticket Under Review</h4>
              </div>
              <div className="bg-white rounded-lg p-4 border border-orange-100">
                <p className="text-orange-900 leading-relaxed">
                  Our team is reviewing your ticket and will provide a solution shortly. Thank you for your patience.
                </p>
              </div>
            </div>
          )}

          {/* AI Explanation (if available) */}
          {ticket.ai_explanation && (
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h5 className="font-semibold text-gray-800 mb-2">How We Analyzed Your Issue</h5>
              <p className="text-gray-700 text-sm">{ticket.ai_explanation}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t bg-gray-50 p-4 flex justify-end">
          <button
            onClick={onClose}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default ClientTicketDetail
