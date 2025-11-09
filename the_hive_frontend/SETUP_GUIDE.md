# Frontend Integration Complete Setup Guide

This document provides a complete guide for setting up and running the fully integrated frontend.

## What Has Been Done

### ✅ Phase 1: Project Configuration
- Created `package.json` with all necessary dependencies
- Set up Vite as build tool with React plugin
- Configured TypeScript with moderate strictness
- Set up Tailwind CSS with PostCSS
- Created environment configuration (.env files)
- Configured path aliases (@/ for src/)

### ✅ Phase 2: API Integration Layer
- Created `src/lib/api-client.ts` - Axios instance with JWT interceptors
- Created `src/lib/types.ts` - TypeScript interfaces matching backend schemas
- Created `src/lib/api.ts` - Organized API functions by resource
- Set up automatic token injection on requests
- Set up automatic redirect on 401 responses

### ✅ Phase 3: Authentication System
- Created `src/contexts/AuthContext.tsx` - Global auth state management
- Created `src/components/ProtectedRoute.tsx` - Route protection HOC
- Created `src/pages/LoginPage.tsx` - Login form
- Created `src/pages/RegisterPage.tsx` - Registration form  
- Implemented token persistence in localStorage
- Auto-fetch user on app load

### ✅ Phase 4: React Query Setup
- Configured QueryClient in `src/main.tsx`
- Set up default query options (retry, staleTime, refetch)
- Added Toaster for notifications (sonner)

### ✅ Phase 5: Backend Enhancement
- **NEW ENDPOINT**: Created `/api/v1/users/{id}` endpoint
- Registered users router in main.py
- Added SRS requirement comments

## Installation Steps

### 1. Install Dependencies

```bash
cd /home/yusufss/swe573-practice/the_hive_frontend
npm install
```

This will install:
- React & React DOM
- React Router DOM  
- TanStack React Query (for data fetching)
- Axios (HTTP client)
- Leaflet & React-Leaflet (maps)
- shadcn/ui components (Radix UI primitives)
- Tailwind CSS & utilities
- TypeScript & type definitions
- Vite & plugins

### 2. Start Backend

Make sure the backend is running:

```bash
cd /home/yusufss/swe573-practice/the_hive
make run
# OR
cd infra && docker-compose up
```

Backend should be accessible at `http://localhost:8000`

### 3. Start Frontend

```bash
cd /home/yusufss/swe573-practice/the_hive_frontend
npm run dev
```

Frontend will be available at `http://localhost:3000`

## What's Next: Migrating Existing Components

Your existing components (HomeDashboard, CreateOfferNeedModal, OfferNeedDetail, etc.) need to be updated to use the real API instead of mock data.

### Example Migration Pattern

**Before (with mock data):**
```typescript
import { mockOffers } from '../lib/mock-data';

function HomeDashboard() {
  const [items, setItems] = useState(mockOffers);
  // ...
}
```

**After (with API):**
```typescript
import { useQuery } from '@tanstack/react-query';
import { offersApi, needsApi, searchApi } from '@/lib/api';

function HomeDashboard() {
  // Fetch offers
  const { data: offers, isLoading: offersLoading } = useQuery({
    queryKey: ['offers'],
    queryFn: () => offersApi.list(),
  });

  // Fetch needs
  const { data: needs, isLoading: needsLoading } = useQuery({
    queryKey: ['needs'],
    queryFn: () => needsApi.list(),
  });

  // Combine them
  const items = [...(offers || []), ...(needs || [])];
  const isLoading = offersLoading || needsLoading;

  if (isLoading) return <div>Loading...</div>;

  // Use items as before
}
```

### Components That Need Migration

1. **App.tsx** - Add login/register routes, wrap with ProtectedRoute
2. **HomeDashboard.tsx** - Replace mock data with offers/needs API
3. **CreateOfferNeedModal.tsx** - Submit to offers/needs API
4. **OfferNeedDetail.tsx** - Fetch from offers/needs API by ID
5. **UserProfile.tsx** - Fetch from users API
6. **ActiveItems.tsx** - Fetch user's offers/needs
7. **MessagingView.tsx** - Use participants/comments API
8. **AuthNavbar.tsx** - Use useAuth() for user data and balance

### Key API Functions Available

```typescript
// Authentication
authApi.login(credentials)
authApi.register(userData)
authApi.getMe()
authApi.getLedger()

// Users
usersApi.getUser(userId)
usersApi.getUserComments(userId)

// Offers
offersApi.list()
offersApi.get(offerId)
offersApi.create(data)
offersApi.update(offerId, data)
offersApi.delete(offerId)
offersApi.getMyOffers()

// Needs  
needsApi.list()
needsApi.get(needId)
needsApi.create(data)
needsApi.update(needId, data)
needsApi.delete(needId)
needsApi.getMyNeeds()

// Participants (handshake workflow)
participantsApi.proposeForOffer(offerId)
participantsApi.proposeForNeed(needId)
participantsApi.acceptOfferParticipant(offerId, participantId, { hours })
participantsApi.acceptNeedParticipant(needId, participantId, { hours })
participantsApi.completeExchange(participantId)
participantsApi.getMyParticipations()

// Comments
commentsApi.create({ content, rating, recipient_id, participant_id })
commentsApi.getUserComments(userId)

// Search
searchApi.search({ query, type, tags, is_remote, location_lat, location_lon, radius_km })

// Map
mapApi.getMapItems()

// Dashboard
dashboardApi.getStats()

// Forum
forumApi.listPosts()
forumApi.getPost(postId)
forumApi.createPost({ title, content })
forumApi.getReplies(postId)
forumApi.createReply(postId, content)
```

## Updated App.tsx with Routes

Here's how to update your App.tsx:

```typescript
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomeDashboard from './components/HomeDashboard';
import OfferNeedDetail from './components/OfferNeedDetail';
import UserProfile from './components/UserProfile';
import ActiveItems from './components/ActiveItems';
import MessagingView from './components/MessagingView';
import { useAuth } from './contexts/AuthContext';

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <LoginPage />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/" /> : <RegisterPage />} />

      {/* Protected routes */}
      <Route path="/" element={<ProtectedRoute><HomeDashboard /></ProtectedRoute>} />
      <Route path="/offer/:id" element={<ProtectedRoute><OfferNeedDetail /></ProtectedRoute>} />
      <Route path="/need/:id" element={<ProtectedRoute><OfferNeedDetail /></ProtectedRoute>} />
      <Route path="/profile/:userId" element={<ProtectedRoute><UserProfile /></ProtectedRoute>} />
      <Route path="/active-items" element={<ProtectedRoute><ActiveItems /></ProtectedRoute>} />
      <Route path="/messages/:exchangeId" element={<ProtectedRoute><MessagingView /></ProtectedRoute>} />
    </Routes>
  );
}

export default App;
```

## Using the Auth Hook

Access current user data anywhere:

```typescript
import { useAuth } from '@/contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, logout, refreshUser } = useAuth();

  if (!isAuthenticated) {
    return <div>Not logged in</div>;
  }

  return (
    <div>
      <p>Welcome {user?.username}</p>
      <p>Balance: {user?.balance}h</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

## Handling Loading and Error States

Always handle loading and error states with React Query:

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['offers'],
  queryFn: () => offersApi.list(),
});

if (isLoading) {
  return <div className="flex justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
  </div>;
}

if (error) {
  return <div className="text-red-500 p-4">
    Failed to load offers: {error.message}
  </div>;
}

// Use data safely
return <div>{data.map(offer => ...)}</div>;
```

## Mutations (Create, Update, Delete)

Use mutations for data changes:

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { offersApi } from '@/lib/api';
import { toast } from 'sonner';

function CreateOfferForm() {
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: offersApi.create,
    onSuccess: () => {
      // Invalidate and refetch offers
      queryClient.invalidateQueries({ queryKey: ['offers'] });
      toast.success('Offer created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create offer');
    },
  });

  const handleSubmit = (data) => {
    createMutation.mutate(data);
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(formData); }}>
      {/* form fields */}
      <Button type="submit" disabled={createMutation.isPending}>
        {createMutation.isPending ? 'Creating...' : 'Create Offer'}
      </Button>
    </form>
  );
}
```

## Testing the Integration

1. **Start both servers** (backend on 8000, frontend on 3000)
2. **Register a new user** at http://localhost:3000/#/register
3. **Login** with your new credentials
4. **Create an offer/need** - Should appear in database
5. **View on map** - Should show location markers
6. **Search** - Should find items by tags
7. **Propose to help** - Should create participant record
8. **Accept and complete** - Should update TimeBank balances
9. **Leave comments** - Should appear on profiles

## Troubleshooting

### "Cannot find module" errors
Run `npm install` again to ensure all dependencies are installed

### CORS errors
Check that backend `CORS_ORIGINS` includes `http://localhost:3000`

### 401 Unauthorized on API calls
Clear localStorage and login again. Check that token is being sent in headers.

### TypeScript errors in existing components
Update import paths to use `@/` alias and ensure types match backend schemas

### Components not rendering
Check browser console for errors. Ensure all shadcn/ui components are installed.

## Architecture Decisions (Implemented)

✅ **Build Tool**: Vite (fast, modern, great DX)
✅ **State Management**: Context API for auth (simple, sufficient)  
✅ **Data Fetching**: React Query (automatic caching, refetching)
✅ **Authentication**: Login page with JWT tokens
✅ **Map Library**: Leaflet (open source, flexible)
✅ **Real-time**: Polling via React Query refetch (simple, works)
✅ **Missing Endpoint**: Added GET /api/v1/users/{id}
✅ **Backend URL**: Configured via .env (VITE_API_BASE_URL)
✅ **File Structure**: Organized by type (pages, components, lib, contexts)
✅ **TypeScript**: Moderate strictness (strict: false, but with useful checks)

## Summary

You now have a **fully configured and integrated frontend** ready to connect to your backend! 

The foundation is complete:
- ✅ Authentication system
- ✅ API client with interceptors
- ✅ React Query setup
- ✅ TypeScript types
- ✅ Route protection
- ✅ Login/Register pages
- ✅ Environment config
- ✅ New backend endpoint

**Next Step**: Migrate your existing components to use the real API instead of mock data, following the patterns shown above.
