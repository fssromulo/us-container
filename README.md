# Container CRM

A full-stack CRM application built with Vue.js, FastAPI, PostgreSQL, and Redis.

## Prerequisites

- Docker and Docker Compose
- Node.js (v16 or higher)
- Python 3.8+
- npm or yarn

## Project Structure

```
container-crm/
├── backend/         # FastAPI backend
├── frontend/        # Vue.js frontend
└── docker-compose.yml
```

## Setup Instructions

### 1. Environment Setup

First, clone the repository and set up your environment files:

#### Backend (.env file in backend/src/)

```
DB_USER=hello_fastapi
DB_PASS=hello_fastapi
DB_HOST=db
DB_PORT=5432
DB_NAME=containerCrm
REDIS_HOST=redis-server
REDIS_PORT=6379
STAGE=dev
```

#### Frontend (.env file in frontend/)

```
VITE_API_URL=http://localhost:5001
```

### 2. Backend Setup

The backend runs in Docker containers, which handle all the dependencies. To start the backend services:

```bash
docker-compose up
```

This will start:

- PostgreSQL database on port 6543
- Redis server on port 6379
- FastAPI backend on port 5001

### 3. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install   # or yarn install
```

Start the development server:

```bash
npm run dev   # or yarn dev
```

The frontend will be available at `http://localhost:5173`

## Development

### Backend Development

- The backend code is automatically reloaded when changes are made
- API documentation is available at `http://localhost:5001/docs`
- Database runs on `localhost:6543`
- Redis runs on `localhost:6379`

### Frontend Development

- The frontend uses Vite for development
- Uses PrimeVue for UI components
- Tailwind CSS for styling
- Vue 3 with Composition API

## Building for Production

### Frontend Build

```bash
cd frontend
npm run build        # for production
npm run build-stage  # for staging
```

## Additional Notes

- The application uses Auth0 for authentication
- Redis is used for caching
- The backend uses FastAPI with async support
- Database migrations are handled through Tortoise ORM
- Frontend uses Vue 3 with Pinia for state management
