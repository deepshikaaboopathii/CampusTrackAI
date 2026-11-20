import React, { useEffect, useState } from 'react';
import api from '../api/client';
export default function PlacementAnalyticsPage() {
  const [data, setData] = useState(null);
  useEffect(() => { api.get('/reports/summary').then(r => setData(r.data)); }, []);
  return <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border dark:border-slate-700"><h2 className="text-2xl font-bold mb-4">Placement Analytics</h2><pre className="text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre></div>;
}
