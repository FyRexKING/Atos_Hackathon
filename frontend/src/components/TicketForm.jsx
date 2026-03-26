/**
 * TicketForm Component
 * Form for users to submit support tickets
 */

import React, { useState } from 'react'
import { submitTicket } from '../api/ticketApi'

const TicketForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  /**
   * Handle form input changes
   */
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    // Clear error when user starts typing
    if (error) setError('')
  }

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validation
    if (!formData.title.trim()) {
      setError('Title is required')
      return
    }
    if (formData.title.length < 5) {
      setError('Title must be at least 5 characters')
      return
    }
    if (!formData.description.trim()) {
      setError('Description is required')
      return
    }
    if (formData.description.length < 10) {
      setError('Description must be at least 10 characters')
      return
    }

    // Submit to API
    setLoading(true)
    const result = await submitTicket(formData)
    setLoading(false)

    if (result.success) {
      // Clear form
      setFormData({ title: '', description: '' })
      // Notify parent component
      onSubmit(result.data)
    } else {
      setError(result.error)
    }
  }

  /**
   * Load sample ticket for demo
   */
  const loadSampleTicket = () => {
    setFormData({
      title: 'Cannot login to account',
      description: 'I tried multiple times but keep getting an authentication error. The email and password are correct.',
    })
    setError('')
  }

  return (
    <div className="h-full bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Submit Ticket</h2>
        <p className="text-gray-600 text-sm mt-1">Describe your issue and our AI will help classify and resolve it</p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title Input */}
        <div>
          <label htmlFor="title" className="block text-sm font-semibold text-gray-700 mb-2">
            Title
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="e.g., Cannot login to account"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            disabled={loading}
          />
          <p className="text-xs text-gray-500 mt-1">{formData.title.length}/200 characters</p>
        </div>

        {/* Description Input */}
        <div>
          <label htmlFor="description" className="block text-sm font-semibold text-gray-700 mb-2">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Provide details about your issue..."
            rows="5"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none"
            disabled={loading}
          />
          <p className="text-xs text-gray-500 mt-1">{formData.description.length}/2000 characters</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={loading}
            className={`flex-1 py-2 px-4 rounded-lg font-semibold transition duration-200 ${
              loading
                ? 'bg-gray-400 text-white cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Submitting...
              </span>
            ) : (
              'Submit Ticket'
            )}
          </button>
          <button
            type="button"
            onClick={loadSampleTicket}
            disabled={loading}
            className="py-2 px-4 rounded-lg font-semibold bg-gray-200 hover:bg-gray-300 text-gray-700 transition duration-200 disabled:opacity-50"
          >
            Demo Data
          </button>
        </div>
      </form>
    </div>
  )
}

export default TicketForm
