# 🚀 Frontend-Backend Integration Guide

## What You Have Now

✅ **Backend APIs Ready** (http://localhost:8000/docs)
- Authentication (`/api/v1/auth/`)
- Users (`/api/v1/users/{id}`)
- Offers (`/api/v1/offers/`)
- Needs (`/api/v1/needs/`)
- Participants (`/api/v1/participants/`)
- Comments (`/api/v1/comments/`)
- Search, Map, Dashboard, Forum

✅ **Frontend Infrastructure Ready**
- API client configured (`src/lib/api.ts`)
- Authentication working (login/register)
- React Query for data fetching
- TypeScript types match backend

✅ **First Real Component Created**
- `src/pages/Dashboard.tsx` - Shows real offers & needs from API

## 🎯 What You Should See NOW

Open http://localhost:3000 and you'll see:

### 1. After Login:
```
┌────────────────────────────────────────┐
│  The Hive          user    Balance: 5h │
│                            [Logout]     │
├────────────────────────────────────────┤
│  Your Balance  │ Active Offers │ Needs │
│      5h        │       0       │   0   │
├────────────────────────────────────────┤
│  Available Offers                      │
│  [No offers available yet]             │
│                                        │
│  Help Needed                           │
│  [No needs posted yet]                 │
└────────────────────────────────────────┘
```

The dashboard is **pulling real data from your backend**!

## 📋 Complete Integration Roadmap

### ✅ Phase 1: DONE - Basic Setup
- [x] Backend APIs running
- [x] Frontend connected
- [x] Authentication working
- [x] Dashboard showing real data

### 🔄 Phase 2: Create Offers & Needs (Next Step)

**Create a form to add offers/needs to the database:**

```typescript
// Example: Create Offer Button
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { offersApi } from '@/lib/api';

const createMutation = useMutation({
  mutationFn: offersApi.create,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['offers'] });
    toast.success('Offer created!');
  },
});

// Usage
createMutation.mutate({
  title: "Help with gardening",
  description: "Need help planting flowers",
  hours_estimated: 2,
  capacity: 1,
  is_remote: false,
  tags: ["gardening", "outdoor"]
});
```

### 📝 Phase 3: Detail Pages

**Show individual offer/need details:**
- View offer/need by ID
- Show participants
- Propose to help
- Accept proposals

### 🤝 Phase 4: Handshake Workflow

**Implement the complete exchange flow:**
1. User creates a Need
2. Another user proposes to help
3. Creator accepts the proposal (specifies hours)
4. Both complete the exchange
5. TimeBank balances update
6. Users leave comments for each other

### 🗺️ Phase 5: Map & Search

**Add map view and search:**
- Show offers/needs on a map (Leaflet)
- Search by tags, location, keywords
- Filter by remote/local

## 🛠️ How to Test Integration Right Now

### Test 1: See Empty Dashboard
```bash
# 1. Open browser
http://localhost:3000

# 2. Login (or register first)
# 3. You should see dashboard with 0 offers, 0 needs
```

### Test 2: Create Data via Backend API
```bash
# Option A: Use Swagger UI
open http://localhost:8000/docs

# Option B: Use curl
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@test.com",
    "username": "alice",
    "password": "password123",
    "timezone": "UTC"
  }'

# Get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=password123"

# Create an offer (use the token from above)
curl -X POST http://localhost:8000/api/v1/offers/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Guitar Lessons",
    "description": "I can teach basic guitar",
    "hours_estimated": 2,
    "capacity": 3,
    "is_remote": true,
    "tags": ["music", "teaching"]
  }'
```

### Test 3: See Data in Frontend
```bash
# Refresh http://localhost:3000
# You should now see:
# - Active Offers: 1
# - A card showing "Guitar Lessons"
```

## 🎨 Next Steps (What to Build)

### Immediate (1-2 hours):
1. **Create Offer/Need Form**
   - Add a "+" button to dashboard
   - Modal with form fields
   - Submit to API
   - Refresh list automatically

2. **Detail Page**
   - Click on offer/need card
   - Show full details
   - Show participants
   - "Propose to Help" button

### Short Term (2-4 hours):
3. **Participant Management**
   - View proposals
   - Accept/reject proposals
   - Complete exchanges

4. **User Profile**
   - View user info
   - Show comments/ratings
   - Transaction history

### Medium Term (4-8 hours):
5. **Search & Filters**
   - Search bar
   - Tag filters
   - Location filters

6. **Map View**
   - Show items on map
   - Click markers for details

7. **Comments/Ratings**
   - Leave feedback
   - View ratings

## 📖 Code Patterns to Follow

### Pattern 1: Fetching Data (Read)
```typescript
import { useQuery } from '@tanstack/react-query';
import { offersApi } from '@/lib/api';

const { data, isLoading, error } = useQuery({
  queryKey: ['offers'],
  queryFn: () => offersApi.list(),
});

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage />;
return <div>{data.map(...)}</div>;
```

### Pattern 2: Creating Data (Write)
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { offersApi } from '@/lib/api';

const queryClient = useQueryClient();

const mutation = useMutation({
  mutationFn: offersApi.create,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['offers'] });
  },
});

// In your form submit:
mutation.mutate(formData);
```

### Pattern 3: Getting Current User
```typescript
import { useAuth } from '@/contexts/AuthContext';

const { user, refreshUser } = useAuth();

// user has: id, username, email, balance, role, etc.
```

## 🐛 Common Issues & Solutions

### Issue 1: "401 Unauthorized"
**Cause:** Token expired or not sent
**Fix:** 
```javascript
// Check token exists
localStorage.getItem('auth_token')

// If missing, logout and login again
```

### Issue 2: CORS Error
**Cause:** Backend not allowing frontend origin
**Fix:** Already configured in docker-compose.yml:
```yaml
CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://frontend
```

### Issue 3: Data Not Showing
**Cause:** Cache not invalidated
**Fix:**
```typescript
queryClient.invalidateQueries({ queryKey: ['offers'] });
```

## 📊 Testing the Golden Path

Follow the test in `tests/test_golden_path_need.py` to verify:

1. **Alice creates a need** → POST `/api/v1/needs/`
2. **Bob searches** → GET `/api/v1/search/?tags=gardening`
3. **Bob proposes** → POST `/api/v1/participants/needs/{id}`
4. **Alice accepts** → POST `/api/v1/participants/needs/{id}/accept`
5. **Exchange completes** → POST `/api/v1/participants/exchange/{id}/complete`
6. **Balances update** → Alice: 2h gained, Bob: 2h spent
7. **Mutual comments** → POST `/api/v1/comments`

**Now build a UI for each of these steps!**

## 🎯 Summary

**What Works:**
- ✅ Login/Register/Logout
- ✅ Dashboard showing real offers/needs
- ✅ TimeBank balance display
- ✅ API client configured
- ✅ Hot reload for development

**What to Build Next:**
- ⏳ Create offer/need form
- ⏳ Detail pages
- ⏳ Handshake workflow
- ⏳ Search & filters
- ⏳ Map view
- ⏳ Comments & ratings

**Start Here:**
1. Test the dashboard (http://localhost:3000)
2. Create some offers via API docs (http://localhost:8000/docs)
3. See them appear in your frontend!
4. Build the create form next

🚀 **You're now ready to build the full application!**
