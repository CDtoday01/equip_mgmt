export const Card = ({ children, className = "" }) => (
  <div className={`border rounded shadow p-4 ${className}`}>{children}</div>
);

export const CardContent = ({ children, className = "" }) => (
  <div className={`p-2 ${className}`}>{children}</div>
);
