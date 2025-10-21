/*
 * IntelliSFIA Multi-Agent AI Page
 * ==============================
 * 
 * Enhanced React page with comprehensive AI capabilities:
 * - CrewAI multi-agent system integration
 * - SFIA semantic ontology knowledge base
 * - Conversation memory and session management
 * - Evidence validation workflows
 * - Real-time AI insights and guidance
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Grid,
  Tab,
  Tabs,
  Paper,
  Chip,
  Alert,
  Snackbar,
  Fab,
  Card,
  CardContent
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Chat as ChatIcon,
  Assessment as AssessmentIcon,
  Verified as VerifiedIcon,
  Dashboard as DashboardIcon,
  SmartToy as SmartToyIcon
} from '@mui/icons-material';

import {
  AIAssessmentPanel,
  ConversationChat,
  EvidenceValidator,
  AIInsightsSidebar,
  type AssessmentResult,
  type EvidenceValidation
} from '../components/AIComponents';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`ai-tabpanel-${index}`}
      aria-labelledby={`ai-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

const MultiAgentAI: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [assessmentResults, setAssessmentResults] = useState<AssessmentResult[]>([]);
  const [validationResults, setValidationResults] = useState<EvidenceValidation[]>([]);
  const [apiStatus, setApiStatus] = useState<'connecting' | 'connected' | 'error'>('connecting');
  const [snackbarMessage, setSnackbarMessage] = useState<string | null>(null);
  const [currentEvidence, setCurrentEvidence] = useState('');

  // Check API connection status
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          setApiStatus('connected');
        } else {
          setApiStatus('error');
        }
      } catch (error) {
        setApiStatus('error');
      }
    };

    checkApiStatus();
    const interval = setInterval(checkApiStatus, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleAssessmentComplete = (result: AssessmentResult) => {
    setAssessmentResults(prev => [result, ...prev.slice(0, 4)]);
    setSnackbarMessage(`Assessment completed for ${result.skill_title} - Level ${result.recommended_level}`);
    
    // Auto-switch to validation tab if evidence exists
    if (currentEvidence) {
      setCurrentTab(2);
    }
  };

  const handleValidationComplete = (result: EvidenceValidation) => {
    setValidationResults(prev => [result, ...prev.slice(0, 2)]);
    setSnackbarMessage(`Evidence validation completed - Quality score: ${result.evidence_quality_score}%`);
  };

  const getApiStatusChip = () => {
    const statusConfig = {
      connecting: { label: 'Connecting...', color: 'warning' as const },
      connected: { label: 'AI Connected', color: 'success' as const },
      error: { label: 'API Offline', color: 'error' as const }
    };

    const config = statusConfig[apiStatus];
    return (
      <Chip
        label={config.label}
        color={config.color}
        size="small"
        icon={<SmartToyIcon />}
      />
    );
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <PsychologyIcon sx={{ mr: 2, fontSize: '2rem' }} />
            Multi-Agent AI System
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            CrewAI Multi-Agent • Semantic Ontology • Conversation Memory • Evidence Validation
          </Typography>
        </Box>
        {getApiStatusChip()}
      </Box>

      {/* API Status Alert */}
      {apiStatus === 'error' && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <strong>AI API is offline.</strong> Please ensure the FastAPI server is running on localhost:8000.
          <br />
          <code>python intellisfia_ai_api.py</code>
        </Alert>
      )}

      <Container maxWidth="xl">
        <Grid container spacing={3}>
          {/* Main Content Area */}
          <Grid item xs={12} lg={9}>
            <Paper sx={{ p: 0 }}>
              <Tabs
                value={currentTab}
                onChange={handleTabChange}
                aria-label="AI Assessment Tools"
                variant="fullWidth"
                sx={{
                  borderBottom: 1,
                  borderColor: 'divider',
                  '& .MuiTab-root': {
                    minHeight: 64,
                    textTransform: 'none',
                    fontSize: '1rem'
                  }
                }}
              >
                <Tab
                  icon={<AssessmentIcon />}
                  label="AI Assessment"
                  iconPosition="start"
                />
                <Tab
                  icon={<ChatIcon />}
                  label="AI Chat"
                  iconPosition="start"
                />
                <Tab
                  icon={<VerifiedIcon />}
                  label="Evidence Validation"
                  iconPosition="start"
                />
                <Tab
                  icon={<DashboardIcon />}
                  label="Assessment History"
                  iconPosition="start"
                />
              </Tabs>

              <TabPanel value={currentTab} index={0}>
                <AIAssessmentPanel onAssessmentComplete={handleAssessmentComplete} />
              </TabPanel>

              <TabPanel value={currentTab} index={1}>
                <ConversationChat />
              </TabPanel>

              <TabPanel value={currentTab} index={2}>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Evidence Quality Validation
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Paste your professional evidence below to validate its quality, completeness, and relevance for SFIA assessment.
                  </Typography>
                </Box>

                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Professional Evidence
                    </Typography>
                    <textarea
                      value={currentEvidence}
                      onChange={(e) => setCurrentEvidence(e.target.value)}
                      placeholder="Paste your CV, project descriptions, achievements, or any professional evidence here..."
                      style={{
                        width: '100%',
                        height: '300px',
                        padding: '12px',
                        border: '1px solid #ddd',
                        borderRadius: '8px',
                        fontFamily: 'Roboto, sans-serif',
                        fontSize: '14px',
                        resize: 'vertical'
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <EvidenceValidator
                      evidence={currentEvidence}
                      onValidationComplete={handleValidationComplete}
                    />
                  </Grid>
                </Grid>
              </TabPanel>

              <TabPanel value={currentTab} index={3}>
                <Typography variant="h6" gutterBottom>
                  Assessment History & Multi-Agent Analytics
                </Typography>
                
                {/* CrewAI Agent Status */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={12} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" color="primary">SFIA Expert</Typography>
                        <Typography variant="body2">Framework specialist</Typography>
                        <Chip label="Active" color="success" size="small" />
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" color="primary">Career Advisor</Typography>
                        <Typography variant="body2">Strategic guidance</Typography>
                        <Chip label="Active" color="success" size="small" />
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" color="primary">Evidence Analyst</Typography>
                        <Typography variant="body2">Quality validation</Typography>
                        <Chip label="Active" color="success" size="small" />
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" color="primary">Semantic Reasoner</Typography>
                        <Typography variant="body2">Ontology processing</Typography>
                        <Chip label="Active" color="success" size="small" />
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
                
                {assessmentResults.length === 0 ? (
                  <Alert severity="info">
                    No assessments completed yet. Use the AI Assessment tab to get started.
                  </Alert>
                ) : (
                  <Grid container spacing={2}>
                    {assessmentResults.map((result, index) => (
                      <Grid item xs={12} md={6} key={result.assessment_id}>
                        <Paper sx={{ p: 2 }}>
                          <Typography variant="h6" gutterBottom>
                            {result.skill_title} ({result.skill_code})
                          </Typography>
                          <Typography variant="h4" color="primary" gutterBottom>
                            Level {result.recommended_level}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            Confidence: {result.confidence}% • {result.assessment_method}
                          </Typography>
                          <Typography variant="body2" sx={{ mt: 1 }}>
                            {result.reasoning.substring(0, 200)}...
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(result.timestamp).toLocaleString()}
                          </Typography>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </TabPanel>
            </Paper>
          </Grid>

          {/* AI Insights Sidebar */}
          <Grid item xs={12} lg={3}>
            <AIInsightsSidebar />
            
            {/* Recent Validation Results */}
            {validationResults.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Recent Validations
                  </Typography>
                  {validationResults.map((result, index) => (
                    <Box key={result.validation_id} sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Quality Score: <strong>{result.evidence_quality_score}%</strong>
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip label={`${result.completeness_score}% Complete`} size="small" />
                        <Chip label={`${result.relevance_score}% Relevant`} size="small" />
                      </Box>
                    </Box>
                  ))}
                </Paper>
              </Box>
            )}

            {/* Semantic Ontology Status */}
            <Box sx={{ mt: 3 }}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Semantic Knowledge Base
                </Typography>
                <Typography variant="body2" gutterBottom>
                  SFIA RDF/OWL Ontology: <strong>Active</strong>
                </Typography>
                <Typography variant="body2" gutterBottom>
                  Skills Mapped: <strong>147 SFIA Skills</strong>
                </Typography>
                <Typography variant="body2" gutterBottom>
                  Ontology Triples: <strong>847+</strong>
                </Typography>
                <Chip label="SPARQL Ready" color="success" size="small" />
              </Paper>
            </Box>

            {/* Quick Actions */}
            <Box sx={{ mt: 3 }}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Chip
                    label="Start New Assessment"
                    clickable
                    onClick={() => setCurrentTab(0)}
                    color="primary"
                  />
                  <Chip
                    label="Chat with AI Advisor"
                    clickable
                    onClick={() => setCurrentTab(1)}
                    color="secondary"
                  />
                  <Chip
                    label="Validate Evidence"
                    clickable
                    onClick={() => setCurrentTab(2)}
                  />
                </Box>
              </Paper>
            </Box>
          </Grid>
        </Grid>
      </Container>

      {/* Floating Action Button for Quick Chat */}
      <Fab
        color="primary"
        aria-label="chat"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          display: currentTab === 1 ? 'none' : 'flex'
        }}
        onClick={() => setCurrentTab(1)}
      >
        <ChatIcon />
      </Fab>

      {/* Success/Error Snackbar */}
      <Snackbar
        open={!!snackbarMessage}
        autoHideDuration={6000}
        onClose={() => setSnackbarMessage(null)}
        message={snackbarMessage}
      />
    </Box>
  );
};

export default MultiAgentAI;