# Contributing to IntelliSFIA

First off, thank you for considering contributing to IntelliSFIA! 🎉

IntelliSFIA is an open source project that aims to provide the most comprehensive and intelligent SFIA (Skills Framework for the Information Age) implementation. Your contributions help make this vision a reality.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community and Communication](#community-and-communication)

## 📜 Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@intellisfia.com](mailto:conduct@intellisfia.com).

## 🤝 How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/yasir2000/IntelliSFIA/issues) to avoid duplicates. When creating a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (screenshots, logs, etc.)
- **Describe the behavior you observed** and what you expected
- **Include environment details** (OS, Python version, Docker version, etc.)

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful** to most users
- **List any similar features** in other tools or frameworks
- **Include mockups or examples** if applicable

### 🛠️ Contributing Code

We welcome code contributions! Here are areas where help is especially needed:

- **Frontend Components**: React components, UI improvements, accessibility
- **Backend APIs**: FastAPI endpoints, database optimization, caching
- **AI/ML Features**: Enhanced algorithms, new LLM integrations, recommendation engines
- **Integrations**: New enterprise system connectors, API improvements
- **Documentation**: User guides, API documentation, tutorials
- **Testing**: Unit tests, integration tests, performance tests
- **DevOps**: Docker improvements, Kubernetes enhancements, CI/CD pipeline

### 📚 Contributing Documentation

Documentation improvements are always welcome:

- **User Documentation**: Getting started guides, feature explanations, tutorials
- **Developer Documentation**: API references, architecture guides, contribution guides
- **Deployment Documentation**: Installation guides, configuration examples, best practices
- **Example Projects**: Sample implementations, use case demonstrations

## 🛠️ Development Setup

### Prerequisites

Ensure you have the following installed:

- **Python 3.11+**
- **Node.js 18+**
- **Docker 20.10+** and **Docker Compose 2.0+**
- **Git 2.25+**
- **PostgreSQL 15+** (for local development)
- **Redis 7+** (for local development)

### Local Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/IntelliSFIA.git
   cd IntelliSFIA
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Set Up Frontend Environment**
   ```bash
   cd sfia_ai_framework/frontend
   npm install
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env.dev
   # Edit .env.dev with your local configuration
   ```

5. **Initialize Database**
   ```bash
   python -m sfia_ai_framework.data.sfia9_data_processor
   ```

6. **Start Development Services**
   
   **Backend** (Terminal 1):
   ```bash
   python -m sfia_ai_framework.web.app
   ```
   
   **Frontend** (Terminal 2):
   ```bash
   cd sfia_ai_framework/frontend
   npm start
   ```

7. **Verify Setup**
   - Backend API: http://localhost:8000
   - Frontend App: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Docker Development Setup

For a containerized development environment:

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

## 📏 Coding Standards

### Python Code Standards

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: 88 characters (Black formatter default)
- **Imports**: Use `isort` for import sorting
- **Type Hints**: Required for all public functions and methods
- **Docstrings**: Required for all public classes and functions (Google style)

**Formatting Tools**:
```bash
# Install formatting tools
pip install black isort flake8 mypy

# Format code
black .
isort .

# Check linting
flake8 .
mypy .
```

**Example Python Code**:
```python
from typing import Dict, List, Optional
from pydantic import BaseModel


class SkillAssessment(BaseModel):
    """Represents a skill assessment result.
    
    Args:
        skill_id: Unique identifier for the skill
        current_level: Current proficiency level (1-7)
        target_level: Desired proficiency level (1-7)
        confidence: Confidence score (0.0-1.0)
    """
    
    skill_id: str
    current_level: int
    target_level: int
    confidence: float
    
    def calculate_gap(self) -> int:
        """Calculate the skill gap between current and target levels.
        
        Returns:
            The difference between target and current levels.
        """
        return self.target_level - self.current_level
```

### TypeScript/React Code Standards

We follow the [Airbnb React/JSX Style Guide](https://github.com/airbnb/javascript/tree/master/react):

- **ESLint Configuration**: Extends `@typescript-eslint/recommended`
- **Prettier**: For consistent code formatting
- **Component Structure**: Functional components with hooks
- **Type Definitions**: Explicit types for all props and state

**Formatting Tools**:
```bash
cd sfia_ai_framework/frontend

# Check linting
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format
```

**Example React Component**:
```typescript
import React, { useState, useEffect } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';

interface SkillCardProps {
  skillId: string;
  title: string;
  description: string;
  level: number;
  onLevelChange: (skillId: string, newLevel: number) => void;
}

export const SkillCard: React.FC<SkillCardProps> = ({
  skillId,
  title,
  description,
  level,
  onLevelChange,
}) => {
  const [loading, setLoading] = useState<boolean>(false);

  const handleLevelChange = async (newLevel: number): Promise<void> => {
    setLoading(true);
    try {
      await onLevelChange(skillId, newLevel);
    } catch (error) {
      console.error('Failed to update skill level:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
      <Typography variant="h6" component="h3">
        {title}
      </Typography>
      <Typography variant="body2" color="textSecondary">
        {description}
      </Typography>
      {loading && <CircularProgress size={20} />}
    </Box>
  );
};
```

### Git Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/) for consistent commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without changing functionality
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates

**Examples**:
```
feat(assessment): add AI-powered skill gap analysis

Implement machine learning algorithm to identify skill gaps
based on user assessment data and organizational requirements.

Closes #123
```

```
fix(auth): resolve JWT token refresh issue

Fix bug where refresh tokens were not properly validated,
causing users to be logged out unexpectedly.

Fixes #456
```

## 🔄 Submitting Changes

### Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow coding standards
   - Add/update tests
   - Update documentation
   - Test your changes thoroughly

3. **Run Tests and Linting**
   ```bash
   # Python tests
   pytest
   flake8 .
   mypy .
   
   # Frontend tests
   cd sfia_ai_framework/frontend
   npm test
   npm run lint
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat(component): add new feature"
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Use a clear and descriptive title
   - Provide detailed description of changes
   - Reference related issues
   - Include screenshots for UI changes
   - Ensure CI checks pass

### Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Tests added/updated and passing
- [ ] Documentation updated if needed
- [ ] No breaking changes (or properly documented)
- [ ] PR description clearly explains changes
- [ ] Related issues referenced

## 🐛 Issue Guidelines

### Before Creating an Issue

- **Search existing issues** to avoid duplicates
- **Check the documentation** for answers to common questions
- **Verify the issue** in the latest version

### Issue Templates

We provide issue templates for:

- **🐛 Bug Report**: For reporting bugs and errors
- **💡 Feature Request**: For suggesting new features
- **📚 Documentation**: For documentation improvements
- **❓ Question**: For asking questions about usage

### Issue Labels

We use labels to categorize issues:

- **Type**: `bug`, `enhancement`, `documentation`, `question`
- **Priority**: `low`, `medium`, `high`, `critical`
- **Component**: `frontend`, `backend`, `ai`, `database`, `deployment`
- **Status**: `needs-triage`, `in-progress`, `needs-review`, `blocked`

## 🧪 Testing

### Running Tests

**Python Backend Tests**:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sfia_ai_framework

# Run specific test file
pytest tests/test_skill_assessment.py

# Run tests with verbose output
pytest -v
```

**Frontend Tests**:
```bash
cd sfia_ai_framework/frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

**Integration Tests**:
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/

# Cleanup
docker-compose -f docker-compose.test.yml down
```

### Writing Tests

**Python Test Example**:
```python
import pytest
from sfia_ai_framework.core.assessment import SkillAssessment


class TestSkillAssessment:
    """Test cases for SkillAssessment class."""
    
    def test_calculate_gap_positive(self):
        """Test skill gap calculation with positive difference."""
        assessment = SkillAssessment(
            skill_id="PROG",
            current_level=2,
            target_level=4,
            confidence=0.8
        )
        assert assessment.calculate_gap() == 2
    
    def test_calculate_gap_zero(self):
        """Test skill gap calculation with no difference."""
        assessment = SkillAssessment(
            skill_id="PROG",
            current_level=3,
            target_level=3,
            confidence=0.9
        )
        assert assessment.calculate_gap() == 0
```

**React Test Example**:
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SkillCard } from './SkillCard';

describe('SkillCard', () => {
  const mockProps = {
    skillId: 'PROG',
    title: 'Programming',
    description: 'Software development skills',
    level: 3,
    onLevelChange: jest.fn(),
  };

  test('renders skill information correctly', () => {
    render(<SkillCard {...mockProps} />);
    
    expect(screen.getByText('Programming')).toBeInTheDocument();
    expect(screen.getByText('Software development skills')).toBeInTheDocument();
  });

  test('calls onLevelChange when level is updated', async () => {
    render(<SkillCard {...mockProps} />);
    
    // Simulate level change interaction
    const levelButton = screen.getByRole('button', { name: /level 4/i });
    fireEvent.click(levelButton);
    
    await waitFor(() => {
      expect(mockProps.onLevelChange).toHaveBeenCalledWith('PROG', 4);
    });
  });
});
```

## 📖 Documentation Standards

### API Documentation

All API endpoints must include:

- **Clear descriptions** of functionality
- **Parameter specifications** with types and examples
- **Response schemas** with example payloads
- **Error codes** and descriptions
- **Usage examples** in multiple languages

### Code Documentation

- **Docstrings**: Required for all public functions, classes, and modules
- **Type Hints**: Required for all function parameters and return values
- **Inline Comments**: For complex logic and business rules only
- **README Files**: For each major component or module

### User Documentation

- **Getting Started**: Step-by-step setup and basic usage
- **Feature Guides**: Detailed explanations of major features
- **API Reference**: Comprehensive API documentation
- **Troubleshooting**: Common issues and solutions
- **Examples**: Real-world usage scenarios

## 💬 Community and Communication

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests, and project discussion
- **GitHub Discussions**: General questions and community chat
- **Discord Server**: Real-time chat and support (coming soon)
- **Email**: Technical questions and private communications

### Community Guidelines

- **Be respectful** and inclusive
- **Stay on topic** in discussions
- **Help others** when you can
- **Provide constructive feedback**
- **Follow the code of conduct**

### Getting Recognition

Contributors are recognized in several ways:

- **Contributors Page**: Listed on the project website
- **Release Notes**: Mentioned in release announcements
- **GitHub Profile**: Contributions show on your GitHub profile
- **Special Badges**: For significant contributions

## 🎓 Learning Resources

### SFIA Framework

- **Official SFIA Website**: https://sfia-online.org/
- **SFIA 9 Documentation**: Framework specifications and guidance
- **Skills and Levels**: Detailed descriptions of all skills and proficiency levels

### Technical Skills

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://reactjs.org/docs/
- **Material-UI**: https://mui.com/
- **CrewAI**: https://github.com/joaomdmoura/crewAI
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Docker**: https://docs.docker.com/
- **Kubernetes**: https://kubernetes.io/docs/

## ❓ Questions?

If you have questions that aren't covered in this guide:

1. **Check the documentation**: https://docs.intellisfia.com
2. **Search existing issues**: https://github.com/yasir2000/IntelliSFIA/issues
3. **Ask in discussions**: https://github.com/yasir2000/IntelliSFIA/discussions
4. **Contact us directly**: contribute@intellisfia.com

## 🙏 Thank You!

Your contributions make IntelliSFIA better for everyone. Whether you're fixing a typo, adding a feature, or helping with documentation, every contribution is valuable and appreciated.

Welcome to the IntelliSFIA community! 🚀

---

*This contributing guide is a living document. If you have suggestions for improvements, please submit a pull request or open an issue.*