# Contributing to GGRock Management System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/YOUR_USERNAME/GGnet1.git
   cd GGnet1
   ```
3. **Install dependencies**
   ```bash
   pnpm install
   ```
4. **Create a branch** for your feature
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### 1. Make Your Changes

- Follow the existing code style
- Use TypeScript for type safety
- Write meaningful commit messages
- Keep commits focused and atomic

### 2. Test Your Changes

```bash
# Run development server
pnpm dev

# Build for production
pnpm build

# Type check
pnpm type-check

# Lint code
pnpm lint
```

### 3. Commit Your Changes

Use conventional commit messages:

```
feat: add new feature
fix: fix bug in component
docs: update documentation
style: format code
refactor: refactor component
test: add tests
chore: update dependencies
```

Examples:
```bash
git commit -m "feat: add user search functionality"
git commit -m "fix: resolve WebSocket reconnection issue"
git commit -m "docs: update API integration guide"
```

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
```

## Code Style Guidelines

### TypeScript

- Use strict type checking
- Avoid `any` types when possible
- Define interfaces for complex types
- Use meaningful variable names

```typescript
// Good
interface UserSession {
  id: string;
  userId: string;
  startTime: Date;
}

const getUserSession = (id: string): UserSession | null => {
  // implementation
};

// Avoid
const getSession = (id: any): any => {
  // implementation
};
```

### React Components

- Use functional components with hooks
- Keep components focused and single-purpose
- Extract reusable logic into custom hooks
- Use proper prop types

```typescript
// Good
interface ButtonProps {
  onClick: () => void;
  label: string;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ onClick, label, disabled = false }) => {
  return (
    <button onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
};

export default Button;
```

### File Naming

- Components: PascalCase (e.g., `ComputerGrid.tsx`)
- Hooks: camelCase with 'use' prefix (e.g., `useGGRockAPI.ts`)
- Utilities: camelCase (e.g., `formatBytes.ts`)
- Types: camelCase (e.g., `ggrock.ts`)

### Directory Structure

```
src/
├── components/       # Reusable UI components
│   └── ui/          # Base UI components (shadcn/ui)
├── pages/           # Page components (routes)
├── hooks/           # Custom React hooks
├── services/        # API clients and services
├── types/           # TypeScript type definitions
├── lib/             # Utility functions
└── App.tsx          # Main application component
```

## Pull Request Process

1. **Update documentation** if you've changed APIs or functionality
2. **Add tests** for new features (when testing is implemented)
3. **Ensure the build passes** (`pnpm build`)
4. **Update the README.md** if needed
5. **Link related issues** in the PR description

### PR Checklist

- [ ] Code follows the style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Build passes successfully

## Areas for Contribution

### High Priority

- [ ] Comprehensive test coverage
- [ ] Accessibility improvements (ARIA labels, keyboard navigation)
- [ ] Performance optimizations
- [ ] Error boundary implementations
- [ ] Internationalization (i18n) support

### Medium Priority

- [ ] Dark mode enhancements
- [ ] Mobile responsiveness improvements
- [ ] Advanced filtering and search
- [ ] Export functionality (CSV, PDF)
- [ ] Notification system

### Documentation

- [ ] API documentation
- [ ] Component documentation (Storybook)
- [ ] Video tutorials
- [ ] More examples and use cases

## Feature Requests

To request a feature:

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with the label `enhancement`
3. **Describe the feature** clearly
4. **Explain the use case** and benefits
5. **Provide examples** if possible

## Bug Reports

To report a bug:

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with the label `bug`
3. **Describe the bug** clearly
4. **Provide steps to reproduce**
5. **Include environment details** (OS, browser, versions)
6. **Add screenshots** if applicable

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Windows 10]
 - Browser: [e.g. Chrome 120]
 - Version: [e.g. 0.1.0]

**Additional context**
Any other context about the problem.
```

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose.

Reviewers will check for:
- Code quality and style
- Type safety
- Performance implications
- Security concerns
- Documentation completeness

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)

## Questions?

If you have questions:
- Open a GitHub Discussion
- Comment on relevant issues
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to GGRock Management System! 🎮

