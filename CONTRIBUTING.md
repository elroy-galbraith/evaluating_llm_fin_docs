# Contributing to LLM Financial Analysis Evaluation Framework

First off, thank you for considering contributing to this project! 🎉

This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

---

## 🤝 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+ (or 3.10+)
- Git
- A text editor or IDE (VS Code recommended)
- At least one LLM API key (Gemini, OpenAI, or Anthropic)

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**
```bash
git clone https://github.com/YOUR-USERNAME/evaluating_llm_fin_docs.git
cd evaluating_llm_fin_docs
```

3. **Add upstream remote**
```bash
git remote add upstream https://github.com/ORIGINAL-OWNER/evaluating_llm_fin_docs.git
```

4. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

5. **Install dependencies**
```bash
pip install -r requirements.txt
```

6. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API key
```

7. **Run tests to verify setup**
```bash
python test_script.py
```

---

## 🎯 How to Contribute

### Types of Contributions

#### 🐛 Bug Reports
Found a bug? Please open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, OS, LLM provider)
- Error messages or logs

#### ✨ Feature Requests
Have an idea? Open an issue describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternative solutions you've considered
- How it benefits the project

#### 🎭 New Investment Personas
Add new investor styles:
1. Research the investor's philosophy
2. Write a clear, comprehensive description
3. Add to `persona_definitions` in `main()`
4. Test with multiple companies
5. Document in README

Example:
```python
"Ray Dalio": """
All-weather portfolio approach with emphasis on diversification across 
asset classes and economic environments. Focus on understanding economic 
cycles, risk parity, and systematic decision-making.
"""
```

#### 📊 New Evaluation Metrics
Enhance evaluation capabilities:
- Add new DSPy Signatures for specific analyses
- Create new metric classes in `ReportMetrics`
- Update evaluation pipeline
- Add tests and documentation

#### 🔧 Performance Improvements
- Optimize token usage
- Reduce LLM calls
- Add caching mechanisms
- Improve processing speed

#### 📚 Documentation
- Improve README clarity
- Add tutorials or guides
- Create example notebooks
- Write blog posts or papers

---

## 🔄 Development Workflow

### Creating a Branch

Always create a new branch for your work:

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
# or
git checkout -b docs/documentation-improvement
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### Making Changes

1. **Write your code**
   - Follow coding standards (see below)
   - Add docstrings to functions and classes
   - Include type hints

2. **Test your changes**
```bash
# Run existing tests
python test_script.py
python test_pipeline.py

# Test your specific changes manually
python -c "from evaluating_llm_fin_reports import YourNewClass; ..."
```

3. **Update documentation**
   - Update README if adding features
   - Add docstrings to new code
   - Update CONTRIBUTING.md if process changes

4. **Commit your changes**
```bash
git add .
git commit -m "Add: Clear description of what you added"
```

Commit message conventions:
- `Add:` - New features
- `Fix:` - Bug fixes
- `Update:` - Changes to existing features
- `Remove:` - Removed features
- `Docs:` - Documentation only
- `Test:` - Test changes only
- `Refactor:` - Code refactoring

---

## 📝 Coding Standards

### Python Style Guide

Follow **PEP 8** with these specifics:

```python
# Use 4 spaces for indentation (no tabs)
def my_function():
    if condition:
        do_something()

# Maximum line length: 100 characters (not 79)
long_variable_name = some_function(arg1, arg2, 
                                   arg3, arg4)

# Use type hints
def process_report(report: str, persona_name: str) -> Dict[str, Any]:
    """Process a report and return results."""
    pass

# Docstring format (Google style)
def evaluate_coverage(question: InvestorQuestion, 
                     report: str) -> QuestionEvaluation:
    """
    Evaluate how well a report answers a specific question.
    
    Args:
        question: The investment question to evaluate
        report: The investment report text
        
    Returns:
        QuestionEvaluation object with detailed assessment
        
    Raises:
        ValueError: If report is empty or invalid
    """
    pass
```

### DSPy Signature Design

When creating new DSPy signatures:

```python
class YourNewSignature(dspy.Signature):
    """Clear one-line description of what this signature does"""
    
    # Input fields - what the LLM receives
    input_data: str = dspy.InputField(
        description="Clear description for the LLM"
    )
    
    # Output fields - what the LLM should produce
    output_result: str = dspy.OutputField(
        description="What format/content is expected"
    )
```

### Code Organization

```python
# Imports at top, grouped:
import os  # Standard library
from pathlib import Path

import dspy  # Third party
from pydantic import BaseModel

from local_module import LocalClass  # Local imports

# Constants in UPPER_CASE
MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 0.0

# Classes in PascalCase
class InvestmentReportGenerator(dspy.Module):
    pass

# Functions in snake_case
def generate_report(persona: str) -> str:
    pass
```

---

## 🧪 Testing

### Running Tests

```bash
# Test core components
python test_script.py

# Test pipeline
python test_pipeline.py

# Test report generation
python test_report_generator.py

# Test your specific changes
python -c "from evaluating_llm_fin_reports import YourClass; YourClass().test_method()"
```

### Writing Tests

Create test files in the root directory:

```python
#!/usr/bin/env python3
"""Test your new feature"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from evaluating_llm_fin_reports import YourNewClass

def test_your_feature():
    """Test description"""
    print("🧪 Testing your feature...")
    
    # Setup
    obj = YourNewClass()
    
    # Test
    result = obj.your_method(test_input)
    
    # Assert
    assert result is not None, "Result should not be None"
    print("✅ Test passed!")

if __name__ == "__main__":
    test_your_feature()
```

### Test Coverage

Aim for tests that cover:
- ✅ Happy path (normal usage)
- ✅ Edge cases (empty inputs, boundary conditions)
- ✅ Error cases (invalid inputs)
- ✅ Integration (components working together)

---

## 📤 Submitting Changes

### Pull Request Process

1. **Push your branch**
```bash
git push origin feature/your-feature-name
```

2. **Create Pull Request** on GitHub
   - Use a clear, descriptive title
   - Reference any related issues (#123)
   - Describe what changed and why
   - Include test results if applicable

3. **PR Template**
```markdown
## Description
Clear description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Manually tested the changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Added docstrings to new functions/classes
- [ ] Updated README if needed
- [ ] Commits have clear messages
```

4. **Review Process**
   - Maintainers will review your PR
   - Address any requested changes
   - Once approved, your PR will be merged!

### After Your PR is Merged

1. **Update your fork**
```bash
git checkout main
git pull upstream main
git push origin main
```

2. **Delete your feature branch**
```bash
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## 🎨 Specific Contribution Areas

### Adding a New Persona

1. **Research the investor** - Read their books, letters, interviews
2. **Distill philosophy** - Extract core investment principles (3-5 key points)
3. **Add to code**:
```python
persona_definitions = {
    "Your Persona": """
    Core principle 1: Description...
    Core principle 2: Description...
    Focus areas: What they look for...
    Red flags: What they avoid...
    """
}
```
4. **Test thoroughly** - Generate 5-10 reports with different companies
5. **Document** - Add to README personas section

### Adding New Metrics

1. **Define metric** - What does it measure? Why is it useful?
2. **Create Pydantic model**:
```python
class YourNewMetric(BaseModel):
    metric_value: float = Field(description="What this measures")
    details: str = Field(description="Additional context")
```
3. **Add computation** - In `ReportEvaluator.compute_metrics()`
4. **Update output** - Modify JSON serialization
5. **Test** - Verify with sample reports

### Improving Documentation

- **README improvements** - Clarify confusing sections
- **Code comments** - Explain complex logic
- **Tutorials** - Step-by-step guides for common tasks
- **Examples** - Real-world usage scenarios
- **API docs** - Detailed function/class documentation

---

## 💬 Communication

- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - Questions, ideas, general chat
- **Pull Requests** - Code review and collaboration

---

## 🏆 Recognition

Contributors will be:
- Listed in README acknowledgments
- Credited in commit history
- Mentioned in release notes for significant contributions

---

## ❓ Questions?

If you have questions:
1. Check the README
2. Search existing issues
3. Ask in GitHub Discussions
4. Open a new issue

---

**Thank you for contributing! 🙌**

*Remember: No contribution is too small. Whether it's fixing a typo, improving documentation, or adding a major feature - every contribution helps make this project better!*
