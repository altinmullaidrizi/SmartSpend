import { useEffect, useState } from "react";
import api from "../api.js";
import { formatEUR } from "../money.js";
import { categoryLabel } from "../categories.js";

export default function Insights() {
  const [tips, setTips] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");
      try {
        const tipsRes = await api.get("/insights/tips");
        setTips(tipsRes.data);
        const anomaliesRes = await api.get("/insights/anomalies");
        setAnomalies(anomaliesRes.data);
      } catch (err) {
        setError("Failed to load insights.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="insights-page">
      <h1>Insights</h1>
      {error && <p className="form-error">{error}</p>}
      {loading && <p>Loading...</p>}

      {!loading && (
        <>
          <div className="card">
            <h2>Budget tips</h2>
            {tips.length === 0 ? (
              <p>Nothing to report. Your spending looks on track.</p>
            ) : (
              <ul className="tips-list">
                {tips.map((tip, idx) => (
                  <li key={idx} className={`tip tip-${tip.severity}`}>
                    <strong>{categoryLabel(tip.category)}:</strong> {tip.message}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="card">
            <h2>Flagged anomalies</h2>
            {anomalies.length === 0 ? (
              <p>Nothing to report. No unusual transactions found.</p>
            ) : (
              <table className="txn-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {anomalies.map((txn) => (
                    <tr key={txn.id} className="anomaly-row">
                      <td>{txn.date}</td>
                      <td>{txn.description}</td>
                      <td>{categoryLabel(txn.category)}</td>
                      <td>{formatEUR(txn.amount_eur)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}
