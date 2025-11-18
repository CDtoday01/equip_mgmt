import React, { useEffect, useState, useCallback } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";

const PeopleManagement = () => {
  const navigate = useNavigate();
  const [people, setPeople] = useState([]);

  const fetchPeople = useCallback(async () => {
    try {
      const res = await api.get("/users/");
      setPeople(res.data);
    } catch (err) {
      console.error("Load people failed:", err);
    }
  }, []);

  useEffect(() => {
    fetchPeople();
  }, [fetchPeople]);

  return (
    <div>
      <h2>人員管理</h2>

      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>EIP</th>
            <th>姓名</th>
            <th>身份證字號</th>
            <th>信箱</th>
            <th>電話</th>
            <th>部門</th>
            <th>職稱</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {people.map(p => (
            <tr key={p.id}>
              <td>{p.eip_account}</td>
              <td>{p.name}</td>
              <td>{p.id_number}</td>
              <td>{p.email}</td>
              <td>{p.phone}</td>
              <td>{p.department_name}</td>
              <td>{p.title}</td>
              <td>
                <button onClick={() => navigate(`/people/${p.id}`)}>
                  查看
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

    </div>
  );
};

export default PeopleManagement;
