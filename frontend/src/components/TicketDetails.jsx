/**
 * TicketDetails Component
 * Shows basic ticket information for admin dashboard
 */

import React from 'react'

const TicketDetails = ({ ticket }) => {
  if (!ticket) {
    return (
      <div className="text-gray-600">
        Select a ticket to view details.
      </div>
    )
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

  /**
   * Get category badge color
   */
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
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-4 border-b">
        <h3 className="text-xl font-bold text-gray-800">Ticket #{ticket.id}</h3>
        <p className="text-gray-600 text-sm">{new Date(ticket.created_at).toLocaleString()}</p>
      </div>

      {/* Title */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 mb-2">Title</h4>
        <p className="text-gray-700">{ticket.title}</p>
      </div>

      {/* Description */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 mb-2">Description</h4>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
        </div>
      </div>

      {/* Classification */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 mb-3">Classification</h4>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-600 font-semibold mb-1">Category</p>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold capitalize ${getCategoryColor(ticket.category)}`}>
              {ticket.category}
            </span>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-600 font-semibold mb-1">Priority</p>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold capitalize ${getPriorityColor(ticket.priority)}`}>
              {ticket.priority}
            </span>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-600 font-semibold mb-1">Impact</p>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold capitalize ${getPriorityColor(ticket.impact)}`}>
              {ticket.impact}
            </span>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-600 font-semibold mb-1">Status</p>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold capitalize ${getStatusColor(ticket.status)}`}>
              {ticket.status.replace('_', ' ')}
            </span>
          </div>
        </div>
      </div>

      {/* AI Analysis */}
      {ticket.ai_explanation && (
        <div>
          <h4 className="text-lg font-semibold text-gray-800 mb-3">AI Analysis</h4>

          {/* AI Decision & Explanation */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between mb-2">
              <h5 className="font-semibold text-blue-800">AI Decision</h5>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                ticket.decision === 'auto_resolve'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-orange-100 text-orange-800'
              }`}>
                {ticket.decision === 'auto_resolve' ? 'Auto Resolve' : 'Human Review'}
              </span>
            </div>
            <p className="text-blue-700">{ticket.ai_explanation}</p>
          </div>

          {/* Confidence Breakdown */}
          {ticket.confidence_breakdown && (
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <h5 className="font-semibold text-gray-800 mb-3">Confidence Analysis</h5>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Overall Score</p>
                  <p className="text-lg font-bold text-gray-800">
                    {(ticket.confidence_breakdown.score * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Similarity Weight</p>
                  <p className="text-lg font-bold text-gray-800">
                    {(ticket.confidence_breakdown.similarity_weight * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Category Match</p>
                  <p className="text-lg font-bold text-gray-800">
                    {(ticket.confidence_breakdown.category_match_weight * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Impact Penalty</p>
                  <p className="text-lg font-bold text-gray-800">
                    {(ticket.confidence_breakdown.impact_penalty_weight * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Similar Tickets */}
          {ticket.similarity_data && ticket.similarity_data.similar_tickets && ticket.similarity_data.similar_tickets.length > 0 && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h5 className="font-semibold text-gray-800 mb-3">Similar Tickets</h5>
              <p className="text-sm text-gray-600 mb-3">
                Average Similarity: {(ticket.similarity_data.avg_similarity * 100).toFixed(1)}%
              </p>
              <div className="space-y-2">
                {ticket.similarity_data.similar_tickets.map((similar, index) => (
                  <div key={index} className="flex justify-between items-center bg-white p-3 rounded border">
                    <div>
                      <p className="font-medium text-gray-800">#{similar.ticket_id}: {similar.title}</p>
                      <p className="text-sm text-gray-600">Category: {similar.category} | Status: {similar.status}</p>
                    </div>
                    <span className="text-sm font-semibold text-blue-600">
                      {(similar.similarity_score * 100).toFixed(1)}% similar
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Human Resolution */}
      {ticket.human_resolution && (
        <div>
          <h4 className="text-lg font-semibold text-gray-800 mb-2">Human Resolution</h4>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800 whitespace-pre-wrap">{ticket.human_resolution}</p>
          </div>
        </div>
      )}

      {/* Timestamps */}
      <div className="pt-4 border-t">
        <h4 className="text-lg font-semibold text-gray-800 mb-3">Timeline</h4>
        <div className="space-y-2 text-sm text-gray-600">
          <div>
            <span className="font-medium">Created:</span> {new Date(ticket.created_at).toLocaleString()}
          </div>
          {ticket.resolved_at && (
            <div>
              <span className="font-medium">Resolved:</span> {new Date(ticket.resolved_at).toLocaleString()}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TicketDetails