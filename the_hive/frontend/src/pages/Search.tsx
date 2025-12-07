// SRS FR-8: Search and Discovery with Semantic Tags
// Displays search results for offers and needs filtered by tags, text, type

import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  InputAdornment,
  ToggleButton,
  ToggleButtonGroup,
  Paper,
  Divider,
} from '@mui/material'
import {
  Search as SearchIcon,
  LocalOffer as OfferIcon,
  HelpOutline as NeedIcon,
  LocationOn as LocationIcon,
  Language as RemoteIcon,
  AccessTime as TimeIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/services/api'

// Search result type from backend
interface SearchResult {
  id: number
  type: 'offer' | 'need'
  title: string
  description: string
  creator_id: number
  is_remote: boolean
  location_name?: string
  capacity: number
  accepted_count: number
  status: string
  tags: string[]
  created_at: string
}

interface SearchResponse {
  results: SearchResult[]
  total: number
  skip: number
  limit: number
}

type SearchType = 'all' | 'offer' | 'need'
type SortOrder = 'recency' | 'relevance'

/**
 * Search Component
 * 
 * Provides search functionality for offers and needs:
 * - Text search in title/description
 * - Filter by type (offer/need/all)
 * - Filter by tags
 * - Sort by recency or relevance
 * 
 * Backend API: GET /api/v1/search
 */
export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  // Get initial values from URL params
  const initialQuery = searchParams.get('query') || ''
  const initialType = (searchParams.get('type') as SearchType) || 'all'
  const initialTags = searchParams.get('tags')?.split(',').filter(Boolean) || []

  // Local state
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [searchType, setSearchType] = useState<SearchType>(initialType)
  const [selectedTags, setSelectedTags] = useState<string[]>(initialTags)
  const [sortBy, setSortBy] = useState<SortOrder>('recency')

  // Build query params for API
  const buildApiParams = () => {
    const params: Record<string, string> = {}
    
    if (searchQuery) params.query = searchQuery
    if (searchType !== 'all') params.type = searchType
    if (sortBy) params.sort_by = sortBy
    
    return params
  }

  // Fetch search results
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['search', searchQuery, searchType, selectedTags, sortBy],
    queryFn: async () => {
      const params = new URLSearchParams(buildApiParams())
      
      // Add tags as multiple params
      selectedTags.forEach(tag => params.append('tags', tag))
      
      const response = await apiClient.get<SearchResponse>(`/search?${params.toString()}`)
      return response.data
    },
    enabled: true, // Always fetch to show all results initially
  })

  // Update URL when search params change
  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('query', searchQuery)
    if (searchType !== 'all') params.set('type', searchType)
    if (selectedTags.length > 0) params.set('tags', selectedTags.join(','))
    
    setSearchParams(params, { replace: true })
  }, [searchQuery, searchType, selectedTags, setSearchParams])

  // Handle tag click - add to filter or navigate to search
  const handleTagClick = (tag: string) => {
    if (!selectedTags.includes(tag)) {
      setSelectedTags([...selectedTags, tag])
    }
  }

  // Remove tag from filter
  const handleRemoveTag = (tagToRemove: string) => {
    setSelectedTags(selectedTags.filter(tag => tag !== tagToRemove))
  }

  // Navigate to offer/need detail
  const handleResultClick = (result: SearchResult) => {
    navigate(`/${result.type}s/${result.id}`)
  }

  // Format date for display
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Search Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Search
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Find offers and needs in your community
        </Typography>
      </Box>

      {/* Search Controls */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          {/* Text Search */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search by title or description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          {/* Type Filter */}
          <Grid item xs={12} md={3}>
            <ToggleButtonGroup
              value={searchType}
              exclusive
              onChange={(_, value) => value && setSearchType(value)}
              fullWidth
              size="small"
            >
              <ToggleButton value="all">All</ToggleButton>
              <ToggleButton value="offer">Offers</ToggleButton>
              <ToggleButton value="need">Needs</ToggleButton>
            </ToggleButtonGroup>
          </Grid>

          {/* Sort Order */}
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortBy}
                label="Sort By"
                onChange={(e) => setSortBy(e.target.value as SortOrder)}
              >
                <MenuItem value="recency">Most Recent</MenuItem>
                <MenuItem value="relevance">Most Relevant</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Active Tag Filters */}
        {selectedTags.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Filtering by tags:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {selectedTags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  onDelete={() => handleRemoveTag(tag)}
                  color="primary"
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Results */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">
          Unable to load search results. Please try again.
        </Alert>
      ) : data?.results.length === 0 ? (
        <Alert severity="info">
          No results found. Try adjusting your search criteria.
        </Alert>
      ) : (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Found {data?.total || 0} result{(data?.total || 0) !== 1 ? 's' : ''}
          </Typography>

          <Grid container spacing={2}>
            {data?.results.map((result) => (
              <Grid item xs={12} md={6} key={`${result.type}-${result.id}`}>
                <Card 
                  sx={{ 
                    height: '100%',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: 4,
                    },
                  }}
                >
                  <CardActionArea onClick={() => handleResultClick(result)}>
                    <CardContent>
                      {/* Type Badge & Title */}
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                        <Chip
                          icon={result.type === 'offer' ? <OfferIcon /> : <NeedIcon />}
                          label={result.type === 'offer' ? 'Offer' : 'Need'}
                          size="small"
                          color={result.type === 'offer' ? 'success' : 'primary'}
                          sx={{ textTransform: 'capitalize' }}
                        />
                        {result.is_remote && (
                          <Chip
                            icon={<RemoteIcon />}
                            label="Remote"
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>

                      <Typography variant="h6" fontWeight={600} gutterBottom>
                        {result.title}
                      </Typography>

                      <Typography 
                        variant="body2" 
                        color="text.secondary" 
                        sx={{ 
                          mb: 2,
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}
                      >
                        {result.description}
                      </Typography>

                      <Divider sx={{ my: 1.5 }} />

                      {/* Meta Info */}
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 1.5 }}>
                        {result.location_name && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <LocationIcon fontSize="small" color="action" />
                            <Typography variant="caption" color="text.secondary">
                              {result.location_name}
                            </Typography>
                          </Box>
                        )}
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <PeopleIcon fontSize="small" color="action" />
                          <Typography variant="caption" color="text.secondary">
                            {result.accepted_count}/{result.capacity} spots
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <TimeIcon fontSize="small" color="action" />
                          <Typography variant="caption" color="text.secondary">
                            {formatDate(result.created_at)}
                          </Typography>
                        </Box>
                      </Box>

                      {/* Tags */}
                      {result.tags.length > 0 && (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {result.tags.map((tag) => (
                            <Chip
                              key={tag}
                              label={tag}
                              size="small"
                              variant="outlined"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleTagClick(tag)
                              }}
                              sx={{ 
                                cursor: 'pointer',
                                '&:hover': { 
                                  backgroundColor: 'action.hover',
                                },
                              }}
                            />
                          ))}
                        </Box>
                      )}
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}
    </Container>
  )
}
