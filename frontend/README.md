# Real-Time Chat Frontend

Modern React frontend for the real-time chat application built with Vite, React Router, and Tailwind CSS.

## Features

- 🔐 **User Authentication** - Login and registration
- 💬 **Real-Time Messaging** - WebSocket integration for instant messaging
- 👥 **Conversation Management** - Create 1-on-1 or group chats
- ⌨️ **Typing Indicators** - See when others are typing
- 🎨 **Modern UI** - Beautiful interface with Tailwind CSS
- 📱 **Responsive Design** - Works on all devices
- 🔔 **Unread Indicators** - Track unread messages

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **WebSocket** - Real-time communication

## Getting Started

### Development with Docker

The easiest way to run the frontend is with Docker Compose (from the root directory):

```bash
docker compose up frontend
```

The app will be available at http://localhost:3000

### Local Development

1. **Install dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Set environment variables**

   Create a `.env` file:

   ```env
   VITE_API_URL=http://localhost:8000/api
   VITE_WS_URL=ws://localhost:8000
   ```

3. **Start development server**

   ```bash
   npm run dev
   ```

4. **Access the application**

   Open http://localhost:3000 in your browser

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable components
│   │   ├── ChatWindow.jsx
│   │   ├── ConversationList.jsx
│   │   ├── LoadingSpinner.jsx
│   │   └── NewConversationModal.jsx
│   ├── context/          # React contexts
│   │   └── AuthContext.jsx
│   ├── pages/            # Page components
│   │   ├── Chat.jsx
│   │   ├── Login.jsx
│   │   └── Register.jsx
│   ├── services/         # API and WebSocket services
│   │   ├── api.js
│   │   └── websocket.js
│   ├── App.jsx           # Main app component
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── index.html            # HTML template
├── vite.config.js        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
└── package.json          # Dependencies

```

## Key Components

### AuthContext

Manages user authentication state across the application.

```jsx
import { useAuth } from "./context/AuthContext";

const { user, login, logout, isAuthenticated } = useAuth();
```

### API Service

Handles all HTTP requests to the backend.

```javascript
import { authAPI, chatAPI } from "./services/api";

// Authentication
await authAPI.login({ email, password });
await authAPI.register(userData);

// Chat
const conversations = await chatAPI.getConversations();
const messages = await chatAPI.getMessages(conversationId);
```

### WebSocket Service

Manages real-time WebSocket connections.

```javascript
import websocketService from "./services/websocket";

// Connect to a conversation
websocketService.connect(conversationId);

// Send a message
websocketService.sendMessage(content);

// Listen for messages
websocketService.onMessage((message) => {
  console.log("New message:", message);
});
```

## Features in Detail

### Authentication

- Session-based authentication with cookies
- Protected routes for authenticated users
- Automatic redirect on login/logout

### Real-Time Messaging

- Instant message delivery via WebSockets
- Automatic reconnection on disconnect
- Message history loaded from API

### Conversations

- Create 1-on-1 or group conversations
- Search and select users
- View conversation participants

### UI/UX

- Smooth scrolling to latest messages
- Visual indicators for own vs. others' messages
- Typing indicators
- Connection status
- Loading states

## Environment Variables

| Variable       | Description     | Default                     |
| -------------- | --------------- | --------------------------- |
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api` |
| `VITE_WS_URL`  | WebSocket URL   | `ws://localhost:8000`       |

## Building for Production

```bash
# Build the application
npm run build

# Preview the build
npm run preview
```

The build output will be in the `dist` directory.

## Customization

### Changing Theme Colors

Edit `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#your-color',
        600: '#your-darker-color',
        // ... other shades
      },
    },
  },
}
```

### Adding New Routes

1. Create page component in `src/pages/`
2. Add route in `src/App.jsx`:

```jsx
<Route path="/your-route" element={<YourComponent />} />
```

## Troubleshooting

### Can't connect to backend

- Ensure the backend is running on port 8000
- Check CORS settings in Django
- Verify environment variables

### WebSocket connection fails

- Check that user is authenticated
- Verify WebSocket URL is correct
- Ensure user is a conversation participant

### Styling issues

- Run `npm run build` to regenerate Tailwind classes
- Clear browser cache
- Check for conflicting CSS

## Contributing

1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - see root LICENSE file
