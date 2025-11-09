# The Hive - Frontend

React + TypeScript frontend for The Hive time-banking platform.

## 🚀 Quick Start

### Using Docker (Recommended)

The easiest way to run everything:

```bash
cd /home/yusufss/swe573-practice/the_hive/infra
docker-compose up
```

This starts the database, backend, and frontend with hot reload. Open http://localhost:3000

👉 **See [DOCKER_QUICKSTART.md](../DOCKER_QUICKSTART.md) for details**

### Using npm

```bash
# Install dependencies
npm install

# Start development server (backend must be running separately)
npm run dev
```

The app will be available at `http://localhost:3000`

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TanStack Query (React Query)** - Data fetching and caching
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Leaflet** - Map integration
- **Sonner** - Toast notifications

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Create environment file (already done)
# Edit .env if needed to change API URL

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui components
│   └── ProtectedRoute.tsx
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication state management
├── lib/                # Utilities and API layer
│   ├── api.ts         # API client functions
│   ├── api-client.ts  # Axios instance with interceptors
│   └── types.ts       # TypeScript types matching backend
├── pages/             # Page components
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── HomeDashboard.tsx
│   ├── OfferNeedDetail.tsx
│   ├── UserProfile.tsx
│   ├── ActiveItems.tsx
│   └── MessagingView.tsx
├── styles/
│   └── globals.css    # Global styles with Tailwind
├── App.tsx            # Route configuration
└── main.tsx           # App entry point with providers
```

## Key Features

### Authentication
- JWT-based authentication with automatic token management
- Login, register, and logout flows
- Protected routes redirect to login when unauthenticated
- Auth state persisted in localStorage

### API Integration
- Centralized API client with request/response interceptors
- Automatic auth token injection on requests
- Automatic redirect to login on 401 responses
- React Query for data caching and automatic refetching

### Components
All components use shadcn/ui for consistent styling:
- Form components (Input, Label, Button)
- Layout components (Card, Dialog, Sheet)
- Feedback components (Toast notifications via Sonner)

## Environment Variables

Create a `.env` file (already created) with:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=The Hive
```

## API Client Usage

The API client is organized by resource:

```typescript
import { authApi, offersApi, needsApi, usersApi } from '@/lib/api';

// Login
const response = await authApi.login({ username, password });

// Fetch offers
const offers = await offersApi.list();

// Create need
const need = await needsApi.create({
  title: "Help with moving",
  description: "Need help moving furniture",
  hours_estimated: 3,
  capacity: 2,
  is_remote: false,
  tags: ["moving", "physical"]
});
```

## React Query Usage

Use React Query hooks for data fetching with automatic caching:

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { offersApi } from '@/lib/api';

// In a component
const { data: offers, isLoading } = useQuery({
  queryKey: ['offers'],
  queryFn: () => offersApi.list(),
});

const createMutation = useMutation({
  mutationFn: offersApi.create,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['offers'] });
  },
});
```

## Development Notes

### TypeScript Strictness
- `strict: false` in tsconfig.json for moderate strictness
- `noUnusedLocals` and `noUnusedParameters` enabled to catch unused code
- Type definitions in `src/lib/types.ts` match backend schemas

### Routing
- Uses HashRouter for compatibility
- Protected routes require authentication
- Routes defined in `App.tsx`

### Map Integration
- Leaflet for interactive maps
- CSS imported in `index.html`
- Components in map view show offers/needs by location

### Styling
- Tailwind CSS with custom theme in `tailwind.config.js`
- CSS variables for theming in `globals.css`
- shadcn/ui components use CSS variables for consistent theming

## Backend Integration Checklist

- ✅ Authentication endpoints (`/api/v1/auth/login`, `/api/v1/auth/register`, `/api/v1/auth/me`)
- ✅ Offers endpoints (`/api/v1/offers/`)
- ✅ Needs endpoints (`/api/v1/needs/`)
- ✅ Users endpoint (`/api/v1/users/{id}`) - **NEW** 
- ✅ Participants endpoints (propose, accept, complete)
- ✅ Comments endpoints
- ✅ Search endpoint (`/api/v1/search/`)
- ✅ Map endpoint (`/api/v1/map/items`)
- ✅ Dashboard endpoint (`/api/v1/dashboard/stats`)
- ✅ Forum endpoints (`/api/v1/forum/posts`)
- ✅ Ledger endpoint (`/api/v1/auth/me/ledger`)

## Next Steps

1. **Install dependencies** - Run `npm install`
2. **Start backend** - Ensure backend is running on port 8000
3. **Start frontend** - Run `npm run dev`
4. **Test authentication** - Register a new account and login
5. **Replace mock data** - Update existing components to use real API calls (see below)

## Migrating from Mock Data

The frontend was originally generated with mock data. To complete the integration:

1. Remove all imports from `../lib/mock-data` (doesn't exist)
2. Replace mock data with API calls using React Query
3. Update components to handle loading and error states
4. Use the `useAuth()` hook for current user data

Example migration:

```typescript
// Before (with mock data)
import { mockOffers } from '../lib/mock-data';

// After (with API)
import { useQuery } from '@tanstack/react-query';
import { offersApi } from '@/lib/api';

const { data: offers, isLoading, error } = useQuery({
  queryKey: ['offers'],
  queryFn: () => offersApi.list(),
});
```

## Troubleshooting

### CORS Errors
Ensure backend has CORS configured for `http://localhost:3000`

### 401 Unauthorized
Check that auth token is being stored and sent correctly. Clear localStorage and re-login.

### Type Errors
Run `npm install` to ensure all type definitions are installed

### Build Errors
Check that all shadcn/ui components exist. Some may need to be added manually.

## Contributing

When adding new features:
1. Add TypeScript types to `src/lib/types.ts`
2. Add API functions to `src/lib/api.ts`
3. Use React Query for data fetching
4. Follow existing component patterns
5. Use shadcn/ui components for consistency
