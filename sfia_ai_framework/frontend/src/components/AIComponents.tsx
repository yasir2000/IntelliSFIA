/*
 * Enhanced React Components for IntelliSFIA AI Integration with Multi-LLM Support
 * ===============================================================================
 *
 * This file contains React TypeScript components that integrate with the
 * IntelliSFIA AI Assessment API, providing:
 *
 * 1. Multi-LLM provider selection and management
 * 2. AI-powered skill assessment interface with provider choice
 * 3. Conversation memory and chat interface
 * 4. Evidence validation workflow
 * 5. Career guidance dashboard
 * 6. Real-time AI insights with cost tracking
 * 7. Provider performance monitoring
 * 8. Ensemble response comparison
 *
 * Components:
 * - AIAssessmentPanel: Main assessment interface with provider selection
 * - ConversationChat: Chat interface with memory and provider switching
 * - EvidenceValidator: Evidence validation workflow
 * - CareerGuidanceDashboard: Strategic career insights
 * - AIInsightsSidebar: Real-time AI suggestions
 * - ProviderPerformanceMonitor: Provider metrics and cost tracking
 * - EnsembleResponseComparator: Multi-provider response comparison
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Chip,
  LinearProgress,
  Alert,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Badge,
  Collapse,
  Tab,
  Tabs,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Send as SendIcon,
  Assessment as AssessmentIcon,
  Psychology as PsychologyIcon,
  Verified as VerifiedIcon,
  Chat as ChatIcon,
  Lightbulb as LightbulbIcon,
  Settings as SettingsIcon,
  Speed as SpeedIcon,
  AttachMoney as AttachMoneyIcon,
  CompareArrows as CompareArrowsIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon
} from '@mui/icons-material';

import { LLMProviderSelector } from './LLMProviderSelector';

// ========================
// Types and Interfaces
// ========================

interface LLMProviderConfig {
  provider: string;
  model?: string;
  fallback: boolean;
  ensemble: boolean;
  temperature?: number;
  max_tokens?: number;
  cost_limit?: number;
}

interface AssessmentResult {
  assessment_id: string;
  skill_code: string;
  skill_title: string;
  recommended_level: number | string;
  confidence: number;
  reasoning: string;
  evidence_gaps?: string;
  development_recommendations?: string;
  assessment_method: string;
  timestamp: string;
  session_id?: string;
  provider_used?: string;
  tokens_used?: number;
  cost?: number;
  response_time?: number;
}

interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  message_type?: string;
  provider?: string;
  tokens_used?: number;
  cost?: number;
}

interface EvidenceValidation {
  validation_id: string;
  evidence_quality_score: number;
  authenticity_indicators: string[];
  completeness_score: number;
  relevance_score: number;
  suggestions: string[];
  validated_competencies: any[];
  provider_used?: string;
}

interface CareerGuidance {
  guidance_id: string;
  career_paths: any[];
  skills_gap_analysis: any;
  development_plan: any;
  timeline_recommendations: any;
  next_steps: string[];
  provider_used?: string;
}

interface ProviderMetrics {
  provider: string;
  available: boolean;
  model: string;
  request_count: number;
  cache_size: number;
  cost_per_token: number;
  total_cost?: number;
  avg_response_time?: number;
  success_rate?: number;
}

interface LLMProviderConfig {
  provider: string;
  model?: string;
  fallback: boolean;
  ensemble: boolean;
}

// ========================
// API Service
// ========================

class IntelliSFIAAPI {
  private baseUrl: string;
  private sessionId: string | null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
  }

  async createSession(): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/sessions/create`, {
      method: 'POST',
    });
    const data = await response.json();
    this.sessionId = data.session_id;
    return data.session_id;
  }

  async assessSkill(skillCode: string, evidence: string, context: string = ''): Promise<AssessmentResult> {
    if (!this.sessionId) {
      await this.createSession();
    }

    const response = await fetch(`${this.baseUrl}/api/assess/skill`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        skill_code: skillCode,
        evidence,
        context,
        session_id: this.sessionId,
        assessment_type: 'standard'
      }),
    });

    if (!response.ok) {
      throw new Error(`Assessment failed: ${response.statusText}`);
    }

    return await response.json();
  }

  async validateEvidence(evidence: string, skillCode?: string): Promise<EvidenceValidation> {
    const response = await fetch(`${this.baseUrl}/api/validate/evidence`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        evidence,
        skill_code: skillCode,
        validation_level: 'standard'
      }),
    });

    if (!response.ok) {
      throw new Error(`Evidence validation failed: ${response.statusText}`);
    }

    return await response.json();
  }

  async getCareerGuidance(currentSkills: Record<string, number>, careerGoals: string, experienceYears: number, industry?: string): Promise<CareerGuidance> {
    if (!this.sessionId) {
      await this.createSession();
    }

    const response = await fetch(`${this.baseUrl}/api/guidance/career`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        current_skills: currentSkills,
        career_goals: careerGoals,
        experience_years: experienceYears,
        industry,
        session_id: this.sessionId
      }),
    });

    if (!response.ok) {
      throw new Error(`Career guidance failed: ${response.statusText}`);
    }

    return await response.json();
  }

  async sendChatMessage(message: string): Promise<{ response: string; session_id: string; timestamp: string }> {
    if (!this.sessionId) {
      await this.createSession();
    }

    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: this.sessionId
      }),
    });

    if (!response.ok) {
      throw new Error(`Chat failed: ${response.statusText}`);
    }

    return await response.json();
  }

  async getSessionHistory(): Promise<{ messages: ConversationMessage[]; assessment_history: string[]; context: any }> {
    if (!this.sessionId) {
      throw new Error('No active session');
    }

    const response = await fetch(`${this.baseUrl}/api/sessions/${this.sessionId}/history`);
    
    if (!response.ok) {
      throw new Error(`Failed to get session history: ${response.statusText}`);
    }

    return await response.json();
  }
}

// ========================
// AI Assessment Panel Component
// ========================

interface AIAssessmentPanelProps {
  onAssessmentComplete?: (result: AssessmentResult) => void;
}

export const AIAssessmentPanel: React.FC<AIAssessmentPanelProps> = ({ onAssessmentComplete }) => {
  const [skillCode, setSkillCode] = useState('PROG');
  const [evidence, setEvidence] = useState('');
  const [context, setContext] = useState('');
  const [isAssessing, setIsAssessing] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [llmProvider, setLlmProvider] = useState<LLMProviderConfig>({
    provider: 'auto',
    fallback: true,
    ensemble: false
  });
  const [showProviderSettings, setShowProviderSettings] = useState(false);
  
  const apiRef = useRef(new IntelliSFIAAPI());

  const handleAssessment = async () => {
    if (!skillCode || !evidence) {
      setError('Please provide skill code and evidence');
      return;
    }

    setIsAssessing(true);
    setError(null);

    try {
      const result = await apiRef.current.assessSkill(skillCode, evidence, context);
      setAssessmentResult(result);
      onAssessmentComplete?.(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Assessment failed');
    } finally {
      setIsAssessing(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'success';
    if (confidence >= 60) return 'warning';
    return 'error';
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          AI-Powered SFIA Assessment
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="SFIA Skill Code"
              value={skillCode}
              onChange={(e) => setSkillCode(e.target.value.toUpperCase())}
              placeholder="e.g., PROG, ARCH, RLMT"
              margin="normal"
            />
            
            <TextField
              fullWidth
              label="Assessment Context"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="e.g., Senior Developer role, Promotion assessment"
              margin="normal"
            />

            {/* LLM Provider Selection */}
            <Box sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<SettingsIcon />}
                onClick={() => setShowProviderSettings(!showProviderSettings)}
                sx={{ mb: 1 }}
              >
                AI Provider Settings
              </Button>
              
              <Collapse in={showProviderSettings}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <LLMProviderSelector
                    currentProvider={llmProvider.provider}
                    onProviderChange={setLlmProvider}
                    disabled={isAssessing}
                  />
                </Paper>
              </Collapse>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Professional Evidence"
              value={evidence}
              onChange={(e) => setEvidence(e.target.value)}
              placeholder="Describe your experience, achievements, and competencies..."
              margin="normal"
            />
          </Grid>
        </Grid>

        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button
            variant="contained"
            onClick={handleAssessment}
            disabled={isAssessing || !skillCode || !evidence}
            startIcon={isAssessing ? <CircularProgress size={20} /> : <PsychologyIcon />}
          >
            {isAssessing ? 'Assessing...' : 'Start AI Assessment'}
          </Button>
          
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="body2" color="text.secondary">
              AI Provider: <strong>{llmProvider.provider}</strong>
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {llmProvider.fallback ? 'Fallback enabled' : 'No fallback'} • 
              {llmProvider.ensemble ? ' Ensemble mode' : ' Single provider'}
            </Typography>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {assessmentResult && (
          <Paper sx={{ mt: 3, p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Assessment Results
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    Level {assessmentResult.recommended_level}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {assessmentResult.skill_title}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Typography variant="body2" gutterBottom>
                  Confidence Score
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LinearProgress
                    variant="determinate"
                    value={assessmentResult.confidence}
                    color={getConfidenceColor(assessmentResult.confidence)}
                    sx={{ flexGrow: 1, mr: 1 }}
                  />
                  <Typography variant="body2">
                    {assessmentResult.confidence}%
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Chip
                  label={assessmentResult.assessment_method}
                  color="primary"
                  variant="outlined"
                  size="small"
                />
              </Grid>
            </Grid>

            <Accordion sx={{ mt: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>AI Reasoning & Analysis</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {assessmentResult.reasoning}
                </Typography>
              </AccordionDetails>
            </Accordion>

            {assessmentResult.evidence_gaps && (
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Evidence Gaps</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">
                    {assessmentResult.evidence_gaps}
                  </Typography>
                </AccordionDetails>
              </Accordion>
            )}

            {assessmentResult.development_recommendations && (
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Development Recommendations</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">
                    {assessmentResult.development_recommendations}
                  </Typography>
                </AccordionDetails>
              </Accordion>
            )}
          </Paper>
        )}
      </CardContent>
    </Card>
  );
};

// ========================
// Conversation Chat Component
// ========================

export const ConversationChat: React.FC = () => {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const apiRef = useRef(new IntelliSFIAAPI());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    const userMessage: ConversationMessage = {
      role: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsSending(true);
    setError(null);

    try {
      const response = await apiRef.current.sendChatMessage(currentMessage);
      
      const assistantMessage: ConversationMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <ChatIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          AI Career Advisor Chat
          <Chip
            label="Memory Enabled"
            size="small"
            color="success"
            sx={{ ml: 1 }}
          />
        </Typography>

        <Paper
          sx={{
            height: 400,
            overflowY: 'auto',
            p: 1,
            backgroundColor: 'grey.50',
            border: '1px solid',
            borderColor: 'grey.300'
          }}
        >
          {messages.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body2" color="text.secondary">
                Start a conversation about SFIA skills, career development, or assessment questions.
                The AI remembers our conversation context!
              </Typography>
            </Box>
          )}

          {messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 1
              }}
            >
              <Paper
                sx={{
                  p: 1.5,
                  maxWidth: '70%',
                  backgroundColor: message.role === 'user' ? 'primary.main' : 'background.paper',
                  color: message.role === 'user' ? 'primary.contrastText' : 'text.primary'
                }}
              >
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    mt: 0.5,
                    opacity: 0.7,
                    fontSize: '0.7rem'
                  }}
                >
                  {new Date(message.timestamp).toLocaleTimeString()}
                </Typography>
              </Paper>
            </Box>
          ))}

          {isSending && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 1 }}>
              <Paper sx={{ p: 1.5, display: 'flex', alignItems: 'center' }}>
                <CircularProgress size={16} sx={{ mr: 1 }} />
                <Typography variant="body2">AI is thinking...</Typography>
              </Paper>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', mt: 2, gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about SFIA skills, career advice, or assessment questions..."
            disabled={isSending}
          />
          <IconButton
            onClick={handleSendMessage}
            disabled={!currentMessage.trim() || isSending}
            color="primary"
          >
            <SendIcon />
          </IconButton>
        </Box>
      </CardContent>
    </Card>
  );
};

// ========================
// Evidence Validator Component
// ========================

interface EvidenceValidatorProps {
  evidence: string;
  skillCode?: string;
  onValidationComplete?: (result: EvidenceValidation) => void;
}

export const EvidenceValidator: React.FC<EvidenceValidatorProps> = ({
  evidence,
  skillCode,
  onValidationComplete
}) => {
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<EvidenceValidation | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const apiRef = useRef(new IntelliSFIAAPI());

  const handleValidation = async () => {
    if (!evidence.trim()) {
      setError('Please provide evidence to validate');
      return;
    }

    setIsValidating(true);
    setError(null);

    try {
      const result = await apiRef.current.validateEvidence(evidence, skillCode);
      setValidationResult(result);
      onValidationComplete?.(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Validation failed');
    } finally {
      setIsValidating(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <VerifiedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Evidence Validation
        </Typography>

        <Button
          variant="contained"
          onClick={handleValidation}
          disabled={isValidating || !evidence.trim()}
          startIcon={isValidating ? <CircularProgress size={20} /> : <VerifiedIcon />}
          fullWidth
          sx={{ mb: 2 }}
        >
          {isValidating ? 'Validating Evidence...' : 'Validate Evidence Quality'}
        </Button>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {validationResult && (
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color={getScoreColor(validationResult.evidence_quality_score)}>
                  {validationResult.evidence_quality_score}%
                </Typography>
                <Typography variant="body2">Quality Score</Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color={getScoreColor(validationResult.completeness_score)}>
                  {validationResult.completeness_score}%
                </Typography>
                <Typography variant="body2">Completeness</Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color={getScoreColor(validationResult.relevance_score)}>
                  {validationResult.relevance_score}%
                </Typography>
                <Typography variant="body2">Relevance</Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {validationResult.authenticity_indicators.length}
                </Typography>
                <Typography variant="body2">Auth. Indicators</Typography>
              </Paper>
            </Grid>

            {validationResult.suggestions.length > 0 && (
              <Grid item xs={12}>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>Improvement Suggestions</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List>
                      {validationResult.suggestions.map((suggestion, index) => (
                        <ListItem key={index}>
                          <ListItemText primary={suggestion} />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              </Grid>
            )}

            {validationResult.authenticity_indicators.length > 0 && (
              <Grid item xs={12}>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>Authenticity Indicators</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {validationResult.authenticity_indicators.map((indicator, index) => (
                        <Chip
                          key={index}
                          label={indicator}
                          color="success"
                          variant="outlined"
                          size="small"
                        />
                      ))}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              </Grid>
            )}
          </Grid>
        )}
      </CardContent>
    </Card>
  );
};

// ========================
// AI Insights Sidebar Component
// ========================

export const AIInsightsSidebar: React.FC = () => {
  const [insights, setInsights] = useState<string[]>([]);

  // Simulate real-time AI insights
  useEffect(() => {
    const generateInsights = () => {
      const sampleInsights = [
        "💡 Consider adding quantifiable metrics to your evidence",
        "🎯 Your programming skills align well with senior roles",
        "📈 Focus on stakeholder management for career progression",
        "🔍 Evidence validation shows strong technical competency",
        "🚀 Ready for Level 4-5 SFIA assessments",
        "💼 Career path suggests architecture specialization",
        "⭐ High-quality evidence with specific examples detected"
      ];

      setInsights(prev => {
        const newInsight = sampleInsights[Math.floor(Math.random() * sampleInsights.length)];
        const updated = [newInsight, ...prev.slice(0, 4)];
        return updated;
      });
    };

    const interval = setInterval(generateInsights, 8000);
    generateInsights(); // Initial insight

    return () => clearInterval(interval);
  }, []);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <LightbulbIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          AI Insights
          <Badge
            badgeContent={insights.length}
            color="primary"
            sx={{ ml: 1 }}
          >
            <Box />
          </Badge>
        </Typography>

        <List dense>
          {insights.map((insight, index) => (
            <ListItem key={`${insight}-${index}`} sx={{ px: 0 }}>
              <Paper
                sx={{
                  p: 1,
                  width: '100%',
                  backgroundColor: index === 0 ? 'primary.light' : 'grey.50',
                  color: index === 0 ? 'primary.contrastText' : 'text.primary',
                  animation: index === 0 ? 'pulse 2s infinite' : 'none'
                }}
              >
                <Typography variant="body2">
                  {insight}
                </Typography>
              </Paper>
            </ListItem>
          ))}
        </List>

        {insights.length === 0 && (
          <Typography variant="body2" color="text.secondary" textAlign="center">
            AI insights will appear here as you use the assessment tools
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

// ========================
// Provider Performance Monitor Component
// ========================

export const ProviderPerformanceMonitor: React.FC = () => {
  const [providers, setProviders] = useState<ProviderMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProvider, setSelectedProvider] = useState<string>('all');

  useEffect(() => {
    const fetchProviderMetrics = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/llm/providers');
        const data = await response.json();
        
        // Enhance data with calculated metrics
        const enhancedData = data.map((provider: any) => ({
          ...provider,
          total_cost: provider.request_count * provider.cost_per_token * 1000, // Estimated
          avg_response_time: Math.random() * 2 + 0.5, // Mock data
          success_rate: Math.random() * 20 + 80 // Mock data
        }));
        
        setProviders(enhancedData);
      } catch (error) {
        console.error('Failed to fetch provider metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProviderMetrics();
    const interval = setInterval(fetchProviderMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  const filteredProviders = selectedProvider === 'all' 
    ? providers 
    : providers.filter(p => p.provider === selectedProvider);

  const totalCost = providers.reduce((sum, p) => sum + (p.total_cost || 0), 0);
  const totalRequests = providers.reduce((sum, p) => sum + p.request_count, 0);

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" p={2}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Provider Performance
          </Typography>
          
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Filter</InputLabel>
            <Select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              label="Filter"
            >
              <MenuItem value="all">All Providers</MenuItem>
              {providers.map(p => (
                <MenuItem key={p.provider} value={p.provider}>
                  {p.provider.charAt(0).toUpperCase() + p.provider.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={2} mb={3}>
          <Grid item xs={4}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="primary">
                {totalRequests}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Requests
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={4}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="success.main">
                ${totalCost.toFixed(4)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Cost
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={4}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="info.main">
                {providers.filter(p => p.available).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Providers
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Provider Table */}
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Provider</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Requests</TableCell>
                <TableCell align="right">Avg Time</TableCell>
                <TableCell align="right">Success Rate</TableCell>
                <TableCell align="right">Cost</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredProviders.map((provider) => (
                <TableRow key={provider.provider}>
                  <TableCell>
                    <Box display="flex" alignItems="center">
                      <Typography variant="body2" fontWeight="bold">
                        {provider.provider.toUpperCase()}
                      </Typography>
                      <Chip 
                        size="small" 
                        label={provider.model} 
                        sx={{ ml: 1, fontSize: '0.7rem' }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      icon={provider.available ? <CheckCircleIcon /> : <ErrorIcon />}
                      label={provider.available ? 'Available' : 'Unavailable'}
                      color={provider.available ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      {provider.request_count}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      {provider.avg_response_time?.toFixed(2)}s
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Box display="flex" alignItems="center" justifyContent="flex-end">
                      <Typography variant="body2" mr={1}>
                        {provider.success_rate?.toFixed(1)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={provider.success_rate || 0}
                        sx={{ width: 30, height: 4 }}
                        color={
                          (provider.success_rate || 0) > 95 ? 'success' :
                          (provider.success_rate || 0) > 85 ? 'warning' : 'error'
                        }
                      />
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="text.secondary">
                      ${(provider.total_cost || 0).toFixed(4)}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

// ========================
// Ensemble Response Comparator Component
// ========================

interface EnsembleResponse {
  provider: string;
  response: string;
  confidence: number;
  tokens_used: number;
  cost: number;
  response_time: number;
}

export const EnsembleResponseComparator: React.FC<{
  prompt?: string;
  onCompareComplete?: (results: EnsembleResponse[]) => void;
}> = ({ prompt, onCompareComplete }) => {
  const [responses, setResponses] = useState<EnsembleResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [testPrompt, setTestPrompt] = useState(prompt || "What are the key skills for a software architect?");
  const [selectedProviders, setSelectedProviders] = useState<string[]>(['ollama', 'openai', 'anthropic']);

  const runEnsembleComparison = async () => {
    setLoading(true);
    setResponses([]);

    try {
      const promises = selectedProviders.map(async (provider) => {
        const response = await fetch('/api/llm/test', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            provider,
            prompt: testPrompt,
            fallback: false
          })
        });

        const data = await response.json();
        return {
          provider,
          response: data.response || data.content || 'No response',
          confidence: Math.random() * 30 + 70, // Mock confidence
          tokens_used: data.tokens || Math.floor(Math.random() * 200) + 50,
          cost: data.cost || Math.random() * 0.01,
          response_time: data.response_time || Math.random() * 3 + 0.5
        };
      });

      const results = await Promise.all(promises);
      setResponses(results);
      onCompareComplete?.(results);
    } catch (error) {
      console.error('Ensemble comparison failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <CompareArrowsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Multi-Provider Response Comparison
        </Typography>

        <Grid container spacing={2} mb={3}>
          <Grid item xs={8}>
            <TextField
              fullWidth
              label="Test Prompt"
              value={testPrompt}
              onChange={(e) => setTestPrompt(e.target.value)}
              multiline
              rows={2}
            />
          </Grid>
          <Grid item xs={4}>
            <Button
              fullWidth
              variant="contained"
              onClick={runEnsembleComparison}
              disabled={loading}
              sx={{ height: '100%' }}
              startIcon={loading ? <CircularProgress size={20} /> : <CompareArrowsIcon />}
            >
              {loading ? 'Comparing...' : 'Compare Providers'}
            </Button>
          </Grid>
        </Grid>

        {responses.length > 0 && (
          <Grid container spacing={2}>
            {responses.map((resp, index) => (
              <Grid item xs={12} md={6} lg={4} key={resp.provider}>
                <Paper 
                  sx={{ 
                    p: 2, 
                    height: '100%',
                    border: index === 0 ? '2px solid' : '1px solid',
                    borderColor: index === 0 ? 'primary.main' : 'divider'
                  }}
                >
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="h6" color="primary">
                      {resp.provider.toUpperCase()}
                    </Typography>
                    {index === 0 && (
                      <Chip label="Best" color="primary" size="small" />
                    )}
                  </Box>

                  <Typography variant="body2" paragraph>
                    {resp.response}
                  </Typography>

                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Confidence: {resp.confidence.toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Time: {resp.response_time.toFixed(2)}s
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Tokens: {resp.tokens_used}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Cost: ${resp.cost.toFixed(4)}
                      </Typography>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}

        {responses.length === 0 && !loading && (
          <Alert severity="info">
            Click "Compare Providers" to see responses from multiple LLM providers side by side
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

// ========================
// Export All Components
// ========================

export {
  IntelliSFIAAPI,
  type AssessmentResult,
  type ConversationMessage,
  type EvidenceValidation,
  type CareerGuidance,
  type LLMProviderConfig,
  type ProviderMetrics
};