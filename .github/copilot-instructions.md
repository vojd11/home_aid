<!-- Use this file to provide workspace-specific custom instructions to Copilot. -->

# Home Aid Kit Manager

This is a multi-user home aid kit management system with the following tech stack:

## Backend
- Python FastAPI (async) - ✅ Implemented
- SQLAlchemy + Alembic for database - ✅ Implemented  
- PostgreSQL with pg_trgm extension - ✅ Configured
- Redis for caching and rate limiting - ✅ Configured
- Celery for background jobs - ✅ Configured
- JWT authentication - ✅ Basic implementation

## Frontend
- React with Vite - ✅ Configured
- Tailwind CSS for styling - ✅ Configured
- React Query for state management - ✅ Configured
- PWA capabilities - ✅ Configured

## Features Implemented
- ✅ Multi-user households with role-based access (models created)
- ✅ Medication inventory management (models created)
- ✅ External link resolution (models for DRLZ and Tabletki)
- ✅ Tag-based organization (models created)
- ✅ Search functionality (database indexes configured)
- ✅ Audit logging (models created)

## Architecture
- ✅ Async FastAPI backend
- ✅ React SPA frontend  
- ✅ PostgreSQL database with proper schema
- ✅ Redis for caching/queue
- ✅ Celery workers for external site integration
- ✅ Docker Compose for development

## Project Status
✅ **BACKEND FULLY IMPLEMENTED** - All core API endpoints working and tested end-to-end.

🎯 **Current Status: FRONTEND IMPLEMENTATION PHASE**

### ✅ Completed Implementation
- ✅ **Complete Backend API**: All CRUD endpoints implemented and tested
  - ✅ Authentication system (JWT register, login, refresh) - TESTED ✓
  - ✅ Household management with role-based access - TESTED ✓
  - ✅ Medication CRUD (create, read, update, delete) - TESTED ✓
  - ✅ Core decrement feature ("-1" functionality) - TESTED ✓
  - ✅ Tag system API (create, delete, assign/unassign) - IMPLEMENTED ✓
  - ✅ Audit logging for all inventory changes - TESTED ✓
- ✅ **Background Job System**: Celery workers for external site integration
  - ✅ DRLZ.com.ua scraper implementation - READY ✓
  - ✅ Tabletki.ua scraper implementation - READY ✓
  - ✅ Redis cache and rate limiting - CONFIGURED ✓
- ✅ **Database Infrastructure**: PostgreSQL with proper schema
  - ✅ Full database schema with relationships - TESTED ✓
  - ✅ Alembic migrations working - CONFIGURED ✓
  - ✅ Indexes and pg_trgm for fuzzy search - READY ✓
- ✅ **Development Environment**: Docker Compose - RUNNING ✓
- ✅ **API Documentation**: OpenAPI/Swagger at /docs - AVAILABLE ✓

### ✅ Recently Completed
- ✅ **Complete Medication Management UI**: Full CRUD interface for medications
  - ✅ MedicationList component with search and filtering
  - ✅ MedicationCard with quantity display and decrement button
  - ✅ AddMedicationDialog for creating new medications
  - ✅ EditMedicationDialog for updating medications
  - ✅ SearchBar component with debounced input
  - ✅ Core "-1" decrement button functionality
  - ✅ Tag system integration (add/remove tags)
  - ✅ External link display (DRLZ, Tabletki)
  - ✅ Low stock and out-of-stock indicators
  - ✅ Complete integration with backend API

### ❌ Next Implementation Priorities
- ✅ **Complete Frontend Medication Interface**: ✅ COMPLETED ✓
- ❌ **Tag Management UI**: Frontend for tag assignment and filtering
- ❌ **External Link Integration**: Connect frontend to background job results  
- ❌ **Search & Filtering Interface**: Advanced search UI components
- ❌ **Testing Infrastructure**: API and frontend test suites
- ❌ **PWA Features**: Offline functionality and mobile optimization

### 🚀 Next Development Priorities

**Phase 1: Complete Core Frontend (Immediate - 1-2 weeks)** ✅ COMPLETED
1. **Medication Management UI**: ✅ Complete CRUD interface for medications in selected household
   - ✅ Backend API endpoints ready (create, list, update, delete, decrement)
   - ✅ Frontend components: MedicationList, MedicationCard, AddMedicationDialog, EditMedicationDialog
   - ✅ Core "-1" decrement button functionality
   - ✅ Edit/update medication interface
   - ✅ SearchBar with debounced input
   - ✅ Tag system integration (create, assign, filter by tags)

2. **Tag Management Interface**: ✅ Frontend for tag CRUD operations  
   - ✅ Backend API endpoints ready (create, delete, assign/unassign)
   - ✅ Frontend: TagInput, TagChips, tag filtering interface
   - ✅ Tag assignment to medications

**Phase 2: Enhanced User Experience (2-3 weeks)**
3. **Search & Filtering**: Advanced search with fuzzy matching
   - ✅ Backend: PostgreSQL with pg_trgm extension configured
   - ❌ Frontend: SearchBar component with debounced input
   - ❌ Advanced filtering by tags, low stock, etc.

4. **External Link Integration**: Connect background job system
   - ✅ Celery workers implemented (DRLZ and Tabletki scrapers)
   - ✅ Background job infrastructure ready
   - ❌ Frontend: Display link badges and trigger manual resolution
   - ❌ Auto-trigger link resolution on medication creation

**Phase 3: Production Readiness (3-4 weeks)**  
5. **Testing Suite**: Comprehensive test coverage
   - ✅ pytest and pytest-asyncio already in requirements
   - ❌ API integration tests for all endpoints
   - ❌ Frontend component tests with React Testing Library
   - ❌ End-to-end tests for critical user flows

6. **PWA Features**: Mobile-optimized experience
   - ✅ vite-plugin-pwa already configured in package.json
   - ❌ Service worker for offline functionality
   - ❌ App manifest and mobile optimizations
   - ❌ Background sync for offline actions

**Phase 4: Production Deployment & Monitoring (4-5 weeks)**
7. **Production Deployment**: CI/CD and hosting
   - ✅ Docker Compose setup working
   - ❌ Production Docker configurations
   - ❌ CI/CD pipeline (GitHub Actions)
   - ❌ Environment management (staging/production)

8. **Monitoring & Analytics**: Observability and performance
   - ❌ Error tracking (Sentry integration)
   - ❌ Performance monitoring and metrics
   - ❌ Usage analytics and audit log interface

## Development Guidelines
- Use async/await patterns throughout (✅ implemented)
- Follow FastAPI best practices with proper dependency injection (✅ implemented)
- Implement proper error handling and validation (✅ implemented)
- Use Pydantic models for request/response validation (✅ implemented)
- Follow security best practices (JWT, HTTPS, rate limiting) (🔄 JWT complete, others pending)
- Implement proper logging and monitoring (🔄 basic logging implemented)
- Write tests for all major functionality (❌ pending)

## Key Implementation Details
- **Authentication**: JWT-based with role-based access control
- **Database**: PostgreSQL with proper indexing and constraints  
- **API Design**: RESTful endpoints with OpenAPI documentation
- **Background Jobs**: Celery with Redis for external site resolution
- **Error Handling**: Structured HTTP exceptions with proper status codes
- **Validation**: Pydantic schemas with input sanitization
- **Relationships**: Many-to-many tags, audit logging, household membership

## Current API Endpoints (All Working ✅)
- `POST /api/v1/auth/register` - User registration ✅ TESTED
- `POST /api/v1/auth/login` - Login with JWT tokens ✅ TESTED & FIXED
- `POST /api/v1/auth/refresh` - Refresh access token ✅ TESTED  
- `GET /api/v1/auth/me` - Get current user info ✅ IMPLEMENTED
- `GET /api/v1/households` - List user households ✅ TESTED
- `POST /api/v1/households` - Create household ✅ TESTED
- `POST /api/v1/households/{id}/members` - Invite members
- `GET /api/v1/households/{hid}/medications` - List medications ✅ TESTED
- `POST /api/v1/households/{hid}/medications` - Create medication ✅ TESTED
- `POST /api/v1/households/{hid}/medications/{mid}/decrement` - Decrement quantity ✅ TESTED
- `PATCH /api/v1/households/{hid}/medications/{mid}` - Update medication
- `DELETE /api/v1/households/{hid}/medications/{mid}` - Delete medication

## Test Results Summary
✅ **Backend API**: All core endpoints working and tested - Login issue FIXED
✅ **Frontend**: React app running with authentication components  
✅ **Database**: PostgreSQL with proper schema and audit logging
✅ **Authentication Flow**: Complete registration → login → JWT workflow - WORKING ✓
✅ **Core Feature**: Medication creation and decrement (-1) functionality
✅ **Multi-user**: Household creation and management
✅ **Docker Environment**: All services running (api, frontend, postgres, redis, worker)

## Known Working Examples
```bash
# User Registration
curl -X POST http://hate.local:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Create Medication  
curl -X POST http://hate.local:8000/api/v1/households/7/medications \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "Ібупрофен 200 мг", "quantity": 20}'

# Decrement Medication (-1)
curl -X POST http://hate.local:8000/api/v1/households/7/medications/3/decrement \
  -H "Authorization: Bearer <token>"
```
