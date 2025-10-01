import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - could trigger logout
      console.error("Unauthorized request");
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post("/users/register/", data),
  login: (data) => api.post("/users/login/", data),
  logout: () => api.post("/users/logout/"),
  getProfile: () => api.get("/users/profile/"),
  getUsers: () => api.get("/users/list/"),
};

// Chat API
export const chatAPI = {
  getConversations: () => api.get("/chat/conversations/"),
  createConversation: (data) => api.post("/chat/conversations/", data),
  getConversation: (id) => api.get(`/chat/conversations/${id}/`),
  getMessages: (conversationId, params) =>
    api.get(`/chat/conversations/${conversationId}/messages/`, { params }),
  healthCheck: () => api.get("/chat/health/"),
};

export default api;
