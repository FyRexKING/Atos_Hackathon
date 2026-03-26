# Complete Frontend Setup & Testing Guide

## Quick Start (3 Minutes)

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Start Development Server
```bash
npm run dev
```

You'll see:
```
VITE v5.0.0 ready in XXX ms

Local:    http://localhost:5173/
Press q to quit
```

### Step 3: Open in Browser
Click the link or paste into browser: **http://localhost:5173**

## ✅ What You'll See

A modern, clean dashboard with 3 columns:

### Left Column: Ticket Form
- Title input field
- Description text area
- "Submit Ticket" button
- "Demo Data" button (fills form with sample data)

### Middle Column: Results & Queue
- **Ticket Result** - Shows AI analysis (classification, confidence, decision)
- **Human Review Queue** - List of pending tickets

### Right Column: Approval Panel
- Selected ticket details
- Approve button (with resolution message)
- Reject button (with rejection reason)

## 🧪 Testing Workflow

### Test 1: Submit a Real Ticket

1. Fill in the form:
   - Title: "Cannot login to account"
   - Description: "I've tried multiple times but keep getting an authentication error"

2. Click "Submit Ticket"

3. See results:
   - Classification (category, priority, impact)
   - Confidence score (0-1)
   - Similar tickets
   - AI explanation
   - Decision (auto-resolve or human_review)

### Test 2: Use Demo Data

1. Click "Demo Data" button
2. Form auto-fills with sample ticket
3. Click "Submit Ticket"
4. See instant results

### Test 3: Review & Approve Tickets

1. Look at "Human Review Queue"
2. Click any pending ticket
3. See ticket details in Approval Panel
4. Try "Approve & Resolve":
   - Click button
   - Enter resolution: "Issue has been resolved"
   - Click "Confirm Approval"
5. Queue refreshes, ticket disappears

### Test 4: Reject a Ticket

1. Select another ticket from queue
2. Click "Reject & Return"
3. Enter reason: "Duplicate of another ticket"
4. Click "Confirm Rejection"
5. Queue refreshes

## 🎨 Features to Verify

### Colors & Styling
- Blue gradient background
- Cards with shadows
- Rounded corners on inputs
- Smooth transitions

### Confidence Badge Colors
- **Green** (≥80%): High confidence
- **Yellow** (60-79%): Medium confidence
- **Red** (<60%): Low confidence

### Priority Badge Colors
- **Red**: High priority
- **Yellow**: Medium priority
- **Green**: Low priority

### Responsive Design
1. Open DevTools (F12)
2. Toggle Device Toolbar
3. Test on mobile/tablet sizes
4. Verify layout stacks properly

## 🔧 Configuration

### Backend API URL
If backend is on different host/port, edit:
```
src/api/ticketApi.js
```

Change:
```javascript
const API_BASE_URL = 'http://localhost:8000'
```

To your backend URL.

## 🚨 Troubleshooting

### "Cannot GET /"
- Make sure you're on http://localhost:5173
- Check dev server is running (npm run dev)

### "Failed to fetch / Cannot connect to backend"
- Backend must be running on http://localhost:8000
- Check backend is started: http://localhost:8000/health
- Verify API_BASE_URL in ticketApi.js

### Form doesn't submit
- Check browser console (F12)
- Verify backend is accessible
- Check input validation (title min 5 chars, description min 10 chars)

### Queue doesn't show tickets
- Click "Refresh" button in queue
- Check backend has pending tickets
- Verify network in DevTools (F12 → Network tab)

### Styling looks wrong
- Hard refresh (Ctrl+F5 or Cmd+Shift+R)
- Clear browser cache
- Make sure npm dependencies installed

## 📦 Project Structure Explained

```
frontend/
├── src/
│   ├── api/ticketApi.js          ← All backend communication
│   ├── components/               ← Reusable UI components
│   │   ├── TicketForm.jsx        ← Form for creating tickets
│   │   ├── TicketResult.jsx      ← Display ticket analysis
│   │   ├── QueueList.jsx         ← List pending tickets
│   │   └── ApprovalPanel.jsx     ← Approve/reject interface
│   ├── pages/
│   │   └── Dashboard.jsx         ← Main layout/page
│   ├── App.jsx                   ← Root component
│   ├── main.jsx                  ← Entry point
│   └── index.css                 ← Global styles
├── index.html                    ← HTML template
├── vite.config.js               ← Build config
└── package.json                 ← Dependencies
```

## 🎯 Component Architecture

### Data Flow
```
Dashboard (state)
├── TicketForm
│   └── onSubmit() → submitTicket API
│       → passes result to parent
├── TicketResult
│   ← receives current ticket
├── QueueList
│   ← refreshTrigger from parent
│   → onSelectTicket() passes to parent
└── ApprovalPanel
    ← receives selected queue ticket
    → onActionComplete() triggers refresh
```

### State Management
- Dashboard holds state: `currentTicket`, `selectedQueueTicket`, `refreshKey`
- Components are presentational
- Parent-child communication via props/callbacks
- No external state library needed

## 🚀 Building for Production

```bash
npm run build
```

This creates optimized build in `dist/` folder.

To preview:
```bash
npm run preview
```

## 📝 Code Quality

All components have:
- JSDoc comments
- Clear variable names
- Proper error handling
- Loading states
- User feedback messages

## 🎓 Learning Resources

### Frontend Details
- See README.md in this directory

### Backend Details
- See ../backend/README.md
- See ../backend/EXAMPLES.md (API examples)
- See ../backend/IMPLEMENTATION.md (Architecture)

### Workflow Explanation
See ../backend/API_TESTING_GUIDE.md

## ✨ Features Implemented

✓ Responsive design (mobile, tablet, desktop)
✓ Form validation
✓ API integration (all endpoints)
✓ Error handling
✓ Loading states with spinners
✓ Success/error messages
✓ Color-coded badges
✓ Demo data button
✓ Queue refresh functionality
✓ Approval/rejection workflow
✓ Clean modern UI with Tailwind

## 🎉 You're Ready!

The frontend is fully functional and integrated with the backend API.

**Start testing:** http://localhost:5173

All features are working and ready to demo!
