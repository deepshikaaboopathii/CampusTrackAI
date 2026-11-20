import React from 'react';
export default function DatasetPage() {
  return (
    <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border dark:border-slate-700 space-y-4">
      <h2 className="text-2xl font-bold">Dataset Management</h2>
      <div className="flex gap-4">
        <a href="http://127.0.0" className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm">Download CSV Template</a>
        <a href="http://127.0.0" className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm">Export All Students CSV</a>
      </div>
    </div>
  );
}
