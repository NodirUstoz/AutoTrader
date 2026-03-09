# AutoTrader - Vehicle Marketplace Platform

A full-featured vehicle marketplace platform where users can buy and sell cars, motorcycles, and other vehicles. Built with Django REST Framework, React, PostgreSQL, Redis, Celery, Elasticsearch, and Docker.

## Features

- **Vehicle Listings** -- Create, manage, and browse vehicle listings with rich media support
- **Advanced Search** -- Filter by make, model, year, price range, mileage, body type, fuel type, transmission, and more
- **VIN Decoder** -- Automatic vehicle identification number lookup and validation
- **Dealer Profiles** -- Verified dealer accounts with inventory management and analytics
- **Vehicle Comparison** -- Side-by-side comparison of up to four vehicles
- **Financing Calculator** -- Monthly payment estimation with configurable loan terms, interest rates, and down payments
- **Saved Searches** -- Receive notifications when new listings match saved criteria
- **Inquiry System** -- Direct messaging to sellers and test drive scheduling
- **Price History** -- Track price changes over time for any listing
- **Responsive UI** -- Fully responsive React frontend optimized for all devices

## Architecture

```
autotrader/
|-- backend/          Django + DRF API server
|   |-- apps/
|   |   |-- accounts/     User management, dealer and buyer profiles
|   |   |-- vehicles/     Vehicle catalog (makes, models, features, images)
|   |   |-- listings/     Marketplace listings, price history, saved searches
|   |   |-- inquiries/    Buyer inquiries and test drive requests
|   |   |-- comparisons/  Vehicle comparison tool
|   |   |-- financing/    Loan calculator and financing applications
|   |-- config/        Django settings, URL routing, WSGI/ASGI, Celery
|   |-- utils/         Pagination, VIN decoder, custom exceptions
|-- frontend/         React SPA with Redux state management
|-- nginx/            Reverse proxy configuration
|-- docker-compose.yml
```

## Tech Stack

| Layer         | Technology                        |
|---------------|-----------------------------------|
| Backend API   | Django 5.0, Django REST Framework |
| Frontend      | React 18, Redux Toolkit           |
| Database      | PostgreSQL 16                     |
| Cache / Broker| Redis 7                           |
| Task Queue    | Celery 5                          |
| Search Engine | Elasticsearch 8                   |
| Reverse Proxy | Nginx                             |
| Containers    | Docker, Docker Compose            |

## Prerequisites

- Docker and Docker Compose (v2.20+)
- GNU Make (optional, for convenience commands)

## Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/autotrader.git
   cd autotrader
   ```

2. **Copy the environment file and adjust values**

   ```bash
   cp .env.example .env
   ```

3. **Build and start all services**

   ```bash
   make build
   make up
   ```

4. **Run database migrations**

   ```bash
   make migrate
   ```

5. **Create a superuser**

   ```bash
   make superuser
   ```

6. **Access the application**

   | Service           | URL                          |
   |-------------------|------------------------------|
   | Frontend          | http://localhost              |
   | API               | http://localhost/api/v1/      |
   | Django Admin      | http://localhost/admin/       |
   | API Documentation | http://localhost/api/v1/docs/ |

## Makefile Commands

```bash
make build        # Build all Docker images
make up           # Start all services in detached mode
make down         # Stop all services
make logs         # Tail service logs
make migrate      # Run Django migrations
make makemigrations  # Generate new migration files
make superuser    # Create a Django superuser
make test         # Run the backend test suite
make lint         # Run linters on backend code
make shell        # Open a Django shell
make flush        # Flush the database (destructive)
make collectstatic  # Collect static files for production
```

## Development

### Backend

The backend uses Django with the Django REST Framework. Key conventions:

- Settings are split into `base.py`, `development.py`, and `production.py`
- Each Django app lives under `backend/apps/`
- API versioning is handled via URL prefixes (`/api/v1/`)
- Authentication uses JWT tokens (SimpleJWT)

### Frontend

The frontend is a React single-page application managed with Redux Toolkit:

- API communication via Axios with interceptors for token refresh
- Component structure: `components/` for reusable UI, `pages/` for route-level views
- Global styles in `src/styles/global.css`

### Environment Variables

See `.env.example` for all configurable values. Key variables:

| Variable              | Description                         |
|-----------------------|-------------------------------------|
| `SECRET_KEY`          | Django secret key                   |
| `DATABASE_URL`        | PostgreSQL connection string        |
| `REDIS_URL`           | Redis connection string             |
| `ELASTICSEARCH_URL`   | Elasticsearch connection string     |
| `ALLOWED_HOSTS`       | Comma-separated list of hostnames   |
| `CORS_ALLOWED_ORIGINS`| Comma-separated frontend origins    |

## Deployment

For production deployments:

1. Set `DJANGO_SETTINGS_MODULE=config.settings.production` in `.env`
2. Set strong, unique values for `SECRET_KEY` and database credentials
3. Configure `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
4. Enable HTTPS in the Nginx configuration
5. Run `make collectstatic` to gather static assets

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` -- Register a new user
- `POST /api/v1/auth/login/` -- Obtain JWT token pair
- `POST /api/v1/auth/token/refresh/` -- Refresh access token
- `GET  /api/v1/auth/profile/` -- Retrieve current user profile

### Vehicles
- `GET    /api/v1/vehicles/` -- List vehicles with filtering
- `POST   /api/v1/vehicles/` -- Create a vehicle (dealers only)
- `GET    /api/v1/vehicles/{id}/` -- Retrieve vehicle details
- `GET    /api/v1/vehicles/makes/` -- List all vehicle makes
- `GET    /api/v1/vehicles/models/` -- List vehicle models
- `GET    /api/v1/vehicles/vin/{vin}/` -- Decode a VIN

### Listings
- `GET    /api/v1/listings/` -- Browse active listings
- `POST   /api/v1/listings/` -- Create a listing
- `GET    /api/v1/listings/{id}/` -- Listing detail with price history
- `POST   /api/v1/listings/saved-searches/` -- Save a search
- `GET    /api/v1/listings/saved-searches/` -- List saved searches

### Inquiries
- `POST   /api/v1/inquiries/` -- Send an inquiry to a seller
- `POST   /api/v1/inquiries/test-drives/` -- Request a test drive

### Comparisons
- `POST   /api/v1/comparisons/` -- Create a comparison
- `GET    /api/v1/comparisons/{id}/` -- Retrieve comparison details

### Financing
- `POST   /api/v1/financing/calculate/` -- Calculate monthly payment
- `POST   /api/v1/financing/apply/` -- Submit a loan application

## License

This project is proprietary software. All rights reserved.
