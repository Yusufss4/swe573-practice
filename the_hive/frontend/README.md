# The Hive - Frontend

React + TypeScript + Vite frontend for The Hive time banking platform.

## Architecture

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **State Management**: TanStack Query + React Context
- **Routing**: React Router v6
- **Maps**: React Leaflet + OpenStreetMap
- **HTTP Client**: Axios

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   │   └── Layout.tsx  # Main layout with navigation
│   ├── pages/          # Route pages (to be implemented)
│   ├── services/       # API client services
│   │   ├── api.ts      # Axios configuration
│   │   └── auth.ts     # Authentication service
│   ├── contexts/       # React contexts
│   │   └── AuthContext.tsx  # Auth state management
│   ├── hooks/          # Custom React hooks
│   ├── types/          # TypeScript type definitions
│   │   └── index.ts    # API types matching backend
│   ├── utils/          # Helper utilities
│   │   ├── config.ts   # Environment configuration
│   │   ├── date.ts     # Date formatting
│   │   └── location.ts # Location utilities
│   ├── App.tsx         # Main app with routing
│   ├── main.tsx        # Entry point
│   └── theme.ts        # MUI theme configuration
├── public/             # Static assets
├── index.html          # HTML template
├── vite.config.ts      # Vite configuration
├── tsconfig.json       # TypeScript configuration
├── package.json        # Dependencies
├── Dockerfile          # Multi-stage Docker build
└── nginx.conf          # Production nginx config
```

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Local Development

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:5173
   - API should be running on http://localhost:8000

### Docker Development

From the `infra` directory:

```bash
docker-compose up
```

This will start:
- PostgreSQL on port 5432
- Backend API on port 8000
- Frontend on port 5173

## Available Scripts

- `npm run dev` - Start Vite dev server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## SRS Requirements Mapping

The frontend implements the following SRS requirements:

### Functional Requirements

- **FR-1**: User Registration and Authentication
  - `src/services/auth.ts` - Login/register/logout
  - `src/contexts/AuthContext.tsx` - Auth state management

- **FR-2**: Profile Management
  - Types in `src/types/index.ts`
  - Profile pages (to be implemented)

- **FR-3**: Offer and Need Management
  - Types and interfaces defined
  - CRUD operations (to be implemented)

- **FR-4**: Calendar and Availability
  - TimeSlot types defined

- **FR-5**: Handshake Mechanism
  - Participant types defined

- **FR-6**: Messaging System
  - Message types defined

- **FR-7**: TimeBank System
  - Balance display in user profile
  - Ledger entry types

- **FR-8**: Tagging and Search
  - Tag types and hierarchy support

- **FR-9**: Map-Based Visualization
  - React Leaflet integration planned
  - Location utilities in `src/utils/location.ts`

- **FR-10**: Comment and Feedback
  - Comment types defined

- **FR-11**: Reporting and Moderation
  - Report types and admin/moderator dashboards

- **FR-13**: Badges
  - Badge types and display logic

- **FR-14**: Active Items Management
  - Dedicated route planned

- **FR-15**: Community Forum
  - Forum types defined

### Non-Functional Requirements

- **NFR-1**: Performance
  - React Query for caching and optimistic updates
  - Code splitting via React Router
  - Vite for fast builds

- **NFR-4**: Security
  - JWT token management
  - HTTPS enforced (nginx config)
  - Secure headers in nginx

- **NFR-7**: Privacy
  - Location utilities use approximate coordinates
  - No exact addresses stored

## API Integration

The frontend communicates with the FastAPI backend via:

- **Base URL**: Configured in `.env` as `VITE_API_BASE_URL`
- **Authentication**: JWT Bearer tokens in Authorization header
- **Request Interceptor**: Automatically attaches token
- **Response Interceptor**: Handles 401 redirects and errors

## Theme & Design

Material-UI theme with:
- **Primary**: Warm orange/amber (#FFA726) - community warmth
- **Secondary**: Blue (#42A5F5) - trust and reliability
- Clean, accessible layout per SRS Section 3.3.1

## Next Steps

Pages to implement (in priority order):

1. **Authentication Pages**
   - Login page
   - Register page

2. **Core Features**
   - Home/Map view with offers/needs visualization
   - Offer list and detail pages
   - Need list and detail pages
   - Create offer/need forms

3. **User Features**
   - User profile pages
   - Active items dashboard
   - Messaging interface

4. **Community**
   - Forum (Discussions & Events tabs)
   - Search functionality

5. **Admin/Moderation**
   - Admin dashboard
   - Moderator dashboard

## Contributing

This frontend follows the same open-source principles as the backend:
- Type-safe code with TypeScript
- Component documentation with SRS references
- Clean code structure
- Comprehensive error handling

## License

Open Source - Same license as The Hive backend
