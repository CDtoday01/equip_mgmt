import React, { useState, useEffect } from "react";
import api from "../api";

// === shadcn component imports ===
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Input } from "@/components/ui/input";

const PeopleManagement = () => {
  const [people, setPeople] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [showRetired, setShowRetired] = useState(true);

  const [searchTerm, setSearchTerm] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("全部部門");

  // === 分頁 ===
  const pageSizeOptions = [10, 20, 50, 100, -1]; // -1 表示全部
  const [pageSize, setPageSize] = useState(10);
  const [page, setPage] = useState(1);

  const [selectedDept, setSelectedDept] = useState("");
  const [newDeptName, setNewDeptName] = useState("");

  // === CSV 新增/更新 ===
  const [addUpdateFile, setAddUpdateFile] = useState(null);
  const [addUpdateCsv, setAddUpdateCsv] = useState(null);
  const [addUpdatePreview, setAddUpdatePreview] = useState(null);
  const [showAddUpdateModal, setShowAddUpdateModal] = useState(false);

  // === CSV 離職 ===
  const [retireFile, setRetireFile] = useState(null);
  const [retireCsv, setRetireCsv] = useState(null);
  const [retirePreview, setRetirePreview] = useState(null);
  const [showRetireModal, setShowRetireModal] = useState(false);

  // === 中文欄位 mapping ===
  const fieldMapAddUpdate = {
    "姓名": "name",
    "身份證字號": "id_number",
    "信箱": "email",
    "電話": "phone",
    "EIP帳號": "eip_account",
    "部門": "department_name",
    "職稱": "title"
  };

  const fieldMapRetire = {
    "姓名": "name",
    "EIP帳號": "eip_account"
  };

  useEffect(() => {
    fetchPeople();
    fetchDepartments();
  }, []);

  const fetchPeople = async () => {
    try {
      const res = await api.get("/api/users/");
      setPeople(res.data.map(p => ({ ...p, selected: false })));
    } catch (err) {
      console.error(err);
    }
  };

  const fetchDepartments = async () => {
    try {
      const res = await api.get("/api/departments/");
      setDepartments(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const getSelectedIds = () => people.filter(p => p.selected).map(p => p.id);

  const toggleSelectAll = (checked) => {
    setPeople(prev => prev.map(p => ({ ...p, selected: checked })));
  };

  const handleBatchAction = async (action, extraData = {}) => {
    const ids = getSelectedIds();
    if (ids.length === 0) return alert("請先選取人員");

    if (action === "retire" && !window.confirm("確定要將選取人員設為離職嗎？")) return;

    try {
      await api.post("/api/users/batch/", { action, ids, ...extraData });
      fetchPeople();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || `${action} 失敗`);
    }
  };

  // === 部門轉移 ===
  const handleTransfer = async () => {
    if (!selectedDept && !newDeptName) return alert("請選擇或輸入部門名稱");

    let department_id = selectedDept;

    if (selectedDept === "__new__") {
      if (!newDeptName) return alert("請輸入新部門名稱");
      try {
        const res = await api.post("/api/departments/", { name: newDeptName });
        department_id = res.data.id;
        setDepartments(prev => [...prev, res.data]);
      } catch (err) {
        console.error(err);
        return alert("新增部門失敗");
      }
    }

    handleBatchAction("transfer", { department_id });
    setSelectedDept("");
    setNewDeptName("");
  };

  // === CSV - 新增/更新 ===
  const handleAddUpdateFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setAddUpdateFile(file);

    const reader = new FileReader();
    reader.onload = () => {
      const lines = reader.result.split(/\r?\n/).filter(Boolean);
      if (lines.length < 2) return alert("CSV 內容太少");

      const headers = lines[0].split(",").map(h => h.trim());
      const jsonArray = lines.slice(1).map(line => {
        const values = line.split(",").map(v => v.trim());
        const obj = {};
        headers.forEach((h, i) => {
          const key = fieldMapAddUpdate[h];
          if (key) obj[key] = values[i] || "";
        });
        return obj;
      });

      setAddUpdateCsv(jsonArray);
      setAddUpdatePreview(jsonArray);
      setShowAddUpdateModal(true);
    };

    reader.readAsText(file);
  };

  const handleConfirmAddUpdate = async () => {
    if (!addUpdateCsv || addUpdateCsv.length === 0) return alert("沒有資料可上傳");

    try {
      await api.post("/api/users/batch/", { action: "import", data: addUpdateCsv });
      setAddUpdateFile(null);
      setAddUpdateCsv(null);
      setAddUpdatePreview(null);
      setShowAddUpdateModal(false);
      fetchPeople();
    } catch (err) {
      console.error(err);
      alert("匯入失敗");
    }
  };

  // === CSV - 離職 ===
  const handleRetireFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setRetireFile(file);

    const reader = new FileReader();
    reader.onload = () => {
      const lines = reader.result.split(/\r?\n/).filter(Boolean);
      if (lines.length < 2) return alert("CSV 內容太少");

      const headers = lines[0].split(",").map(h => h.trim());
      const jsonArray = lines.slice(1).map(line => {
        const values = line.split(",").map(v => v.trim());
        const obj = {};
        headers.forEach((h, i) => {
          const key = fieldMapRetire[h];
          if (key) obj[key] = values[i] || "";
        });
        return obj;
      });

      setRetireCsv(jsonArray);

      const toRetire = [];
      const unmatched = [];

      jsonArray.forEach(row => {
        const match = people.find(p => p.eip_account === row.eip_account && p.name === row.name);
        if (match && match.is_active) {
          toRetire.push({ id: match.id, name: match.name, eip_account: match.eip_account });
        } else {
          unmatched.push({ 姓名: row.name, "EIP帳號": row.eip_account, status: match ? "已離職" : "未匹配" });
        }
      });

      setRetirePreview({ toRetire, unmatched });
      setShowRetireModal(true);
    };

    reader.readAsText(file);
  };

  const handleConfirmRetire = async () => {
    if (!retirePreview || retirePreview.toRetire.length === 0) return alert("沒有可離職的員工");

    setShowRetireModal(false);
    const ids = retirePreview.toRetire.map(p => p.id);

    try {
      await api.post("/api/users/batch/", { action: "retire", ids });
      setRetireFile(null);
      setRetireCsv(null);
      setRetirePreview(null);
      fetchPeople();
    } catch (err) {
      console.error(err);
      alert("離職操作失敗");
    }
  };

  // === 搜尋 + 篩選 ===
  const filteredPeople = people
    .filter(p => showRetired || p.is_active)
    .filter(p => (departmentFilter === "全部部門" ? true : p.department_name === departmentFilter))
    .filter(p => {
      const t = searchTerm.trim().toLowerCase();
      if (!t) return true;
      return (
        (p.name || "").toLowerCase().includes(t) ||
        (p.eip_account || "").toLowerCase().includes(t) ||
        (p.id_number || "").toLowerCase().includes(t) ||
        (p.email || "").toLowerCase().includes(t) ||
        (p.phone || "").toLowerCase().includes(t) ||
        (p.title || "").toLowerCase().includes(t) ||
        (p.department_name || "").toLowerCase().includes(t)
      );
    });

  // === 分頁 ===
  const total = filteredPeople.length;
  const totalPages = pageSize === -1 ? 1 : Math.ceil(total / pageSize);

  const paginated = pageSize === -1
    ? filteredPeople
    : filteredPeople.slice((page - 1) * pageSize, page * pageSize);

  const changePageSize = (size) => {
    setPageSize(size);
    setPage(1);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">人員資料表</h2>

      <div className="flex items-center gap-4 mb-4">
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={showRetired} onChange={(e) => setShowRetired(e.target.checked)} />
          顯示離職員工
        </label>
      </div>

      {/* === 搜尋 & 部門篩選 === */}
      <div className="flex gap-4 mb-4">
        <Input
          placeholder="搜尋姓名 / EIP帳號 / 身分證字號…"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          className="w-full"
        />

        <Select
          value={departmentFilter}
          onValueChange={setDepartmentFilter}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="全部部門" />
          </SelectTrigger>
          <SelectContent className="bg-white border rounded shadow-md">
            <SelectItem value="全部部門">全部部門</SelectItem>
            {departments.map(d => (
              <SelectItem key={d.id} value={String(d.name)}>
                {d.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* === CSV 上傳按鈕 === */}
      <div className="flex gap-4 mb-4">
        <Button onClick={() => document.getElementById("uploadAddUpdate").click()}>上傳 CSV (新增/更新)</Button>
        <input id="uploadAddUpdate" type="file" accept=".csv" style={{ display: "none" }} onChange={handleAddUpdateFileSelect} />
        {addUpdateFile && <span>{addUpdateFile.name}</span>}

        <Button onClick={() => document.getElementById("uploadRetire").click()}>上傳 CSV (離職)</Button>
        <input id="uploadRetire" type="file" accept=".csv" style={{ display: "none" }} onChange={handleRetireFileSelect} />
        {retireFile && <span>{retireFile.name}</span>}
      </div>

      {/* === 分頁（上） === */}
      <div className="flex justify-between items-center my-2">
        <div className="flex items-center gap-2">
          每頁：
          <Select value={String(pageSize)} onValueChange={(v) => changePageSize(Number(v))}>
            <SelectTrigger className="w-[120px]"><SelectValue /></SelectTrigger>
            {/* 修正: 加上 bg-white border shadow-md */}
            <SelectContent className="bg-white border shadow-md">
              {pageSizeOptions.map(s => (
                <SelectItem key={s} value={String(s)}>{s === -1 ? "全部" : s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" disabled={page === 1} onClick={() => setPage(p => p - 1)}>上一頁</Button>
          <span>{page} / {totalPages}</span>
          <Button variant="outline" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>下一頁</Button>
        </div>
      </div>

      {/* === shadcn Table === */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="text-center"><input type="checkbox" onChange={(e) => toggleSelectAll(e.target.checked)} /></TableHead>
            <TableHead>姓名</TableHead>
            <TableHead>EIP帳號</TableHead>
            <TableHead>身份證字號</TableHead>
            <TableHead>信箱</TableHead>
            <TableHead>電話</TableHead>
            <TableHead>部門</TableHead>
            <TableHead>職稱</TableHead>
            <TableHead className="text-center">狀態</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {paginated.map((p, i) => (
            <TableRow
              key={p.id}
              className={`${p.selected ? "bg-blue-100" : p.is_active ? (i % 2 === 0 ? "bg-gray-50" : "bg-white") : "bg-gray-200 text-gray-500"}`}
            >
              <TableCell className="text-center">
                <input
                  type="checkbox"
                  checked={p.selected || false}
                  onChange={e => {
                    const checked = e.target.checked;
                    setPeople(prev => prev.map(pp => pp.id === p.id ? { ...pp, selected: checked } : pp));
                  }}
                />
              </TableCell>
              <TableCell>{p.name}</TableCell>
              <TableCell>{p.eip_account}</TableCell>
              <TableCell>{p.id_number}</TableCell>
              <TableCell>{p.email}</TableCell>
              <TableCell>{p.phone}</TableCell>
              <TableCell>{p.department_name || "-"}</TableCell>
              <TableCell>{p.title}</TableCell>
              <TableCell className="text-center">{p.is_active ? "在職" : "離職"}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* === 分頁（下） === */}
      <div className="flex justify-between items-center my-4">
        <div className="flex items-center gap-2">
          每頁：
          <Select value={String(pageSize)} onValueChange={(v) => changePageSize(Number(v))}>
            <SelectTrigger className="w-[120px]"><SelectValue /></SelectTrigger>
            {/* 修正: 加上 bg-white border shadow-md */}
            <SelectContent className="bg-white border shadow-md">
              {pageSizeOptions.map(s => (
                <SelectItem key={s} value={String(s)}>{s === -1 ? "全部" : s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" disabled={page === 1} onClick={() => setPage(p => p - 1)}>上一頁</Button>
          <span>{page} / {totalPages}</span>
          <Button variant="outline" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>下一頁</Button>
        </div>
      </div>

      {/* === 批量操作 === */}
      <div className="mt-4 flex gap-4 items-center">
        <Select 
          value={selectedDept} 
          onValueChange={(val) => {
            if (val === "reset") setSelectedDept("");
            else setSelectedDept(val);
          }}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="請選擇部門" />
          </SelectTrigger>
          <SelectContent className="bg-white border rounded shadow-md">
            <SelectItem value="reset">-- 請選擇部門 --</SelectItem>
            {departments.map(d => (
              <SelectItem key={d.id} value={String(d.id)}>
                {d.name}
              </SelectItem>
            ))}
            <SelectItem value="__new__">新增部門...</SelectItem>
          </SelectContent>
        </Select>

        {selectedDept === "__new__" && (
          <Input
            placeholder="輸入新部門名稱"
            value={newDeptName}
            onChange={e => setNewDeptName(e.target.value)}
            className="w-[200px]"
          />
        )}

        <Button onClick={handleTransfer}>轉移單位</Button>
        <Button variant="destructive" onClick={() => handleBatchAction("retire")}>離職</Button>
      </div>

      {/* === Modal: 新增/更新 CSV === */}
      <Dialog open={showAddUpdateModal} onOpenChange={setShowAddUpdateModal}>
        <DialogContent className="max-w-3xl">
          <DialogHeader><DialogTitle>新增/更新 CSV 預覽</DialogTitle></DialogHeader>
          <div className="overflow-auto max-h-[400px]">
            <Table>
              <TableHeader>
                <TableRow>
                  {Object.keys(fieldMapAddUpdate).map(h => (<TableHead key={h}>{h}</TableHead>))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {addUpdatePreview?.map((row, idx) => (
                  <TableRow key={idx} className={idx % 2 === 0 ? "bg-gray-50" : "bg-white"}>
                    {Object.keys(fieldMapAddUpdate).map(h => (
                      <TableCell key={h}>{row[fieldMapAddUpdate[h]]}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <DialogFooter>
            <Button onClick={handleConfirmAddUpdate}>確認上傳</Button>
            <Button variant="outline" onClick={() => setShowAddUpdateModal(false)}>取消</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* === Modal: 離職 === */}
      <Dialog open={showRetireModal} onOpenChange={setShowRetireModal}>
        <DialogContent className="max-w-3xl">
          <DialogHeader><DialogTitle>離職 CSV 預覽</DialogTitle></DialogHeader>

          <h3 className="font-semibold mt-2">即將離職名單</h3>
          <Table>
            <TableHeader>
              <TableRow><TableHead>姓名</TableHead><TableHead>EIP帳號</TableHead></TableRow>
            </TableHeader>
            <TableBody>
              {retirePreview?.toRetire.map(p => (
                <TableRow key={p.id} className="bg-gray-50">
                  <TableCell>{p.name}</TableCell>
                  <TableCell>{p.eip_account}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <h3 className="font-semibold mt-4">未匹配名單</h3>
          <Table>
            <TableHeader>
              <TableRow><TableHead>姓名</TableHead><TableHead>EIP帳號</TableHead><TableHead>狀態</TableHead></TableRow>
            </TableHeader>
            <TableBody>
              {retirePreview?.unmatched.map((row, idx) => (
                <TableRow key={idx} className={idx % 2 === 0 ? "bg-gray-50" : "bg-white"}>
                  <TableCell>{row.姓名}</TableCell>
                  <TableCell>{row["EIP帳號"]}</TableCell>
                  <TableCell>{row.status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <DialogFooter>
            <Button onClick={handleConfirmRetire}>確認離職</Button>
            <Button variant="outline" onClick={() => setShowRetireModal(false)}>取消</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

    </div>
  );
};

export default PeopleManagement;