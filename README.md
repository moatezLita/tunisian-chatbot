# SalesGPT - AI Sales Intelligence Platform 🚀

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![React](https://img.shields.io/badge/react-v18.0+-blue.svg)

SalesGPT is an AI-powered platform that revolutionizes sales outreach by generating highly personalized cold emails through intelligent company analysis. Leveraging Groq's Mixtral-8x7b-32768 model, it provides sales teams with deep insights and compelling message generation.

## ✨ Features

- 🔍 Intelligent website analysis and data extraction
- 💡 Advanced company insights generation
- ✉️ Personalized cold email creation
- 🔄 Batch processing capabilities
- 📊 Performance tracking and analytics

## 🏗️ System Architecture

The system consists of two main components:

1. **Chat Service (VPS)**: Handles all AI interactions using Groq's API
2. **Local Application**: Contains the business logic and frontend interface

### Component Distribution

#### VPS Server (54.38.189.103)
Hosts the core LLM chat service that handles all AI interactions.
```
chat-service/
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Container build instructions
└── app/
    ├── main.py                # FastAPI + WebSocket implementation
    ├── config.py              # Environment and configuration
    └── services/
        └── groq_client.py     # Groq API wrapper
```

#### Local Machine
Hosts the business logic and frontend application.
```
salesgpt/
├── frontend/                  # React application
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/        # API integration
│   │   └── hooks/           # Custom React hooks
│   └── package.json
└── backend/                  # Business logic service
    ├── main.py              # FastAPI application
    ├── services/
    │   ├── scraper.py       # Website scraping
    │   ├── analyzer.py      # Content analysis
    │   └── email.py         # Email generation
    └── utils/
        └── prompts.py       # LLM prompt templates
```

## 🚀 Getting Started

### Prerequisites

For Docker deployment:
- Docker and Docker Compose
- Groq API key
- Bash shell (for automated deployment script)

For local development:
- Python 3.8+
- Node.js 16+
- Docker and Docker Compose
- Groq API key

### Installation

#### Option 1: Automated Docker Deployment (Recommended)

1. Clone the repository
```bash
git clone https://github.com/yourusername/salesgpt.git
cd salesgpt
```

2. Set up environment variables
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. Run the deployment script
```bash
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Check for necessary prerequisites
- Create required Docker networks
- Build and start all containers
- Display service URLs and container status
- Show real-time logs

#### Option 2: Manual Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/salesgpt.git
cd salesgpt
```

2. Set up environment variables
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. Start the services using Docker Compose
```bash
docker-compose up -d --build
```

4. For local development without Docker:
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8001

# Frontend
cd frontend
npm install
npm start
```

## 🛠️ Development

### Project Structure

```
salesgpt/
├── chat-service/          # VPS AI Service
├── frontend/             # React Application
└── backend/             # Business Logic Service
```

### Deployment Steps

#### 1. VPS Deployment
```bash
# SSH into VPS
ssh user@54.38.189.103

# Clone repository
git clone your-repo-url
cd chat-service

# Set up environment
echo "GROQ_API_KEY=your-key-here" > .env

# Deploy with Docker
docker-compose up -d

# Verify deployment
docker-compose logs -f
```

#### 2. Local Development
```bash
# Backend setup
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8001

# Frontend setup
cd frontend
npm install
npm start
```

### Enhanced Deployment Script

```bash
#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="salesgpt"
NETWORK_NAME="${PROJECT_NAME}-network"

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_message "❌ .env file not found! Please create one from .env.example" "$RED"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_message "❌ Docker is not running. Please start Docker first!" "$RED"
    exit 1
fi

# Create network if it doesn't exist
if ! docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
    print_message "🌐 Creating Docker network: $NETWORK_NAME" "$YELLOW"
    docker network create $NETWORK_NAME
fi

# Stop and remove existing containers
print_message "🔍 Checking for running containers..." "$YELLOW"
docker-compose down -v 2>/dev/null

# Remove existing images
print_message "🗑️ Removing existing images..." "$YELLOW"
docker-compose rm -f 2>/dev/null

# Build and start containers
print_message "🏗️ Building and starting containers..." "$YELLOW"
docker-compose up -d --build

# Check if containers are running
if [ $? -eq 0 ]; then
    print_message "✅ Deployment successful!" "$GREEN"
    print_message "📋 Services:" "$GREEN"
    echo "- API: http://localhost:8000"
    echo "- API Docs: http://localhost:8000/docs"
    echo "- MongoDB: mongodb://localhost:27017"
    
    print_message "\n📊 Container Status:" "$YELLOW"
    docker-compose ps
    
    print_message "\n📜 Logs will appear below (Ctrl+C to exit):" "$YELLOW"
    docker-compose logs -f
else
    print_message "❌ Deployment failed!" "$RED"
    exit 1
fi
```

## 🔧 Customization

SalesGPT can be customized for different business use cases:

### Business Use Cases

#### 1. Software and SaaS Sales
- **Target**: Software companies, startups, tech products
- **Customization**:
  - Modify scraper to detect tech stack information
  - Add pricing page analysis
  - Focus on technical pain points

#### 2. Real Estate Agents
- **Target**: Property listings, real estate agencies
- **Customization**:
  - Adapt scraper for property details
  - Add location-based analysis
  - Focus on property features and market comparisons

#### 3. Recruitment and HR
- **Target**: Company career pages, LinkedIn profiles
- **Customization**:
  - Modify scraper for job postings and company culture
  - Add team size analysis
  - Focus on growth indicators

#### 4. Digital Marketing Agencies
- **Target**: Business websites needing marketing services
- **Customization**:
  - Add SEO analysis components
  - Include social media presence checking
  - Focus on digital marketing gaps

### Configuration Options

#### 1. Industry Settings (.env)
```env
INDUSTRY_TYPE=saas|real_estate|recruitment|marketing
ANALYSIS_DEPTH=basic|detailed|comprehensive
CUSTOM_METRICS=growth,pricing,technology,location
```

#### 2. Analysis Parameters (config.py)
```python
ANALYSIS_CONFIG = {
    'max_urls_per_batch': 50,
    'analysis_timeout': 300,
    'priority_metrics': ['market_position', 'growth_indicators', 'pain_points'],
    'custom_metrics': ['your_custom_metric']
}
```

## 📊 Core Features

### 1. Company Analysis
- Website content scraping
- Key information extraction
- Industry and market analysis
- Competitor identification
- Tech stack detection

### 2. Email Generation
- Personalized opening lines
- Value proposition alignment
- Pain point addressing
- Call-to-action optimization
- A/B testing variations

### 3. Batch Processing
- Multiple company analysis
- Bulk email generation
- Performance tracking
- Export capabilities

## 💰 Monetization Strategy

### 1. Pricing Tiers

Basic ($99/month):
- 100 analyses/month
- Basic email templates
- CSV export

Pro ($299/month):
- 500 analyses/month
- Advanced personalization
- API access
- Team collaboration

Enterprise ($999+/month):
- Unlimited analyses
- Custom templates
- Priority support
- Advanced analytics

### 2. Marketing Plan

1. LinkedIn Campaign
- Share success stories
- Post engagement statistics
- Educational content

2. Free Trial Program
- 10 free analyses
- Response rate tracking
- Case study creation

3. Partnership Program
- Agency collaborations
- Affiliate marketing
- Integration partners

## 📈 Project Progress

### ✅ Completed Components

- Backend infrastructure setup
- Core services implementation
- Basic API endpoints
- Initial testing

### 🚧 In Progress

- Backend enhancements (rate limiting, validation)
- Comprehensive test suite

### ❌ Pending Tasks

- Frontend development
- Authentication & authorization
- Advanced features implementation
- Performance optimization
- Documentation completion
- Monitoring & logging setup
- Production deployment

### 🎯 Next Priority Tasks

1. Frontend Development
2. Authentication System
3. Documentation
4. Testing Enhancement

## 📝 API Documentation

API documentation is available at `http://localhost:8001/docs` after starting the backend service.

## 🤝 Contributing

We welcome contributions! Please check out our [Contributing Guide](CONTRIBUTING.md) for guidelines on how to proceed.

### Development Process

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Support

If you find this project helpful, please consider giving it a star ⭐️

## 🔒 Security

For security concerns, please email security@yourdomain.com.

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/yourusername/salesgpt](https://github.com/yourusername/salesgpt)

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for their powerful LLM infrastructure
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework

## 📈 Roadmap

- [ ] Enhanced email personalization
- [ ] Integration with popular CRM systems
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Custom template builder