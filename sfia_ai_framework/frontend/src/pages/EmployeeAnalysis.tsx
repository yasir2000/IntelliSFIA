import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Alert,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Paper,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useEmployeeAnalysis } from '../hooks';

interface AnalysisResult {
  employee_id: string;
  analysis_timestamp: string;
  suggestions: Array<{
    skill_name: string;
    skill_code: string;
    current_level?: number;
    suggested_level: number;
    confidence_score: number;
    reasoning: string;
    supporting_evidence?: string[];
    improvement_areas?: string[];
    timeline_estimate?: string;
  }>;
}

const EmployeeAnalysis: React.FC = () => {
  const [employeeId, setEmployeeId] = useState('');
  const [analysisType, setAnalysisType] = useState<'standard' | 'deep' | 'real_time'>('standard');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const { mutate: analyzeEmployee, isLoading, error } = useEmployeeAnalysis();

  const handleAnalyze = () => {
    if (!employeeId.trim()) return;

    analyzeEmployee(
      { employee_id: employeeId, analysis_type: analysisType },
      {
        onSuccess: (data) => {
          setAnalysisResult(data as AnalysisResult);
        },
      }
    );
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setEmployeeId('');
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  const getLevelColor = (level: number) => {
    if (level >= 5) return '#4caf50';
    if (level >= 3) return '#ff9800';
    return '#f44336';
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Employee SFIA Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Analyze individual employee skills and get intelligent SFIA level suggestions
        </Typography>
      </Box>

      {/* Input Form */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Employee Information
          </Typography>
          
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Employee ID"
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                placeholder="e.g., EMP001, john.doe, 12345"
                disabled={isLoading}
              />
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Analysis Type</InputLabel>
                <Select
                  value={analysisType}
                  label="Analysis Type"
                  onChange={(e) => setAnalysisType(e.target.value as any)}
                  disabled={isLoading}
                >
                  <MenuItem value="standard">Standard</MenuItem>
                  <MenuItem value="deep">Deep Analysis</MenuItem>
                  <MenuItem value="real_time">Real-time</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={<SearchIcon />}
                onClick={handleAnalyze}
                disabled={!employeeId.trim() || isLoading}
              >
                {isLoading ? 'Analyzing...' : 'Analyze Employee'}
              </Button>
            </Grid>

            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                size="large"
                startIcon={<RefreshIcon />}
                onClick={handleReset}
                disabled={isLoading}
              >
                Reset
              </Button>
            </Grid>
          </Grid>

          {isLoading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Analyzing employee {employeeId}... This may take a few moments.
              </Typography>
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              Analysis failed: {error.message}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <>
          {/* Summary Metrics */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <PersonIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h4" fontWeight="bold">
                  {analysisResult.suggestions.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Skills Analyzed
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <TrendingUpIcon color="success" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h4" fontWeight="bold">
                  {(analysisResult.suggestions.reduce((sum, s) => sum + s.confidence_score, 0) / analysisResult.suggestions.length * 100).toFixed(0)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Confidence
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="primary">
                  {(analysisResult.suggestions.reduce((sum, s) => sum + (s.current_level || 0), 0) / analysisResult.suggestions.length).toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Current Level
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="secondary">
                  {(analysisResult.suggestions.reduce((sum, s) => sum + s.suggested_level, 0) / analysisResult.suggestions.length).toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Suggested Level
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          {/* Detailed Analysis */}
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  SFIA Level Suggestions for {analysisResult.employee_id}
                </Typography>
                <Button
                  startIcon={<DownloadIcon />}
                  variant="outlined"
                  size="small"
                >
                  Download Report
                </Button>
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Analysis completed on {new Date(analysisResult.analysis_timestamp).toLocaleString()}
              </Typography>

              {analysisResult.suggestions.map((suggestion, index) => (
                <Accordion key={index} sx={{ mb: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
                      <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        {suggestion.skill_name}
                      </Typography>
                      <Chip
                        label={`Level ${suggestion.suggested_level}`}
                        sx={{ 
                          backgroundColor: getLevelColor(suggestion.suggested_level),
                          color: 'white',
                          fontWeight: 'bold'
                        }}
                      />
                      <Chip
                        label={`${(suggestion.confidence_score * 100).toFixed(0)}%`}
                        color={getConfidenceColor(suggestion.confidence_score) as any}
                        variant="outlined"
                      />
                    </Box>
                  </AccordionSummary>
                  
                  <AccordionDetails>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom>
                          Analysis Details
                        </Typography>
                        
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            Current Level: {suggestion.current_level || 'Not assessed'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Suggested Level: {suggestion.suggested_level}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Skill Code: {suggestion.skill_code}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Timeline: {suggestion.timeline_estimate || 'Not specified'}
                          </Typography>
                        </Box>

                        <Typography variant="subtitle2" gutterBottom>
                          Confidence Score
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                          <LinearProgress
                            variant="determinate"
                            value={suggestion.confidence_score * 100}
                            sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="body2">
                            {(suggestion.confidence_score * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom>
                          Reasoning
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {suggestion.reasoning}
                        </Typography>

                        {suggestion.supporting_evidence && suggestion.supporting_evidence.length > 0 && (
                          <>
                            <Typography variant="subtitle2" gutterBottom>
                              Supporting Evidence
                            </Typography>
                            <List dense>
                              {suggestion.supporting_evidence.map((evidence, idx) => (
                                <ListItem key={idx} sx={{ pl: 0 }}>
                                  <ListItemText 
                                    primary={`• ${evidence}`}
                                    primaryTypographyProps={{ variant: 'body2' }}
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </>
                        )}

                        {suggestion.improvement_areas && suggestion.improvement_areas.length > 0 && (
                          <>
                            <Typography variant="subtitle2" gutterBottom>
                              Improvement Areas
                            </Typography>
                            <List dense>
                              {suggestion.improvement_areas.map((area, idx) => (
                                <ListItem key={idx} sx={{ pl: 0 }}>
                                  <ListItemText 
                                    primary={`• ${area}`}
                                    primaryTypographyProps={{ variant: 'body2' }}
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </>
                        )}
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              ))}
            </CardContent>
          </Card>
        </>
      )}

      {/* Placeholder for empty state */}
      {!analysisResult && !isLoading && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <PersonIcon sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Analysis Results
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Enter an employee ID above and click "Analyze Employee" to get started
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default EmployeeAnalysis;