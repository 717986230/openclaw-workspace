# OpenDevin Sample Project

This sample project demonstrates OpenDevin integration with OpenClaw for code generation and testing.

## Project Structure

```
sample-project/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── sample_fastapi_app.py        # Sample FastAPI application
├── test_sample_app.py           # Test suite for the application
├── opendevin.yaml              # OpenDevin configuration
└── pytest.ini                  # Pytest configuration
```

## Setup

### Prerequisites

- Python 3.11+
- pip
- Docker (for sandboxed execution)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
# Run the FastAPI application
python sample_fastapi_app.py

# Or using uvicorn directly
uvicorn sample_fastapi_app:app --reload --port 8000
```

## Running Tests

```bash
# Run all tests
pytest test_sample_app.py -v

# Run with coverage
pytest test_sample_app.py --cov=sample_fastapi_app --cov-report=html

# Run specific test class
pytest test_sample_app.py::TestTaskCreation -v

# Run with markers
pytest test_sample_app.py -m "not slow" -v
```

## Using OpenDevin

### Generate Code

```bash
# Generate similar code
openclaw opendevin generate \
  --spec "Create a REST API for project management" \
  --language python \
  --framework fastapi \
  --output ./generated
```

### Generate Tests

```bash
# Generate tests for the application
openclaw opendevin test-generate \
  --source sample_fastapi_app.py \
  --output test_generated.py \
  --framework pytest
```

### Run with OpenDevin

```bash
# Run tests using OpenDevin test runner
openclaw opendevin test \
  --path . \
  --coverage \
  --report html
```

## API Documentation

Once the application is running, access the API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user information

### Tasks

- `POST /tasks` - Create a new task
- `GET /tasks` - List all tasks (with optional filters)
- `GET /tasks/{task_id}` - Get a specific task
- `PATCH /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task

### Health

- `GET /health` - Health check endpoint

## Testing Examples

### Register User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","name":"Test User"}'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Create Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"My Task","description":"Task description"}'
```

## License

This sample project is part of the OpenDevin integration for OpenClaw.
