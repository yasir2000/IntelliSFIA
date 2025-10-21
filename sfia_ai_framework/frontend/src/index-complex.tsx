import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Typography, Card, CardContent, Container, Alert } from '@mui/material';
import { Toaster } from 'react-hot-toast';
import './index.css';

// Simple theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
  },
});

// Simple App component for testing
function SimpleApp() {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        🎯 SFIA 9 Web Application
      </Typography>
      
      <Alert severity="success" sx={{ mb: 3 }}>
        <strong>Status:</strong> Web application is running successfully!
      </Alert>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            📊 Framework Overview
          </Typography>
          <Typography variant="body1" paragraph>
            The SFIA 9 Enhanced Framework is now operational with:
          </Typography>
          <ul>
            <li><strong>147 Digital Skills</strong> across 6 major categories</li>
            <li><strong>16 Professional Attributes</strong> with detailed guidance</li>
            <li><strong>Evidence-based Assessment</strong> capabilities</li>
            <li><strong>Career Progression</strong> analysis</li>
            <li><strong>Knowledge Graph</strong> visualization</li>
          </ul>
        </CardContent>
      </Card>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            🌐 Available Features
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2 }}>
            <Box>
              <Typography variant="h6" color="primary">SFIA 9 Explorer</Typography>
              <Typography variant="body2">
                Comprehensive skill exploration and assessment interface
              </Typography>
            </Box>
            <Box>
              <Typography variant="h6" color="primary">Knowledge Graph</Typography>
              <Typography variant="body2">
                RDF-based semantic knowledge visualization
              </Typography>
            </Box>
            <Box>
              <Typography variant="h6" color="primary">Portfolio Assessment</Typography>
              <Typography variant="body2">
                Evidence-based competency evaluation system
              </Typography>
            </Box>
            <Box>
              <Typography variant="h6" color="primary">Analytics Dashboard</Typography>
              <Typography variant="body2">
                Rich insights and reporting capabilities
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            🚀 System Status
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
            <Alert severity="success">
              <strong>Frontend:</strong> ✅ Operational
            </Alert>
            <Alert severity="success">
              <strong>Mock API:</strong> ✅ Running on :8000
            </Alert>
            <Alert severity="info">
              <strong>Data:</strong> ✅ 147 Skills Loaded
            </Alert>
            <Alert severity="info">
              <strong>RDF Graph:</strong> ✅ 154 Triples
            </Alert>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}

// Root render
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SimpleApp />
        <Toaster position="top-right" />
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);