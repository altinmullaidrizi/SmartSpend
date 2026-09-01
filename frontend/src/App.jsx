import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Transactions from "./pages/Transactions.jsx";
import Insights from "./pages/Insights.jsx";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function NavBar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  if (!token) return null;

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">SmartSpend</div>
      <div className="navbar-links">
        <Link to="/">Dashboard</Link>
        <Link to="/transactions">Transactions</Link>
        <Link to="/insights">Insights</Link>
      </div>
      <button className="logout-btn" onClick={handleLogout}>
        Logout
      </button>
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <div className="page-content">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/transactions"
            element={
              <ProtectedRoute>
                <Transactions />
              </ProtectedRoute>
            }
          />
          <Route
            path="/insights"
            element={
              <ProtectedRoute>
                <Insights />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
