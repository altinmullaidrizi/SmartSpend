import { useEffect, useState, useCallback } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import api from "../api.js";
import { formatEUR } from "../money.js";
import { categoryLabel } from "../categories.js";

const COLORS = [
  "#4f6df5",
  "#f5a623",
  "#7ed321",
  "#d0021b",
  "#9013fe",
  "#50e3c2",
  "#b8e986",
  "#4a90d9",
  "#f8e71c",
  "#bd10e0",
  "#417505",
  "#8b572a",
];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [seeding, setSeeding] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [summaryRes, txnRes] = await Promise.all([
        api.get("/insights/summary"),
        api.get("/transactions"),
      ]);
      setSummary(summaryRes.data);
      setTransactions(txnRes.data);
    } catch (err) {
      setError("Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSeed() {
    setSeeding(true);
    try {
      await api.post("/transactions/seed?n=200");
      await load();
    } catch (err) {
      setError("Failed to load demo data.");
    } finally {
      setSeeding(false);
    }
  }

  const pieData = summary
    ? Object.entries(summary.by_category).map(([category, amount]) => ({
        name: categoryLabel(category),
        value: amount,
      }))
    : [];

  const recent = transactions.slice(0, 10);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button onClick={handleSeed} disabled={seeding}>
          {seeding ? "Loading demo data..." : "Load demo data"}
        </button>
      </div>

      {error && <p className="form-error">{error}</p>}
      {loading && <p>Loading...</p>}

      {!loading && summary && (
        <>
          <div className="card">
            <h2>Total spend</h2>
            <p className="total-amount">{formatEUR(summary.total)}</p>
          </div>

          <div className="card">
            <h2>Spend by category</h2>
            {pieData.length === 0 ? (
              <p>No transactions yet. Load demo data or add a transaction to get started.</p>
            ) : (
              <ResponsiveContainer width="100%" height={320}>
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={110}
                    label={(entry) => `${entry.name}: ${formatEUR(entry.value)}`}
                  >
                    {pieData.map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatEUR(value)} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="card">
            <h2>Recent transactions</h2>
            {recent.length === 0 ? (
              <p>No transactions yet.</p>
            ) : (
              <ul className="txn-list">
                {recent.map((txn) => (
                  <li
                    key={txn.id}
                    className={txn.is_anomaly ? "txn-item anomaly" : "txn-item"}
                  >
                    <span className="txn-desc">{txn.description}</span>
                    <span className="txn-category">{categoryLabel(txn.category)}</span>
                    <span className="txn-amount">{formatEUR(txn.amount_eur)}</span>
                    {txn.is_anomaly && <span className="badge">anomaly</span>}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
    </div>
  );
}
