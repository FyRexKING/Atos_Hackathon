/**
 * Ticket API Integration Layer
 * Handles all communication with the FastAPI backend
 */

import axios from 'axios'

// Configure axios instance
const API_BASE_URL = 'http://localhost:8000'

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include auth token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    console.log('📝 API Request:', {
      url: config.url,
      method: config.method,
      hasToken: !!token,
      tokenLength: token ? token.length : 0
    })
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    } else {
      console.warn('⚠️ No auth token found in localStorage!')
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response error interceptor for better debugging
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('❌ Auth failed (401):', {
        url: error.response.config?.url,
        detail: error.response.data?.detail,
        headers: error.response.config?.headers
      })
    }
    return Promise.reject(error)
  }
)

/**
 * Submit a new ticket to the backend
 * @param {Object} data - Ticket data { title, description }
 * @returns {Promise<Object>} - Response from backend with classification, confidence, decision
 */
export const submitTicket = async (data) => {
  try {
    const response = await axiosInstance.post('/api/ticket', {
      title: data.title,
      description: data.description,
    })
    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    console.error('Error submitting ticket:', error)
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to submit ticket',
    }
  }
}

/**
 * Get all pending tickets from backend
 * @returns {Promise<Object>} - Array of pending tickets
 */
export const getPendingTickets = async () => {
  try {
    const response = await axiosInstance.get('/api/tickets/pending')
    return {
      success: true,
      data: response.data.tickets || [],
    }
  } catch (error) {
    console.error('Error fetching pending tickets:', error)
    return {
      success: false,
      error: 'Failed to fetch pending tickets',
      data: [],
    }
  }
}

/**
 * Get current user's tickets
 * @returns {Promise<Object>} - Array of user's tickets
 */
export const getMyTickets = async () => {
  try {
    const response = await axiosInstance.get('/api/tickets/my')
    return {
      success: true,
      data: response.data.tickets || [],
    }
  } catch (error) {
    console.error('Error fetching my tickets:', error)
    return {
      success: false,
      error: 'Failed to fetch your tickets',
      data: [],
    }
  }
}

/**
 * Get a specific ticket by ID
 * @param {number} ticketId - Ticket ID
 * @returns {Promise<Object>} - Ticket data
 */
export const getTicket = async (ticketId) => {
  try {
    const response = await axiosInstance.get(`/api/ticket/${ticketId}`)
    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    console.error('Error fetching ticket:', error)
    return {
      success: false,
      error: 'Failed to fetch ticket',
    }
  }
}

/**
 * Resolve a ticket (human approval)
 * @param {number} ticketId - Ticket ID
 * @param {string} resolution - Resolution message
 * @returns {Promise<Object>} - Updated ticket
 */
export const resolveTicket = async (ticketId, resolution) => {
  try {
    const response = await axiosInstance.patch(`/api/ticket/${ticketId}/resolve`, {
      resolution,
    })
    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    console.error('Error resolving ticket:', error)
    return {
      success: false,
      error: 'Failed to resolve ticket',
    }
  }
}

/**
 * Reject a ticket (human rejection)
 * @param {number} ticketId - Ticket ID
 * @param {string} reason - Rejection reason
 * @returns {Promise<Object>} - Updated ticket
 */
export const rejectTicket = async (ticketId, reason) => {
  try {
    const response = await axiosInstance.patch(`/api/ticket/${ticketId}/reject`, {
      reason,
    })
    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    console.error('Error rejecting ticket:', error)
    return {
      success: false,
      error: 'Failed to reject ticket',
    }
  }
}

/**
 * Get system statistics
 * @returns {Promise<Object>} - Statistics data
 */
export const getStatistics = async () => {
  try {
    const response = await axiosInstance.get('/api/stats')
    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    console.error('Error fetching statistics:', error)
    return {
      success: false,
      error: 'Failed to fetch statistics',
    }
  }
}

/**
 * Assign ticket to a team (admin only)
 * @param {number} ticketId - Ticket ID
 * @param {string} team - Team name
 * @param {string} note - Optional note
 * @returns {Promise<Object>} - Updated ticket
 */
export const assignTicketToTeam = async (ticketId, team, note = '') => {
  try {
    console.log('🔄 Assigning ticket:', { ticketId, team, note })
    const response = await axiosInstance.post(`/api/admin/ticket/${ticketId}/assign`, {
      team,
      note,
    })
    console.log('✅ Assignment successful:', response.data)
    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to assign ticket'
    console.error('❌ Assignment failed:', {
      ticketId,
      status: error.response?.status,
      error: errorMessage,
      fullError: error.response?.data
    })
    return {
      success: false,
      error: errorMessage,
    }
  }
}

/**
 * Reject ticket with custom message (admin only)
 * @param {number} ticketId - Ticket ID
 * @param {string} message - Rejection message to send to client
 * @returns {Promise<Object>} - Updated ticket
 */
export const rejectTicketWithMessage = async (ticketId, message) => {
  try {
    console.log('❌ Rejecting ticket:', { ticketId, messageLength: message.length })
    const response = await axiosInstance.post(`/api/admin/ticket/${ticketId}/reject`, {
      message,
    })
    console.log('✅ Rejection successful:', response.data)
    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to reject ticket'
    console.error('❌ Rejection failed:', {
      ticketId,
      status: error.response?.status,
      error: errorMessage,
      fullError: error.response?.data
    })
    return {
      success: false,
      error: errorMessage,
    }
  }
}

/**
 * Approve AI resolution (admin only)
 * @param {number} ticketId - Ticket ID
 * @param {string} note - Optional approval note
 * @returns {Promise<Object>} - Updated ticket
 */
export const approveAIResolution = async (ticketId, note = '') => {
  try {
    const response = await axiosInstance.post(`/api/admin/ticket/${ticketId}/approve-ai`, {
      note,
    })
    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    console.error('Error approving AI resolution:', error)
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to approve AI resolution',
    }
  }
}

export default axiosInstance
