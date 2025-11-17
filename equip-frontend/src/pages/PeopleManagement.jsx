import React, { useState, useEffect } from "react";
import axios from "axios";

const PeopleManagement = () => {
  const [people, setPeople] = useState([]);
  const [selected, setSelected] = useState([]);
  const [showAction, setShowAction] = useState(false);
  const [departments, setDepartments] = useState([]);

  // Dialog 狀態
  const [dialogType, setDialogType] = useState(null);
  const [targetDepartment, setTargetDepartment] = useState("");
  const [updateFields, setUpdateFields] = useState({});

  useEffect(() => {
    fetchPeople();
    fetchDepartments();
  }, []);

  const fetchPeople = async () => {
    const response = await axios.get("/api/users/");
    setPeople(response.data);
  };

  const fetchDepartments = async () => {
    const response = await axios.get("/api/departments/");
    setDepartments(response.data);
  };

  // 勾選邏輯
  const toggleSelect = (id) => {
    const updated = selected.includes(id)
      ? selected.filter((x) => x !== id)
      : [...selected, id];
    setSelected(updated);
    setShowAction(updated.length > 0);
  };

  const selectAll = () => {
    setSelected(people.map((p) => p.id));
    setShowAction(true);
  };

  const deselectAll = () => {
    setSelected([]);
    setShowAction(false);
  };

  // 統一發送批量請求
  const sendBatchRequest = async (payload) => {
    await axios.post("/api/users/batch/", payload);
    setDialogType(null);
    fetchPeople();
    setSelected([]);
    setShowAction(false);
  };

  // 動作：離職
  const batchDeactivate = () => {
    sendBatchRequest({
      action: "deactivate",
      users: selected
    });
  };

  // 動作：刪除
  const batchDelete = () => {
    sendBatchRequest({
      action: "delete",
      users: selected
    });
  };

  // 動作：轉調
  const batchTransfer = () => {
    sendBatchRequest({
      action: "transfer",
      users: selected,
      department_id: targetDepartment
    });
  };

  // 動作：批量更新
  const batchUpdate = () => {
    const updateData = selected.map((id) => ({
      id,
      ...updateFields,
    }));

    sendBatchRequest({
      action: "update",
      users: updateData,
    });
  };

  return (
    <div>
      <h2>人員管理</h2>

      {showAction && (
        <div className="action-bar">
          <button onClick={() => setDialogType("transfer")}>批量轉調</button>
          <button onClick={() => setDialogType("update")}>批量更新</button>
          <button onClick={() => setDialogType("deactivate")}>標記離職</button>
          <button onClick={() => setDialogType("delete")}>刪除</button>
          <button onClick={selectAll}>全選</button>
          <button onClick={deselectAll}>取消全選</button>
        </div>
      )}

      <table className="user-table">
        <thead>
          <tr>
            <th></th>
            <th>姓名</th>
            <th>部門</th>
            <th>職稱</th>
            <th>EIP帳號</th>
          </tr>
        </thead>
        <tbody>
          {people.map((person) => (
            <tr key={person.id}>
              <td>
                <input
                  type="checkbox"
                  checked={selected.includes(person.id)}
                  onChange={() => toggleSelect(person.id)}
                />
              </td>
              <td>{person.name}</td>
              <td>{person.department_name}</td>
              <td>{person.title}</td>
              <td>{person.eip_account}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Dialogs */}
      {dialogType === "transfer" && (
        <div className="dialog">
          <h3>批量轉調</h3>
          <select onChange={(e) => setTargetDepartment(e.target.value)}>
            <option value="">請選擇部門</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
          <button onClick={batchTransfer}>確定</button>
          <button onClick={() => setDialogType(null)}>取消</button>
        </div>
      )}

      {dialogType === "update" && (
        <div className="dialog">
          <h3>批量更新欄位</h3>

          <input
            placeholder="新職稱"
            onChange={(e) =>
              setUpdateFields({ ...updateFields, title: e.target.value })
            }
          />

          <input
            placeholder="新分機/電話"
            onChange={(e) =>
              setUpdateFields({ ...updateFields, phone: e.target.value })
            }
          />

          <button onClick={batchUpdate}>套用</button>
          <button onClick={() => setDialogType(null)}>取消</button>
        </div>
      )}

      {dialogType === "deactivate" && (
        <div className="dialog">
          <h3>批量標記離職</h3>
          <p>確定要標記 {selected.length} 人為離職嗎？</p>
          <button onClick={batchDeactivate}>確定</button>
          <button onClick={() => setDialogType(null)}>取消</button>
        </div>
      )}

      {dialogType === "delete" && (
        <div className="dialog">
          <h3>刪除人員</h3>
          <p>⚠ 此操作無法復原。確定要刪除 {selected.length} 位人員？</p>
          <button onClick={batchDelete}>刪除</button>
          <button onClick={() => setDialogType(null)}>取消</button>
        </div>
      )}
    </div>
  );
};

export default PeopleManagement;
