# Contributing to NextAstroTarget 🤝

Thank you for your interest in contributing to NextAstroTarget! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of Python, tkinter, and SQLite
- Familiarity with astronomy/astrophotography concepts (helpful but not required)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/NextAstroTarget.git
   cd NextAstroTarget
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Run Tests**
   ```bash
   python -m pytest tests/
   ```

5. **Start Development**
   ```bash
   python main.py
   ```

## 📝 Development Guidelines

### Code Style

- **PEP 8**: Follow Python PEP 8 style guidelines
- **Type Hints**: Use type hints where appropriate
- **Docstrings**: Include comprehensive docstrings for all public functions and classes
- **Comments**: Write clear, concise comments for complex logic

### Example Code Style

```python
def calculate_altitude(ra: float, dec: float, lst: float, latitude: float) -> float:
    """
    Calculate altitude for given celestial coordinates.
    
    Args:
        ra: Right ascension in degrees
        dec: Declination in degrees  
        lst: Local sidereal time in degrees
        latitude: Observer latitude in degrees
        
    Returns:
        float: Altitude in degrees
        
    Raises:
        ValueError: If coordinates are out of valid range
    """
    # Implementation here
    pass
```

### Commit Messages

Use clear, descriptive commit messages following this format:

```
type(scope): brief description

Longer explanation if needed

- Added feature X
- Fixed issue Y
- Updated documentation
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(database): add support for multiple catalog formats
fix(gui): resolve crash when Excel file is missing
docs(readme): update installation instructions
```

## 🏗️ Project Structure

```
NextAstroTarget/
├── src/
│   ├── database/          # Database management
│   │   ├── __init__.py
│   │   └── database_manager.py
│   ├── gui/              # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── database_init_gui.py
│   │   └── target_selection_gui.py
│   ├── target_selection/ # Target algorithms
│   │   ├── __init__.py
│   │   └── target_selector.py
│   └── utils/            # Utilities
│       ├── __init__.py
│       ├── logger.py
│       └── error_handling.py
├── tests/                # Unit tests
├── docs/                 # Documentation
├── config/              # Configuration files
└── assets/              # Icons and resources
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_database_manager.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Write unit tests for all new functionality
- Use descriptive test names: `test_should_calculate_correct_altitude_for_zenith_object`
- Include edge cases and error conditions
- Mock external dependencies (file system, network calls)

### Test Example

```python
import pytest
from src.target_selection.target_selector import TargetSelector

class TestTargetSelector:
    def test_should_calculate_correct_altitude_for_zenith_object(self):
        """Test altitude calculation for object at zenith."""
        # Given
        selector = TargetSelector(mock_db_manager)
        ra, dec = 180.0, 45.0  # Object coordinates
        lst, lat = 180.0, 45.0  # Observer at same coordinates
        
        # When
        altitude = selector.calculate_altitude(ra, dec, lst, lat)
        
        # Then
        assert abs(altitude - 90.0) < 0.1  # Should be at zenith
```

## 🐛 Bug Reports

### Before Submitting

1. **Search existing issues** to avoid duplicates
2. **Update to latest version** if possible
3. **Gather information:**
   - Operating system and version
   - Python version
   - NextAstroTarget version
   - Steps to reproduce
   - Expected vs actual behavior
   - Log files from `logs/` directory

### Bug Report Template

Use the GitHub issue template or include:

- Clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior  
- Environment details
- Log files (if applicable)
- Screenshots (if applicable)

## ✨ Feature Requests

### Guidelines

- **Search existing issues** first
- **Clearly describe** the feature and its benefits
- **Provide use cases** and examples
- **Consider scope** - start with smaller, focused features
- **Think about compatibility** with existing functionality

### Feature Implementation Process

1. **Discuss** the feature in an issue first
2. **Get approval** from maintainers
3. **Create feature branch**: `feature/your-feature-name`
4. **Implement** with tests and documentation
5. **Submit pull request**

## 🔄 Pull Request Process

### Before Submitting

1. **Create feature branch** from `main`
2. **Write tests** for new functionality
3. **Update documentation** as needed
4. **Run tests** and ensure they pass
5. **Check code style** with linting tools
6. **Write clear commit messages**

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No merge conflicts
```

### Review Process

1. **Automated checks** must pass (tests, linting)
2. **Code review** by maintainers
3. **Address feedback** if needed
4. **Approval** required before merge
5. **Squash and merge** preferred for clean history

## 📚 Documentation

### Types of Documentation

- **Code Documentation**: Docstrings and inline comments
- **User Documentation**: README, user guides, tutorials
- **Developer Documentation**: API docs, architecture guides
- **Process Documentation**: Contributing guidelines, issue templates

### Documentation Standards

- **Clear and concise** language
- **Examples** for complex features
- **Keep updated** with code changes
- **Use markdown** for formatting
- **Include screenshots** for GUI features

## 🏷️ Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] Update version numbers
- [ ] Update changelog
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag release
- [ ] Build and test installers

## 💬 Community

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General discussions, questions
- **Pull Requests**: Code contributions, reviews

### Code of Conduct

- **Be respectful** and professional
- **Be welcoming** to newcomers
- **Be constructive** in feedback
- **Be collaborative** and helpful
- **Focus on the code**, not the person

## 🎯 Areas for Contribution

### Good First Issues

- Documentation improvements
- Unit test additions
- UI/UX enhancements
- Bug fixes
- Code refactoring

### Advanced Contributions

- New astronomical algorithms
- Database optimization
- Performance improvements
- New data source integrations
- Advanced GUI features

### Expertise Needed

- **Astronomy/Astrophotography**: Domain knowledge for better target selection
- **Python Development**: Core application development
- **GUI Design**: tkinter expertise for better user experience
- **Database Design**: SQLite optimization and schema design
- **Testing**: Unit testing, integration testing, UI testing

## 🏆 Recognition

Contributors are recognized in:
- **README.md**: Contributor list
- **Release Notes**: Major contributions
- **GitHub**: Contributor graphs and statistics
- **Documentation**: Author credits

## 📞 Getting Help

### For Contributors

- **GitHub Discussions**: Ask questions about development
- **Issues**: Report problems or request clarification
- **Code Review**: Get feedback on your contributions

### For Users

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Check user guides and FAQ
- **Discussions**: Ask usage questions

---

Thank you for contributing to NextAstroTarget! Your efforts help make astronomy and astrophotography more accessible to everyone. 🌟