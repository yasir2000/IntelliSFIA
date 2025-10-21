import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  Assessment as AssessmentIcon,
  Category as CategoryIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import { apiService } from '../services/api';


interface SFIA9Skill {
  code: string;
  name: string;
  category: string;
  subcategory: string;
  description: string;
  guidance_notes: string;
  url?: string;
  available_levels: number[];
  level_descriptions: Record<string, string>;
  sfia_version: string;
}

interface SFIA9LevelDefinition {
  level: number;
  guiding_phrase: string;
  essence: string;
  url?: string;
}

interface SFIA9Statistics {
  sfia_version: string;
  total_attributes: number;
  total_skills: number;
  total_categories: number;
  total_subcategories: number;
  level_definitions: number;
  data_loaded: boolean;
}

const SFIA9Explorer: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [statistics, setStatistics] = useState<SFIA9Statistics | null>(null);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SFIA9Skill[]>([]);
  
  // Detail dialogs
  const [selectedSkill, setSelectedSkill] = useState<SFIA9Skill | null>(null);
  const [skillDialogOpen, setSkillDialogOpen] = useState(false);
  
  // Evidence assessment
  const [assessmentSkill, setAssessmentSkill] = useState('');
  const [assessmentLevel, setAssessmentLevel] = useState(4);
  const [assessmentEvidence, setAssessmentEvidence] = useState('');
  const [assessmentResult, setAssessmentResult] = useState<any>(null);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/api/sfia9/statistics');
      if ((response.data as any).success) {
        setStatistics((response.data as any).statistics);
      }
    } catch (error) {
      console.error('Error loading SFIA 9 statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      setLoading(true);
      const response = await apiService.get(`/api/sfia9/skills?query=${encodeURIComponent(searchQuery)}&limit=20`);
      if ((response.data as any).success) {
        setSearchResults((response.data as any).skills);
      }
    } catch (error) {
      console.error('Error searching skills:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSkillClick = async (skillCode: string) => {
    try {
      setLoading(true);
      const response = await apiService.get(`/api/sfia9/skills/${skillCode}`);
      if ((response.data as any).success) {
        setSelectedSkill((response.data as any).skill);
        setSkillDialogOpen(true);
      }
    } catch (error) {
      console.error('Error loading skill details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssessEvidence = async () => {
    if (!assessmentSkill || !assessmentEvidence.trim()) return;
    
    try {
      setLoading(true);
      const response = await apiService.post('/api/sfia9/assess-evidence', {
        skill_code: assessmentSkill,
        level: assessmentLevel,
        evidence: assessmentEvidence
      });
      if ((response.data as any).success) {
        setAssessmentResult((response.data as any).assessment);
      }
    } catch (error) {
      console.error('Error assessing evidence:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderOverviewTab = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        SFIA 9 Enhanced Framework
      </Typography>
      
      {statistics && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <AssessmentIcon color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4">{statistics.total_skills}</Typography>
                    <Typography variant="body2" color="textSecondary">Skills</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <InfoIcon color="secondary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4">{statistics.total_attributes}</Typography>
                    <Typography variant="body2" color="textSecondary">Attributes</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <CategoryIcon color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4">{statistics.total_categories}</Typography>
                    <Typography variant="body2" color="textSecondary">Categories</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <TrendingUpIcon color="warning" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4">7</Typography>
                    <Typography variant="body2" color="textSecondary">Levels</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      
      {statistics?.data_loaded ? (
        <Alert severity="success" sx={{ mb: 2 }}>
          SFIA 9 framework data successfully loaded (Version {statistics.sfia_version})
        </Alert>
      ) : (
        <Alert severity="warning" sx={{ mb: 2 }}>
          SFIA 9 framework data not loaded
        </Alert>
      )}
      
      <Typography variant="body1" paragraph>
        The SFIA 9 Enhanced Framework provides comprehensive coverage of modern digital skills and professional attributes.
        Explore skills, attributes, and levels to understand competency requirements and career progression paths.
      </Typography>
      
      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
        Key Features:
      </Typography>
      <Box component="ul" sx={{ pl: 2 }}>
        <Typography component="li" variant="body1">147 specialized skills across 6 major categories</Typography>
        <Typography component="li" variant="body1">16 professional attributes including digital mindset and collaboration</Typography>
        <Typography component="li" variant="body1">Detailed level descriptions for skills progression (Levels 1-7)</Typography>
        <Typography component="li" variant="body1">Evidence-based competency assessment capabilities</Typography>
        <Typography component="li" variant="body1">Integration with IoC Portfolio Assessment methodology</Typography>
      </Box>
    </Box>
  );

  const renderSearchTab = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        Search SFIA 9 Skills
      </Typography>
      
      <Box display="flex" gap={2} sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="Search skills..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Enter skill name, code, or description"
        />
        <Button
          variant="contained"
          onClick={handleSearch}
          disabled={loading || !searchQuery.trim()}
          startIcon={<SearchIcon />}
        >
          Search
        </Button>
      </Box>
      
      {loading && <CircularProgress />}
      
      {searchResults.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Code</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Subcategory</TableCell>
                <TableCell>Levels</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {searchResults.map((skill) => (
                <TableRow key={skill.code}>
                  <TableCell>
                    <Chip label={skill.code} size="small" color="primary" />
                  </TableCell>
                  <TableCell>{skill.name}</TableCell>
                  <TableCell>{skill.category}</TableCell>
                  <TableCell>{skill.subcategory}</TableCell>
                  <TableCell>
                    {skill.available_levels.map((level) => (
                      <Chip key={level} label={level} size="small" sx={{ mr: 0.5 }} />
                    ))}
                  </TableCell>
                  <TableCell>
                    <Button size="small" onClick={() => handleSkillClick(skill.code)}>
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );

  const renderAssessmentTab = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        Evidence Assessment
      </Typography>
      
      <Typography variant="body1" paragraph>
        Assess how well your evidence demonstrates competency in a specific SFIA skill at a particular level.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Assessment Input</Typography>
              
              <TextField
                fullWidth
                label="Skill Code"
                value={assessmentSkill}
                onChange={(e) => setAssessmentSkill(e.target.value.toUpperCase())}
                placeholder="e.g., PROG, DBDS, ARCH"
                sx={{ mb: 2 }}
              />
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Level</InputLabel>
                <Select
                  value={assessmentLevel}
                  onChange={(e) => setAssessmentLevel(e.target.value as number)}
                  label="Level"
                >
                  {[1, 2, 3, 4, 5, 6, 7].map((level) => (
                    <MenuItem key={level} value={level}>
                      Level {level}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <TextField
                fullWidth
                multiline
                rows={6}
                label="Evidence"
                value={assessmentEvidence}
                onChange={(e) => setAssessmentEvidence(e.target.value)}
                placeholder="Provide detailed evidence of your competency in this skill..."
                sx={{ mb: 2 }}
              />
              
              <Button
                fullWidth
                variant="contained"
                onClick={handleAssessEvidence}
                disabled={loading || !assessmentSkill || !assessmentEvidence.trim()}
              >
                Assess Evidence
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          {assessmentResult && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Assessment Results</Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="textSecondary">Match Score</Typography>
                  <Typography variant="h4" color="primary">
                    {(assessmentResult.match_score * 100).toFixed(1)}%
                  </Typography>
                </Box>
                
                <Alert 
                  severity={
                    assessmentResult.match_score >= 0.7 ? 'success' :
                    assessmentResult.match_score >= 0.5 ? 'info' :
                    assessmentResult.match_score >= 0.3 ? 'warning' : 'error'
                  }
                  sx={{ mb: 2 }}
                >
                  {assessmentResult.assessment}
                </Alert>
                
                {assessmentResult.recommendations && (
                  <Box>
                    <Typography variant="body2" fontWeight="bold" gutterBottom>
                      Recommendations:
                    </Typography>
                    {assessmentResult.recommendations.map((rec: string, index: number) => (
                      <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                        • {rec}
                      </Typography>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          SFIA 9 Framework Explorer
        </Typography>
        
        <Paper sx={{ p: 3, mt: 3 }}>
          <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
            <Tab label="Overview" />
            <Tab label="Search Skills" />
            <Tab label="Evidence Assessment" />
          </Tabs>
          
          <Box sx={{ mt: 3 }}>
            {tabValue === 0 && renderOverviewTab()}
            {tabValue === 1 && renderSearchTab()}
            {tabValue === 2 && renderAssessmentTab()}
          </Box>
        </Paper>
      </Box>
      
      {/* Skill Details Dialog */}
      <Dialog
        open={skillDialogOpen}
        onClose={() => setSkillDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedSkill && `${selectedSkill.code} - ${selectedSkill.name}`}
        </DialogTitle>
        <DialogContent>
          {selectedSkill && (
            <Box>
              <Typography variant="body1" paragraph>
                <strong>Category:</strong> {selectedSkill.category}
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>Subcategory:</strong> {selectedSkill.subcategory}
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>Available Levels:</strong> {selectedSkill.available_levels.join(', ')}
              </Typography>
              
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Description
              </Typography>
              <Typography variant="body2" paragraph>
                {selectedSkill.description}
              </Typography>
              
              <Typography variant="h6" gutterBottom>
                Guidance Notes
              </Typography>
              <Typography variant="body2" paragraph>
                {selectedSkill.guidance_notes.substring(0, 500)}...
              </Typography>
              
              {Object.keys(selectedSkill.level_descriptions).length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Level Descriptions
                  </Typography>
                  {Object.entries(selectedSkill.level_descriptions).map(([level, desc]) => (
                    <Accordion key={level}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Level {level}</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2">{desc}</Typography>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSkillDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default SFIA9Explorer;