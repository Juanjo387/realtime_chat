# React Frontend Guide

## 🎉 Overview

The real-time chat application now includes a **modern React frontend** built with:

- **React 18** with Hooks
- **Vite** for lightning-fast development
- **Tailwind CSS** for beautiful styling
- **React Router** for navigation
- **WebSocket** integration for real-time messaging

## 🚀 Quick Start

### Using Docker (Recommended)

From the project root:

```bash
# Start all services (backend + frontend)
docker compose up --build

# Or start just the frontend
docker compose up frontend
```

**Access the application:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Local Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## ✨ Features

### 1. **User Authentication**

- Beautiful login and registration forms
- Real-time validation with error messages
- Session-based authentication
- Protected routes

### 2. **Real-Time Messaging**

- Instant message delivery via WebSockets
- Automatic reconnection on disconnect
- Message history from Redis
- Typing indicators
- Read receipts

### 3. **Conversation Management**

- Create 1-on-1 chats
- Create group conversations
- View all conversations
- Select users from list
- Beautiful conversation UI

### 4. **Modern UI/UX**

- Responsive design (mobile & desktop)
- Smooth animations
- Loading states
- Error handling
- Toast notifications
- Gradient backgrounds
- Modern typography

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/              # Reusable UI components
│   │   ├── ChatWindow.jsx      # Main chat interface
│   │   ├── ConversationList.jsx # Sidebar with conversations
│   │   ├── LoadingSpinner.jsx   # Loading indicator
│   │   └── NewConversationModal.jsx # Create new chat modal
│   │
│   ├── context/                 # React Context providers
│   │   └── AuthContext.jsx     # Global auth state
│   │
│   ├── pages/                   # Route pages
│   │   ├── Chat.jsx            # Main chat page
│   │   ├── Login.jsx           # Login page
│   │   └── Register.jsx        # Registration page
│   │
│   ├── services/                # External integrations
│   │   ├── api.js              # HTTP API client
│   │   └── websocket.js        # WebSocket service
│   │
│   ├── App.jsx                  # Main app with routing
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles + Tailwind
│
├── public/                      # Static assets
├── index.html                   # HTML template
├── package.json                 # Dependencies
├── vite.config.js               # Vite configuration
├── tailwind.config.js           # Tailwind theme
└── Dockerfile                   # Docker configuration
```

## 🔧 Key Components Explained

### AuthContext

Global authentication state manager:

```jsx
const { user, login, register, logout, isAuthenticated } = useAuth();

// Login
await login(email, password);

// Register
await register({
  email,
  first_name,
  last_name,
  password,
  password_confirm,
});

// Logout
await logout();
```

### API Service

Centralized API communication:

```javascript
import { authAPI, chatAPI } from "./services/api";

// Get all conversations
const response = await chatAPI.getConversations();

// Get messages for a conversation
const messages = await chatAPI.getMessages(conversationId, { limit: 50 });

// Create conversation
await chatAPI.createConversation({ participant_ids: [1, 2, 3] });
```

### WebSocket Service

Real-time messaging handler:

```javascript
import websocketService from "./services/websocket";

// Connect to conversation
websocketService.connect(conversationId);

// Send message
websocketService.sendMessage("Hello!");

// Send typing indicator
websocketService.sendTyping(true);

// Listen for messages
const unsubscribe = websocketService.onMessage((message) => {
  console.log("New message:", message);
});

// Cleanup
websocketService.disconnect();
unsubscribe();
```

## 🎨 UI Components

### Login Page

- Gradient background (purple to blue)
- Centered card layout
- Form validation
- Link to registration

### Register Page

- Multi-field form
- Real-time validation
- Error messages per field
- Password confirmation

### Chat Page

Three-column layout:

1. **Sidebar**: User profile, conversations list, new chat button
2. **Chat Window**: Messages, typing indicators, input field
3. **Modal**: User selection for new conversations

### Conversation List

- Avatar with initials
- Conversation name
- Participant count
- Unread badge
- Active state highlighting

### Chat Window

- Connection status indicator
- Message bubbles (own vs others)
- Timestamps
- Typing indicators
- Auto-scroll to bottom
- Send button

## 🎯 User Flow

1. **Registration**

   - User fills registration form
   - Frontend validates input
   - API creates user account
   - Auto-login and redirect to chat

2. **Login**

   - User enters credentials
   - API authenticates
   - Session cookie set
   - Redirect to chat

3. **Starting a Chat**

   - Click "New Chat" button
   - Modal opens with user list
   - Select one or more users
   - Create conversation
   - Automatically open chat

4. **Real-Time Messaging**
   - Select conversation
   - WebSocket connects
   - Load message history
   - Type and send messages
   - See typing indicators
   - Messages appear instantly

## 🔐 Authentication Flow

```
User → Login Form → API (/api/users/login/)
                     ↓
              Set Session Cookie
                     ↓
            Redirect to /chat
                     ↓
         AuthContext checks session
                     ↓
            Load user profile
                     ↓
          Render chat interface
```

## 📡 WebSocket Connection

```
Chat Page Mount
     ↓
Select Conversation
     ↓
WebSocket.connect(conversationId)
     ↓
Verify Authentication (cookies sent automatically)
     ↓
Check User is Participant
     ↓
Connection Established
     ↓
Receive Historical Messages (HTTP)
     ↓
Real-Time Updates (WebSocket)
```

## 🎨 Styling Guide

### Tailwind Classes

Custom classes defined in `index.css`:

```css
.btn-primary       /* Primary button with gradient */
/* Primary button with gradient */
.btn-secondary     /* Secondary button */
.input-field       /* Text input with focus styles */
.card; /* White card with shadow */
```

### Color Palette

```javascript
primary: {
  50:  '#f5f3ff',  // Lightest
  100: '#ede9fe',
  ...
  600: '#7c3aed',  // Main brand color
  ...
  900: '#4c1d95',  // Darkest
}
```

## ⚙️ Configuration

### Environment Variables

Create `frontend/.env`:

```env
# API endpoints
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000

# For production
# VITE_API_URL=https://your-domain.com/api
# VITE_WS_URL=wss://your-domain.com
```

### Vite Proxy (Development)

Already configured in `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://web:8000',
    changeOrigin: true,
  },
  '/ws': {
    target: 'ws://web:8000',
    ws: true,
  },
}
```

## 🐛 Troubleshooting

### Cannot connect to backend

**Problem**: Frontend can't reach API

**Solutions**:

```bash
# Check backend is running
curl http://localhost:8000/api/chat/health/

# Verify CORS settings in Django settings.py
CORS_ALLOW_ALL_ORIGINS = True  # For development

# Check environment variables
echo $VITE_API_URL
```

### WebSocket connection fails

**Problem**: Real-time messaging not working

**Solutions**:

1. Ensure user is logged in (check cookies)
2. Verify user is conversation participant
3. Check WebSocket URL in browser console
4. Ensure backend WebSocket server is running (Daphne)

### Styling not updating

**Problem**: CSS changes not appearing

**Solutions**:

```bash
# Rebuild Tailwind
npm run build

# Clear Vite cache
rm -rf node_modules/.vite

# Hard refresh browser
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)
```

### Module not found errors

**Problem**: Import errors in React

**Solutions**:

```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check file paths and extensions
# Import should match: import Component from './Component.jsx'
```

## 📦 Building for Production

```bash
# Build optimized production bundle
npm run build

# Output will be in dist/ directory

# Preview production build locally
npm run preview

# Files to deploy:
dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   └── index-[hash].css
└── vite.svg
```

### Deploy to Vercel/Netlify

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel

# Or use Netlify
netlify deploy --prod
```

## 🚢 Docker Deployment

The frontend is already configured in `docker-compose.yml`:

```yaml
frontend:
  build:
    context: ./frontend
  ports:
    - "3000:3000"
  environment:
    - VITE_API_URL=http://localhost:8000/api
    - VITE_WS_URL=ws://localhost:8000
  depends_on:
    - web
```

## 🎯 Next Steps / Future Enhancements

- [ ] File upload support (images, documents)
- [ ] Emoji picker
- [ ] Message reactions
- [ ] Message search
- [ ] User presence (online/offline status)
- [ ] Push notifications
- [ ] Dark mode
- [ ] Message threads/replies
- [ ] Voice messages
- [ ] Video calls (WebRTC)
- [ ] End-to-end encryption

## 📚 Resources

- [React Documentation](https://react.dev)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [React Router](https://reactrouter.com)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## 🤝 Contributing

1. Create feature branch
2. Make changes to frontend code
3. Test thoroughly (all browsers)
4. Ensure responsive design works
5. Submit pull request

## 📝 Testing the Frontend

### Manual Testing Checklist

- [ ] Registration with valid data succeeds
- [ ] Registration with invalid data shows errors
- [ ] Login with correct credentials works
- [ ] Login with wrong credentials fails
- [ ] Logout works and redirects to login
- [ ] Can create 1-on-1 conversation
- [ ] Can create group conversation
- [ ] Messages send and appear instantly
- [ ] Typing indicators work
- [ ] Unread counts update
- [ ] Works on mobile devices
- [ ] Works in different browsers

### Browser Compatibility

Tested and working in:

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## 🎉 Conclusion

You now have a fully functional, modern React frontend for your real-time chat application! The frontend provides:

✅ Beautiful, responsive UI
✅ Real-time WebSocket messaging
✅ Complete user authentication
✅ Conversation management
✅ Production-ready code
✅ Docker deployment support

**Start chatting now!**

```bash
docker compose up --build
# Open http://localhost:3000
```

---

**Built with ❤️ using React, Vite, and Tailwind CSS**
