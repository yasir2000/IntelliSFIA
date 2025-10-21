/*
 * LLM Provider Selection Component
 * ===============================
 * 
 * React component for selecting and managing multiple LLM providers
 * in the IntelliSFIA AI Framework
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  LinearProgress,
  Button,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Speed as SpeedIcon,
  AttachMoney as CostIcon,
  Storage as CacheIcon,
  Cloud as CloudIcon,
  Computer as LocalIcon,
  Check as CheckIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

// ========================
// Types and Interfaces
// ========================

interface LLMProviderStatus {
  provider: string;
  available: boolean;
  model: string;
  request_count: number;
  cache_size: number;
  cost_per_token: number;
}

interface LLMProviderConfig {
  provider: string;
  model?: string;
  fallback: boolean;
  ensemble: boolean;
}

interface ProviderTestResult {
  provider: string;
  model: string;
  response: string;
  tokens: number;
  cost: number;
  response_time: number;
  success: boolean;
  error?: string;
}

// ========================
// API Service for LLM Providers
// ========================

class LLMProviderAPI {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async getProviders(): Promise<LLMProviderStatus[]> {
    const response = await fetch(`${this.baseUrl}/api/llm/providers`);
    if (!response.ok) throw new Error('Failed to fetch providers');
    return await response.json();
  }

  async getAvailableProviders(): Promise<{ providers: string[]; count: number }> {
    const response = await fetch(`${this.baseUrl}/api/llm/available`);
    if (!response.ok) throw new Error('Failed to fetch available providers');
    return await response.json();
  }

  async testProvider(config: LLMProviderConfig): Promise<ProviderTestResult> {
    const response = await fetch(`${this.baseUrl}/api/llm/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    if (!response.ok) throw new Error('Provider test failed');
    return await response.json();
  }
}

// ========================
// Provider Selection Component
// ========================

interface LLMProviderSelectorProps {
  onProviderChange?: (config: LLMProviderConfig) => void;
  currentProvider?: string;
  disabled?: boolean;
}

export const LLMProviderSelector: React.FC<LLMProviderSelectorProps> = ({
  onProviderChange,
  currentProvider = 'auto',
  disabled = false
}) => {
  const [providers, setProviders] = useState<LLMProviderStatus[]>([]);
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);
  const [selectedProvider, setSelectedProvider] = useState(currentProvider);
  const [fallbackEnabled, setFallbackEnabled] = useState(true);
  const [ensembleEnabled, setEnsembleEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const api = new LLMProviderAPI();
    
    const loadProvidersOnMount = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const [providersData, availableData] = await Promise.all([
          api.getProviders(),
          api.getAvailableProviders()
        ]);
        
        setProviders(providersData);
        setAvailableProviders(availableData.providers);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load providers');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadProvidersOnMount();
  }, []);

  const loadProviders = async () => {
    const api = new LLMProviderAPI();
    setIsLoading(true);
    setError(null);
    
    try {
      const [providersData, availableData] = await Promise.all([
        api.getProviders(),
        api.getAvailableProviders()
      ]);
      
      setProviders(providersData);
      setAvailableProviders(availableData.providers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load providers');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider);
    
    const config: LLMProviderConfig = {
      provider,
      fallback: fallbackEnabled,
      ensemble: ensembleEnabled
    };
    
    onProviderChange?.(config);
  };

  const handleFallbackChange = (enabled: boolean) => {
    setFallbackEnabled(enabled);
    
    const config: LLMProviderConfig = {
      provider: selectedProvider,
      fallback: enabled,
      ensemble: ensembleEnabled
    };
    
    onProviderChange?.(config);
  };

  const handleEnsembleChange = (enabled: boolean) => {
    setEnsembleEnabled(enabled);
    
    const config: LLMProviderConfig = {
      provider: selectedProvider,
      fallback: fallbackEnabled,
      ensemble: enabled
    };
    
    onProviderChange?.(config);
  };

  const getProviderIcon = (provider: string) => {
    const localProviders = ['ollama'];
    return localProviders.includes(provider.toLowerCase()) ? <LocalIcon /> : <CloudIcon />;
  };

  const getProviderChip = (provider: LLMProviderStatus) => {
    return (
      <Chip
        icon={provider.available ? <CheckIcon /> : <ErrorIcon />}
        label={provider.provider}
        color={provider.available ? 'success' : 'error'}
        variant={provider.available ? 'filled' : 'outlined'}
        size="small"
        sx={{ mr: 1, mb: 1 }}
      />
    );
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            LLM Provider Selection
          </Typography>
          <LinearProgress />
          <Typography variant="body2" sx={{ mt: 1 }}>
            Loading providers...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            LLM Provider Selection
          </Typography>
          <Tooltip title="Refresh providers">
            <IconButton onClick={loadProviders} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Select Provider</InputLabel>
              <Select
                value={selectedProvider}
                label="Select Provider"
                onChange={(e) => handleProviderChange(e.target.value)}
                disabled={disabled}
              >
                <MenuItem value="auto">
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <SpeedIcon sx={{ mr: 1 }} />
                    Auto (Best Available)
                  </Box>
                </MenuItem>
                {availableProviders.map((provider) => {
                  const providerData = providers.find(p => p.provider === provider);
                  return (
                    <MenuItem key={provider} value={provider}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getProviderIcon(provider)}
                        <Box sx={{ ml: 1 }}>
                          <Typography variant="body2">
                            {provider.charAt(0).toUpperCase() + provider.slice(1)}
                          </Typography>
                          {providerData && (
                            <Typography variant="caption" color="text.secondary">
                              {providerData.model}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </MenuItem>
                  );
                })}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', flexDirection: 'column' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={fallbackEnabled}
                    onChange={(e) => handleFallbackChange(e.target.checked)}
                    disabled={disabled}
                  />
                }
                label="Enable Fallback"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={ensembleEnabled}
                    onChange={(e) => handleEnsembleChange(e.target.checked)}
                    disabled={disabled}
                  />
                }
                label="Ensemble Mode"
              />
            </Box>
          </Grid>
        </Grid>

        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Available Providers ({availableProviders.length}):
          </Typography>
          <Box>
            {providers.map((provider) => getProviderChip(provider))}
          </Box>
        </Box>

        <Accordion sx={{ mt: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Provider Details & Statistics</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Provider</TableCell>
                    <TableCell>Model</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Requests</TableCell>
                    <TableCell align="right">Cache</TableCell>
                    <TableCell align="right">Cost/Token</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {providers.map((provider) => (
                    <TableRow key={provider.provider}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getProviderIcon(provider.provider)}
                          <Typography variant="body2" sx={{ ml: 1 }}>
                            {provider.provider}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {provider.model}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={provider.available ? 'Available' : 'Offline'}
                          color={provider.available ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                          <SpeedIcon sx={{ fontSize: 14, mr: 0.5 }} />
                          {provider.request_count}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                          <CacheIcon sx={{ fontSize: 14, mr: 0.5 }} />
                          {provider.cache_size}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                          <CostIcon sx={{ fontSize: 14, mr: 0.5 }} />
                          ${provider.cost_per_token.toFixed(6)}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>
      </CardContent>
    </Card>
  );
};

// ========================
// Provider Test Component
// ========================

export const LLMProviderTester: React.FC = () => {
  const [testResults, setTestResults] = useState<ProviderTestResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const api = new LLMProviderAPI();

  const testProvider = async (provider: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const config: LLMProviderConfig = {
        provider,
        fallback: false,
        ensemble: false
      };
      
      const result = await api.testProvider(config);
      setTestResults(prev => [result, ...prev.slice(0, 4)]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Test failed');
    } finally {
      setIsLoading(false);
    }
  };

  const testAllProviders = async () => {
    const providers = ['ollama', 'openai', 'anthropic', 'google', 'cohere'];
    
    for (const provider of providers) {
      try {
        await testProvider(provider);
        // Small delay between tests
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (err) {
        console.warn(`Failed to test ${provider}:`, err);
      }
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Provider Testing
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            onClick={testAllProviders}
            disabled={isLoading}
            sx={{ mr: 1 }}
          >
            {isLoading ? 'Testing...' : 'Test All Providers'}
          </Button>
          
          <Button
            variant="outlined"
            onClick={() => testProvider('auto')}
            disabled={isLoading}
          >
            Test Auto Selection
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {testResults.length > 0 && (
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Recent Test Results:
            </Typography>
            
            {testResults.map((result, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="h6" color={result.success ? 'success.main' : 'error.main'}>
                      {result.provider} {result.success ? '✓' : '✗'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {result.model}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2">
                      {result.tokens} tokens • ${result.cost.toFixed(4)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {result.response_time.toFixed(2)}s
                    </Typography>
                  </Box>
                </Box>
                
                {result.success ? (
                  <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                    "{result.response.substring(0, 100)}..."
                  </Typography>
                ) : (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    {result.error}
                  </Alert>
                )}
              </Paper>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default LLMProviderSelector;