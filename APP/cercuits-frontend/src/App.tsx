import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout/MainLayout';
import { LoginPage } from './pages/LoginPage/LoginPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route path="/" element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/tickets" replace />} />
          <Route path="tickets" element={<div>Tickets Page</div>} />
          <Route path="knowledge-library" element={<div>Knowledge Library</div>} />
          <Route path="monitor" element={<div>Monitor</div>} />
          <Route path="testing" element={<div>Testing</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;