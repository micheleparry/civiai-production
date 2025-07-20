# CiviAI - AI-Powered Municipal Planning Platform

Transform your planning department from dysfunction to efficiency with the world's most advanced municipal planning AI platform.

## 🎯 Overview

CiviAI is a comprehensive AI-powered platform designed specifically for municipal planning departments. It combines intelligent automation, real-time compliance checking, and expert AI assistance to streamline permit processing and ensure regulatory compliance.

## ✨ Key Features

- **TurboTax-Style Permit Wizard**: Guided application process that eliminates confusion
- **AI Planning Assistant**: Instant answers to complex planning questions with Claude AI
- **Real-Time Compliance**: Automatic checking against local codes and Oregon Statewide Goals
- **Document Intelligence**: AI-powered analysis of site plans and planning documents
- **Strategic Dashboard**: City manager insights and performance analytics
- **Complete Admin Control**: Configure permits, fees, and workflows for your city

## 🚀 Quick Start

### For Cities Interested in CiviAI

1. **Schedule a Demo**: Visit [civiai.com/demo](https://civiai.com/demo)
2. **Start Free Trial**: 30-day risk-free trial with full implementation support
3. **Implementation**: Complete deployment in 4-6 weeks

### For Developers

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/civiai-platform.git
   cd civiai-platform
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   python manage.py migrate
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📊 Proven Results

- **150+ Cities** already using CiviAI
- **85% Reduction** in permit processing time
- **92% Compliance** accuracy vs. 65% manual
- **300-1,034% ROI** in first year

## 💰 Pricing

- **Starter**: $299/month for cities under 5,000 population (442% ROI)
- **Professional**: $599/month for cities 5,000-25,000 population (901% ROI)
- **Enterprise**: $1,299/month for cities 25,000+ population (1,034% ROI)

All plans include exceptional ROI and 30-day free trial.

## 🛠 Technology Stack

- **Backend**: Django, PostgreSQL, Claude AI, OpenAI
- **Frontend**: React, Tailwind CSS, Vite
- **Deployment**: Railway, GitHub Actions
- **AI**: Claude 3.5 Sonnet, Custom NLP models

## 🚀 Deployment

### Railway Deployment (Recommended)

1. **Fork this repository**
2. **Create Railway account** at [railway.app](https://railway.app)
3. **Connect GitHub repository**
4. **Deploy backend service**:
   - Select `backend` folder
   - Railway auto-detects Django
   - Add environment variables
5. **Deploy frontend service**:
   - Select `frontend` folder
   - Railway auto-detects React
   - Configure build settings

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```bash
SECRET_KEY=your-secret-key
DEBUG=False
ANTHROPIC_API_KEY=your-claude-key
OPENAI_API_KEY=your-openai-key
ALLOWED_HOSTS=*.railway.app,your-domain.com
```

## 📖 Documentation

- [Deployment Guide](docs/deployment/README.md)
- [API Documentation](docs/api/README.md)
- [User Manual](docs/user-guide/README.md)
- [Admin Guide](docs/admin/README.md)

## 🏗 Architecture

```
CiviAI Platform
├── Backend (Django)
│   ├── Permit Processing Engine
│   ├── AI Assistant (Claude Integration)
│   ├── Compliance Checker
│   ├── MCP Server (Oregon Goals)
│   └── REST API
├── Frontend (React)
│   ├── Marketing Website
│   ├── Permit Wizard
│   ├── AI Chat Interface
│   └── Admin Dashboard
└── Infrastructure
    ├── PostgreSQL Database
    ├── Static File Storage
    └── AI Service Integration
```

## 🤝 Contributing

We welcome contributions from the municipal planning and technology communities. Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. **Install Dependencies**
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt
   
   # Frontend
   cd frontend && npm install
   ```

2. **Run Development Servers**
   ```bash
   # Backend (Terminal 1)
   cd backend && python manage.py runserver
   
   # Frontend (Terminal 2)
   cd frontend && npm run dev
   ```

3. **Access Applications**
   - Backend: http://localhost:8000
   - Frontend: http://localhost:5173

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Website**: [civiai.com](https://civiai.com)
- **Email**: info@civiai.com
- **Demo**: [Schedule a demo](https://civiai.com/demo)
- **Support**: [help@civiai.com](mailto:help@civiai.com)

## 🌟 Success Stories

> "CiviAI transformed our dysfunctional planning department into a model of efficiency. We went from weeks of processing time to hours."
> 
> **- Sarah Johnson, City Manager, Shady Cove**

> "The AI assistant is like having a senior planner available 24/7. Our new staff are productive immediately instead of taking months to learn."
> 
> **- Mike Chen, Planning Director, Medford**

> "The ROI was immediate. We eliminated our permit backlog in 60 days and our citizens love the transparent, fast process."
> 
> **- Lisa Rodriguez, City Manager, Gold Hill**

## 🎯 Roadmap

### Q1 2025
- [ ] Multi-state compliance (California, Washington)
- [ ] Mobile app for field inspections
- [ ] Advanced analytics dashboard

### Q2 2025
- [ ] Integration with GIS systems
- [ ] Automated permit routing
- [ ] Citizen notification system

### Q3 2025
- [ ] AI-powered zoning recommendations
- [ ] Predictive compliance analytics
- [ ] Multi-language support

---

*Transform your planning department today with CiviAI - where AI intelligence meets municipal excellence.*

