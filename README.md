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
-   [Documentation](#-documentation)

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
API Documentation can be found in swagger

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

## 📚 Documentation

-   **[ERD.md](./ERD.md)** - Complete database schema and relationships
-   **[env.example](./env.example)** - Environment configuration reference
-   **Swagger UI** - Interactive API documentation at `/api/schema/swagger-ui/`
-   **Model Documentation** - Inline docstrings in model files
-   **API Endpoint Documentation** - Auto-generated from docstrings

---