// src/api.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/",
});

// ====== Token 相關 ======
const getAccessToken = () => localStorage.getItem("access_token");
const getRefreshToken = () => localStorage.getItem("refresh_token");

const saveTokens = (access, refresh) => {
  localStorage.setItem("access_token", access);
  if (refresh) localStorage.setItem("refresh_token", refresh);
};

const clearTokens = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};

// ====== 主動檢查 token 是否快過期 ======
const isTokenExpiringSoon = (token) => {
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const exp = payload.exp * 1000;
    return exp - Date.now() < 60 * 1000; // 少於60秒視為快過期
  } catch {
    return true;
  }
};

// ====== 重新刷新 access token ======
async function refreshAccessToken() {
  const refresh = getRefreshToken();
  if (!refresh) throw new Error("No refresh token");

  const response = await axios.post("http://127.0.0.1:8000/api/users/refresh/", {
    refresh,
  });

  const newAccess = response.data.access;
  saveTokens(newAccess, refresh);
  return newAccess;
}

// ====== 攔截器設定 ======
api.interceptors.request.use(async (config) => {
  const url = config.url || "";

  // 不對登入或刷新 API 附加 token
  if (url.includes("users/login") || url.includes("users/token/refresh")) {
    return config;
  }

  let token = getAccessToken();

  // 主動刷新
  if (isTokenExpiringSoon(token)) {
    try {
      token = await refreshAccessToken();
    } catch (err) {
      clearTokens();
      window.location.href = "/login";
      throw err;
    }
  }

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// 被動刷新
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    // 若 access token 過期 → 試著 refresh
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const newAccess = await refreshAccessToken();
        api.defaults.headers.common["Authorization"] = `Bearer ${newAccess}`;
        originalRequest.headers["Authorization"] = `Bearer ${newAccess}`;
        return api(originalRequest);
      } catch {
        clearTokens();
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;
