import axios from "axios";

// Single axios instance for talking to the FastAPI backend
const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// In-memory token storage (cleared on page refresh — revisit later if you want persistence)
let authToken: string | null = null;

export function setAuthToken(token: string) {
  authToken = token;
}

export function getAuthToken() {
  return authToken;
}

export function clearAuthToken() {
  authToken = null;
}

// Attach JWT to every outgoing request automatically
api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

export default api;