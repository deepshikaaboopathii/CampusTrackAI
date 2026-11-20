import React, { useEffect, useState } from 'react';
import api from '../api/client';

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.get('/students', { params: { search, limit: 25 } }).then(res => setStudents(res.data.students || res.data || [])).catch(console.error);
  }, [search]);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Student Directory</h2>
        <input type="text" placeholder="Search students..." value={search} onChange={e => setSearch(e.target.value)} className="px-3 py-2 rounded-lg border dark:bg-slate-800 dark:border-slate-700" />
      </div>
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-slate-100 dark:bg-slate-700 text-xs uppercase">
            <tr>
              <th className="p-3">ID</th><th className="p-3">Name</th><th className="p-3">Dept</th><th className="p-3">CGPA</th><th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {students.map((s, i) => (
              <tr key={i} className="border-t border-slate-200 dark:border-slate-700">
                <td className="p-3">{s.student_id}</td><td className="p-3 font-medium">{s.name}</td><td className="p-3">{s.department}</td><td className="p-3">{s.cgpa}</td><td className="p-3">{s.placement_status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
