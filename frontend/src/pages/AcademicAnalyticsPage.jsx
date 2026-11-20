import React, { useEffect, useState } from 'react';
import api from '../api/client';
export default function AcademicAnalyticsPage() {
  const [data, setData] = useState(null);
  useEffect(() => { api.get('/dashboard/stats').then(r => setData(r.data)); }, []);
  return <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border dark:border-slate-700"><h2 className="text-2xl font-bold mb-4">Academic Analytics</h2><pre className="text-xs overflow-auto">{JSON.stringify(data?.department_stats || data, null, 2)}</pre></div>;
}
