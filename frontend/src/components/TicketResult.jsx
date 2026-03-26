/**
 * TicketResult Component
 * Displays ticket classification, confidence, decision, and resolution
 * Shows AI resolution to clients when ticket is auto-resolved
 */

import React from 'react'

const TicketResult = ({ ticket }) => {
  if (!ticket) {
    return (
      <div className="h-full bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg shadow-lg p-6 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <svg className="w-12 h-12 mx-auto mb-3 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>No ticket submitted yet</p>
          <p className="text-xs mt-1">Submit a ticket to see analysis</p>
        </div>
      </div>
    )
  }

  const { classification, similarity, confidence, decision, explanation, resolution, ticket_id, status, resolution_source } = ticket
  const isAutoResolved = decision === 'auto_resolve'

  /**
   * Get badge color based on confidence score
   */
  const getConfidenceBadgeColor = (score) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800'
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  /**
   * Get decision badge color
   */
  const getDecisionColor = () => {
    return isAutoResolved ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
  }

  /**
   * Get status badge color
   */
  const getStatusColor = (st) => {
    switch (st) {
      case 'resolved':
        return 'bg-green-100 text-green-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      case 'assigned':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-orange-100 text-orange-800'
    }
  }

  return (
    <div className="h-full bg-white rounded-lg shadow-lg p-6 overflow-y-auto">
      {/* Header */}
      <div className="mb-6 pb-4 border-b">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Analysis Result</h2>
            <p className="text-gray-600 text-sm">Ticket #{ticket_id}</p>
          </div>
          <div className="flex gap-2">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getDecisionColor()}`}>
              {isAutoResolved ? 'Auto Resolved' : 'Human Review'}
            </span>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(status)}`}>
              {status}
            </span>
          </div>
        </div>
      </div>

      {/* PROMINENT AI RESOLUTION SECTION (for auto-resolved tickets) */}
      {isAutoResolved && resolution && (
        <div className="mb-6 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 rounded-lg p-5 shadow-md">
          <div className="flex items-start gap-3 mb-3">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold text-green-900">Your Ticket Has Been Resolved</h3>
              <p className="text-sm text-green-700 mt-1">AI has automatically resolved your ticket with high confidence</p>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-green-200 mt-3">
            <p className="text-sm font-semibold text-gray-700 mb-2">Resolution</p>
            <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">{resolution.resolution}</p>
          </div>
          {resolution.explanation && (
            <div className="bg-white rounded-lg p-4 border border-green-200 mt-3">
              <p className="text-sm font-semibold text-gray-700 mb-2">Why This Solution</p>
              <p className="text-sm text-gray-700 leading-relaxed">{resolution.explanation}</p>
            </div>
          )}
        </div>
      )}

      {/* REJECTION MESSAGE SECTION */}
      {ticket.rejection_message && status === 'rejected' && (
        <div className="mb-6 bg-red-50 border-2 border-red-300 rounded-lg p-5">
          <div className="flex items-start gap-3 mb-3">
            <svg className="w-6 h-6 text-red-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <h3 className="text-lg font-bold text-red-900">Ticket Rejected</h3>
          </div>
          <div className="bg-white rounded-lg p-4 border border-red-200">
            <p className="text-sm text-gray-800 leading-relaxed">{ticket.rejection_message}</p>
          </div>
        </div>
      )}

      {/* ASSIGNED TEAM SECTION */}
      {ticket.assigned_team && status === 'assigned' && (
        <div className="mb-6 bg-blue-50 border-2 border-blue-300 rounded-lg p-5">
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
            </svg>
            <div>
              <h3 className="text-lg font-bold text-blue-900">Assigned to {ticket.assigned_team}</h3>
              <p className="text-sm text-blue-700 mt-1">Your ticket has been assigned to the {ticket.assigned_team} team for specialized handling</p>
            </div>
          </div>
        </div>
      )}

      {/* Classification */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Classification</h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <p className="text-xs text-gray-600 font-semibold mb-1">Category</p>
            <p className="text-lg font-bold text-blue-600">{classification.category}</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
            <p className="text-xs text-gray-600 font-semibold mb-1">Priority</p>
            <p className="text-lg font-bold text-purple-600">{classification.priority}</p>
          </div>
          <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-200">
            <p className="text-xs text-gray-600 font-semibold mb-1">Impact</p>
            <p className="text-lg font-bold text-indigo-600">{classification.impact}</p>
          </div>
        </div>
      </div>

      {/* Confidence Score */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Confidence Score</h3>
        <div className="flex items-center gap-4">
          <div className={`px-4 py-2 rounded-full font-bold text-lg ${getConfidenceBadgeColor(confidence.score)}`}>
            {(confidence.score * 100).toFixed(1)}%
          </div>
          <div className="flex-1 bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${
                confidence.score >= 0.8
                  ? 'bg-green-500'
                  : confidence.score >= 0.6
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${confidence.score * 100}%` }}
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-2 mt-3 text-xs text-gray-600">
          <div>
            <p className="font-semibold">Similarity</p>
            <p className="text-gray-800">{(confidence.similarity_weight * 100).toFixed(1)}%</p>
          </div>
          <div>
            <p className="font-semibold">Category Match</p>
            <p className="text-gray-800">{(confidence.category_match_weight * 100).toFixed(1)}%</p>
          </div>
          <div>
            <p className="font-semibold">Impact Weight</p>
            <p className="text-gray-800">{(confidence.impact_penalty_weight * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>

      {/* Similar Tickets */}
      {similarity.similar_tickets.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Similar Tickets</h3>
          <div className="space-y-2">
            {similarity.similar_tickets.map((ticket, idx) => (
              <div key={idx} className="bg-gray-50 p-3 rounded-lg flex justify-between items-start border border-gray-200">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-800">#{ticket.ticket_id}: {ticket.title}</p>
                  <p className="text-xs text-gray-600 mt-1">Category: {ticket.category} • Status: {ticket.status}</p>
                </div>
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-semibold flex-shrink-0">
                  {(ticket.similarity_score * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Explanation */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p className="text-sm font-semibold text-gray-700 mb-2">AI Analysis Summary</p>
        <p className="text-sm text-gray-700 leading-relaxed">{explanation}</p>
      </div>
    </div>
  )
}

export default TicketResult
