# Internal Logistics Platform - Backend API

Django REST Framework backend for managing logistics operations in Lagos.

## System Architecture

```mermaid
graph TB
    subgraph "Client Applications"
        A1[Admin Dashboard<br/>React Web App]
        A2[Rider Mobile App<br/>React Native]
    end
    
    subgraph "API Gateway & Auth"
        B1[NGINX/Load Balancer]
        B2[Django REST Framework]
        B3[JWT Authentication]
    end
    
    subgraph "Application Layer"
        C1[Users Module<br/>Auth & RBAC]
        C2[Orders Module<br/>Lifecycle Management]
        C3[Riders Module<br/>Profile & Earnings]
        C4[Tracking Module<br/>GPS & Location]
        C5[Payments Module<br/>Paystack Integration]
        C6[Analytics Module<br/>Reports & Metrics]
        C7[Notifications Module<br/>In-App Alerts]
    end
    
    subgraph "Data Layer"
        D1[(PostgreSQL<br/>Main Database)]
        D2[(Redis<br/>Cache & Sessions)]
    end
    
    subgraph "External Services"
        E1[Paystack API<br/>Payment Processing]
        E2[Resend<br/>Email Service]
        E3[Google Cloud Storage<br/>Image Storage]
    end
    
    subgraph "Background Jobs"
        F1[Celery Workers<br/>Async Tasks]
        F2[Celery Beat<br/>Scheduled Jobs]
    end
    
    A1 & A2 -->|HTTPS/REST| B1
    B1 --> B2
    B2 --> B3
    
    B3 --> C1
    B2 --> C2 & C3 & C4 & C5 & C6 & C7
    
    C1 & C2 & C3 & C4 & C5 & C6 & C7 --> D1
    C1 & C2 --> D2
    
    C5 <-->|Initialize/Verify| E1
    E1 -.->|Webhook| C5
    
    C1 & C2 -->|Send Emails| E2
    C2 -->|Upload/Retrieve| E3
    
    C2 & C7 --> F1
    F2 --> F1
    F1 --> D1
    
    style B2 fill:#4CAF50
    style D1 fill:#2196F3
    style E1 fill:#FF9800
    style E2 fill:#9C27B0
    style E3 fill:#F44336
```

### Component Responsibilities

| Component | Purpose |
|-----------|---------|
| **Users Module** | Authentication, authorization, role management (Admin/Manager/Rider) |
| **Orders Module** | Order creation, assignment, status tracking, delivery lifecycle |
| **Riders Module** | Rider profiles, task management, earnings calculation |
| **Tracking Module** | Real-time GPS tracking, location history |
| **Payments Module** | Paystack integration, transaction verification, webhooks |
| **Analytics Module** | Business reports, metrics, trends analysis |
| **Notifications Module** | Event-driven notifications, in-app alerts |

## Features

- **Role-Based Authentication**: Admin, Manager, and Rider roles with JWT
- **Order Management**: Full lifecycle from creation to delivery
- **Real-time Tracking**: GPS location tracking for riders and orders
- **Payment Integration**: Paystack payment processing and webhooks
- **Analytics & Reporting**: Business metrics and performance insights
- **Notifications**: Event-driven notification system

## Tech Stack

- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **Payments**: Paystack API
- **Background Jobs**: Celery + Redis (optional)
- **API Docs**: Swagger/OpenAPI (drf-spectacular)

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis (optional, for Celery)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Delivery_Backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Project Structure

```
apps/
├── users/          # Authentication & user management
├── riders/         # Rider operations & profiles
├── orders/         # Order lifecycle management
├── tracking/       # GPS tracking & location
├── payments/       # Paystack integration
├── analytics/      # Reporting & metrics
├── notifications/  # Event notifications
└── common/         # Shared utilities
```

## API Endpoints

### Authentication
- `POST /api/users/register/` - Register new user (admin only)
- `POST /api/users/login/` - Login and get JWT tokens
- `POST /api/users/refresh/` - Refresh access token

### Orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/` - List all orders
- `GET /api/orders/{id}/` - Order details
- `POST /api/orders/{id}/assign/` - Assign to rider

### Riders
- `GET /api/riders/tasks/` - Get rider's tasks
- `PATCH /api/riders/task/{id}/status/` - Update task status
- `GET /api/riders/earnings/` - View earnings

### Tracking
- `POST /api/tracking/location/` - Submit rider location
- `GET /api/tracking/orders/{id}/location/` - Track order

### Payments
- `POST /api/payments/initialize/` - Initialize payment
- `GET /api/payments/verify/` - Verify payment
- `POST /api/payments/webhook/` - Paystack webhook

### Analytics
- `GET /api/analytics/delivery-summary/` - Delivery statistics
- `GET /api/analytics/rider-performance/` - Rider metrics
- `GET /api/analytics/financials/` - Financial reports

## Running Tests

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

### Environment Variables

Ensure all production environment variables are set:
- `SECRET_KEY` - Django secret key
- `DEBUG=False`
- `ALLOWED_HOSTS` - Your domain
- `DATABASE_URL` - PostgreSQL connection string
- `PAYSTACK_SECRET_KEY` - Production Paystack key

### Deploy to Render/Railway

1. Create new web service
2. Set environment variables
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn config.wsgi:application`
5. Database will auto-create migrations

## Contributing

1. Create feature branch
2. Make changes with tests
3. Run tests and linting
4. Submit pull request

## License

Proprietary - Internal Use Only
