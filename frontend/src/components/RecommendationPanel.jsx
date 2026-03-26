/**
 * RecommendationPanel Component
 * Displays AI-generated recommendations, action plans, and suggested solutions for tickets
 * Allows admins to assign tickets, manually resolve, or escalate
 */

import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

const RecommendationPanel = ({ ticket, onActionComplete }) => {
  const { token } = useAuth()
  const [recommendations, setRecommendations] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('plan') // 'plan', 'solutions', 'explain'
  
  // Action states
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState('')
  const [actionSuccess, setActionSuccess] = useState('')
  
  // Form states
  const [selectedTeam, setSelectedTeam] = useState('')
  const [resolutionText, setResolutionText] = useState('')
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [showResolveModal, setShowResolveModal] = useState(false)

  const teams = [
    { name: 'Account & Security Team', description: 'For auth & access issues' },
    { name: 'Billing Team', description: 'For payment & billing issues' },
    { name: 'Infrastructure Team', description: 'For system & performance issues' },
    { name: 'General Support Team', description: 'For other issues' }
  ]

  useEffect(() => {
    if (ticket && token) {
      fetchRecommendations()
    }
  }, [ticket?.id, token])

  const fetchRecommendations = async () => {
    try {
      setLoading(true)
      setError('')

      const response = await fetch(
        `http://localhost:8000/api/admin/recommendations/ticket/${ticket.id}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      )

      if (!response.ok) {
        throw new Error(`Failed to fetch recommendations: ${response.statusText}`)
      }

      const data = await response.json()
      setRecommendations(data)
    } catch (err) {
      console.error('Error fetching recommendations:', err)
      setError(err.message || 'Failed to load recommendations')
    } finally {
      setLoading(false)
    }
  }

  const handleAssignToTeam = async () => {
    if (!selectedTeam) {
      setActionError('Please select a team')
      return
    }

    setActionLoading(true)
    setActionError('')
    setActionSuccess('')

    try {
      const response = await fetch(
        `http://localhost:8000/api/admin/recommendations/ticket/${ticket.id}/assign`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            assigned_to_team: selectedTeam,
            admin_notes: ''
          })
        }
      )

      if (!response.ok) {
        throw new Error(`Assignment failed: ${response.statusText}`)
      }

      setActionSuccess(`✓ Assigned to ${selectedTeam}`)
      setSelectedTeam('')
      setShowAssignModal(false)
      setTimeout(() => onActionComplete(), 1500)
    } catch (err) {
      setActionError(err.message || 'Failed to assign ticket')
    } finally {
      setActionLoading(false)
    }
  }

  const handleManualResolve = async () => {
    if (!resolutionText.trim()) {
      setActionError('Please provide a resolution message')
      return
    }

    setActionLoading(true)
    setActionError('')
    setActionSuccess('')

    try {
      const response = await fetch(
        `http://localhost:8000/api/admin/recommendations/ticket/${ticket.id}/resolve-manually`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            resolution_text: resolutionText
          })
        }
      )

      if (!response.ok) {
        throw new Error(`Resolution failed: ${response.statusText}`)
      }

      setActionSuccess('✓ Ticket manually resolved')
      setResolutionText('')
      setShowResolveModal(false)
      setTimeout(() => onActionComplete(), 1500)
    } catch (err) {
      setActionError(err.message || 'Failed to resolve ticket')
    } finally {
      setActionLoading(false)
    }
  }

  if (!ticket) {
    return (
      <div className="glass-effect rounded-xl p-1">
        <div className="bg-white rounded-lg p-6 text-center">
          <div className="text-gray-400 py-8">
            <svg className="w-12 h-12 mx-auto mb-3 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="font-semibold">Select a ticket to view AI recommendations</p>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="glass-effect rounded-xl p-1">
        <div className="bg-white rounded-lg p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-effect rounded-xl p-1">
        <div className="bg-white rounded-lg p-6">
          <div className="text-red-600 p-4 bg-red-50 rounded-lg">
            <p className="font-semibold">⚠️ Error Loading Recommendations</p>
            <p className="text-sm mt-1">{error}</p>
            <button 
              onClick={fetchRecommendations}
              className="mt-3 text-sm font-semibold text-red-700 hover:text-red-900 underline"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!recommendations) {
    return (
      <div className="glass-effect rounded-xl p-1">
        <div className="bg-white rounded-lg p-6 text-center">
          <p className="text-gray-500">No recommendations available</p>
        </div>
      </div>
    )
  }

  const isHighImpact = recommendations.is_high_impact
  const confidencePercent = (recommendations.confidence_score * 100).toFixed(0)
  const isNewIssueType = recommendations.is_new_issue_type

  return (
    <div className="glass-effect rounded-xl p-1">
      <div className="bg-white rounded-lg p-6">
        {/* Header */}
        <div className="mb-6 pb-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800 mb-3">🤖 AI Recommendations</h2>
          
          {/* Status Badges */}
          <div className="flex flex-wrap gap-2">
            {/* Confidence Score */}
            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
              recommendations.confidence_score >= 0.8 
                ? 'bg-green-100 text-green-800' 
                : recommendations.confidence_score >= 0.6
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-orange-100 text-orange-800'
            }`}>
              Confidence: {confidencePercent}%
            </div>

            {/* High Impact Badge */}
            {isHighImpact && (
              <div className="px-3 py-1 rounded-full text-sm font-semibold bg-red-100 text-red-800">
                🚨 High Impact - Auto-Escalate
              </div>
            )}

            {/* New Issue Type Badge */}
            {isNewIssueType && (
              <div className="px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-800">
                ⭐ New Issue Type
              </div>
            )}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 border-b border-gray-200">
          {[
            { id: 'plan', label: '📋 Action Plan', icon: '📋' },
            { id: 'solutions', label: '💡 Solutions', icon: '💡' },
            { id: 'explain', label: '🧠 Reasoning', icon: '🧠' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 font-semibold transition-all text-sm ${
                activeTab === tab.id
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="mb-6">
          {activeTab === 'plan' && recommendations.action_plan && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">
                  <span className="font-semibold">Estimated time:</span> {recommendations.action_plan.estimated_time} | 
                  <span className="font-semibold ml-2">Difficulty:</span> {recommendations.action_plan.difficulty}
                </p>
              </div>
              <div className="space-y-3">
                {recommendations.action_plan.steps.map((step, idx) => (
                  <div key={idx} className="flex gap-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <div className="flex-shrink-0">
                      <div className="flex items-center justify-center h-8 w-8 rounded-full bg-purple-600 text-white font-bold text-sm">
                        {step.step}
                      </div>
                    </div>
                    <div className="flex-grow">
                      <p className="font-semibold text-gray-800 text-sm">{step.action}</p>
                      <p className="text-gray-600 text-sm mt-1">{step.details}</p>
                      <div className="mt-2">
                        <span className={`text-xs font-bold px-2 py-1 rounded ${
                          step.priority === 'high' ? 'bg-red-100 text-red-800'
                          : step.priority === 'medium' ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                        }`}>
                          {step.priority.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'solutions' && recommendations.suggested_solutions && (
            <div className="space-y-4">
              {recommendations.suggested_solutions.length > 0 ? (
                recommendations.suggested_solutions.map((solution, idx) => (
                  <div key={idx} className="border border-gray-300 rounded-lg p-4 bg-white">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-semibold text-gray-800">{solution.title}</p>
                        <div className="flex gap-2 mt-1 flex-wrap">
                          <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded font-semibold">
                            #{solution.rank} Match
                          </span>
                          <span className={`text-xs px-2 py-1 rounded font-semibold ${
                            solution.type === 'historical_match' ? 'bg-green-100 text-green-800'
                            : solution.type === 'kb_article' ? 'bg-blue-100 text-blue-800'
                            : 'bg-orange-100 text-orange-800'
                          }`}>
                            {solution.type === 'historical_match' ? '📊 Past Ticket'
                            : solution.type === 'kb_article' ? '📚 KB Article'
                            : '🤖 AI Suggestion'}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-gray-800">
                          {(solution.confidence * 100).toFixed(0)}%
                        </p>
                        <p className="text-xs text-gray-500">confidence</p>
                      </div>
                    </div>
                    <p className="text-gray-700 text-sm mt-3 mb-3">{solution.solution}</p>
                    {solution.action_steps && solution.action_steps.length > 0 && (
                      <div className="bg-gray-50 p-3 rounded mt-3 text-sm">
                        <p className="font-semibold text-gray-800 mb-2">Steps:</p>
                        <ol className="list-decimal list-inside space-y-1 text-gray-700">
                          {solution.action_steps.map((step, i) => (
                            <li key={i}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}
                    <p className="text-xs text-gray-500 mt-3">Source: {solution.source}</p>
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <p>No suggested solutions available</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'explain' && recommendations.explainability && (
            <div className="space-y-4">
              <div className="bg-gray-50 border border-gray-300 rounded-lg p-4">
                <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {recommendations.explainability.reasoning_chain}
                </p>
              </div>

              {recommendations.explainability.confidence_breakdown && (
                <div className="bg-white border border-gray-300 rounded-lg p-4">
                  <p className="font-semibold text-gray-800 mb-3">Confidence Breakdown:</p>
                  <div className="space-y-2 text-sm">
                    {Object.entries(recommendations.explainability.confidence_breakdown).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center">
                        <span className="text-gray-700">{key}:</span>
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full"
                            style={{ width: `${value * 100}%` }}
                          ></div>
                        </div>
                        <span className="font-semibold text-gray-800 w-12 text-right">
                          {(value * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {recommendations.explainability.recommended_team && (
                <div className="bg-purple-50 border border-purple-300 rounded-lg p-4">
                  <p className="font-semibold text-purple-900 mb-1">Recommended Team Assignment:</p>
                  <p className="text-purple-800 text-sm">{recommendations.explainability.recommended_team}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Alerts */}
        {actionError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-300 text-red-800 rounded-lg text-sm">
            ⚠️ {actionError}
          </div>
        )}

        {actionSuccess && (
          <div className="mb-4 p-3 bg-green-50 border border-green-300 text-green-800 rounded-lg text-sm">
            ✅ {actionSuccess}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 pt-6 border-t border-gray-200">
          <button
            onClick={() => setShowAssignModal(true)}
            className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-2 px-4 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all"
            disabled={actionLoading}
          >
            {actionLoading ? '⏳ Loading...' : '👤 Assign to Team'}
          </button>
          <button
            onClick={() => setShowResolveModal(true)}
            className="flex-1 bg-gradient-to-r from-green-600 to-green-700 text-white font-semibold py-2 px-4 rounded-lg hover:from-green-700 hover:to-green-800 transition-all"
            disabled={actionLoading}
          >
            {actionLoading ? '⏳ Loading...' : '✅ Manually Resolve'}
          </button>
        </div>

        {/* Assign Modal */}
        {showAssignModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h3 className="text-lg font-bold text-gray-800 mb-4">Assign Ticket to Team</h3>
              
              <div className="space-y-3 mb-4">
                {teams.map(team => (
                  <label key={team.name} className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name="team"
                      value={team.name}
                      checked={selectedTeam === team.name}
                      onChange={(e) => setSelectedTeam(e.target.value)}
                      className="mt-1"
                    />
                    <div>
                      <p className="font-semibold text-gray-800 text-sm">{team.name}</p>
                      <p className="text-gray-600 text-xs">{team.description}</p>
                    </div>
                  </label>
                ))}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowAssignModal(false)}
                  className="flex-1 px-4 py-2 rounded-lg border border-gray-300 text-gray-700 font-semibold hover:bg-gray-50"
                  disabled={actionLoading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleAssignToTeam}
                  className="flex-1 px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700"
                  disabled={actionLoading || !selectedTeam}
                >
                  {actionLoading ? '⏳' : '✓'} Assign
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Resolve Modal */}
        {showResolveModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h3 className="text-lg font-bold text-gray-800 mb-4">Manually Resolve Ticket</h3>
              
              <textarea
                value={resolutionText}
                onChange={(e) => setResolutionText(e.target.value)}
                placeholder="Enter your resolution message..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent mb-4 h-24"
              />

              <div className="flex gap-3">
                <button
                  onClick={() => setShowResolveModal(false)}
                  className="flex-1 px-4 py-2 rounded-lg border border-gray-300 text-gray-700 font-semibold hover:bg-gray-50"
                  disabled={actionLoading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleManualResolve}
                  className="flex-1 px-4 py-2 rounded-lg bg-green-600 text-white font-semibold hover:bg-green-700"
                  disabled={actionLoading || !resolutionText.trim()}
                >
                  {actionLoading ? '⏳' : '✓'} Resolve
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default RecommendationPanel
