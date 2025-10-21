import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Tabs,
  Tab,
  Alert,
  LinearProgress,
  Chip,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,

  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  Psychology as PsychologyIcon
} from '@mui/icons-material';
import { apiService } from '../services/api';
import { useSnackbar } from 'notistack';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`portfolio-tabpanel-${index}`}
      aria-labelledby={`portfolio-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface PortfolioEntry {
  id: string;
  date: string;
  title: string;
  content: string;
  type: string;
  supervisor_verified: boolean;
}

interface SupervisorComment {
  id: string;
  supervisor_name: string;
  supervisor_role: string;
  organization: string;
  comment: string;
  accuracy_confirmation: boolean;
  contextual_evaluation: boolean;
}

interface AssessmentResult {
  assessment_id: string;
  student_name: string;
  skill_assessed: string;
  level_assessed: number;
  total_score: number;
  proficiency_level: string;
  pass_status: boolean;
  technical_score: number;
  reflection_score: number;
  generic_responsibility_pass: boolean;
  assessor_name: string;
  assessment_date: string;
  recommendations: string[];
}

const PortfolioAssessment: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [portfolioEntries, setPortfolioEntries] = useState<PortfolioEntry[]>([]);
  const [supervisorComments, setSupervisorComments] = useState<SupervisorComment[]>([]);
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResult | null>(null);
  const [guidanceResult, setGuidanceResult] = useState<any>(null);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [templateResult, setTemplateResult] = useState<any>(null);
  const [methodologyDialog, setMethodologyDialog] = useState(false);
  
  // Form states
  const [studentName, setStudentName] = useState('');
  const [assessorName, setAssessorName] = useState('');
  const [suggestedSkill, setSuggestedSkill] = useState('');
  const [suggestedLevel, setSuggestedLevel] = useState<number>(3);
  const [activitiesDescription, setActivitiesDescription] = useState('');
  const [studentLevel, setStudentLevel] = useState('placement');
  
  const { enqueueSnackbar } = useSnackbar();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>, type: 'portfolio' | 'supervisor') => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string);
          if (type === 'portfolio') {
            setPortfolioEntries(data);
            enqueueSnackbar('Portfolio entries loaded successfully', { variant: 'success' });
          } else {
            setSupervisorComments(data);
            enqueueSnackbar('Supervisor comments loaded successfully', { variant: 'success' });
          }
        } catch (error) {
          enqueueSnackbar('Error parsing JSON file', { variant: 'error' });
        }
      };
      reader.readAsText(file);
    }
  };

  const handleAssessPortfolio = async () => {
    if (!portfolioEntries.length || !supervisorComments.length || !studentName || !assessorName) {
      enqueueSnackbar('Please provide all required information', { variant: 'warning' });
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.assessPortfolio({
        portfolio_entries: portfolioEntries,
        supervisor_comments: supervisorComments,
        student_info: { name: studentName, id: `student_${Date.now()}` },
        assessor_info: { name: assessorName, id: `assessor_${Date.now()}` },
        suggested_skill: suggestedSkill || undefined,
        suggested_level: suggestedLevel || undefined
      });

      if (response.success && response.summary) {
        setAssessmentResult(response.summary);
        enqueueSnackbar('Portfolio assessment completed successfully', { variant: 'success' });
      } else {
        enqueueSnackbar(response.message || 'Assessment failed', { variant: 'error' });
      }
    } catch (error) {
      enqueueSnackbar('Error during portfolio assessment', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleGetGuidance = async () => {
    if (!activitiesDescription) {
      enqueueSnackbar('Please provide activities description', { variant: 'warning' });
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.getPortfolioGuidance({
        activities_description: activitiesDescription,
        student_level: studentLevel
      });

      if (response.status === 'success') {
        setGuidanceResult(response.guidance);
        enqueueSnackbar('Portfolio guidance generated successfully', { variant: 'success' });
      } else {
        enqueueSnackbar('Failed to generate guidance', { variant: 'error' });
      }
    } catch (error) {
      enqueueSnackbar('Error generating portfolio guidance', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleValidatePortfolio = async () => {
    if (!portfolioEntries.length || !suggestedSkill) {
      enqueueSnackbar('Please provide portfolio entries and skill code', { variant: 'warning' });
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.validatePortfolioEvidence({
        portfolio_entries: portfolioEntries,
        skill_code: suggestedSkill,
        skill_level: suggestedLevel
      });

      if (response.success) {
        setValidationResult(response);
        enqueueSnackbar('Portfolio validation completed', { variant: 'success' });
      } else {
        enqueueSnackbar(response.error || 'Validation failed', { variant: 'error' });
      }
    } catch (error) {
      enqueueSnackbar('Error during portfolio validation', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTemplate = async () => {
    if (!suggestedSkill) {
      enqueueSnackbar('Please provide skill code', { variant: 'warning' });
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.generatePortfolioTemplate({
        skill_code: suggestedSkill,
        skill_level: suggestedLevel,
        placement_context: 'Industrial placement or internship'
      });

      if (response.success) {
        setTemplateResult(response);
        enqueueSnackbar('Portfolio template generated successfully', { variant: 'success' });
      } else {
        enqueueSnackbar(response.error || 'Template generation failed', { variant: 'error' });
      }
    } catch (error) {
      enqueueSnackbar('Error generating portfolio template', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const getProficiencyColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'competency': return 'success';
      case 'proficiency': return 'primary';
      case 'developing': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SchoolIcon />
          Portfolio Assessment (IoC Methodology)
        </Typography>
        <Button
          variant="outlined"
          startIcon={<InfoIcon />}
          onClick={() => setMethodologyDialog(true)}
        >
          About IoC Methodology
        </Button>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Assessment" icon={<AssessmentIcon />} />
          <Tab label="Guidance" icon={<PsychologyIcon />} />
          <Tab label="Validation" icon={<CheckCircleIcon />} />
          <Tab label="Template" icon={<AssignmentIcon />} />
        </Tabs>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Assessment Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Portfolio Data Upload
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Button
                    variant="outlined"
                    component="label"
                    startIcon={<UploadIcon />}
                    fullWidth
                    sx={{ mb: 1 }}
                  >
                    Upload Portfolio Entries (JSON)
                    <input
                      type="file"
                      hidden
                      accept=".json"
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleFileUpload(e, 'portfolio')}
                    />
                  </Button>
                  {portfolioEntries.length > 0 && (
                    <Alert severity="success">
                      {portfolioEntries.length} portfolio entries loaded
                    </Alert>
                  )}
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Button
                    variant="outlined"
                    component="label"
                    startIcon={<UploadIcon />}
                    fullWidth
                    sx={{ mb: 1 }}
                  >
                    Upload Supervisor Comments (JSON)
                    <input
                      type="file"
                      hidden
                      accept=".json"
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleFileUpload(e, 'supervisor')}
                    />
                  </Button>
                  {supervisorComments.length > 0 && (
                    <Alert severity="success">
                      {supervisorComments.length} supervisor comments loaded
                    </Alert>
                  )}
                </Box>

                <TextField
                  fullWidth
                  label="Student Name"
                  value={studentName}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setStudentName(e.target.value)}
                  sx={{ mb: 2 }}
                />

                <TextField
                  fullWidth
                  label="Assessor Name"
                  value={assessorName}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAssessorName(e.target.value)}
                  sx={{ mb: 2 }}
                />

                <Grid container spacing={2}>
                  <Grid item xs={8}>
                    <TextField
                      fullWidth
                      label="Suggested SFIA Skill Code (Optional)"
                      value={suggestedSkill}
                      onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => setSuggestedSkill(e.target.value)}
                      placeholder="e.g., DTAN, PROG, BUAN"
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <FormControl fullWidth>
                      <InputLabel>Level</InputLabel>
                      <Select
                        value={suggestedLevel}
                        label="Level"
                        onChange={(e) => setSuggestedLevel(e.target.value as number)}
                      >
                        {Array.from({ length: 7 }, (_, i) => i + 1).map((level) => (
                          <MenuItem key={level} value={level}>
                            {level}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>

                <Button
                  variant="contained"
                  onClick={handleAssessPortfolio}
                  disabled={loading}
                  fullWidth
                  sx={{ mt: 2 }}
                >
                  Assess Portfolio
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {assessmentResult && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TrendingUpIcon />
                    Assessment Results
                  </Typography>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2">Student: {assessmentResult.student_name}</Typography>
                    <Typography variant="subtitle2">Skill: {assessmentResult.skill_assessed}</Typography>
                    <Typography variant="subtitle2">Assessor: {assessmentResult.assessor_name}</Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Total Score: {assessmentResult.total_score.toFixed(1)}/100
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={assessmentResult.total_score}
                      sx={{ height: 8, borderRadius: 4, mb: 1 }}
                    />
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <Chip
                        label={`Technical: ${assessmentResult.technical_score.toFixed(1)}/64`}
                        size="small"
                        color="primary"
                      />
                      <Chip
                        label={`Reflection: ${assessmentResult.reflection_score.toFixed(1)}/36`}
                        size="small"
                        color="secondary"
                      />
                    </Box>
                  </Box>

                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip
                      label={assessmentResult.proficiency_level}
                      color={getProficiencyColor(assessmentResult.proficiency_level) as any}
                      variant="filled"
                    />
                    <Chip
                      label={assessmentResult.pass_status ? "Overall Pass" : "Overall Fail"}
                      color={assessmentResult.pass_status ? "success" : "error"}
                      icon={assessmentResult.pass_status ? <CheckCircleIcon /> : <WarningIcon />}
                    />
                    <Chip
                      label={assessmentResult.generic_responsibility_pass ? "Generic Pass" : "Generic Fail"}
                      color={assessmentResult.generic_responsibility_pass ? "success" : "error"}
                      variant="outlined"
                    />
                  </Box>

                  {assessmentResult.recommendations.length > 0 && (
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Recommendations ({assessmentResult.recommendations.length})</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {assessmentResult.recommendations.map((rec, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <CheckCircleIcon fontSize="small" />
                              </ListItemIcon>
                              <ListItemText primary={rec} />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  )}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Guidance Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Portfolio Mapping Guidance
                </Typography>
                
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Activities Description"
                  value={activitiesDescription}
                  onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => setActivitiesDescription(e.target.value)}
                  placeholder="Describe the student's activities, projects, and responsibilities..."
                  sx={{ mb: 2 }}
                />

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Student Level</InputLabel>
                  <Select
                    value={studentLevel}
                    label="Student Level"
                    onChange={(e) => setStudentLevel(e.target.value)}
                  >
                    <MenuItem value="placement">Placement/Internship</MenuItem>
                    <MenuItem value="graduate">Graduate</MenuItem>
                    <MenuItem value="undergraduate">Undergraduate</MenuItem>
                    <MenuItem value="postgraduate">Postgraduate</MenuItem>
                  </Select>
                </FormControl>

                <Button
                  variant="contained"
                  onClick={handleGetGuidance}
                  disabled={loading}
                  fullWidth
                >
                  Get Guidance
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {guidanceResult && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recommended SFIA Skills
                  </Typography>
                  
                  {guidanceResult.recommended_skills && guidanceResult.recommended_skills.map((skill: any, index: number) => (
                    <Paper key={index} sx={{ p: 2, mb: 2 }}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {skill.skill_name} ({skill.skill_code})
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Suggested Level: {skill.suggested_level} | Confidence: {(skill.confidence * 100).toFixed(0)}%
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        {skill.matching_keywords?.map((keyword: string) => (
                          <Chip key={keyword} label={keyword} size="small" sx={{ mr: 1, mb: 1 }} />
                        ))}
                      </Box>
                    </Paper>
                  ))}

                  {guidanceResult.best_practices && (
                    <Accordion sx={{ mt: 2 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Best Practices</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {guidanceResult.best_practices.map((practice: string, index: number) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <CheckCircleIcon fontSize="small" color="success" />
                              </ListItemIcon>
                              <ListItemText primary={practice} />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  )}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Validation Tab */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Portfolio Validation
                </Typography>
                
                <Alert severity="info" sx={{ mb: 2 }}>
                  Upload portfolio entries first in the Assessment tab
                </Alert>

                <Grid container spacing={2}>
                  <Grid item xs={8}>
                    <TextField
                      fullWidth
                      label="SFIA Skill Code"
                      value={suggestedSkill}
                      onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => setSuggestedSkill(e.target.value)}
                      placeholder="e.g., DTAN, PROG, BUAN"
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <FormControl fullWidth>
                      <InputLabel>Level</InputLabel>
                      <Select
                        value={suggestedLevel}
                        label="Level"
                        onChange={(e) => setSuggestedLevel(e.target.value as number)}
                      >
                        {Array.from({ length: 7 }, (_, i) => i + 1).map((level) => (
                          <MenuItem key={level} value={level}>
                            {level}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>

                <Button
                  variant="contained"
                  onClick={handleValidatePortfolio}
                  disabled={loading || !portfolioEntries.length}
                  fullWidth
                  sx={{ mt: 2 }}
                >
                  Validate Portfolio
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {validationResult && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Validation Results
                  </Typography>
                  
                  <Typography variant="subtitle2" gutterBottom>
                    {validationResult.skill_code} Level {validationResult.skill_level}
                  </Typography>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      Coverage: {validationResult.coverage_metrics.coverage_percentage.toFixed(1)}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={validationResult.coverage_metrics.coverage_percentage}
                      color={validationResult.coverage_metrics.coverage_percentage >= 85 ? "success" : "warning"}
                      sx={{ height: 8, borderRadius: 4, mb: 1 }}
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      Multiple Entries: {validationResult.coverage_metrics.multiple_entry_percentage.toFixed(1)}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={validationResult.coverage_metrics.multiple_entry_percentage}
                      color={validationResult.coverage_metrics.multiple_entry_percentage >= 85 ? "success" : "warning"}
                      sx={{ height: 8, borderRadius: 4, mb: 1 }}
                    />
                  </Box>

                  <Chip
                    label={validationResult.meets_ioc_criteria ? "Meets IoC Criteria" : "Does Not Meet Criteria"}
                    color={validationResult.meets_ioc_criteria ? "success" : "error"}
                    icon={validationResult.meets_ioc_criteria ? <CheckCircleIcon /> : <WarningIcon />}
                    sx={{ mb: 2 }}
                  />

                  {validationResult.recommendations?.length > 0 && (
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Recommendations</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {validationResult.recommendations.map((rec: string, index: number) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <CheckCircleIcon fontSize="small" />
                              </ListItemIcon>
                              <ListItemText primary={rec} />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  )}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Template Tab */}
      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Generate Portfolio Template
                </Typography>
                
                <Grid container spacing={2} sx={{ mb: 2 }}>
                  <Grid item xs={8}>
                    <TextField
                      fullWidth
                      label="SFIA Skill Code"
                      value={suggestedSkill}
                      onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => setSuggestedSkill(e.target.value)}
                      placeholder="e.g., DTAN, PROG, BUAN"
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <FormControl fullWidth>
                      <InputLabel>Level</InputLabel>
                      <Select
                        value={suggestedLevel}
                        label="Level"
                        onChange={(e) => setSuggestedLevel(e.target.value as number)}
                      >
                        {Array.from({ length: 7 }, (_, i) => i + 1).map((level) => (
                          <MenuItem key={level} value={level}>
                            {level}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>

                <Button
                  variant="contained"
                  onClick={handleGenerateTemplate}
                  disabled={loading}
                  fullWidth
                >
                  Generate Template
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {templateResult && (
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                      Portfolio Template
                    </Typography>
                    <Button
                      startIcon={<DownloadIcon />}
                      onClick={() => {
                        const blob = new Blob([JSON.stringify(templateResult, null, 2)], {
                          type: 'application/json'
                        });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `portfolio-template-${templateResult.skill_code}-L${templateResult.skill_level}.json`;
                        a.click();
                      }}
                    >
                      Download
                    </Button>
                  </Box>
                  
                  <Typography variant="subtitle2" gutterBottom>
                    {templateResult.skill_name} ({templateResult.skill_code}) Level {templateResult.skill_level}
                  </Typography>

                  <Accordion defaultExpanded>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Assessment Criteria</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" color="primary">
                        Technical Achievement (Weight: {templateResult.assessment_criteria?.technical_achievement?.weight})
                      </Typography>
                      <List dense>
                        {templateResult.assessment_criteria?.technical_achievement?.criteria?.map((criterion: string, index: number) => (
                          <ListItem key={index}>
                            <ListItemText primary={`• ${criterion}`} />
                          </ListItem>
                        ))}
                      </List>
                      
                      <Typography variant="subtitle2" color="secondary" sx={{ mt: 2 }}>
                        Reflection (Weight: {templateResult.assessment_criteria?.reflection?.weight})
                      </Typography>
                      <List dense>
                        {templateResult.assessment_criteria?.reflection?.criteria?.map((criterion: string, index: number) => (
                          <ListItem key={index}>
                            <ListItemText primary={`• ${criterion}`} />
                          </ListItem>
                        ))}
                      </List>
                    </AccordionDetails>
                  </Accordion>

                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Scoring Thresholds</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip label={`Competency: ${templateResult.scoring_thresholds?.competency}+`} color="success" />
                        <Chip label={`Proficiency: ${templateResult.scoring_thresholds?.proficiency}+`} color="primary" />
                        <Chip label={`Developing: ${templateResult.scoring_thresholds?.developing}`} color="warning" />
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* IoC Methodology Dialog */}
      <Dialog 
        open={methodologyDialog} 
        onClose={() => setMethodologyDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Institute of Coding (IoC) Portfolio Mapping Methodology
        </DialogTitle>
        <DialogContent>
          <Typography paragraph>
            The IoC portfolio mapping methodology is a criterion-based assessment approach for evaluating 
            student portfolios against SFIA skills and levels, specifically designed for academic institutions 
            and workplace assessments.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Assessment Components
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="primary" gutterBottom>
              Technical Achievement (Weight: 16 points)
            </Typography>
            <Typography variant="body2" paragraph>
              • Multiple portfolio entries for at least 85% of skill components<br/>
              • Supervisor verification of entry accuracy<br/>
              • Evidence-based content with specific details<br/>
              • Contextual evaluation by workplace supervisor
            </Typography>
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="secondary" gutterBottom>
              Reflection (Weight: 9 points)
            </Typography>
            <Typography variant="body2" paragraph>
              • Professional writing style throughout<br/>
              • Clear identification of personal development areas<br/>
              • Demonstration of professional accountability<br/>
              • Evidence-based reflection with before/after comparisons
            </Typography>
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="warning.main" gutterBottom>
              Generic Responsibility Characteristics
            </Typography>
            <Typography variant="body2" paragraph>
              • 13+ of 17 core SFIA characteristics demonstrated<br/>
              • 26+ instances of core characteristics<br/>
              • 44+ total instances of all characteristics
            </Typography>
          </Box>

          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Scoring Thresholds
          </Typography>
          <Typography variant="body2">
            • <strong>Competency:</strong> 85+ points (excellent performance)<br/>
            • <strong>Proficiency:</strong> 65+ points (satisfactory performance)<br/>
            • <strong>Developing:</strong> Below 65 points (needs improvement)
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMethodologyDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PortfolioAssessment;