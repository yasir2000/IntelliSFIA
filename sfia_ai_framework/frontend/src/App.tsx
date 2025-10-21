import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import EnterpriseIntegration from './pages/EnterpriseIntegration';
import EmployeeAnalysis from './pages/EmployeeAnalysis';
import DepartmentAnalysis from './pages/DepartmentAnalysis';
import OrganizationInsights from './pages/OrganizationInsights';
import Scenarios from './pages/Scenarios';
import MultiAgentAI from './pages/MultiAgentAI';
import KnowledgeGraph from './pages/KnowledgeGraph';
import Analytics from './pages/Analytics';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import PortfolioAssessment from './pages/PortfolioAssessment';
import SFIA9Explorer from './pages/SFIA9Explorer';

function App() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/enterprise" element={<EnterpriseIntegration />} />
          <Route path="/employee-analysis" element={<EmployeeAnalysis />} />
          <Route path="/department-analysis" element={<DepartmentAnalysis />} />
          <Route path="/organization-insights" element={<OrganizationInsights />} />
          <Route path="/scenarios" element={<Scenarios />} />
          <Route path="/agents" element={<MultiAgentAI />} />
          <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
          <Route path="/portfolio-assessment" element={<PortfolioAssessment />} />
          <Route path="/sfia9-explorer" element={<SFIA9Explorer />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Box>
  );
}

export default App;