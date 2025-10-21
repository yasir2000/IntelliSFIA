// Simple test server
const http = require('http');

const server = http.createServer((req, res) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  
  res.writeHead(200, { 
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  });
  
  if (req.url === '/health') {
    res.end(JSON.stringify({ status: 'OK', message: 'Test server running' }));
  } else if (req.url === '/api/sfia9/statistics') {
    res.end(JSON.stringify({
      success: true,
      data: {
        success: true,
        statistics: {
          sfia_version: "SFIA 9",
          total_skills: 147,
          total_categories: 6,
          message: "Test data loaded successfully"
        }
      }
    }));
  } else {
    res.end(JSON.stringify({ error: 'Not found' }));
  }
});

server.listen(8001, () => {
  console.log('🧪 Test server running on http://localhost:8001');
  console.log('📊 Test endpoints: /health, /api/sfia9/statistics');
});