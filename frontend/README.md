# AI Support Ticket System - Frontend

A modern React + Vite frontend for the AI-powered support ticket system with Human-in-the-Loop workflows.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Backend API running on http://localhost:8000

### Installation & Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

The application will start on **http://localhost:5173**

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── ticketApi.js         # API integration with Axios
│   ├── components/
│   │   ├── TicketForm.jsx       # Ticket submission form
│   │   ├── TicketResult.jsx     # Results display
│   │   ├── QueueList.jsx        # Pending tickets queue
│   │   └── ApprovalPanel.jsx    # Human approval interface
│   ├── pages/
│   │   └── Dashboard.jsx        # Main dashboard layout
│   ├── App.jsx                  # Root component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── index.html                   # HTML template
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind CSS config
├── postcss.config.js           # PostCSS config
└── package.json                # Dependencies
```

## 🎨 Features

### 1. Ticket Submission Form
- Clean input form with title and description
- Input validation (min length requirements)
- Loading state with spinner
- Demo data button for quick testing
- Error messages

### 2. Ticket Analysis Display
- Category, Priority, Impact badges
- Confidence score with visual progress bar
- Color-coded confidence (green/yellow/red)
- Similar tickets display
- AI explanation
- Suggested resolution (if auto-resolved)

### 3. Human Queue Management
- List of pending tickets awaiting human review
- Refresh functionality
- Click to select ticket for review
- Priority and confidence badges
- Timestamp display

### 4. Approval Panel
- Approve with custom resolution message
- Reject with reason
- Error handling
- Success confirmation
- Auto-refresh queue after action

### 5. Responsive Design
- Mobile-friendly layout
- 3-column grid on desktop
- 1-column stack on mobile
- Tailwind CSS styling
- Clean modern UI

## 🔌 API Integration

All API calls go through `/src/api/ticketApi.js`:

```javascript
// Submit a ticket
submitTicket({ title: "...", description: "..." })

// Get pending tickets
getPendingTickets()

// Get specific ticket
getTicket(ticketId)

// Resolve a ticket
resolveTicket(ticketId, resolution)

// Reject a ticket
rejectTicket(ticketId, reason)

// Get statistics
getStatistics()
```

### Base URL
```
http://localhost:8000
```

### Typical Workflow

1. **User submits ticket** via form
   - Validate inputs
   - Send to backend API
   - Display results

2. **System analyzes ticket**
   - Classification (category, priority, impact)
   - Similarity search
   - Confidence calculation
   - Decision (auto-resolve or human review)

3. **Human reviews if needed**
   - Select ticket from queue
   - Review AI analysis
   - Approve with custom message
   - Or reject with reason

## 🎯 Component Details

### TicketForm
- Controlled component with validation
- Submits to `/api/ticket` endpoint
- Shows loading spinner during submission
- Demo data button loads sample ticket

### TicketResult
- Displays full ticket analysis
- Shows classification details
- Displays confidence with progress bar
- Lists similar tickets
- Shows AI explanation
- Displays suggested resolution

### QueueList
- Fetches pending tickets from backend
- Selectable ticket items
- Shows priority and confidence badges
- Refresh button
- Empty state message

### ApprovalPanel
- Two-stage approval/rejection
- Text input for messages
- Error and success messages
- Loading state
- Triggers queue refresh on action

### Dashboard
- Main layout component
- 3-column grid layout
- State management
- Coordinates all components

## 🎨 Styling

### Colors
- Primary: Blue (#2563eb)
- Success: Green (#16a34a)
- Warning: Yellow (#ea8c15)
- Danger: Red (#dc2626)

### Components
- Cards with shadows
- Rounded corners
- Smooth transitions
- Gradient backgrounds
- Responsive grid

## 🔒 Error Handling

- API error messages displayed to user
- Validation errors for form inputs
- Loading states during API calls
- Error recovery options (refresh, retry)
- Try-catch blocks in API calls

## 🧪 Testing

### Manual Testing Workflow

1. **Open application**
   - Navigate to http://localhost:5173
   - Verify all components load

2. **Submit a ticket**
   - Fill in title and description
   - Click "Submit Ticket"
   - See analysis results

3. **Test demo data**
   - Click "Demo Data" button
   - Form fills with sample data
   - Submit and see results

4. **Review queue**
   - Click on ticket in queue
   - See ticket details in approval panel
   - Test approve/reject actions

5. **Test approval workflow**
   - Click "Approve & Resolve"
   - Enter resolution message
   - Confirm approval
   - Queue refreshes automatically

## 📦 Dependencies

- **react** 18.2.0 - UI library
- **react-dom** 18.2.0 - React DOM rendering
- **axios** 1.6.0 - HTTP client
- **tailwindcss** 3.3.6 - Utility CSS framework
- **vite** 5.0.8 - Build tool

## 🚀 Build & Deploy

### Development Build
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 🔗 Integration with Backend

The frontend expects the backend API to be running on:
```
http://localhost:8000
```

If running on a different host/port, update the `API_BASE_URL` in:
```
src/api/ticketApi.js
```

## 📝 Environment Variables

Currently, no environment variables are needed. To add them:

1. Create `.env` file in root directory
2. Add variables (e.g., `VITE_API_URL=...`)
3. Update `ticketApi.js` to use `import.meta.env.VITE_*`

## 🎓 Learning Resources

See backend documentation in:
- `../backend/README.md` - Backend setup
- `../backend/EXAMPLES.md` - API examples
- `../backend/IMPLEMENTATION.md` - Architecture details

## ⚡ Performance

- Fast initial load (Vite)
- Efficient API calls with Axios
- Component-level state management
- No unnecessary re-renders
- Optimized Tailwind CSS

## 🐛 Troubleshooting

### "Cannot connect to backend"
- Verify backend is running on http://localhost:8000
- Check API Base URL in `ticketApi.js`
- Check CORS configuration on backend

### "Form submission fails"
- Check browser console for errors
- Verify backend API is accessible
- Check input validation requirements

### "Queue doesn't update"
- Click "Refresh" button in queue
- Check browser network tab
- Verify backend is returning data

## 📞 Support

For backend issues, see backend documentation.
For frontend issues, check component console logs.

## 📄 License

Built as part of AI Support Ticket System project.
