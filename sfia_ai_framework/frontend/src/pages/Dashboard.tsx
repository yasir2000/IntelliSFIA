import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  Business as BusinessIcon,
  Analytics as AnalyticsIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Launch as LaunchIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { 
  useHealthCheck, 
  useEnterpriseStatus, 
  useOrganizationInsights 
} from '../hooks';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Mock data for the dashboard
const mockActivityData = [
  { date: '2025-10-15', employeeAnalyses: 23, departmentAnalyses: 5, insights: 2 },
  { date: '2025-10-16', employeeAnalyses: 31, departmentAnalyses: 8, insights: 3 },
  { date: '2025-10-17', employeeAnalyses: 45, departmentAnalyses: 12, insights: 4 },
  { date: '2025-10-18', employeeAnalyses: 38, departmentAnalyses: 9, insights: 3 },
  { date: '2025-10-19', employeeAnalyses: 52, departmentAnalyses: 15, insights: 5 },
  { date: '2025-10-20', employeeAnalyses: 41, departmentAnalyses: 11, insights: 4 },
  { date: '2025-10-21', employeeAnalyses: 29, departmentAnalyses: 7, insights: 3 },
];

const mockRecentActivities = [
  {
    id: 1,
    type: 'employee_analysis',
    title: 'Employee Analysis Completed',
    description: 'Analysis for John Doe (EMP001) completed successfully',
    timestamp: '2 minutes ago',
    status: 'success',
  },
  {
    id: 2,
    type: 'department_analysis',
    title: 'Department Analysis Started',
    description: 'Engineering department analysis in progress',
    timestamp: '5 minutes ago',
    status: 'pending',
  },
  {
    id: 3,
    type: 'system_alert',
    title: 'System Integration Alert',
    description: 'SAP connection experiencing intermittent issues',
    timestamp: '12 minutes ago',
    status: 'warning',
  },
  {
    id: 4,
    type: 'report_generated',
    title: 'Report Generated',
    description: 'Q4 SFIA compliance report ready for download',
    timestamp: '1 hour ago',
    status: 'success',
  },
];

const COLORS = ['#667eea', '#764ba2', '#28a745', '#ffc107', '#dc3545'];

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: healthData, isLoading: healthLoading, refetch: refetchHealth } = useHealthCheck();
  const { data: enterpriseStatus } = useEnterpriseStatus();
  const { data: organizationInsights, isLoading: insightsLoading } = useOrganizationInsights();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <CheckCircleIcon color="disabled" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'unhealthy':
        return 'error';
      default:
        return 'default';
    }
  };

  const pieChartData = organizationInsights ? 
    Object.entries(organizationInsights.departments).map(([name, data]) => ({
      name,
      value: data.employee_count,
    })) : [];

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome to IntelliSFIA - Your intelligent SFIA framework dashboard
        </Typography>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <BusinessIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {enterpriseStatus?.systems?.length || 0}
                  </Typography>
                  <Typography color="text.secondary">
                    Connected Systems
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon color="success" fontSize="small" sx={{ mr: 0.5 }} />
                <Typography variant="body2" color="success.main">
                  +2 this week
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                  <AnalyticsIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    47
                  </Typography>
                  <Typography color="text.secondary">
                    Active Analyses
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon color="success" fontSize="small" sx={{ mr: 0.5 }} />
                <Typography variant="body2" color="success.main">
                  +12 today
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <PeopleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    1,234
                  </Typography>
                  <Typography color="text.secondary">
                    SFIA Suggestions
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon color="success" fontSize="small" sx={{ mr: 0.5 }} />
                <Typography variant="body2" color="success.main">
                  +89 this week
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <CheckCircleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    94%
                  </Typography>
                  <Typography color="text.secondary">
                    Compliance Score
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon color="success" fontSize="small" sx={{ mr: 0.5 }} />
                <Typography variant="body2" color="success.main">
                  +2% improvement
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Activity Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h6" component="h2">
                  Analysis Activity
                </Typography>
                <Button
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={() => window.location.reload()}
                >
                  Refresh
                </Button>
              </Box>
              
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={mockActivityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis />
                  <RechartsTooltip 
                    formatter={(value, name) => [value, typeof name === 'string' ? name.replace(/([A-Z])/g, ' $1').replace(/^./, (str: string) => str.toUpperCase()) : name]}
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="employeeAnalyses" 
                    stroke="#667eea" 
                    strokeWidth={2}
                    name="Employee Analyses"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="departmentAnalyses" 
                    stroke="#764ba2" 
                    strokeWidth={2}
                    name="Department Analyses"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="insights" 
                    stroke="#28a745" 
                    strokeWidth={2}
                    name="Organization Insights"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" component="h2" sx={{ mb: 3 }}>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<PeopleIcon />}
                  onClick={() => navigate('/employee-analysis')}
                >
                  Analyze Employee
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<BusinessIcon />}
                  onClick={() => navigate('/department-analysis')}
                >
                  Department Insights
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<AnalyticsIcon />}
                  onClick={() => navigate('/scenarios')}
                >
                  Run AI Scenario
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<CheckCircleIcon />}
                  onClick={() => navigate('/reports')}
                >
                  Generate Report
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Health */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h6" component="h2">
                  System Health
                </Typography>
                <Tooltip title="Refresh health status">
                  <IconButton size="small" onClick={() => refetchHealth()}>
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
              </Box>

              {healthLoading ? (
                <LinearProgress />
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {healthData?.map((service, index) => (
                    <Box key={index} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getStatusIcon(service.status)}
                        <Typography variant="body2">{service.service}</Typography>
                      </Box>
                      <Chip 
                        label={service.status} 
                        size="small" 
                        color={getStatusColor(service.status) as any}
                        variant="outlined"
                      />
                    </Box>
                  )) || (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CheckCircleIcon color="success" />
                      <Typography variant="body2">All systems operational</Typography>
                    </Box>
                  )}

                  {enterpriseStatus && (
                    <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Typography variant="body2" fontWeight="medium">
                          Enterprise Integration
                        </Typography>
                        <Chip 
                          label={enterpriseStatus.initialized ? 'Active' : 'Inactive'}
                          size="small"
                          color={enterpriseStatus.initialized ? 'success' : 'default'}
                          variant="outlined"
                        />
                      </Box>
                      {enterpriseStatus.systems && enterpriseStatus.systems.length > 0 && (
                        <Typography variant="caption" color="text.secondary">
                          {enterpriseStatus.systems.length} systems connected
                        </Typography>
                      )}
                    </Box>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Department Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" sx={{ mb: 3 }}>
                Department Distribution
              </Typography>
              
              {insightsLoading ? (
                <LinearProgress />
              ) : pieChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No department data available
                  </Typography>
                  <Button
                    size="small"
                    startIcon={<LaunchIcon />}
                    onClick={() => navigate('/organization-insights')}
                    sx={{ mt: 1 }}
                  >
                    Generate Insights
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                Recent Activity
              </Typography>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Activity</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Time</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockRecentActivities.map((activity) => (
                      <TableRow key={activity.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getStatusIcon(activity.status)}
                            <Typography variant="body2" fontWeight="medium">
                              {activity.title}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {activity.description}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={activity.status} 
                            size="small" 
                            color={getStatusColor(activity.status) as any}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {activity.timestamp}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View details">
                            <IconButton size="small">
                              <LaunchIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;