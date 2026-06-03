# Online Cinema API Service

Online Cinema is a backend web application that allows users to browse movies, manage personal watchlists, rate and comment on content, purchase access to movies, and manage orders through an integrated payment system.

The project provides a complete movie platform ecosystem including authentication, authorization, shopping cart functionality, payment processing, notifications, background tasks, file storage, automated testing, and CI/CD deployment.

## Key Features

- Secure authentication and authorization via JWT
- Email account activation
- Password reset via email
- Role-based access control (USER / MODERATOR / ADMIN)
- User profile management
- Avatar upload support via MinIO
- Movie catalog management
- Genres, actors, directors, and certifications
- Search, filtering, and sorting functionality
- Favorites system
- Movie ratings
- Comments and replies
- Movie reactions (likes/dislikes)
- Shopping cart functionality
- Order management
- Stripe Checkout integration
- Stripe Webhook processing
- Payment status tracking
- Purchased movies tracking
- Notification system
- Background tasks with Celery
- Docker and Docker Compose support
- Automated testing with Pytest
- Code quality checks with Ruff
- CI/CD deployment to AWS EC2

## Technical Stack

* **Framework:** FastAPI
* **Programming Language:** Python 3.11
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Migrations:** Alembic
* **Authentication:** JWT
* **Task Queue:** Celery
* **Message Broker:** Redis
* **Object Storage:** MinIO (S3-compatible)
* **Email Testing:** MailHog
* **Payment System:** Stripe Checkout & Webhooks
* **Dependency Management:** Poetry
* **Containerization:** Docker & Docker Compose
* **Testing:** Pytest
* **Code Quality:** Ruff, MyPy
* **Coverage Reports:** Pytest-Cov
* **Documentation:** OpenAPI (Swagger)
* **CI/CD:** GitHub Actions
* **Deployment:** AWS EC2

---

## 1. Clone the Repository

Start by cloning the project repository from GitHub:

```bash
git clone <repository-url>
cd online-cinema
```

---

## 2. Install Dependencies

This project uses Poetry for dependency management.

```bash
pip install poetry

poetry install
```

---

## 3. Create a `.env` File

Create a `.env` file in the project root directory.

```env
ENV=dev

ASYNC_DATABASE_URL=
SYNC_DATABASE_URL=

JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=

SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=

MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=

S3_ENDPOINT_URL=
S3_PUBLIC_ENDPOINT_URL=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET_NAME=
S3_REGION=

STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

BACKEND_URL=
```

---

## 4. Run with Docker

Build and start all services:

```bash
docker compose up -d --build
```

Stop all services:

```bash
docker compose down
```

---

## 5. Apply Database Migrations

```bash
docker compose exec web alembic upgrade head
```

---

## 6. Available Services

### FastAPI Application

```text
http://127.0.0.1:8000
```

### Swagger Documentation

```text
http://127.0.0.1:8000/api/v1/docs
```

### MailHog

```text
http://127.0.0.1:8025
```

### MinIO Console

```text
http://127.0.0.1:9001
```

---

## Running Tests

Run all tests:

```bash
poetry run pytest
```

Generate coverage report:

```bash
poetry run pytest --cov=src --cov-report=term-missing
```

---

## Code Quality

Run Ruff lint checks:

```bash
poetry run ruff check .
```

Check formatting:

```bash
poetry run ruff format --check .
```

Format the codebase:

```bash
poetry run ruff format .
```

Run type checking:

```bash
poetry run mypy src
```

---

## Stripe Testing

The project uses Stripe in test mode.

Test card:

```text
4242 4242 4242 4242
```

Use any future expiration date, any CVC, and any ZIP code.

Payment flow:

```text
Cart
→ Order
→ Stripe Checkout
→ Stripe Webhook
→ Payment Successful
→ Order Paid
```

---

## API Documentation

Interactive API documentation is available via Swagger UI:

```text
http://127.0.0.1:8000/api/v1/docs
```

---

## CI/CD Pipeline

GitHub Actions pipeline automatically performs:

- Dependency installation
- Ruff lint checks
- Ruff formatting checks
- MyPy type checking
- Alembic migrations
- Automated tests
- Coverage reporting
- Deployment to AWS EC2

Deployment flow:

```text
Push to develop
→ CI Pipeline
→ CD Pipeline
→ AWS EC2 Update
→ Docker Rebuild
→ Alembic Migration
→ Application Deployment
```

---

## AWS Deployment

The project is deployed on AWS EC2.

Infrastructure includes:

- FastAPI
- PostgreSQL
- Redis
- Celery Worker
- Celery Beat
- MinIO
- MailHog

Server configuration:

- Elastic IP
- Docker Compose
- 16 GB EBS Volume
- 2 GB Swap Memory