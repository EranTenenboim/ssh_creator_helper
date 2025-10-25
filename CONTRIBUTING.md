# Contributing to SSH Creator Helper

Thank you for your interest in contributing to SSH Creator Helper! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip
- Git
- Shell access (for testing SSH functionality)

### Quick Start

1. Clone the repository:
   ```bash
   git clone git@github.com:EranTenenboim/ssh_creator_helper.git
   cd ssh_creator_helper
   ```

2. Run the development setup:
   ```bash
   ./setup-dev.sh
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Development Workflow

### Code Standards

- Follow Google Python Style Guide
- Use meaningful variable and function names
- Add docstrings to all functions
- Keep functions small and focused
- Write comprehensive tests

### Testing

We use pytest for testing. The test suite includes:

- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test complete workflows
- **Security Tests**: Validate security aspects
- **Mock Tests**: Safe testing of SSH operations

Run tests with:
```bash
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make test-security     # Run security tests only
```

### Code Quality

Before submitting a PR, ensure:

1. All tests pass: `make test`
2. Code is linted: `make lint`
3. Security scan passes: `make security-scan`
4. Shell script is valid: `make shell-test`

### Pre-commit Hooks

Pre-commit hooks are configured to run automatically. They include:

- Code formatting (black, isort)
- Linting (flake8)
- Security scanning (bandit)
- Shell script validation (shellcheck)

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run the full test suite: `make ci-test`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

### Commit Message Format

Use clear, descriptive commit messages:

```
feat: add SSH connection testing functionality
fix: resolve permission validation issue
docs: update README with new features
test: add unit tests for key creation
```

## Testing Guidelines

### Unit Tests

- Test each function in isolation
- Use mocks for external dependencies
- Test both success and failure cases
- Aim for high code coverage

### Integration Tests

- Test complete workflows
- Use real SSH operations where safe
- Test error handling and edge cases

### Security Tests

- Validate file permissions
- Test input sanitization
- Verify secure defaults
- Check for potential vulnerabilities

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

- **Test Matrix**: Python 3.8, 3.9, 3.10, 3.11
- **Linting**: flake8, shellcheck
- **Security**: bandit, trivy
- **Coverage**: Code coverage reporting
- **Integration**: Full workflow testing

## Security Considerations

When contributing:

- Never commit SSH keys or sensitive data
- Use secure file permissions (600 for private keys)
- Validate all user inputs
- Follow principle of least privilege
- Test security configurations thoroughly

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions
- Update this CONTRIBUTING.md if needed
- Include examples in documentation

## Questions?

If you have questions about contributing, please:

1. Check existing issues and discussions
2. Create a new issue with the "question" label
3. Contact the maintainers

Thank you for contributing to SSH Creator Helper! 🚀
