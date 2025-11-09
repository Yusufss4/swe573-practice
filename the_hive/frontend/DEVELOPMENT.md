# The Hive - Frontend Development Guide

## Quick Reference

### Component Creation Pattern

```tsx
// SRS FR-X: Brief description
import { /* MUI components */ } from '@mui/material'
import { /* hooks */ } from 'react'
import { /* types */ } from '@/types'

interface ComponentProps {
  // Props definition
}

const ComponentName: React.FC<ComponentProps> = ({ prop1, prop2 }) => {
  // Component logic
  
  return (
    // JSX
  )
}

export default ComponentName
```

### API Service Pattern

```ts
// SRS FR-X: Service description
import apiClient from './api'
import type { /* types */ } from '@/types'

export const fetchItems = async (): Promise<Item[]> => {
  const response = await apiClient.get<Item[]>('/items')
  return response.data
}

export const createItem = async (data: CreateItemRequest): Promise<Item> => {
  const response = await apiClient.post<Item>('/items', data)
  return response.data
}
```

### React Query Hook Pattern

```ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as itemsService from '@/services/items'

export const useItems = () => {
  return useQuery({
    queryKey: ['items'],
    queryFn: itemsService.fetchItems,
  })
}

export const useCreateItem = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: itemsService.createItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })
}
```

## Key Concepts

### Authentication Flow

1. User submits credentials
2. `AuthContext` calls `authService.login()`
3. Service stores JWT in localStorage
4. Axios interceptor attaches token to requests
5. On 401, user is redirected to login

### SRS Traceability

Every file should have SRS comments:
```ts
// SRS FR-7.2: Provider gains hours, requester loses hours
// SRS NFR-7: Location data must be approximate
```

### Type Safety

Always import types from `@/types`:
```ts
import type { User, Offer, Need } from '@/types'
```

### Error Handling

```ts
try {
  const data = await apiClient.get('/endpoint')
} catch (error) {
  // Error is formatted by axios interceptor
  console.error(error.message)
  // Show user-friendly error
}
```

## File Naming Conventions

- Components: `PascalCase.tsx`
- Services: `camelCase.ts`
- Utilities: `camelCase.ts`
- Types: `index.ts` (default export)

## Import Aliases

Use path aliases for clean imports:
```ts
import Layout from '@/components/Layout'
import { useAuth } from '@/contexts/AuthContext'
import * as authService from '@/services/auth'
import type { User } from '@/types'
import config from '@/utils/config'
```

## Testing (Future)

Structure:
```
tests/
├── unit/
│   ├── components/
│   ├── services/
│   └── utils/
└── integration/
    └── flows/
```

## Deployment

### Development
```bash
docker-compose up
```

### Production Build
```bash
npm run build
# Outputs to dist/
```

### Production Docker
```bash
docker build --target production -t the-hive-frontend .
docker run -p 80:80 the-hive-frontend
```
