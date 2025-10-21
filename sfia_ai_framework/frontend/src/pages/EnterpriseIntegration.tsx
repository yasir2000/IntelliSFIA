import React from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Button,
  Grid,
  Alert,
} from '@mui/material';
import {
  Business as BusinessIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
} from '@mui/icons-material';

const EnterpriseIntegration: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Enterprise Integration
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Connect and manage enterprise systems for real-time SFIA analysis
        </Typography>
      </Box>

      <Alert severity="info" sx={{ mb: 4 }}>
        Enterprise integration allows you to connect to SAP, Power BI, databases, and other business systems 
        for automated SFIA analysis and workforce intelligence.
      </Alert>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <BusinessIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                System Connections
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Connect to enterprise systems like SAP, Power BI, databases, and more.
              </Typography>
              <Button variant="contained" startIcon={<AddIcon />}>
                Add System
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <SettingsIcon sx={{ fontSize: 40, color: 'secondary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Configuration
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Configure real-time processing, caching, and analysis settings.
              </Typography>
              <Button variant="outlined" startIcon={<SettingsIcon />}>
                Configure
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default EnterpriseIntegration;