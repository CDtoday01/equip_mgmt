import axios from "axios";

// 1. 建立主要的 api 實例
const api = axios.create({
  baseURL: "http://127.0.0.1:8000/",
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
    // 建議將緩衝時間稍微拉長一點，例如 2-3 分鐘，避免網路延遲導致邊界問題
    return exp - Date.now() < 60 * 1000; 
  } catch {
    return true;
  }
};

// ====== 重新刷新 access token ======
async function refreshAccessToken() {
  const refresh = getRefreshToken();
  if (!refresh) {
    throw new Error("No refresh token available");
  }

  try {
    // ✅ 修正重點：這裡不要用 api.post，改用 axios.post
    // 使用原始 axios 可以避開我們自己設定的 interceptors，防止無限迴圈
    const response = await axios.post("http://127.0.0.1:8000/api/users/token/refresh/", {
      refresh,
    });

    const newAccess = response.data.access;
    // 有些後端 refresh 也會回傳新的 refresh token，如果有就一起存
    const newRefresh = response.data.refresh; 
    saveTokens(newAccess, newRefresh || refresh);
    
    return newAccess;
  } catch (error) {
    // ✅ 如果連換發 Token 都失敗 (例如 401)，代表 Refresh Token 也過期了
    // 這時候必須強制登出，不能讓它拋出錯誤給攔截器去重試
    console.error("Refresh token expired or invalid", error);
    clearTokens();
    window.location.href = "/login";
    throw error; // 終止後續行為
  }
}

// ====== Request 攔截器 ======
api.interceptors.request.use(async (config) => {
  const url = config.url || "";

  // 略過登入與刷新
  if (url.includes("users/login") || url.includes("users/token/refresh")) {
    return config;
  }

  let token = getAccessToken();

  // 主動刷新機制
  if (token && isTokenExpiringSoon(token)) {
    try {
      // 這裡如果失敗，refreshAccessToken 內部已經會處理轉址
      token = await refreshAccessToken(); 
    } catch (err) {
      return Promise.reject(err);
    }
  }

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
}, (error) => Promise.reject(error));

// ====== Response 攔截器 ======
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // 如果 config 不存在 (極少數情況)，直接 reject
    if (!originalRequest) return Promise.reject(error);

    const status = error.response?.status;

    // ✅ 增加判斷：如果是 Refresh Token 的 API 報錯，絕對不要重試，直接 reject
    if (originalRequest.url.includes("users/token/refresh")) {
        return Promise.reject(error);
    }

    // 若 access token 過期 (401) 且尚未重試過
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const newAccess = await refreshAccessToken();
        
        // 更新 header
        api.defaults.headers.common["Authorization"] = `Bearer ${newAccess}`;
        originalRequest.headers["Authorization"] = `Bearer ${newAccess}`;
        
        // 重送原請求
        return api(originalRequest);
      } catch (refreshError) {
        // refreshAccessToken 裡面已經處理過登出了，這裡通常接不到錯誤，
        // 但為了保險起見，catch 住並 reject
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;