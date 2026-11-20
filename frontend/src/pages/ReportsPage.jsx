import React, { useEffect, useState } from 'react';
import api from '../api/client';
export default function ReportsPage() {
  const [report, setReport] = useState(null);
  useEffect(() => { api.get('/reports/training-needed').then(r => setReport(r.data)); }, []);
  return <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border dark:border-slate-700"><h2 className="text-2xl font-bold mb-4">Intervention & Training Report</h2><pre className="text-xs overflow-auto">{JSON.stringify(report, null, 2)}</pre></div>;
}
