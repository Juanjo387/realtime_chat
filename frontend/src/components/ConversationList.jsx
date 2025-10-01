export default function ConversationList({
  conversations,
  selectedConversation,
  onSelectConversation,
  loading,
}) {
  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500 p-4 text-center">
        <p className="text-sm">No conversations yet. Start a new chat!</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {conversations.map((conversation) => (
        <button
          key={conversation.id}
          onClick={() => onSelectConversation(conversation)}
          className={`w-full p-4 border-b border-gray-200 hover:bg-gray-50 transition-colors text-left ${
            selectedConversation?.id === conversation.id ? "bg-primary-50" : ""
          }`}
        >
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center text-white font-semibold flex-shrink-0">
              {conversation.is_group ? (
                <svg
                  className="w-6 h-6"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                </svg>
              ) : (
                conversation.participants[0]?.first_name?.[0] || "?"
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="font-medium text-gray-900 truncate">
                  {conversation.name || conversation.display_name || "Chat"}
                </p>
                {conversation.unread_count > 0 && (
                  <span className="ml-2 bg-primary-600 text-white text-xs rounded-full px-2 py-1">
                    {conversation.unread_count}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-500 truncate">
                {conversation.participants.length} participant
                {conversation.participants.length !== 1 ? "s" : ""}
              </p>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
