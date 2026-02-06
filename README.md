# SME Financial Health Assessment Platform

<p align="center">
  <img src="docs/logo.png" alt="SME Finance Logo" width="120" />
</p>

<p align="center">
  <strong>AI-Powered Financial Health Analysis for Small and Medium Enterprises</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#api-documentation">API Docs</a> •
  <a href="#deployment">Deployment</a>
</p>

---

## 🎯 Overview

The SME Financial Health Assessment Platform helps small and medium enterprise owners understand their business's financial health through AI-powered analysis, automated bookkeeping assistance, tax compliance checking, and personalized recommendations.

### Key Benefits
- **Simplified Financial Understanding** - Complex financial metrics explained in plain language
- **AI-Powered Insights** - LLM-generated recommendations and analysis
- **Tax Compliance** - GST validation, calculations, and compliance tracking
- **Automated Categorization** - Smart transaction categorization and bookkeeping
- **Multi-language Support** - English and Hindi interface

## ✨ Features

### 📊 Financial Analysis
- Health score calculation (0-100)
- Cash flow forecasting
- Industry benchmarking
- Break-even analysis
- Scenario modeling (optimistic/pessimistic)

### 🔒 Security & Compliance
- JWT authentication with refresh tokens
- AES-256 encryption for sensitive data
- GST validation and calculations
- TDS computation
- Compliance checklists

### 📈 Advanced Features
- Automated transaction categorization
- Working capital optimization
- Financial product recommendations
- Risk assessment scoring
- Report generation (PDF/Excel)

### 🌍 Accessibility
- Multilingual UI (English/Hindi)
- Mobile-responsive design
- Offline data caching
- Low-bandwidth optimization

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0 |
| **Frontend** | React 18, TypeScript, Material-UI |
| **Database** | PostgreSQL 15, Redis |
| **AI/LLM** | OpenAI GPT-4 / Claude 3 |
| **Security** | JWT, bcrypt, Fernet encryption |
| **DevOps** | Docker, Alembic, pytest |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Option 1: Docker (Recommended)

```bash
# Clone and start
git clone https://github.com/yourusername/sme-finance-platform.git
cd sme-finance-platform

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Access the application
# Frontend: http://localhost
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Run server
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📚 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | User registration |
| `/auth/login` | POST | User authentication |
| `/api/upload` | POST | Upload financial files |
| `/api/financial/summary` | GET | Financial overview |
| `/api/analysis/risk` | GET | Risk assessment |
| `/api/advanced/forecast/cash-flow` | POST | Cash flow forecast |
| `/api/advanced/tax/calculate-gst` | POST | GST calculation |
| `/api/reports/generate` | POST | Generate reports |

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services.py -v
```

## 📦 Deployment

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection | Yes |
| `SECRET_KEY` | JWT signing key | Yes |
| `ENCRYPTION_KEY` | Data encryption key | Yes |
| `OPENAI_API_KEY` | OpenAI API key | No |
| `ANTHROPIC_API_KEY` | Anthropic API key | No |

### Production Deployment

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker exec sme_finance_backend alembic upgrade head
```

## 📁 Project Structure

```
sme-finance-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, security, database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   ├── tests/            # Pytest tests
│   ├── alembic/          # DB migrations
│   └── main.py           # Application entry
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   └── i18n.ts       # Translations
│   └── index.html
└── docker-compose.yml
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Built for AIDEL Hackathon 2026
- Powered by OpenAI and Anthropic APIs
- UI components from Material-UI

---

<p align="center">Made with ❤️ for Indian SMEs</p>
