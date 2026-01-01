# Test Suite

This directory contains all tests for the Home Aid Kit Manager application.

## Directory Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── api/                     # API endpoint tests
│   ├── __init__.py
│   ├── test_anc_api.py      # ANC API endpoint tests
│   ├── test_auth_errors.py  # Authentication error tests
│   ├── test_drlz_api.py     # DRLZ API endpoint tests
│   ├── test_login.py        # Login API tests
│   └── test_registration.py # Registration API tests
├── integration/             # Integration tests
│   ├── __init__.py
│   ├── test_anc_integration.py   # ANC service integration tests
│   ├── test_anc_integration.sh   # ANC integration test script
│   └── test_drlz_integration.py  # DRLZ service integration tests
├── services/                # Service layer tests
│   ├── __init__.py
│   ├── test_anc_direct.py   # Direct ANC service tests
│   ├── test_anc_service.py  # ANC service unit tests
│   ├── test_anc_updated.py  # Updated ANC service tests
│   ├── test_mht_direct.py   # Direct MHT service tests
│   ├── test_mht_viewer.py   # MHT viewer service tests
│   └── test_store_prices.py # Store prices service tests
├── unit/                    # Unit tests
│   ├── __init__.py
│   └── test_instruction_sections.py # Instruction parsing tests
└── utils/                   # Test utilities and fixtures
    ├── __init__.py
    └── test_login.html      # HTML test file for login
```

## Test Categories

### API Tests (`tests/api/`)
Tests for FastAPI endpoints and HTTP API functionality:
- Authentication endpoints (login, registration, token refresh)
- CRUD operations for medications, households, users
- External service API endpoints (DRLZ, ANC)
- Error handling and validation

### Integration Tests (`tests/integration/`)
End-to-end tests that verify complete workflows:
- External service integration (DRLZ scraping, ANC lookup)
- Database operations with real data
- Background job processing
- Multi-service interactions

### Service Tests (`tests/services/`)
Tests for business logic and service layer:
- External API scrapers (DRLZ, ANC, MHT)
- Data processing and transformation
- Price comparison services
- Medication lookup services

### Unit Tests (`tests/unit/`)
Isolated tests for individual functions and classes:
- Utility functions
- Data validation
- Model methods
- Helper functions

## Running Tests

### Install Test Dependencies
```bash
cd backend
pip install pytest pytest-asyncio httpx
```

### Run All Tests
```bash
# From project root
pytest

# With coverage
pytest --cov=backend/app --cov-report=html
```

### Run Specific Test Categories
```bash
# API tests only
pytest tests/api/

# Integration tests only
pytest tests/integration/

# Service tests only
pytest tests/services/

# Unit tests only
pytest tests/unit/
```

### Run Specific Test Files
```bash
# Run ANC API tests
pytest tests/api/test_anc_api.py

# Run DRLZ integration tests
pytest tests/integration/test_drlz_integration.py
```

### Run Tests with Markers
```bash
# Run only fast tests
pytest -m "not slow"

# Run authentication tests
pytest -m auth

# Run DRLZ-related tests
pytest -m drlz
```

## Test Configuration

Test configuration is managed through:
- `pytest.ini`: pytest configuration and markers
- `conftest.py`: shared fixtures and test setup
- Environment variables for test database and API URLs

## Test Markers

Available pytest markers:
- `unit`: Unit tests
- `integration`: Integration tests  
- `api`: API tests
- `services`: Service tests
- `slow`: Slow running tests
- `auth`: Authentication related tests
- `drlz`: DRLZ service tests
- `anc`: ANC service tests
- `mht`: MHT service tests

## Writing New Tests

### Test File Naming
- API tests: `test_<feature>_api.py`
- Service tests: `test_<service>_service.py`
- Integration tests: `test_<feature>_integration.py`
- Unit tests: `test_<module>_unit.py`

### Test Function Naming
- Use descriptive names: `test_create_medication_success()`
- Include expected outcome: `test_login_with_invalid_credentials_returns_401()`
- Group related tests in classes: `class TestMedicationAPI:`

### Using Fixtures
```python
def test_create_medication(async_client, test_user_data, auth_headers):
    # Test implementation using shared fixtures
    pass
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines with:
- Isolated test database
- Mock external services
- Parallel test execution
- Coverage reporting

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure backend path is in PYTHONPATH
2. **Database connection**: Check test database configuration
3. **External services**: Use mocks for flaky external APIs
4. **Async tests**: Use `pytest-asyncio` for async test functions

### Test Database
Tests use a separate test database to avoid conflicts with development data.
Configure `DATABASE_URL` with `_test` suffix for test runs.
