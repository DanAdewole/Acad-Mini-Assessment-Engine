# 📚 Mini Assessment Engine

A comprehensive, production-ready Django REST API for managing educational assessments, exams, and automated grading with AI support.

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16+-blue.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

---

## 📋 Table of Contents

-   [Features](#-features)
-   [Tech Stack](#-tech-stack)
-   [Quick Start](#-quick-start)
-   [Installation](#-installation)
-   [Docker Setup](#-docker-setup)
-   [Project Structure](#-project-structure)
-   [User Roles](#-user-roles)
-   [Grading Methods](#-grading-methods)
-   [API Documentation](#-api-documentation)
-   [Configuration](#-configuration)
-   [Testing](#-testing)
-   [Deployment](#-deployment)
-   [Documentation](#-documentation)
-   [Contributing](#-contributing)

---

## ✨ Features

### Core Functionality

-   🎓 **Multi-tenant Course Management** - Courses, exams, questions
-   📝 **4 Question Types** - Multiple choice, True/False, Short answer, Essay
-   ⚡ **Automatic Grading** - Instant grading with multiple AI options
-   🤖 **AI-Powered** - Support for OpenAI GPT and Google Gemini
-   👥 **Role-Based Access** - Students, Instructors, Admins
-   🔐 **Secure Authentication** - Token-based auth with email/password
-   📊 **Rich Analytics** - Detailed submission statistics and insights
-   🔄 **Regrade Support** - Instructors can regrade submissions
-   ⏱️ **Timed Exams** - Configurable start/end times and duration

### Technical Excellence

-   🚀 **RESTful API** - Clean, well-documented endpoints
-   📖 **OpenAPI/Swagger** - Interactive API documentation
-   🔍 **Advanced Filtering** - Search, filter, and sort all resources
-   ⚡ **Query Optimization** - N+1 query prevention with select_related/prefetch_related
-   🛡️ **Custom Permissions** - Granular access control
-   📦 **Modular Architecture** - Reusable components and mixins
-   🎨 **Consistent Responses** - Standardized success/error formatting
-   🐳 **Docker Ready** - Complete containerization support

---

## 🛠️ Tech Stack

### Backend

-   **Django 5.2** - Web framework
-   **Django REST Framework 3.16+** - API framework
-   **drf-spectacular** - OpenAPI 3 schema generation
-   **PostgreSQL / SQLite** - Database

### AI & Grading

-   **scikit-learn** - TF-IDF text similarity (Mock grading)
-   **OpenAI GPT** - AI-powered grading (optional)
-   **Google Gemini** - AI-powered grading (optional)

### DevOps

-   **Poetry** - Dependency management
-   **Docker & Docker Compose** - Containerization
-   **Ruff** - Linting and formatting

---

## 🚀 Quick Start

### Prerequisites

-   Python 3.11+
-   Poetry (recommended) or pip
-   PostgreSQL 15+ (optional, SQLite works for dev)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mini_assessment_engine.git
cd mini_assessment_engine
```

### 2. Install Dependencies

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

### 3. Set Up Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your settings
# Minimum required:
SECRET_KEY=your-secret-key-here
DEBUG=True
GRADING_SERVICE=mock
```

### 4. Run Migrations

```bash
poetry run python manage.py migrate
```

### 5. Create Superuser

```bash
poetry run python manage.py createsuperuser
```

### 6. Start Development Server

```bash
poetry run python manage.py runserver
```

### 7. Access the Application

-   **API:** http://127.0.0.1:8000/api/
-   **Swagger UI:** http://127.0.0.1:8000/api/docs/
-   **ReDoc:** http://127.0.0.1:8000/api/redoc/
-   **Django Admin:** http://127.0.0.1:8000/admin/

---

## 📦 Installation

### Option 1: Local Development (Poetry)

1. **Install Poetry**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Install Dependencies**

```bash
poetry install
```

3. **Activate Virtual Environment**

```bash
poetry shell
```

4. **Set Up Database**

```bash
# SQLite (default - no setup needed)
python manage.py migrate

# PostgreSQL
# 1. Create database: createdb assessment_engine
# 2. Update DATABASE_URL in .env
# 3. Run migrations: python manage.py migrate
```

5. **Run Server**

```bash
python manage.py runserver
```

### Option 2: Local Development (pip)

1. **Create Virtual Environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Follow steps 4-6 from Option 1**

---

## 🐳 Docker Setup

### Quick Start with Docker Compose

1. **Build and Start Services**

```bash
docker-compose up --build
```

2. **Run Migrations (first time)**

```bash
docker-compose exec web python manage.py migrate
```

3. **Create Superuser**

```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Access the Application**

-   API: http://localhost:8000/api/
-   Swagger: http://localhost:8000/api/schema/swagger-ui/

### Docker Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f web

# Run commands in container
docker-compose exec web python manage.py <command>

# Rebuild after code changes
docker-compose up --build
```

### Production Docker

For production, update `docker-compose.yml`:

```yaml
environment:
    - DEBUG=False
    - SECRET_KEY=your-production-secret-key
    - DATABASE_URL=your-production-database-url
    - ALLOWED_HOSTS=yourdomain.com
```

---

## 📁 Project Structure

```
mini_assessment_engine/
│
├── assessment_engine/          # Main project configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL routing
│   ├── responses.py           # Standardized API responses
│   ├── permissions.py         # Custom permission classes
│   ├── exceptions.py          # Custom exception handling
│   ├── mixins.py              # Reusable view mixins
│   ├── base_views.py          # Base ViewSet classes
│   └── grading/               # Grading service modules
│       ├── base.py            # Abstract grading interface
│       ├── mock_grading.py    # TF-IDF based grading
│       ├── ai_grading.py      # OpenAI GPT grading
│       └── gemini_grading.py  # Google Gemini grading
│
├── users/                      # User management app
│   ├── models.py              # Custom User model
│   ├── serializers.py         # User serializers
│   ├── views.py               # Authentication views
│   └── urls.py                # User endpoints
│
├── courses/                    # Course management app
│   ├── models.py              # Course model
│   ├── serializers.py         # Course serializers
│   ├── views.py               # Course views
│   └── urls.py                # Course endpoints
│
├── exams/                      # Exam management app
│   ├── models.py              # Exam & Question models
│   ├── serializers.py         # Exam serializers
│   ├── views.py               # Exam views
│   └── urls.py                # Exam endpoints
│
├── submissions/                # Submission management app
│   ├── models.py              # Submission & Answer models
│   ├── serializers.py         # Submission serializers
│   ├── views.py               # Submission views
│   ├── utils.py               # Grading service factory
│   └── urls.py                # Submission endpoints
│
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── pyproject.toml             # Poetry dependencies
├── .env.example               # Environment variables template
├── ERD.md                     # Database schema documentation
└── README.md                  # This file
```

---

## 👥 User Roles

The system supports three user roles with distinct permissions:

### 1. **Student** 👨‍🎓

**Capabilities:**

-   View published courses and active exams
-   Submit exam answers
-   View their own submissions and grades
-   View detailed feedback on answers

**Restrictions:**

-   Cannot create or edit courses/exams
-   Cannot view other students' submissions
-   Cannot access admin features

### 2. **Instructor** 👨‍🏫

**Capabilities:**

-   All Student capabilities
-   Create and manage courses
-   Create and manage exams and questions
-   View all student submissions for their courses
-   Regrade submissions
-   View submission statistics
-   Publish/unpublish courses and exams

**Restrictions:**

-   Cannot access system-wide admin features
-   Cannot manage users
-   Limited to their own courses

### 3. **Admin** 👨‍💼

**Capabilities:**

-   All Instructor capabilities
-   Full system access
-   Manage all users
-   Access all courses and exams
-   System configuration
-   Delete submissions (for data cleanup)
-   Update/delete any resource

**Use Cases:**

-   System administration
-   User management
-   Data cleanup
-   Technical support

---

## 🎯 Grading Methods

The system supports three grading methods that can be switched via configuration:

### 1. **Mock Grading** (TF-IDF Based)

**Best For:** Development, testing, cost-sensitive deployments

**Features:**

-   ✅ **Free** - No API costs
-   ✅ **Fast** - ~10ms per answer
-   ✅ **Offline** - No internet required
-   ✅ **Consistent** - Deterministic results

**How It Works:**

-   Uses TF-IDF (Term Frequency-Inverse Document Frequency)
-   Calculates cosine similarity between student and expected answers
-   Good for exact matches and keyword-based grading
-   ~70-80% accuracy for objective questions

**Configuration:**

```bash
GRADING_SERVICE=mock
```

### 2. **OpenAI GPT Grading**

**Best For:** High-stakes assessments, detailed feedback

**Features:**

-   🎯 **Accurate** - ~90-95% accuracy
-   📝 **Detailed Feedback** - Comprehensive analysis
-   🤖 **Context-Aware** - Understands nuance
-   💰 **Paid** - API costs apply

**Supported Models:**

-   `gpt-4o-mini` - Most cost-effective ($0.15/1M tokens)
-   `gpt-4o` - Balanced performance
-   `gpt-4-turbo` - Fast and capable
-   `gpt-3.5-turbo` - Budget option

**Configuration:**

```bash
GRADING_SERVICE=ai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
```

### 3. **Google Gemini Grading** ⭐ **Recommended**

**Best For:** Most use cases, best free tier

**Features:**

-   🎯 **Accurate** - ~90-95% accuracy
-   🚀 **Fast** - Especially with gemini-1.5-flash
-   💸 **Free Tier** - 1500 requests/day
-   📝 **Detailed Feedback** - Comprehensive analysis

**Supported Models:**

-   `gemini-1.5-flash` - Fast and efficient (recommended)
-   `gemini-1.5-pro` - Best quality
-   `gemini-pro` - General purpose

**Configuration:**

```bash
GRADING_SERVICE=gemini
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxx
GEMINI_MODEL=gemini-1.5-flash
```

### Grading Comparison

| Feature              | Mock        | OpenAI     | Gemini              |
| -------------------- | ----------- | ---------- | ------------------- |
| **Cost**             | Free        | Paid       | Free tier available |
| **Speed**            | ~10ms       | ~1-3s      | ~500ms-2s           |
| **Accuracy**         | 70-80%      | 90-95%     | 90-95%              |
| **Feedback Quality** | Basic       | Excellent  | Excellent           |
| **Setup Complexity** | None        | API key    | API key             |
| **Best For**         | Dev/Testing | Production | Production          |

---

## 📖 API Documentation

### Interactive Documentation

-   **Swagger UI:** http://localhost:8000/api/schema/swagger-ui/
-   **ReDoc:** http://localhost:8000/api/schema/redoc/
-   **OpenAPI JSON:** http://localhost:8000/api/schema.json
-   **OpenAPI YAML:** http://localhost:8000/api/schema.yaml

### Main Endpoints

#### Authentication

```bash
POST   /api/auth/register/     # Register new user
POST   /api/auth/login/        # Login (get token)
POST   /api/auth/logout/       # Logout (invalidate token)
GET    /api/auth/me/           # Get current user info
POST   /api/auth/change-password/  # Change password
```

#### Courses

```bash
GET    /api/courses/           # List courses
POST   /api/courses/           # Create course (Instructor/Admin)
GET    /api/courses/{id}/      # Get course details
PUT    /api/courses/{id}/      # Update course (Instructor/Admin)
DELETE /api/courses/{id}/      # Delete course (Admin)
```

#### Exams

```bash
GET    /api/exams/             # List exams
POST   /api/exams/             # Create exam (Instructor/Admin)
GET    /api/exams/{id}/        # Get exam details
PUT    /api/exams/{id}/        # Update exam (Instructor/Admin)
DELETE /api/exams/{id}/        # Delete exam (Admin)
```

#### Questions

```bash
GET    /api/questions/         # List questions
POST   /api/questions/         # Create question (Instructor/Admin)
GET    /api/questions/{id}/    # Get question details
PUT    /api/questions/{id}/    # Update question (Instructor/Admin)
DELETE /api/questions/{id}/    # Delete question (Admin)
```

#### Submissions

```bash
GET    /api/submissions/       # List submissions
POST   /api/submissions/       # Submit exam answers (Student)
GET    /api/submissions/{id}/  # Get submission details
DELETE /api/submissions/{id}/  # Delete submission (Admin)
GET    /api/submissions/my_submissions/  # Get my submissions
GET    /api/submissions/exam/{exam_id}/  # Get exam submissions (Instructor/Admin)
GET    /api/submissions/{id}/stats/      # Get submission statistics
POST   /api/submissions/{id}/regrade/    # Regrade submission (Instructor/Admin)
```

### Authentication

All endpoints except registration and login require authentication:

```bash
# Include token in header
Authorization: Token your-auth-token-here
```

---

## ⚙️ Configuration

### Environment Variables

See `env.example` for all available options:

#### Core Settings

```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Database

```bash
# SQLite (default)
DATABASE_URL=

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

#### Grading Service

```bash
# Mock (free, default)
GRADING_SERVICE=mock

# OpenAI
GRADING_SERVICE=ai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini

# Gemini
GRADING_SERVICE=gemini
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxx
GEMINI_MODEL=gemini-1.5-flash
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
poetry run python manage.py test

# Run specific app tests
poetry run python manage.py test users
poetry run python manage.py test courses

# Run with coverage
poetry run coverage run --source='.' manage.py test
poetry run coverage report
```

### Test Data

```bash
# Create test users
poetry run python manage.py create_test_users

# Load fixtures
poetry run python manage.py loaddata fixtures/sample_data.json
```

---

## 🚀 Deployment

### Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set GRADING_SERVICE=gemini
heroku config:set GEMINI_API_KEY=your-key

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### Railway/Render

Similar process - see their respective documentation.

### VPS (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip postgresql nginx

# Clone repo
git clone your-repo-url
cd mini_assessment_engine

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install --no-dev

# Set up Gunicorn
poetry add gunicorn

# Configure Nginx
# Set up systemd service
# Enable SSL with Let's Encrypt
```

---

## 📚 Documentation

-   **[ERD.md](./ERD.md)** - Complete database schema and relationships
-   **[env.example](./env.example)** - Environment configuration reference
-   **Swagger UI** - Interactive API documentation at `/api/schema/swagger-ui/`
-   **Model Documentation** - Inline docstrings in model files
-   **API Endpoint Documentation** - Auto-generated from docstrings

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

-   Follow PEP 8
-   Use Ruff for linting and formatting
-   Write docstrings for all functions/classes
-   Add tests for new features

```bash
# Format code
poetry run ruff format .

# Lint code
poetry run ruff check .
```

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Daniel Adewole**

-   Email: adedaniel504@gmail.com
-   GitHub: [@yourusername](https://github.com/yourusername)

---

## 🙏 Acknowledgments

-   Django and Django REST Framework communities
-   OpenAI and Google for AI APIs
-   All contributors and testers

---

## 📞 Support

For support:

-   📧 Email: adedaniel504@gmail.com
-   🐛 Issues: GitHub Issues
-   📖 Docs: See documentation links above

---

## 🗺️ Roadmap

### Planned Features

-   [ ] Real-time exam proctoring
-   [ ] Video question support
-   [ ] Plagiarism detection
-   [ ] Advanced analytics dashboard
-   [ ] Mobile app (React Native)
-   [ ] Bulk import/export
-   [ ] Peer review system
-   [ ] Discussion forums

---

**Built with ❤️ using Django and DRF**
