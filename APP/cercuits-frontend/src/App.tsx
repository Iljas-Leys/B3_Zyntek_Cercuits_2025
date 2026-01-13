import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout/MainLayout';
import { LoginPage } from './pages/LoginPage/LoginPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AIResponsePage } from './pages/AIResponsePage/AIResponsePage';
import EmailEditorPage from './pages/EmailEditorPage/EmailEditorPage';
import './App.css';
import HomePage from './pages/HomePage/HomePage';
import { NotFoundPage } from './pages/NotFoundPage/NotFoundPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* Routes inside MainLayout */}
        <Route path="/" element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }>

          {/* Default after login */}
          <Route index element={<Navigate to="/tickets" replace />} />
          <Route path="tickets" element={<HomePage />} />
          <Route path="email-editor" element={<EmailEditorPage />} />
          <Route path="ai-response/:emailId" element={<AIResponsePage />} />
          <Route path="ai-response" element={<AIResponsePage />} />
          <Route path="knowledge-library" element={<div>Knowledge Library</div>} />
          <Route path="monitoring" element={<div>Monitoring Page</div>} />
          <Route path="consistency-test" element={<div>Consistency Test Page</div>} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;