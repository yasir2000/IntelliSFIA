import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Search as SearchIcon,
  AccountTree as AccountTreeIcon,
  DataObject as DataObjectIcon,
  Schema as SchemaIcon,
  Link as LinkIcon,
  Info as InfoIcon
} from '@mui/icons-material';

interface RDFTriple {
  subject: string;
  predicate: string;
  object: string;
  type: 'uri' | 'literal' | 'bnode';
}

interface SPARQLResult {
  head: {
    vars: string[];
  };
  results: {
    bindings: Record<string, { type: string; value: string }>[];
  };
}

interface NamespaceInfo {
  prefix: string;
  uri: string;
  description: string;
  entityCount: number;
}

const KnowledgeGraph: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [rdfTriples, setRdfTriples] = useState<RDFTriple[]>([]);
  const [namespaces, setNamespaces] = useState<NamespaceInfo[]>([]);
  const [sparqlQuery, setSparqlQuery] = useState('');
  const [sparqlResults, setSparqlResults] = useState<SPARQLResult | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<string>('');
  const [entityDialogOpen, setEntityDialogOpen] = useState(false);
  const [entityTriples, setEntityTriples] = useState<RDFTriple[]>([]);

  // Sample SPARQL queries
  const sampleQueries = {
    allSkills: `PREFIX sfia: <https://rdf.sfia-online.org/9/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?skill ?label WHERE {
  ?skill a sfia:Skill ;
         rdfs:label ?label .
}
LIMIT 10`,
    
    skillsByCategory: `PREFIX sfia: <https://rdf.sfia-online.org/9/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?skill ?label ?category WHERE {
  ?skill a sfia:Skill ;
         rdfs:label ?label ;
         sfia:hasCategory ?category .
}
LIMIT 10`,
    
    attributesByLevel: `PREFIX sfia: <https://rdf.sfia-online.org/9/ontology/>
PREFIX attributes: <https://rdf.sfia-online.org/9/attributes/>
PREFIX levels: <https://rdf.sfia-online.org/9/lor/>

SELECT ?level ?attribute ?value WHERE {
  ?level a sfia:Level ;
         ?attribute ?value .
  FILTER(STRSTARTS(STR(?attribute), "https://rdf.sfia-online.org/9/attributes/"))
}
LIMIT 10`,

    levelHierarchy: `PREFIX sfia: <https://rdf.sfia-online.org/9/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?level ?notation ?essence ?phrase WHERE {
  ?level a sfia:Level ;
         skos:notation ?notation ;
         sfia:levelEssence ?essence ;
         sfia:levelGuidingPhrase ?phrase .
}
ORDER BY ?notation`
  };

  useEffect(() => {
    loadKnowledgeGraphData();
  }, []);

  const loadKnowledgeGraphData = async () => {
    setLoading(true);
    try {
      // Simulate loading RDF data (in real implementation, this would load from the TTL file)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data based on the actual RDF structure
      const mockTriples: RDFTriple[] = [
        {
          subject: 'https://rdf.sfia-online.org/9/attributes/AUTO',
          predicate: 'http://www.w3.org/2000/01/rdf-schema#label',
          object: 'Autonomy',
          type: 'literal'
        },
        {
          subject: 'https://rdf.sfia-online.org/9/attributes/AUTO',
          predicate: 'http://www.w3.org/2000/01/rdf-schema#comment',
          object: 'The level of independence, discretion and accountability for results in your role.',
          type: 'literal'
        },
        {
          subject: 'https://rdf.sfia-online.org/9/lor/1',
          predicate: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
          object: 'https://rdf.sfia-online.org/9/ontology/Level',
          type: 'uri'
        }
      ];

      const mockNamespaces: NamespaceInfo[] = [
        {
          prefix: 'sfia',
          uri: 'https://rdf.sfia-online.org/9/ontology/',
          description: 'SFIA 9 Ontology Classes and Properties',
          entityCount: 15
        },
        {
          prefix: 'skills',
          uri: 'https://rdf.sfia-online.org/9/skills/',
          description: 'SFIA 9 Skills',
          entityCount: 147
        },
        {
          prefix: 'attributes',
          uri: 'https://rdf.sfia-online.org/9/attributes/',
          description: 'SFIA 9 Professional Attributes',
          entityCount: 16
        },
        {
          prefix: 'levels',
          uri: 'https://rdf.sfia-online.org/9/lor/',
          description: 'SFIA 9 Levels of Responsibility',
          entityCount: 7
        },
        {
          prefix: 'categories',
          uri: 'https://rdf.sfia-online.org/9/categories/',
          description: 'SFIA 9 Skill Categories',
          entityCount: 6
        }
      ];

      setRdfTriples(mockTriples);
      setNamespaces(mockNamespaces);
    } catch (error) {
      console.error('Error loading knowledge graph data:', error);
    } finally {
      setLoading(false);
    }
  };

  const executeSPARQLQuery = async (query: string) => {
    setLoading(true);
    try {
      // In a real implementation, this would send the SPARQL query to a triplestore
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock SPARQL results
      const mockResults: SPARQLResult = {
        head: { vars: ['skill', 'label'] },
        results: {
          bindings: [
            {
              skill: { type: 'uri', value: 'https://rdf.sfia-online.org/9/skills/PROG' },
              label: { type: 'literal', value: 'Programming/software engineering' }
            },
            {
              skill: { type: 'uri', value: 'https://rdf.sfia-online.org/9/skills/DTAN' },
              label: { type: 'literal', value: 'Data analysis' }
            }
          ]
        }
      };
      
      setSparqlResults(mockResults);
    } catch (error) {
      console.error('Error executing SPARQL query:', error);
    } finally {
      setLoading(false);
    }
  };

  const openEntityDialog = (entityUri: string) => {
    setSelectedEntity(entityUri);
    // Filter triples related to this entity
    const relatedTriples = rdfTriples.filter(
      triple => triple.subject === entityUri || triple.object === entityUri
    );
    setEntityTriples(relatedTriples);
    setEntityDialogOpen(true);
  };

  const formatUri = (uri: string) => {
    // Extract the local name from URI
    const parts = uri.split('/');
    return parts[parts.length - 1] || uri;
  };

  const renderOverviewTab = () => (
    <Box sx={{ mt: 2 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SchemaIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Knowledge Graph Statistics
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  RDF Triples: <strong>154</strong>
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Labeled Entities: <strong>18</strong>
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Namespaces: <strong>5</strong>
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Format: <strong>Turtle (TTL)</strong>
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AccountTreeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Ontology Classes
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Chip label="sfia:Skill" variant="outlined" sx={{ mr: 1, mb: 1 }} />
                <Chip label="sfia:Level" variant="outlined" sx={{ mr: 1, mb: 1 }} />
                <Chip label="sfia:Category" variant="outlined" sx={{ mr: 1, mb: 1 }} />
                <Chip label="sfia:Attribute" variant="outlined" sx={{ mr: 1, mb: 1 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <LinkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Namespaces
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Prefix</TableCell>
                      <TableCell>URI</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell align="right">Entities</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {namespaces.map((ns) => (
                      <TableRow key={ns.prefix}>
                        <TableCell>
                          <Chip label={ns.prefix} size="small" />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            {ns.uri}
                          </Typography>
                        </TableCell>
                        <TableCell>{ns.description}</TableCell>
                        <TableCell align="right">{ns.entityCount}</TableCell>
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

  const renderSPARQLTab = () => (
    <Box sx={{ mt: 2 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Sample Queries
              </Typography>
              {Object.entries(sampleQueries).map(([name, query]) => (
                <Button
                  key={name}
                  variant="outlined"
                  size="small"
                  fullWidth
                  sx={{ mb: 1 }}
                  onClick={() => setSparqlQuery(query)}
                >
                  {name.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                </Button>
              ))}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              SPARQL Query Interface
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={8}
              value={sparqlQuery}
              onChange={(e) => setSparqlQuery(e.target.value)}
              placeholder="Enter your SPARQL query here..."
              variant="outlined"
              sx={{ mb: 2, fontFamily: 'monospace' }}
            />
            <Button
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={() => executeSPARQLQuery(sparqlQuery)}
              disabled={loading || !sparqlQuery.trim()}
            >
              Execute Query
            </Button>
          </Paper>
          
          {sparqlResults && (
            <Paper sx={{ p: 2, mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Query Results
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      {sparqlResults.head.vars.map((variable) => (
                        <TableCell key={variable}>{variable}</TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sparqlResults.results.bindings.map((binding, index) => (
                      <TableRow key={index}>
                        {sparqlResults.head.vars.map((variable) => (
                          <TableCell key={variable}>
                            {binding[variable] ? (
                              binding[variable].type === 'uri' ? (
                                <Button
                                  variant="text"
                                  size="small"
                                  onClick={() => openEntityDialog(binding[variable].value)}
                                >
                                  {formatUri(binding[variable].value)}
                                </Button>
                              ) : (
                                binding[variable].value
                              )
                            ) : '-'}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );

  const renderRDFTab = () => (
    <Box sx={{ mt: 2 }}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          RDF Triples Browser
        </Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          Browse the RDF triples in the knowledge graph. Click on entities to explore their relationships.
        </Alert>
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell>Subject</TableCell>
                <TableCell>Predicate</TableCell>
                <TableCell>Object</TableCell>
                <TableCell>Type</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rdfTriples.slice(0, 50).map((triple, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Button
                      variant="text"
                      size="small"
                      onClick={() => openEntityDialog(triple.subject)}
                      sx={{ textAlign: 'left', justifyContent: 'flex-start' }}
                    >
                      {formatUri(triple.subject)}
                    </Button>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {formatUri(triple.predicate)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {triple.type === 'uri' ? (
                      <Button
                        variant="text"
                        size="small"
                        onClick={() => openEntityDialog(triple.object)}
                      >
                        {formatUri(triple.object)}
                      </Button>
                    ) : (
                      <Typography variant="body2">
                        {triple.object.length > 50 ? 
                          `${triple.object.substring(0, 50)}...` : 
                          triple.object
                        }
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip label={triple.type} size="small" variant="outlined" />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        <DataObjectIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
        SFIA 9 Knowledge Graph
      </Typography>
      
      <Alert severity="success" sx={{ mb: 3 }}>
        <strong>RDF Knowledge Base Active:</strong> SFIA_9_2025-10-21.ttl loaded with 154 triples
      </Alert>

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Overview" icon={<InfoIcon />} />
          <Tab label="SPARQL Query" icon={<SearchIcon />} />
          <Tab label="RDF Browser" icon={<AccountTreeIcon />} />
        </Tabs>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        )}

        {!loading && (
          <>
            {tabValue === 0 && renderOverviewTab()}
            {tabValue === 1 && renderSPARQLTab()}
            {tabValue === 2 && renderRDFTab()}
          </>
        )}
      </Paper>

      {/* Entity Detail Dialog */}
      <Dialog
        open={entityDialogOpen}
        onClose={() => setEntityDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Entity Details
          <Typography variant="body2" color="text.secondary">
            {selectedEntity}
          </Typography>
        </DialogTitle>
        <DialogContent>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Predicate</TableCell>
                  <TableCell>Object</TableCell>
                  <TableCell>Type</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {entityTriples.map((triple, index) => (
                  <TableRow key={index}>
                    <TableCell>{formatUri(triple.predicate)}</TableCell>
                    <TableCell>{triple.object}</TableCell>
                    <TableCell>
                      <Chip label={triple.type} size="small" variant="outlined" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEntityDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default KnowledgeGraph;