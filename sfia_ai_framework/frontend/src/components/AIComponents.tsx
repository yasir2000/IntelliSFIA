/*
 * Enhanced React Components for IntelliSFIA AI Integration
 * ======================================================
 *
 * This file contains React TypeScript components that integrate with the
 * IntelliSFIA AI Assessment API, providing:
 *
 * 1. AI-powered skill assessment interface
 * 2. Conversation memory and chat interface
 * 3. Evidence validation workflow
 * 4. Career guidance dashboard
 * 5. Real-time AI insights
 *
 * Components:
 * - AIAssessmentPanel: Main assessment interface
 * - ConversationChat: Chat interface with memory
 * - EvidenceValidator: Evidence validation workflow
 * - CareerGuidanceDashboard: Strategic career insights
 * - AIInsightsSidebar: Real-time AI suggestions
 */

import React, { useState, useEffect, useRef } from 'react';
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
  Collapse
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Send as SendIcon,
  Assessment as AssessmentIcon,
  Psychology as PsychologyIcon,
  Verified as VerifiedIcon,
  Chat as ChatIcon,
  Lightbulb as LightbulbIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

import { LLMProviderSelector } from './LLMProviderSelector';

// ========================
// Types and Interfaces
// ========================

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
}

interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  message_type?: string;
}

interface EvidenceValidation {
  validation_id: string;
  evidence_quality_score: number;
  authenticity_indicators: string[];
  completeness_score: number;
  relevance_score: number;
  suggestions: string[];
  validated_competencies: any[];
}

interface CareerGuidance {
  guidance_id: string;
  career_paths: any[];
  skills_gap_analysis: any;
  development_plan: any;
  timeline_recommendations: any;
  next_steps: string[];
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
// Export All Components
// ========================

export {
  IntelliSFIAAPI,
  type AssessmentResult,
  type ConversationMessage,
  type EvidenceValidation,
  type CareerGuidance
};