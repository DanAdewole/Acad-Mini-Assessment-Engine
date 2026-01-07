# Contributing to Mini Assessment Engine

Thank you for considering contributing to the Mini Assessment Engine! 🎉

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

---

## 📜 Code of Conduct

This project follows a Code of Conduct. Please be respectful and professional in all interactions.

---

## 🚀 Getting Started

### 1. Fork the Repository
Click the "Fork" button at the top right of the repository page.

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR_USERNAME/mini_assessment_engine.git
cd mini_assessment_engine
```

### 3. Add Upstream Remote
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/mini_assessment_engine.git
```

### 4. Set Up Development Environment
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start dev server
python manage.py runserver
```

---

## 💻 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding tests

### 2. Make Your Changes
- Write clean, readable code
- Follow the coding standards
- Add/update tests
- Update documentation if needed

### 3. Commit Your Changes
```bash
git add .
git commit -m "Brief description of changes"
```

Commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- First line should be 50 characters or less
- Reference issues: "Fix #123: Description"

### 4. Keep Your Branch Updated
```bash
git fetch upstream
git rebase upstream/main
```

### 5. Push to Your Fork
```bash
git push origin feature/your-feature-name
```

---

## 📝 Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- Maximum line length: 88 characters (Black standard)

### Format Code
```bash
# Format all files
poetry run ruff format .

# Lint all files
poetry run ruff check .

# Fix auto-fixable issues
poetry run ruff check --fix .
```

### Docstrings
Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Type Hints
Always use type hints:
```python
def calculate_score(answers: List[Answer]) -> float:
    pass
```

### Naming Conventions
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
poetry run python manage.py test

# Run specific app
poetry run python manage.py test users

# Run with verbosity
poetry run python manage.py test --verbosity=2
```

### Write Tests
- Add tests for new features
- Maintain or improve code coverage
- Test edge cases and error conditions

Example test:
```python
from django.test import TestCase
from users.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='student'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_student)
```

---

## 📤 Submitting Changes

### 1. Push Your Branch
```bash
git push origin feature/your-feature-name
```

### 2. Create Pull Request
- Go to your fork on GitHub
- Click "Compare & pull request"
- Fill in the PR template
- Link any related issues

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated documentation

## Screenshots (if applicable)

## Related Issues
Fixes #(issue number)
```

### 3. Code Review
- Respond to feedback promptly
- Make requested changes
- Keep the conversation professional

### 4. Merge
- Once approved, a maintainer will merge your PR
- Delete your feature branch after merge

---

## 🐛 Reporting Bugs

### Before Reporting
- Check if the bug has already been reported
- Try to reproduce the bug
- Gather relevant information

### Bug Report Template
```markdown
**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. ...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11.5]
- Django version: [e.g., 5.2]

**Screenshots:**
If applicable

**Additional Context:**
Any other relevant information
```

---

## 💡 Suggesting Features

### Feature Request Template
```markdown
**Feature Description:**
Clear description of the feature

**Use Case:**
Why is this feature needed?

**Proposed Solution:**
How should it work?

**Alternatives Considered:**
Other approaches you've thought about

**Additional Context:**
Any mockups, diagrams, or examples
```

---

## 📚 Areas Needing Help

- 📝 **Documentation** - Improve guides, add examples
- 🧪 **Testing** - Increase test coverage
- 🐛 **Bug Fixes** - Check open issues
- ✨ **Features** - See roadmap in README
- 🌐 **Translations** - Add i18n support
- 🎨 **UI/UX** - Improve API usability

---

## 🤝 Community

- **Discussions:** Use GitHub Discussions for questions
- **Issues:** Report bugs and request features
- **Pull Requests:** Submit code changes

---

## 📝 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort! 🎉

---

## 📞 Questions?

If you have questions about contributing:
- Check the [README.md](./README.md)
- Check existing issues and discussions
- Open a new discussion
- Email: adedaniel504@gmail.com
