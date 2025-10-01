import { useState, useEffect, useRef } from "react";
import { chatAPI } from "../services/api";
import websocketService from "../services/websocket";

export default function ChatWindow({ conversation, currentUser }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [typingUser, setTypingUser] = useState(null);
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  useEffect(() => {
    loadMessages();
    connectWebSocket();

    return () => {
      websocketService.disconnect();
    };
  }, [conversation.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const response = await chatAPI.getMessages(conversation.id);
      if (response.data.status === "success") {
        setMessages(response.data.data.messages);
      }
    } catch (error) {
      console.error("Error loading messages:", error);
    } finally {
      setLoading(false);
    }
  };

  const connectWebSocket = () => {
    websocketService.connect(conversation.id);

    websocketService.onConnection((isConnected) => {
      setConnected(isConnected);
    });

    websocketService.onMessage((message) => {
      setMessages((prev) => [...prev, message]);
    });

    websocketService.onTyping((data) => {
      if (data.is_typing) {
        setTypingUser(data.user_name);
        clearTimeout(typingTimeoutRef.current);
        typingTimeoutRef.current = setTimeout(() => {
          setTypingUser(null);
        }, 3000);
      } else {
        setTypingUser(null);
      }
    });
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !connected) return;

    websocketService.sendMessage(newMessage.trim());
    setNewMessage("");
  };

  const handleTyping = () => {
    if (connected) {
      websocketService.sendTyping(true);
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = setTimeout(() => {
        websocketService.sendTyping(false);
      }, 1000);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {conversation.name || conversation.display_name || "Chat"}
            </h2>
            <p className="text-sm text-gray-500">
              {connected ? (
                <span className="text-green-600">● Connected</span>
              ) : (
                <span className="text-gray-400">○ Connecting...</span>
              )}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {conversation.participants.slice(0, 3).map((participant) => (
              <div
                key={participant.id}
                className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-xs font-semibold"
                title={participant.full_name}
              >
                {participant.first_name[0]}
                {participant.last_name[0]}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => {
              const isOwn = message.sender_id === currentUser?.id;
              return (
                <div
                  key={message.id || index}
                  className={`flex ${isOwn ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md xl:max-w-lg ${
                      isOwn
                        ? "bg-primary-600 text-white"
                        : "bg-white text-gray-900"
                    } rounded-lg px-4 py-2 shadow-sm`}
                  >
                    {!isOwn && (
                      <p className="text-xs font-semibold mb-1 opacity-75">
                        {message.sender_name}
                      </p>
                    )}
                    <p className="break-words">{message.content}</p>
                    <p
                      className={`text-xs mt-1 ${
                        isOwn ? "text-primary-100" : "text-gray-500"
                      }`}
                    >
                      {formatTime(message.timestamp)}
                    </p>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Typing Indicator */}
      {typingUser && (
        <div className="px-4 py-2 text-sm text-gray-500 italic bg-gray-50">
          {typingUser} is typing...
        </div>
      )}

      {/* Message Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => {
              setNewMessage(e.target.value);
              handleTyping();
            }}
            placeholder="Type a message..."
            className="flex-1 input-field"
            disabled={!connected}
          />
          <button
            type="submit"
            disabled={!connected || !newMessage.trim()}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
