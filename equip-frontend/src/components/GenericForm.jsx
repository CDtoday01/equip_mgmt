import React, { useState, useEffect, useRef, useMemo } from "react";
import Papa from "papaparse";
import debounce from "lodash/debounce";

const GenericForm = ({ fields, onAddSingle, onAddCSV, initialValues, onOwnerInput }) => {
  const [mode, setMode] = useState("single");
  const [formData, setFormData] = useState({});
  const [csvFile, setCsvFile] = useState(null);
  const [csvFileName, setCsvFileName] = useState("未選擇檔案"); // ✅ 新增
  const [ownerCandidates, setOwnerCandidates] = useState([]);
  const [showOwnerDropdown, setShowOwnerDropdown] = useState(false);
  const [highlightIndex, setHighlightIndex] = useState(0);
  const isComposing = useRef(false);

  const initialState = useMemo(
    () => fields.reduce((acc, f) => ({ ...acc, [f.name]: "" }), {}),
    [fields]
  );

  useEffect(() => {
    if (initialValues) {
      const mapped = {
        ...initialState,
        ...initialValues,
        owner_user_display: initialValues.holder?.name || "",
        owner_user: initialValues.owner_user || initialValues.holder?.id || "",
      };
      setFormData(mapped);
    } else {
      setFormData({ ...initialState });
    }
  }, [initialValues, initialState]);

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setFormData({ ...initialState, ...initialValues });
    setCsvFile(null);
    setCsvFileName("未選擇檔案"); // ✅ 新增
    setOwnerCandidates([]);
    setShowOwnerDropdown(false);
    setHighlightIndex(0);
  };

  const debouncedOwnerInput = useRef(
    debounce(async (value) => {
      if (!onOwnerInput || value.trim() === "") return;
      try {
        const candidates = await onOwnerInput(value);
        setOwnerCandidates(candidates);
        setShowOwnerDropdown(candidates.length > 0);
        setHighlightIndex(0);
      } catch {
        setOwnerCandidates([]);
        setShowOwnerDropdown(false);
      }
    }, 500)
  ).current;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (name === "owner_user" && !isComposing.current) {
      debouncedOwnerInput(value);
    }
  };

  const handleCompositionStart = () => (isComposing.current = true);
  const handleCompositionEnd = (e) => {
    isComposing.current = false;
    handleInputChange(e);
  };

  const handleOwnerSelect = (person) => {
    setFormData((prev) => ({
      ...prev,
      owner_user: person.id,
      owner_user_display: person.name,
    }));
    setShowOwnerDropdown(false);
  };

  const handleOwnerKeyDown = (e) => {
    if (!showOwnerDropdown) return;
    if (e.key === "ArrowDown") {
      setHighlightIndex((prev) => (prev + 1) % ownerCandidates.length);
      e.preventDefault();
    } else if (e.key === "ArrowUp") {
      setHighlightIndex((prev) => (prev - 1 + ownerCandidates.length) % ownerCandidates.length);
      e.preventDefault();
    } else if (e.key === "Enter") {
      handleOwnerSelect(ownerCandidates[highlightIndex]);
      e.preventDefault();
    } else if (e.key === "Escape") {
      setShowOwnerDropdown(false);
    }
  };

  const handleSingleSubmit = (e) => {
    e.preventDefault();
    onAddSingle(formData, !!initialValues?.id);
    setFormData({ ...initialState });
    setOwnerCandidates([]);
    setShowOwnerDropdown(false);
    setHighlightIndex(0);
  };

  const handleCSVChange = (e) => {
    const file = e.target.files[0];
    setCsvFile(file);
    setCsvFileName(file ? file.name : "未選擇檔案"); // ✅ 新增
  };

  const handleCSVSubmit = (e) => {
    e.preventDefault();
    if (!csvFile) return;
    Papa.parse(csvFile, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        onAddCSV(results.data);
        setCsvFile(null);
        setCsvFileName("未選擇檔案"); // ✅ 重置顯示
        e.target.reset();
      },
    });
  };

  const isEditing = !!initialValues?.id;

  return (
    <div style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "20px", position: "relative" }}>
      <div style={{ marginBottom: "10px" }}>
        <button
          type="button"
          onClick={() => handleModeChange("single")}
          style={{
            marginRight: "10px",
            background: mode === "single" ? "#007bff" : "#ccc",
            color: "#fff",
          }}
        >
          單筆新增
        </button>
        <button
          type="button"
          onClick={() => handleModeChange("csv")}
          style={{
            background: mode === "csv" ? "#007bff" : "#ccc",
            color: "#fff",
          }}
        >
          CSV 匯入
        </button>
      </div>

      {mode === "single" && (
        <form onSubmit={handleSingleSubmit} autoComplete="off">
          {fields.map((f) => {
            const isRequired = f.required;
            if (f.name === "owner_user") {
              return (
                <div key={f.name} style={{ position: "relative", marginBottom: "5px" }}>
                  <input
                    type="text"
                    name={f.name}
                    placeholder={f.label}
                    value={formData.owner_user_display || ""}
                    onChange={handleInputChange}
                    onCompositionStart={handleCompositionStart}
                    onCompositionEnd={handleCompositionEnd}
                    onKeyDown={handleOwnerKeyDown}
                    required={isRequired}
                    style={{ width: "200px", padding: "5px" }}
                  />
                  {showOwnerDropdown && (
                    <ul
                      style={{
                        position: "absolute",
                        top: "30px",
                        left: 0,
                        border: "1px solid #ccc",
                        background: "#fff",
                        listStyle: "none",
                        margin: 0,
                        padding: 0,
                        width: "200px",
                        maxHeight: "150px",
                        overflowY: "auto",
                        zIndex: 100,
                      }}
                    >
                      {ownerCandidates.map((p, idx) => (
                        <li
                          key={p.id}
                          onClick={() => handleOwnerSelect(p)}
                          style={{
                            padding: "5px",
                            cursor: "pointer",
                            background: idx === highlightIndex ? "#007bff" : "#fff",
                            color: idx === highlightIndex ? "#fff" : "#000",
                          }}
                        >
                          {p.name} {p.department ? `(${p.department})` : ""}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              );
            }
            return (
              <input
                key={f.name}
                type={f.type}
                name={f.name}
                placeholder={f.label}
                value={formData[f.name] || ""}
                onChange={handleInputChange}
                required={isRequired}
                style={{ marginRight: "10px", marginBottom: "5px" }}
              />
            );
          })}
          <button type="submit">{isEditing ? "修改" : "新增"}</button>
        </form>
      )}

      {mode === "csv" && (
        <form onSubmit={handleCSVSubmit}>
          <input type="file" accept=".csv" onChange={handleCSVChange} style={{ marginRight: "10px" }} />
          <button type="submit">匯入 CSV</button>
          <span style={{ marginLeft: "10px" }}>{csvFileName}</span> {/* ✅ 顯示檔案名稱 */}
        </form>
      )}
    </div>
  );
};

export default GenericForm;
