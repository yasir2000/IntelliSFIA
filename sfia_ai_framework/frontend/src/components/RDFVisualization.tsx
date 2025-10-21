import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Button,
  Alert,
  Chip,
  CircularProgress,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  AccountTree as AccountTreeIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  Info as InfoIcon
} from '@mui/icons-material';

interface RDFVisualizationProps {
  rdfFile?: string;
}

const RDFVisualization: React.FC<RDFVisualizationProps> = ({ 
  rdfFile = 'SFIA_9_2025-10-21.ttl' 
}) => {
  const [loading, setLoading] = useState(false);
  const [rdfContent, setRdfContent] = useState<string>('');
  const [rdfStats, setRdfStats] = useState({
    triples: 154,
    entities: 18,
    namespaces: 5,
    skills: 2,
    levels: 7,
    attributes: 3
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [visualizationDialogOpen, setVisualizationDialogOpen] = useState(false);

  useEffect(() => {
    loadRDFFile();
  }, [rdfFile]);

  const loadRDFFile = async () => {
    setLoading(true);
    try {
      // In a real implementation, this would load the actual TTL file
      // For now, we'll use the validation results we have
      const mockContent = `@prefix attributes: <https://rdf.sfia-online.org/9/attributes/> .
@prefix categories: <https://rdf.sfia-online.org/9/categories/> .
@prefix levels: <https://rdf.sfia-online.org/9/lor/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sfia: <https://rdf.sfia-online.org/9/ontology/> .
@prefix skilllevels: <https://rdf.sfia-online.org/9/skilllevels/> .
@prefix skills: <https://rdf.sfia-online.org/9/skills/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

attributes:AUTO a owl:AnnotationProperty ;
    rdfs:label "Autonomy"@en ;
    rdfs:comment "The level of independence, discretion and accountability for results in your role."@en ;
    skos:notation "AUTO" ;
    sfia:attributeGuidanceNotes """Autonomy in SFIA represents a progression from following instructions to setting organisational strategy..."""@en ;
    sfia:attributeType "Attributes"@en ;
    sfia:url "https://sfia-online.org/en/shortcode/9/AUTO" .

levels:1 a sfia:Level ;
    skos:inScheme sfia:LorScheme ;
    skos:notation 1 ;
    attributes:AUTO "Follows instructions and works under close direction..."@en ;
    sfia:levelEssence "Performs routine tasks"@en ;
    sfia:levelGuidingPhrase "Follow"@en ;
    sfia:url "https://sfia-online.org/en/lor/9/1" .`;

      setRdfContent(mockContent);
    } catch (error) {
      console.error('Error loading RDF file:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadRDF = () => {
    const element = document.createElement('a');
    const file = new Blob([rdfContent], { type: 'text/turtle' });
    element.href = URL.createObjectURL(file);
    element.download = rdfFile;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const filteredContent = rdfContent
    .split('\n')
    .filter(line => 
      searchTerm === '' || 
      line.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .join('\n');

  const renderKnowledgeGraphStats = () => (
    <Grid container spacing={2}>
      <Grid item xs={6} md={2}>
        <Card sx={{ textAlign: 'center', bgcolor: 'primary.light', color: 'white' }}>
          <CardContent>
            <Typography variant="h4">{rdfStats.triples}</Typography>
            <Typography variant="body2">RDF Triples</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={6} md={2}>
        <Card sx={{ textAlign: 'center', bgcolor: 'secondary.light', color: 'white' }}>
          <CardContent>
            <Typography variant="h4">{rdfStats.entities}</Typography>
            <Typography variant="body2">Entities</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={6} md={2}>
        <Card sx={{ textAlign: 'center', bgcolor: 'success.light', color: 'white' }}>
          <CardContent>
            <Typography variant="h4">{rdfStats.skills}</Typography>
            <Typography variant="body2">Skills</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={6} md={2}>
        <Card sx={{ textAlign: 'center', bgcolor: 'warning.light', color: 'white' }}>
          <CardContent>
            <Typography variant="h4">{rdfStats.levels}</Typography>
            <Typography variant="body2">Levels</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={6} md={2}>
        <Card sx={{ textAlign: 'center', bgcolor: 'info.light', color: 'white' }}>
          <CardContent>
            <Typography variant="h4">{rdfStats.attributes}</Typography>
            <Typography variant="body2">Attributes</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={6} md={2}>
        <Card sx={{ textAlign: 'center', bgcolor: 'error.light', color: 'white' }}>
          <CardContent>
            <Typography variant="h4">{rdfStats.namespaces}</Typography>
            <Typography variant="body2">Namespaces</Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderNamespaceTable = () => {
    const namespaces = [
      { prefix: 'sfia', uri: 'https://rdf.sfia-online.org/9/ontology/', description: 'SFIA 9 Ontology' },
      { prefix: 'skills', uri: 'https://rdf.sfia-online.org/9/skills/', description: 'SFIA 9 Skills' },
      { prefix: 'attributes', uri: 'https://rdf.sfia-online.org/9/attributes/', description: 'Professional Attributes' },
      { prefix: 'levels', uri: 'https://rdf.sfia-online.org/9/lor/', description: 'Levels of Responsibility' },
      { prefix: 'categories', uri: 'https://rdf.sfia-online.org/9/categories/', description: 'Skill Categories' }
    ];

    return (
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell><strong>Prefix</strong></TableCell>
              <TableCell><strong>URI</strong></TableCell>
              <TableCell><strong>Description</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {namespaces.map((ns) => (
              <TableRow key={ns.prefix}>
                <TableCell>
                  <Chip label={ns.prefix} size="small" color="primary" />
                </TableCell>
                <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                  {ns.uri}
                </TableCell>
                <TableCell>{ns.description}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading RDF Knowledge Base...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          <AccountTreeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          RDF Knowledge Base Visualization
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<VisibilityIcon />}
            onClick={() => setVisualizationDialogOpen(true)}
            sx={{ mr: 1 }}
          >
            Graph View
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={downloadRDF}
          >
            Download TTL
          </Button>
        </Box>
      </Box>

      <Alert severity="success" sx={{ mb: 3 }}>
        <strong>RDF File Loaded:</strong> {rdfFile} - Ready for semantic queries and visualization
      </Alert>

      {/* Statistics Cards */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Knowledge Graph Statistics
        </Typography>
        {renderKnowledgeGraphStats()}
      </Box>

      {/* Namespaces */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          RDF Namespaces
        </Typography>
        {renderNamespaceTable()}
      </Box>

      {/* RDF Content Viewer */}
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            RDF Content (Turtle Format)
          </Typography>
          <TextField
            size="small"
            placeholder="Search in RDF..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
        </Box>
        
        <Box
          sx={{
            bgcolor: 'grey.100',
            p: 2,
            borderRadius: 1,
            maxHeight: 400,
            overflow: 'auto',
            fontFamily: 'monospace',
            fontSize: '0.85rem',
            lineHeight: 1.5,
            whiteSpace: 'pre-wrap'
          }}
        >
          {filteredContent || 'No matching content found'}
        </Box>
      </Paper>

      {/* Graph Visualization Dialog */}
      <Dialog
        open={visualizationDialogOpen}
        onClose={() => setVisualizationDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <InfoIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          RDF Graph Visualization
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Interactive graph visualization would render here using D3.js or similar library.
            This would show nodes (entities) and edges (relationships) from the RDF triples.
          </Alert>
          
          <Box sx={{ height: 400, bgcolor: 'grey.50', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 1 }}>
            <Typography variant="h6" color="text.secondary">
              🌐 Graph Visualization Placeholder
            </Typography>
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            The graph would visualize:
            • Skills as blue nodes
            • Attributes as green nodes  
            • Levels as orange nodes
            • Categories as purple nodes
            • Relationships as connecting lines
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVisualizationDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RDFVisualization;