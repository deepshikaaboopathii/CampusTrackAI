import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import LoginModal from './components/LoginModal';

import DashboardPage from './pages/DashboardPage';
import StudentsPage from './pages/StudentsPage';
import AcademicAnalyticsPage from './pages/AcademicAnalyticsPage';
import PlacementAnalyticsPage from './pages/PlacementAnalyticsPage';
import PredictorPage from './pages/PredictorPage';
import ModelEvaluationPage from './pages/ModelEvaluationPage';
import DatasetPage from './pages/DatasetPage';
import ReportsPage from './pages/ReportsPage';
import ProjectDocsPage from './pages/ProjectDocsPage';

export default function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);

  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-gradient-to-br from-white via-purple-50/40 to-pink-50/40 text-slate-800 flex flex-col font-sans transition-colors duration-200">
            {/* Sidebar */}
            <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

            {/* Header */}
            <Header
              collapsed={collapsed}
              onOpenLogin={() => setIsLoginOpen(true)}
            />

            {/* Main Content Area */}
            <main
              className={`flex-1 transition-all duration-300 pt-20 p-6 ${
                collapsed ? 'ml-20' : 'ml-64'
              }`}
            >
              <div className="max-w-7xl mx-auto">
                <Routes>
                  <Route path="/" element={<DashboardPage />} />
                  <Route path="/students" element={<StudentsPage />} />
                  <Route path="/analytics/academic" element={<AcademicAnalyticsPage />} />
                  <Route path="/analytics/placement" element={<PlacementAnalyticsPage />} />
                  <Route path="/predictor" element={<PredictorPage />} />
                  <Route path="/ml-models" element={<ModelEvaluationPage />} />
                  <Route path="/datasets" element={<DatasetPage />} />
                  <Route path="/reports" element={<ReportsPage />} />
                  <Route path="/project-docs" element={<ProjectDocsPage />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </div>
            </main>

            {/* Login Modal */}
            <LoginModal
              isOpen={isLoginOpen}
              onClose={() => setIsLoginOpen(false)}
            />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
