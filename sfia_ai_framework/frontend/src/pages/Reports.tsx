import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Reports: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Reports
      </Typography>
      <Card>
        <CardContent>
          <Typography>Report generation and management coming soon...</Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Reports;