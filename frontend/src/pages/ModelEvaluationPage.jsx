import React, { useEffect, useState } from 'react';
import api from '../api/client';

export default function ModelEvaluationPage() {
  const [metrics, setMetrics] = useState(null);
  useEffect(() => { api.get('/ml/metrics').then(res => setMetrics(res.data)).catch(console.error); }, []);
  return (
    <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
      <h2 className="text-2xl font-bold mb-4">ML Model Evaluation Metrics</h2>
      <pre className="text-xs bg-slate-100 dark:bg-slate-900 p-4 rounded-lg overflow-auto">{metrics ? JSON.stringify(metrics, null, 2) : 'Loading ML metrics...'}</pre>
    </div>
  );
}
