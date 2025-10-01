class WebSocketService {
  constructor() {
    this.socket = null;
    this.conversationId = null;
    this.messageHandlers = [];
    this.typingHandlers = [];
    this.connectionHandlers = [];
    this.errorHandlers = [];
  }

  connect(conversationId) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.disconnect();
    }

    this.conversationId = conversationId;
    const wsUrl = `${
      import.meta.env.VITE_WS_URL || "ws://localhost:8000"
    }/ws/chat/${conversationId}/`;

    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log("WebSocket connected");
      this.connectionHandlers.forEach((handler) => handler(true));
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    this.socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      this.errorHandlers.forEach((handler) => handler(error));
    };

    this.socket.onclose = () => {
      console.log("WebSocket disconnected");
      this.connectionHandlers.forEach((handler) => handler(false));
    };
  }

  handleMessage(data) {
    switch (data.type) {
      case "message":
        this.messageHandlers.forEach((handler) => handler(data.message));
        break;
      case "typing":
        this.typingHandlers.forEach((handler) => handler(data));
        break;
      case "connection_established":
        console.log("Connection established:", data.message);
        break;
      case "error":
        console.error("WebSocket error:", data.message);
        this.errorHandlers.forEach((handler) => handler(data.message));
        break;
      default:
        console.log("Unknown message type:", data);
    }
  }

  sendMessage(content) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(
        JSON.stringify({
          type: "message",
          content: content,
        })
      );
    } else {
      console.error("WebSocket is not connected");
    }
  }

  sendTyping(isTyping) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(
        JSON.stringify({
          type: "typing",
          is_typing: isTyping,
        })
      );
    }
  }

  sendReadReceipt() {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(
        JSON.stringify({
          type: "read",
        })
      );
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.conversationId = null;
    }
  }

  onMessage(handler) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter((h) => h !== handler);
    };
  }

  onTyping(handler) {
    this.typingHandlers.push(handler);
    return () => {
      this.typingHandlers = this.typingHandlers.filter((h) => h !== handler);
    };
  }

  onConnection(handler) {
    this.connectionHandlers.push(handler);
    return () => {
      this.connectionHandlers = this.connectionHandlers.filter(
        (h) => h !== handler
      );
    };
  }

  onError(handler) {
    this.errorHandlers.push(handler);
    return () => {
      this.errorHandlers = this.errorHandlers.filter((h) => h !== handler);
    };
  }

  isConnected() {
    return this.socket && this.socket.readyState === WebSocket.OPEN;
  }
}

export default new WebSocketService();
