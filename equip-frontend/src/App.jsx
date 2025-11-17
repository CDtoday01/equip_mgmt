import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import PeopleManagement from "./pages/PeopleManagement";
import AssetManagement from "./pages/AssetManagement";
import InventoryRecords from "./pages/InventoryRecords";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import Login from "./pages/Login";

const AppContent = ({ isAuthenticated, setIsAuthenticated }) => {
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    setIsAuthenticated(false);
  };

  return (
    <div style={{ padding: "20px" }}>
      {isAuthenticated && (
        <nav style={{ marginBottom: "20px" }}>
          <Link to="/">🏠 首頁</Link> |{" "}
          <Link to="/users">👥 人員管理</Link> |{" "}
          <Link to="/assets">💼 資產管理</Link> |{" "}
          <Link to="/inventory">📦 出入庫紀錄</Link> |{" "}
          <Link to="/reports">📊 報表</Link> |{" "}
          <Link to="/settings">⚙️ 系統設定</Link> |{" "}
          <button onClick={handleLogout} style={{ marginLeft: "10px" }}>
            登出
          </button>
        </nav>
      )}

      <Routes>
        <Route
          path="/"
          element={isAuthenticated ? <h1>資產管理系統首頁</h1> : <Navigate to="/login" replace />}
        />
        <Route
          path="/users"
          element={isAuthenticated ? <PeopleManagement /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/assets"
          element={isAuthenticated ? <AssetManagement /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/inventory"
          element={isAuthenticated ? <InventoryRecords /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/reports"
          element={isAuthenticated ? <Reports /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/settings"
          element={isAuthenticated ? <Settings /> : <Navigate to="/login" replace />}
        />
        <Route path="/login" element={<Login onLogin={() => setIsAuthenticated(true)} />} />
      </Routes>
    </div>
  );
};

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem("access_token"));

  return (
    <Router>
      <AppContent isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
    </Router>
  );
};

export default App;
