import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { chatAPI, authAPI } from "../services/api";
import ConversationList from "../components/ConversationList";
import ChatWindow from "../components/ChatWindow";
import NewConversationModal from "../components/NewConversationModal";

export default function Chat() {
  const { user, logout } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [showNewChat, setShowNewChat] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const response = await chatAPI.getConversations();
      if (response.data.status === "success") {
        setConversations(response.data.data);
      }
    } catch (error) {
      console.error("Error loading conversations:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = async (participantIds) => {
    try {
      const response = await chatAPI.createConversation({
        participant_ids: participantIds,
      });

      if (response.data.status === "success") {
        const newConversation = response.data.data;
        setConversations([newConversation, ...conversations]);
        setSelectedConversation(newConversation);
        setShowNewChat(false);
      }
    } catch (error) {
      console.error("Error creating conversation:", error);
      throw error;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-bold text-gray-900">Messages</h1>
            <button
              onClick={logout}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>
          </div>

          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold">
              {user?.first_name?.[0]}
              {user?.last_name?.[0]}
            </div>
            <div className="flex-1">
              <p className="font-medium text-gray-900">{user?.full_name}</p>
              <p className="text-sm text-gray-500">{user?.email}</p>
            </div>
          </div>
        </div>

        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={() => setShowNewChat(true)}
            className="w-full btn-primary"
          >
            + New Chat
          </button>
        </div>

        {/* Conversations List */}
        <ConversationList
          conversations={conversations}
          selectedConversation={selectedConversation}
          onSelectConversation={setSelectedConversation}
          loading={loading}
        />
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <ChatWindow conversation={selectedConversation} currentUser={user} />
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                No conversation selected
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Choose a conversation or start a new one
              </p>
            </div>
          </div>
        )}
      </div>

      {/* New Conversation Modal */}
      {showNewChat && (
        <NewConversationModal
          onClose={() => setShowNewChat(false)}
          onCreateConversation={handleNewConversation}
          currentUserId={user?.id}
        />
      )}
    </div>
  );
}
