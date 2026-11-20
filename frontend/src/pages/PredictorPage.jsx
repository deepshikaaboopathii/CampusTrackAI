import React, { useState } from 'react';
import api from '../api/client';

export default function PredictorPage() {
  const [form, setForm] = useState({ cgpa: 8.2, attendance: 88, backlog_count: 0, aptitude_score: 78, technical_score: 82, communication_score: 75, programming_rating: 4, internships: 1, projects: 2 });
  const [result, setResult] = useState(null);

  const handlePredict = async (e) => {
    e.preventDefault();
    const res = await api.post('/ml/predict', form);
    setResult(res.data);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <form onSubmit={handlePredict} className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 space-y-3">
        <h2 className="text-xl font-bold mb-2">Placement AI Predictor</h2>
        {Object.entries(form).map(([k, v]) => (
          <div key={k} className="flex justify-between items-center">
            <label className="text-sm capitalize">{k.replace(/_/g, ' ')}</label>
            <input type="number" step="any" value={v} onChange={e => setForm({ ...form, [k]: parseFloat(e.target.value) })} className="w-32 p-1.5 rounded border dark:bg-slate-700" />
          </div>
        ))}
        <button type="submit" className="w-full py-2.5 bg-indigo-600 text-white rounded-lg font-medium">Run Prediction</button>
      </form>
      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
        <h3 className="text-lg font-bold mb-3">Prediction Output</h3>
        <pre className="text-xs bg-slate-100 dark:bg-slate-900 p-4 rounded-lg overflow-auto">{result ? JSON.stringify(result, null, 2) : 'Submit student metrics to run ML inference.'}</pre>
      </div>
    </div>
  );
}
