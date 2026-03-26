/**
 * ApprovalPanel Component
 * Panel for admin to approve, reject, or assign tickets
 */

import React, { useState } from 'react'
import {
  assignTicketToTeam,
  rejectTicketWithMessage,
} from '../api/ticketApi'

const ApprovalPanel = ({ ticket, onActionComplete }) => {
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState('')
  const [actionSuccess, setActionSuccess] = useState('')
  
  // Form states
  const [selectedTeam, setSelectedTeam] = useState('')
  const [teamNote, setTeamNote] = useState('')
  const [rejectionMessage, setRejectionMessage] = useState('')
  
  // UI states
  const [activeAction, setActiveAction] = useState(null)

  if (!ticket) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-gray-500 py-8">
          <svg className="w-12 h-12 mx-auto mb-3 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>Select a ticket to review</p>
        </div>
      </div>
    )
  }

  const isAutoResolved = ticket.decision === 'auto_resolve'
  const teams = ['Support', 'Engineering', 'Billing', 'Infrastructure', 'Security']

  const handleAssignToTeam = async () => {
    if (!selectedTeam) {
      setActionError('Please select a team')
      return
    }

    setActionLoading(true)
    setActionError('')
    setActionSuccess('')

    const result = await assignTicketToTeam(ticket.id, selectedTeam, teamNote)
    setActionLoading(false)

    if (result.success) {
      setActionSuccess(`Ticket assigned to ${selectedTeam}!`)
      setSelectedTeam('')
      setTeamNote('')
      setActiveAction(null)
      setTimeout(() => onActionComplete(), 1500)
    } else {
      setActionError(result.error)
    }
  }

  const handleRejectTicket = async () => {
    if (!rejectionMessage.trim()) {
      setActionError('Please provide a rejection message')
      return
    }

    setActionLoading(true)
    setActionError('')
    setActionSuccess('')

    const result = await rejectTicketWithMessage(ticket.id, rejectionMessage)
    setActionLoading(false)

    if (result.success) {
      setActionSuccess('Ticket rejected - message sent to client!')
      setRejectionMessage('')
      setActiveAction(null)
      setTimeout(() => onActionComplete(), 1500)
    } else {
      setActionError(result.error)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Ticket Review & Action</h2>

      {/* Ticket Summary */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
        <div className="mb-3">
          <p className="text-sm text-gray-600 font-semibold">Ticket #{ticket.id}</p>
          <p className="text-lg font-bold text-gray-800 mt-1">{ticket.title}</p>
        </div>
        <div className="grid grid-cols-4 gap-3 text-sm mt-4">
          <div className="bg-white p-2 rounded border border-gray-200">
            <p className="text-gray-600 text-xs">Category</p>
            <p className="font-semibold text-gray-800">{ticket.category}</p>
          </div>
          <div className="bg-white p-2 rounded border border-gray-200">
            <p className="text-gray-600 text-xs">Priority</p>
            <p className="font-semibold text-gray-800">{ticket.priority}</p>
          </div>
          <div className="bg-white p-2 rounded border border-gray-200">
            <p className="text-gray-600 text-xs">Confidence</p>
            <p className="font-semibold text-gray-800">{(ticket.confidence_score * 100).toFixed(0)}%</p>
          </div>
          <div className={`p-2 rounded border ${isAutoResolved ? 'bg-green-50 border-green-200' : 'bg-orange-50 border-orange-200'}`}>
            <p className="text-gray-600 text-xs">Status</p>
            <p className={`font-semibold ${isAutoResolved ? 'text-green-800' : 'text-orange-800'}`}>
              {isAutoResolved ? 'AI Resolved' : 'Pending'}
            </p>
          </div>
        </div>
      </div>

      {/* Description */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6 max-h-32 overflow-y-auto border border-gray-200">
        <p className="text-sm text-gray-600 font-semibold mb-2">Description</p>
        <p className="text-sm text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
      </div>

      {/* Messages */}
      {actionError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-4 flex items-start gap-2">
          <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <span>{actionError}</span>
        </div>
      )}

      {actionSuccess && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm mb-4 flex items-start gap-2">
          <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        {/* Assign to Team */}
        <button
          onClick={() => setActiveAction(activeAction === 'assign' ? null : 'assign')}
          disabled={actionLoading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
          Assign Team
        </button>

        {/* Reject Ticket */}
        <button
          onClick={() => setActiveAction(activeAction === 'reject' ? null : 'reject')}
          disabled={actionLoading}
          className="bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          Reject
        </button>
      </div>

      {/* ASSIGN TO TEAM FORM */}
      {activeAction === 'assign' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Assign to Team</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Select Team</label>
              <select
                value={selectedTeam}
                onChange={(e) => setSelectedTeam(e.target.value)}
                disabled={actionLoading}
                className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Select a team --</option>
                {teams.map((team) => (
                  <option key={team} value={team}>
                    {team}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Note (optional)</label>
              <textarea
                value={teamNote}
                onChange={(e) => setTeamNote(e.target.value)}
                placeholder="Add any notes for the assigned team..."
                rows="2"
                disabled={actionLoading}
                className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleAssignToTeam}
                disabled={actionLoading || !selectedTeam}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200 disabled:opacity-50"
              >
                {actionLoading ? 'Assigning...' : 'Assign'}
              </button>
              <button
                onClick={() => {
                  setActiveAction(null)
                  setSelectedTeam('')
                  setTeamNote('')
                }}
                disabled={actionLoading}
                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 px-4 rounded-lg transition duration-200 disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* REJECT FORM */}
      {activeAction === 'reject' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <h3 className="text-lg font-semibold text-red-900 mb-3">Reject Ticket</h3>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Message to Client</label>
            <textarea
              value={rejectionMessage}
              onChange={(e) => setRejectionMessage(e.target.value)}
              placeholder="Explain why this ticket is being rejected. This message will be sent to the client."
              rows="4"
              disabled={actionLoading}
              className="w-full px-3 py-2 border border-red-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 resize-none"
            />
            <div className="flex gap-2 mt-3">
              <button
                onClick={handleRejectTicket}
                disabled={actionLoading || !rejectionMessage.trim()}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200 disabled:opacity-50"
              >
                {actionLoading ? 'Rejecting...' : 'Confirm Rejection'}
              </button>
              <button
                onClick={() => {
                  setActiveAction(null)
                  setRejectionMessage('')
                }}
                disabled={actionLoading}
                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 px-4 rounded-lg transition duration-200 disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ApprovalPanel
