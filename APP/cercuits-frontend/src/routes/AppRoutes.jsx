import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import pages
import HomePage from '../pages/HomePage/HomePage';
import AIResponsePage from '../pages/AIResponsePage/AIResponsePage';
import EmailEditorPage from '../pages/EmailEditorPage/EmailEditorPage';
import KnowledgeBasePage from '../pages/KnowledgeBasePage/KnowledgeBasePage';
import MonitoringPage from '../pages/MonitoringPage/MonitoringPage';
import ConsistencyTestPage from '../pages/ConsistencyTestPage/ConsistencyTestPage';

// Import layout
// import MainLayout from '../components/layout/MainLayout/MainLayout';

// Import constants
import { ROUTES } from '../utils/constants';

const AppRoutes = () => {
  return (
    <Router>
      <Routes>
        {/* Main routes with layout */}
        <Route path="/" >
          <Route path={ROUTES.HOME} element={<HomePage />} />
          <Route path={ROUTES.AI_RESPONSE} element={<AIResponsePage />} />
          <Route path={ROUTES.EMAIL_EDITOR} element={<EmailEditorPage />} />
          <Route path={ROUTES.KNOWLEDGE_BASE} element={<KnowledgeBasePage />} />
          <Route path={ROUTES.MONITORING} element={<MonitoringPage />} />
          <Route path={ROUTES.CONSISTENCY_TEST} element={<ConsistencyTestPage />} />
          
          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
        </Route>
      </Routes>

      
    </Router>
  );
};

export default AppRoutes;
