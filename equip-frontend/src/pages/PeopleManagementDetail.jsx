import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api";

const PeopleManagementDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [person, setPerson] = useState(null);

  useEffect(() => {
    api.get(`/users/${id}/`)
      .then(res => setPerson(res.data))
      .catch(err => console.error("Detail error:", err));
  }, [id]);

  if (!person) return <p>載入中...</p>;

  return (
    <div>
      <h2>人員資訊</h2>

      <p><strong>EIP：</strong> {person.eip_account}</p>
      <p><strong>姓名：</strong> {person.name}</p>
      <p><strong>身份證字號：</strong> {person.id_number}</p>
      <p><strong>Email：</strong> {person.email}</p>
      <p><strong>電話：</strong> {person.phone}</p>
      <p><strong>部門：</strong> {person.department_name ?? "無"}</p>
      <p><strong>職稱：</strong> {person.title}</p>

      <button onClick={() => navigate(`/people/${id}/edit`)}>編輯</button>
      <button onClick={() => navigate("/people")}>返回</button>
    </div>
  );
};

export default PeopleManagementDetail;
