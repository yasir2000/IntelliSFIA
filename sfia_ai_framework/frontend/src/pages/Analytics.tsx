import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Analytics: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Analytics
      </Typography>
      <Card>
        <CardContent>
          <Typography>Advanced analytics and insights coming soon...</Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Analytics;