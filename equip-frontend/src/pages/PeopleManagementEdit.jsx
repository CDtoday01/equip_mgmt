import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api";

const PeopleManagementEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    eip_account: "",
    department: "",
  });

  const [departments, setDepartments] = useState([]);

  useEffect(() => {
    api.get(`/users/${id}/`).then(res => {
      setFormData({
        name: res.data.name,
        email: res.data.email,
        eip_account: res.data.eip_account,
        department: res.data.department,
      });
    });

    api.get("/departments/").then(res => {
      setDepartments(res.data);
    });
  }, [id]);

  const handleChange = e => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value || null}));
  };

  const handleSave = async () => {
    try {
      await api.put(`/users/${id}/`, formData);
      alert("更新成功！");
      navigate(`/people/${id}`);
    } catch (err) {
      console.error("Update failed:", err);
      alert("更新失敗");
    }
  };

  return (
    <div>
      <h2>編輯人員</h2>

      <label>姓名：</label>
      <input name="name" value={formData.name} onChange={handleChange} />

      <br />

      <label>Email：</label>
      <input name="email" value={formData.email} onChange={handleChange} />

      <br />

      <label>EIP 帳號：</label>
      <input name="eip_account" value={formData.eip_account} onChange={handleChange} />

      <br />

      <label>部門：</label>
      <select name="department" value={formData.department ?? ""} onChange={handleChange}>
        <option value="">請選擇</option>
        {departments.map(dep => (
          <option key={dep.id} value={dep.id}>
            {dep.name}
          </option>
        ))}
      </select>

      <br /><br />

      <button onClick={handleSave}>儲存</button>
      <button onClick={() => navigate(`/people/${id}`)}>取消</button>
    </div>
  );
};

export default PeopleManagementEdit;
