import { useEffect, useState, useCallback } from "react";
import api from "../api.js";
import { formatEUR } from "../money.js";
import { CATEGORIES, categoryLabel } from "../categories.js";

const emptyForm = { description: "", amount_eur: "", category: "", date: "" };

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [filterCategory, setFilterCategory] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async (category) => {
    setLoading(true);
    setError("");
    try {
      const params = {};
      if (category) params.category = category;
      const res = await api.get("/transactions", { params });
      setTransactions(res.data);
    } catch (err) {
      setError("Failed to load transactions.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(filterCategory);
  }, [load, filterCategory]);

  async function handleAdd(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const payload = {
        description: form.description,
        amount_eur: parseFloat(form.amount_eur),
      };
      if (form.category) payload.category = form.category;
      if (form.date) payload.date = form.date;
      await api.post("/transactions", payload);
      setForm(emptyForm);
      await load(filterCategory);
    } catch (err) {
      setError("Failed to add transaction.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id) {
    try {
      await api.delete(`/transactions/${id}`);
      await load(filterCategory);
    } catch (err) {
      setError("Failed to delete transaction.");
    }
  }

  return (
    <div className="transactions-page">
      <h1>Transactions</h1>

      <div className="card">
        <h2>Add transaction</h2>
        <form className="txn-form" onSubmit={handleAdd}>
          <label htmlFor="description">Description</label>
          <input
            id="description"
            type="text"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            required
          />
          <label htmlFor="amount">Amount (EUR)</label>
          <input
            id="amount"
            type="number"
            step="0.01"
            value={form.amount_eur}
            onChange={(e) => setForm({ ...form, amount_eur: e.target.value })}
            required
          />
          <label htmlFor="category">Category</label>
          <select
            id="category"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
          >
            <option value="">Auto-detect</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {categoryLabel(c)}
              </option>
            ))}
          </select>
          <label htmlFor="date">Date</label>
          <input
            id="date"
            type="date"
            value={form.date}
            onChange={(e) => setForm({ ...form, date: e.target.value })}
          />
          <button type="submit" disabled={submitting}>
            {submitting ? "Adding..." : "Add transaction"}
          </button>
        </form>
      </div>

      {error && <p className="form-error">{error}</p>}

      <div className="card">
        <div className="filter-row">
          <label htmlFor="filter-category">Filter by category</label>
          <select
            id="filter-category"
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
          >
            <option value="">All categories</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {categoryLabel(c)}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : transactions.length === 0 ? (
          <p>No transactions found.</p>
        ) : (
          <table className="txn-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th>Amount</th>
                <th>Anomaly</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((txn) => (
                <tr key={txn.id} className={txn.is_anomaly ? "anomaly-row" : ""}>
                  <td>{txn.date}</td>
                  <td>{txn.description}</td>
                  <td>{categoryLabel(txn.category)}</td>
                  <td>{formatEUR(txn.amount_eur)}</td>
                  <td>{txn.is_anomaly && <span className="badge">anomaly</span>}</td>
                  <td>
                    <button className="delete-btn" onClick={() => handleDelete(txn.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
