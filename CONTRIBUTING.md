# Contributing to ggNet

Thank you for your interest in contributing to ggNet!

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20.x
- Git

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/itcaffenet-Ljubinje/GGnet1.git
cd GGnet1

# 2. Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 3. Run backend
python -m uvicorn src.main:app --reload

# 4. Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Write docstrings
- Run tests before committing

### TypeScript (Frontend)
- Use functional components
- Type all props and state
- Follow React best practices

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Pull Request Process

1. Update README.md if needed
2. Ensure all tests pass
3. Update CHANGELOG if applicable
4. Request review from maintainers

## Questions?

Open an issue or contact: support@itcaffenet.com

