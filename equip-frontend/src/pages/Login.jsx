import React, { useState } from "react";
import axios from "axios"; // 登入用獨立 axios，不經過攔截器

const Login = () => {
  const [eipAccount, setEipAccount] = useState("");
  const [idNumber, setIdNumber] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/users/login/", {
        eip_account: eipAccount,
        password: idNumber
      }, { withCredentials: true });

      const { access, refresh } = response.data;
      localStorage.setItem("access_token", access);
      localStorage.setItem("refresh_token", refresh);

      window.location.href = "/";
    } catch (err) {
      console.error("Login failed:", err.response?.data || err.message);
      setError(err.response?.data?.detail || "登入失敗，請檢查帳號或密碼");
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "50px auto" }}>
      <h2>登入系統</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>EIP 帳號：</label>
          <input
            type="text"
            value={eipAccount}
            onChange={(e) => setEipAccount(e.target.value)}
            required
          />
        </div>
        <div style={{ marginTop: "10px" }}>
          <label>身份證字號：</label>
          <input
            type="password"
            value={idNumber}
            onChange={(e) => setIdNumber(e.target.value)}
            required
          />
        </div>
        <button type="submit" style={{ marginTop: "20px" }}>
          登入
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default Login;
