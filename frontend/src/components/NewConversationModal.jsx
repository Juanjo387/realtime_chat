import { useState, useEffect } from "react";
import { authAPI } from "../services/api";

export default function NewConversationModal({
  onClose,
  onCreateConversation,
  currentUserId,
}) {
  const [users, setUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await authAPI.getUsers();
      if (response.data.status === "success") {
        setUsers(response.data.data);
      }
    } catch (error) {
      setError("Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  const toggleUser = (userId) => {
    setSelectedUsers((prev) =>
      prev.includes(userId)
        ? prev.filter((id) => id !== userId)
        : [...prev, userId]
    );
  };

  const handleCreate = async () => {
    if (selectedUsers.length === 0) {
      setError("Please select at least one user");
      return;
    }

    setCreating(true);
    setError("");

    try {
      await onCreateConversation([currentUserId, ...selectedUsers]);
    } catch (error) {
      setError(
        error.response?.data?.message || "Failed to create conversation"
      );
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[80vh] flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              New Conversation
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : users.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No other users found
            </p>
          ) : (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700 mb-3">
                Select users to start a conversation:
              </p>
              {users.map((user) => (
                <button
                  key={user.id}
                  onClick={() => toggleUser(user.id)}
                  className={`w-full p-3 rounded-lg border-2 transition-colors text-left ${
                    selectedUsers.includes(user.id)
                      ? "border-primary-600 bg-primary-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center text-white font-semibold flex-shrink-0">
                      {user.first_name[0]}
                      {user.last_name[0]}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">
                        {user.full_name}
                      </p>
                      <p className="text-sm text-gray-500">{user.email}</p>
                    </div>
                    {selectedUsers.includes(user.id) && (
                      <svg
                        className="w-6 h-6 text-primary-600"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="p-6 border-t border-gray-200">
          <div className="flex space-x-3">
            <button onClick={onClose} className="flex-1 btn-secondary">
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={selectedUsers.length === 0 || creating}
              className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {creating
                ? "Creating..."
                : `Create ${selectedUsers.length > 1 ? "Group" : "Chat"}`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
