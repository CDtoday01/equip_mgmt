import React, { useEffect, useState } from "react";
import GenericForm from "../components/GenericForm";
import api from "../api";

const PeopleManagement = () => {
  const [people, setPeople] = useState([]);
  const [editingPerson, setEditingPerson] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: "name", direction: "asc" });

  // =======================
  // 欄位設定
  // =======================
  const fields = [
    { name: "name", label: "姓名", type: "text" },
    { name: "id_number", label: "身份證字號", type: "text" },
    { name: "email", label: "信箱", type: "email" },
    { name: "phone", label: "電話", type: "text" },
    { name: "department", label: "部門", type: "text" },
    { name: "eip_account", label: "EIP帳號", type: "text" },
    { name: "title", label: "職稱", type: "text" },
  ];

  // =======================
  // 抓取人員資料
  // =======================
  const fetchPeople = async () => {
    try {
      const res = await api.get("users/");
      setPeople(res.data);
    } catch (err) {
      console.error("取得人員資料失敗:", err.response?.data || err);
    }
  };

  useEffect(() => {
    fetchPeople();
  }, []);

  // =======================
  // 單筆新增 / 編輯
  // =======================
  const handleAddSingle = async (person) => {
    try {
      const payload = {
        name: person.name?.trim() ?? "",
        id_number: person.id_number?.trim() ?? "",
        email: person.email?.trim() ?? "",
        phone: person.phone?.trim() ?? "",
        department: person.department?.trim() ?? "",
        eip_account: person.eip_account?.trim() ?? "",
        title: person.title?.trim() ?? "",
      };

      let res;
      if (editingPerson) {
        res = await api.put(`users/${editingPerson.id_number}/`, payload);
        setPeople((prev) =>
          prev.map((p) =>
            p.id_number === editingPerson.id_number ? res.data : p
          )
        );
        setEditingPerson(null);
      } else {
        res = await api.post("users/", payload);
        setPeople((prev) => [...prev, res.data]);
      }

      alert("資料已成功儲存！");
    } catch (err) {
      console.error("新增/更新失敗錯誤:", err.response?.data || err);
      alert("操作失敗，詳細資訊請查看 console");
    }
  };

  // =======================
  // CSV 匯入
  // =======================
  const handleAddCSV = async (csvData) => {
    try {
      const peopleList = csvData
        .map((row) => ({
          name: row["姓名"]?.trim() ?? "",
          id_number: row["身份證字號"]?.trim() ?? "",
          email: row["信箱"]?.trim() ?? "",
          phone: row["電話"]?.trim() ?? "",
          department: row["部門"]?.trim() ?? "",
          title: row["職稱"]?.trim() ?? "",
          eip_account: row["EIP帳號"]?.trim() ?? "",
        }))
        .filter((p) => p.name && p.id_number && p.eip_account && p.department);

      if (peopleList.length === 0) {
        alert("沒有有效資料可匯入。");
        return;
      }

      const res = await api.post("users/bulk/", peopleList);
      console.log("匯入結果：", res.data);
      alert(`CSV 匯入完成！新增 ${res.data.created} 筆、更新 ${res.data.updated} 筆。`);

      await fetchPeople(); // 匯入後重新抓最新資料
    } catch (err) {
      console.error("CSV 匯入整批失敗：", err.response?.data || err);
      alert("CSV 匯入失敗，詳細資訊請查看 console");
    }
  };

  // =======================
  // 刪除
  // =======================
  const handleDelete = async (id_number) => {
    if (!window.confirm("確定要刪除嗎？")) return;
    try {
      await api.delete(`users/${id_number}/`);
      setPeople((prev) => prev.filter((p) => p.id_number !== id_number));
      alert("刪除成功！");
    } catch (err) {
      console.error(err);
      alert("刪除失敗");
    }
  };

  const handleEdit = (person) => setEditingPerson(person);
  const cancelEdit = () => setEditingPerson(null);

  // =======================
  // 排序
  // =======================
  const handleSort = (key) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === "asc" ? "desc" : "asc",
    }));
  };

  const getSortIndicator = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === "asc" ? " ↑" : " ↓";
  };

  const sortedPeople = [...people].sort((a, b) => {
    const valA = (a[sortConfig.key] ?? "").toString().toLowerCase();
    const valB = (b[sortConfig.key] ?? "").toString().toLowerCase();
    if (valA < valB) return sortConfig.direction === "asc" ? -1 : 1;
    if (valA > valB) return sortConfig.direction === "asc" ? 1 : -1;
    return 0;
  });

  // =======================
  // UI
  // =======================
  return (
    <div style={{ padding: "20px" }}>
      <h1>人員管理</h1>
      <GenericForm
        fields={fields}
        onAddSingle={handleAddSingle}
        onAddCSV={handleAddCSV}
        initialValues={editingPerson || {}}
      />
      {editingPerson && (
        <button onClick={cancelEdit} style={{ marginBottom: "10px", backgroundColor: "#ccc" }}>
          取消編輯
        </button>
      )}

      <h2>人員列表</h2>
      {people.length === 0 ? (
        <p>目前沒有資料</p>
      ) : (
        <table border="1" cellPadding="5" cellSpacing="0">
          <thead>
            <tr>
              <th>#</th>
              <th onClick={() => handleSort("name")} style={{ cursor: "pointer" }}>
                姓名{getSortIndicator("name")}
              </th>
              <th onClick={() => handleSort("id_number")} style={{ cursor: "pointer" }}>
                身份證字號{getSortIndicator("id_number")}
              </th>
              <th>信箱</th>
              <th>電話</th>
              <th>部門</th>
              <th>職稱</th>
              <th>EIP帳號</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {sortedPeople.map((p, idx) => (
              <tr key={p.id_number}>
                <td>{idx + 1}</td>
                <td>{p.name}</td>
                <td>{p.id_number}</td>
                <td>{p.email}</td>
                <td>{p.phone}</td>
                <td>{p.department}</td>
                <td>{p.title}</td>
                <td>{p.eip_account}</td>
                <td>
                  <button onClick={() => handleEdit(p)} style={{ marginRight: "5px" }}>編輯</button>
                  <button onClick={() => handleDelete(p.id_number)}>刪除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default PeopleManagement;
