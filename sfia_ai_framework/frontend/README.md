# IntelliSFIA Frontend

Modern React-based web application for the IntelliSFIA framework - an intelligent SFIA (Skills Framework for the Information Age) analysis platform with AI-powered workforce intelligence.

## 🚀 Features

### Core Capabilities
- **📊 Comprehensive Dashboard** - Real-time system overview with activity metrics
- **👤 Employee Analysis** - Individual SFIA skill assessment and level suggestions
- **🏢 Department Analysis** - Team-wide capability assessment and insights
- **🏢 Organization Insights** - Enterprise-wide SFIA compliance and intelligence
- **🔌 Enterprise Integration** - Connect to SAP, Power BI, databases, and other business systems
- **🎯 Real-World Scenarios** - AI-powered analysis for hiring, career development, team formation
- **🤖 Multi-Agent AI** - Collaborative AI agents for complex workforce analysis
- **🔍 Knowledge Graph** - Interactive SFIA relationship visualization
- **📈 Advanced Analytics** - Deep insights and predictive workforce analytics
- **📋 Comprehensive Reports** - Automated report generation and compliance tracking

### Technical Features
- **⚡ Modern React Architecture** - Built with React 18, TypeScript, and Material-UI
- **🔄 Real-time Updates** - WebSocket integration for live data streaming
- **📱 Responsive Design** - Optimized for desktop, tablet, and mobile devices
- **🎨 Beautiful UI/UX** - Professional design with smooth animations and interactions
- **🔒 Secure API Integration** - JWT authentication and secure API communication
- **📊 Rich Data Visualization** - Interactive charts and graphs using Recharts
- **🌐 Progressive Web App** - Installable PWA with offline capabilities
- **♿ Accessibility** - WCAG compliant with full keyboard navigation support

## 🏗️ Architecture

```
frontend/
├── public/                 # Static assets and HTML template
├── src/
│   ├── components/        # Reusable UI components
│   │   └── Layout.tsx     # Main application layout with navigation
│   ├── pages/            # Page components for each route
│   │   ├── Dashboard.tsx         # Main dashboard with metrics and charts
│   │   ├── EmployeeAnalysis.tsx  # Individual employee SFIA analysis
│   │   ├── DepartmentAnalysis.tsx # Department-wide analysis
│   │   ├── EnterpriseIntegration.tsx # Enterprise system management
│   │   ├── OrganizationInsights.tsx  # Organization-wide insights
│   │   ├── Scenarios.tsx         # Real-world AI scenarios
│   │   ├── MultiAgentAI.tsx      # Multi-agent AI interface
│   │   ├── KnowledgeGraph.tsx    # SFIA knowledge graph visualization
│   │   ├── Analytics.tsx         # Advanced analytics and insights
│   │   ├── Reports.tsx           # Report generation and management
│   │   └── Settings.tsx          # Application configuration
│   ├── services/         # API and external service integration
│   │   └── api.ts        # Comprehensive API service layer
│   ├── hooks/            # Custom React hooks for data management
│   │   └── index.ts      # Data fetching and state management hooks
│   ├── utils/            # Utility functions and helpers
│   ├── App.tsx           # Main application component with routing
│   ├── index.tsx         # Application entry point
│   └── index.css         # Global styles and CSS variables
├── package.json          # Dependencies and build scripts
└── tsconfig.json         # TypeScript configuration
```

## 🛠️ Technology Stack

### Core Technologies
- **React 18** - Modern React with concurrent features
- **TypeScript** - Type-safe JavaScript development
- **Material-UI (MUI) v5** - Comprehensive React component library
- **React Router v6** - Client-side routing and navigation
- **React Query** - Server state management and caching

### Data Visualization
- **Recharts** - Beautiful and customizable charts
- **D3.js** - Advanced data visualization capabilities
- **React Flow** - Interactive node-based diagrams

### State Management & API
- **React Query** - Server state synchronization
- **Axios** - HTTP client for API communication
- **React Hook Form** - Performant form management
- **React Hot Toast** - Elegant notification system

### UI/UX Enhancement
- **Framer Motion** - Smooth animations and transitions
- **React Beautiful DnD** - Drag and drop functionality
- **React Virtualized** - Efficient large list rendering
- **Date-fns** - Modern date utility library

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm/yarn
- Access to IntelliSFIA backend API
- Modern web browser with ES6+ support

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sfia_ai_framework/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Environment Configuration**
   Create a `.env` file in the frontend directory:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_WS_URL=ws://localhost:8000/ws
   REACT_APP_VERSION=1.0.0
   ```

4. **Start development server**
   ```bash
   npm start
   # or
   yarn start
   ```

5. **Open browser**
   Navigate to `http://localhost:3000`

### Production Build

```bash
npm run build
# or
yarn build
```

This creates an optimized production build in the `build/` directory.

## 🔧 Configuration

### API Integration
The frontend communicates with the IntelliSFIA backend through a comprehensive API service layer:

```typescript
// Configure API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Available API endpoints
- GET  /health                    # System health check
- POST /api/analyze/employee      # Employee SFIA analysis
- POST /api/analyze/department    # Department analysis
- GET  /api/insights/organization # Organization insights
- POST /api/enterprise/initialize # Enterprise integration setup
- GET  /api/enterprise/status     # Enterprise system status
- POST /api/scenarios/{type}      # Run AI scenarios
- GET  /api/agents/status         # Multi-agent AI status
- GET  /api/knowledge-graph       # Knowledge graph data
- GET  /api/analytics/{type}      # Analytics data
- POST /api/reports/generate      # Generate reports
```

### Theme Customization
The application uses Material-UI's theming system with custom branding:

```typescript
const theme = createTheme({
  palette: {
    primary: { main: '#667eea' },
    secondary: { main: '#764ba2' },
    background: { default: '#f8f9fa' }
  },
  typography: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
  }
});
```

## 📱 Page Components

### Dashboard (`/dashboard`)
- **System Overview** - Health status, connected systems, active analyses
- **Activity Charts** - Real-time analysis activity and trends
- **Quick Actions** - Fast access to common tasks
- **Recent Activity** - Latest system events and notifications

### Employee Analysis (`/employee-analysis`)
- **Employee Input** - ID-based employee lookup with analysis type selection
- **SFIA Suggestions** - AI-powered skill level recommendations
- **Confidence Scoring** - Machine learning confidence metrics
- **Detailed Reports** - Comprehensive analysis with evidence and improvement areas

### Enterprise Integration (`/enterprise`)
- **System Connections** - Manage SAP, Power BI, database connections
- **Real-time Configuration** - Processing settings and cache management
- **Health Monitoring** - Enterprise system status and performance
- **Data Synchronization** - Automated data sync and error handling

### Department Analysis (`/department-analysis`)
- **Team Assessment** - Department-wide SFIA capability analysis
- **Skill Distribution** - Visual representation of team skills
- **Gap Analysis** - Identify skill deficiencies and training needs
- **Performance Metrics** - Team effectiveness and growth indicators

### Organization Insights (`/organization-insights`)
- **Enterprise Overview** - Organization-wide SFIA compliance
- **Strategic Planning** - Workforce intelligence for decision making
- **Compliance Reporting** - Automated SFIA compliance tracking
- **Predictive Analytics** - Future workforce planning insights

## 🎨 Design System

### Color Palette
- **Primary**: `#667eea` (IntelliSFIA Blue)
- **Secondary**: `#764ba2` (Deep Purple)
- **Success**: `#28a745` (Green)
- **Warning**: `#ffc107` (Amber)
- **Error**: `#dc3545` (Red)
- **Background**: `#f8f9fa` (Light Gray)

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: 600-700 font weight
- **Body Text**: 400-500 font weight
- **Captions**: 400 font weight, smaller size

### Component Patterns
- **Cards**: Elevated surfaces with 12px border radius
- **Buttons**: 8px border radius, consistent padding
- **Forms**: Outlined text fields with validation
- **Navigation**: Left sidebar with active state indicators
- **Status Indicators**: Color-coded chips and badges

## 🔄 State Management

### React Query Integration
The application uses React Query for server state management:

```typescript
// Example: Employee analysis hook
const { mutate: analyzeEmployee, isLoading } = useEmployeeAnalysis();

// Usage in components
analyzeEmployee(
  { employee_id: 'EMP001', analysis_type: 'standard' },
  {
    onSuccess: (data) => setResults(data),
    onError: (error) => toast.error(error.message)
  }
);
```

### Custom Hooks
- `useHealthCheck()` - System health monitoring
- `useEmployeeAnalysis()` - Employee SFIA analysis
- `useEnterpriseStatus()` - Enterprise integration status
- `useOrganizationInsights()` - Organization-wide insights
- `useAgentStatus()` - Multi-agent AI status

## 📊 Data Visualization

### Chart Types
- **Line Charts** - Activity trends and time series data
- **Pie Charts** - Department distribution and skill categories
- **Bar Charts** - SFIA level distribution and comparisons
- **Scatter Plots** - Correlation analysis and clustering
- **Heatmaps** - Skill matrices and performance grids

### Interactive Features
- **Tooltips** - Detailed information on hover
- **Zoom & Pan** - Navigate large datasets
- **Filtering** - Dynamic data exploration
- **Export** - Download charts as images or data

## 🔒 Security

### Authentication
- JWT token-based authentication
- Automatic token refresh handling
- Secure storage in localStorage
- Session timeout management

### API Security
- HTTPS-only communication in production
- Request/response interceptors for error handling
- CORS configuration for cross-origin requests
- Input validation and sanitization

## 📱 Progressive Web App

### PWA Features
- **Installable** - Add to home screen on mobile devices
- **Offline Support** - Service worker for offline functionality
- **Push Notifications** - Real-time alerts and updates
- **Responsive Design** - Optimized for all screen sizes

### Performance
- **Code Splitting** - Lazy loading of page components
- **Bundle Optimization** - Tree shaking and minification
- **Caching Strategy** - Efficient asset and API response caching
- **Loading States** - Smooth user experience during data fetching

## 🚀 Deployment

### Build Process
```bash
# Development build
npm start

# Production build
npm run build

# Serve production build locally
npm run serve
```

### Environment Variables
```env
# API Configuration
REACT_APP_API_URL=https://api.intellisfia.com
REACT_APP_WS_URL=wss://api.intellisfia.com/ws

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_REAL_TIME=true

# Third-party Services
REACT_APP_SENTRY_DSN=https://...
REACT_APP_ANALYTICS_ID=GA-...
```

### Docker Deployment
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🧪 Testing

### Testing Strategy
- **Unit Tests** - Component logic and utility functions
- **Integration Tests** - API service integration
- **E2E Tests** - Complete user workflows
- **Visual Regression** - UI consistency testing

### Running Tests
```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run e2e tests
npm run test:e2e
```

## 🤝 Contributing

### Development Guidelines
1. Follow TypeScript best practices
2. Use Material-UI components consistently
3. Implement proper error handling
4. Add loading states for async operations
5. Write comprehensive tests
6. Document new features and APIs

### Code Style
- ESLint and Prettier configuration
- Consistent naming conventions
- Component organization patterns
- Import/export best practices

## 📈 Performance Monitoring

### Metrics Tracking
- **Core Web Vitals** - LCP, FID, CLS measurements
- **Bundle Analysis** - Code splitting effectiveness
- **API Performance** - Request/response times
- **User Analytics** - Feature usage and engagement

### Optimization Techniques
- **Lazy Loading** - Dynamic imports for route components
- **Memoization** - React.memo and useMemo for expensive operations
- **Virtualization** - Efficient rendering of large lists
- **Image Optimization** - WebP format and responsive images

## 📞 Support

### Documentation
- **API Documentation** - Comprehensive endpoint reference
- **Component Library** - Storybook component showcase
- **User Guides** - Step-by-step feature tutorials
- **Video Tutorials** - Visual learning resources

### Community
- **GitHub Issues** - Bug reports and feature requests
- **Discussions** - Community support and questions
- **Slack Channel** - Real-time developer communication
- **Monthly Releases** - Regular feature updates and improvements

---

**IntelliSFIA Frontend** - Empowering organizations with intelligent SFIA analysis and workforce intelligence through modern web technology.