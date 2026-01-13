import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout/MainLayout';
import { LoginPage } from './pages/LoginPage/LoginPage';
import { ProtectedRoute } from './components/ProtectedRoute';

// Pages routes
import HomePage from './pages/HomePage/HomePage';
import AIResponsePage from './pages/AIResponsePage/AIResponsePage';
import EmailEditorPage from './pages/EmailEditorPage/EmailEditorPage';
import KnowledgeBasePage from './pages/KnowledgeBasePage/KnowledgeBasePage';
import MonitoringPage from './pages/MonitoringPage/MonitoringPage';
import ConsistencyTestPage from './pages/ConsistencyTestPage/ConsistencyTestPage';

import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected (everything inside MainLayout) */}
        <Route path="/" element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }>

          {/* Default after login */}
          <Route index element={<Navigate to="/tickets" replace />} />

          {/* Real pages */}
          <Route path="tickets" element={<HomePage />} />
          <Route path="ai-response" element={<AIResponsePage />} />
          <Route path="email-editor" element={<EmailEditorPage />} />
          <Route path="knowledge-library" element={<KnowledgeBasePage />} />
          <Route path="monitoring" element={<MonitoringPage />} />
          <Route path="consistency-test" element={<ConsistencyTestPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;