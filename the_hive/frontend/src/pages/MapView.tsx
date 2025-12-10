// SRS FR-8 & FR-9: Interactive Map View with Offers/Needs Display
// Provides location-based browsing with filtering and search capabilities

import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Chip,
  Avatar,
  InputAdornment,
  ToggleButtonGroup,
  ToggleButton,
  IconButton,
  Drawer,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  CircularProgress,
  Alert,
  Tooltip,
  Badge,
  FormControlLabel,
  Checkbox,
  Autocomplete,
} from '@mui/material'
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  LocalOffer as OfferIcon,
  EventNote as NeedIcon,
  Person as PersonIcon,
  LocationOn as LocationIcon,
  Close as CloseIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
} from '@mui/icons-material'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/services/api'
import type { Offer, Need } from '@/types'

// Fix Leaflet default marker icons issue with webpack
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Custom marker icons for Offers (green) and Needs (blue)
const offerIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const needIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

interface MapFeedItem {
  id: number
  type: 'offer' | 'need'
  title: string
  description?: string | null
  is_remote: boolean
  approximate_lat?: number | null
  approximate_lon?: number | null
  location_name?: string | null
  tags?: Array<{ id: number; name: string }> | null
  creator?: {
    id: number
    username: string
    full_name?: string
    profile_image?: string
    profile_image_type?: string
    overall_rating?: number
  }
  accepted_participants?: Array<{
    id: number
    username: string
    profile_image?: string
    profile_image_type?: string
  }>
  capacity?: number
  accepted_count?: number
  distance_km?: number | null
}

interface MapFeedResponse {
  items: MapFeedItem[]
  total: number
}

// Avatar emoji mappings
const AVATAR_EMOJIS: Record<string, string> = {
  bee: '🐝', butterfly: '🦋', ladybug: '🐞', ant: '🐜',
  bird: '🐦', owl: '🦉', turtle: '🐢', frog: '🐸',
  rabbit: '🐰', fox: '🦊', bear: '🐻', wolf: '🐺',
  flower: '🌸', sunflower: '🌻', tree: '🌳', mushroom: '🍄',
}

// Component to handle map center updates
const MapCenterUpdater = ({ center }: { center: [number, number] }) => {
  const map = useMap()
  useEffect(() => {
    map.setView(center, map.getZoom())
  }, [center, map])
  return null
}

/**
 * SRS FR-9: Interactive Map View
 * SRS FR-8: Location-based filtering and display
 */
const MapView = () => {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  // Get initial values from URL params
  const initialTag = searchParams.get('tag') || ''
  const initialType = searchParams.get('type') as 'all' | 'offers' | 'needs' | null
  
  // Filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [tagSearchQuery, setTagSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState<'all' | 'offers' | 'needs'>(initialType || 'all')
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false)
  const [selectedTags, setSelectedTags] = useState<string[]>(initialTag ? [initialTag] : [])
  const [remoteOnly, setRemoteOnly] = useState<boolean>(false)
  const [distanceFilter, setDistanceFilter] = useState<number>(50) // km
  const [sortBy, setSortBy] = useState<'recent' | 'distance' | 'popularity' | 'rating'>('recent')
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null)
  const [locationName, setLocationName] = useState<string | null>(null)
  const [locationError, setLocationError] = useState<string | null>(null)
  
  // Map state
  const [mapCenter, setMapCenter] = useState<[number, number]>([41.0082, 28.9784]) // Default: Istanbul, Turkey
  const [selectedItem, setSelectedItem] = useState<MapFeedItem | null>(null)

  // Request user's location on mount
  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const coords: [number, number] = [position.coords.latitude, position.coords.longitude]
          setUserLocation(coords)
          setMapCenter(coords) // Center map on user's location
          setLocationError(null)
          
          // Reverse geocode to get location name
          try {
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${coords[0]}&lon=${coords[1]}&zoom=10`
            )
            const data = await response.json()
            const locationStr = data.address?.city || data.address?.town || data.address?.county || data.address?.state || 'Current Location'
            setLocationName(locationStr)
          } catch (error) {
            console.error('Error getting location name:', error)
            setLocationName('Current Location')
          }
        },
        (error) => {
          console.error('Error getting location:', error)
          setLocationError(error.message)
          // Keep default Istanbul location if permission denied
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0
        }
      )
    } else {
      setLocationError('Geolocation is not supported by your browser')
    }
  }, [])

  // Clear URL params after applying filters (keep URL clean)
  useEffect(() => {
    if (initialTag || initialType) {
      // Clear params after they've been applied to state
      setSearchParams({}, { replace: true })
    }
  }, []) // Only run on mount

  // SRS FR-9: Fetch map feed data
  const { data: mapFeed, isLoading, error, refetch } = useQuery<MapFeedResponse>({
    queryKey: ['mapFeed', typeFilter, remoteOnly, userLocation, distanceFilter, selectedTags],
    queryFn: async () => {
      const params = new URLSearchParams()

      // Add user location for distance calculation
      if (userLocation) {
        params.append('user_lat', userLocation[0].toString())
        params.append('user_lon', userLocation[1].toString())
      }

      // Add type filter
      if (typeFilter === 'offers') {
        params.append('type', 'offer')
      } else if (typeFilter === 'needs') {
        params.append('type', 'need')
      }
      // If 'all', don't add type parameter - backend will return both

      // Add remote filter
      if (remoteOnly) {
        params.append('is_remote', 'true')
      }

      // Add tags filter with semantic expansion
      if (selectedTags.length > 0) {
        params.append('tags', selectedTags.join(','))
      }
      
      const response = await apiClient.get<MapFeedResponse>(`/map/feed?${params.toString()}`)
      return response.data
    },
  })

  // Filter and search items locally (can be optimized to use backend search)
  const filteredItems = useMemo(() => {
    if (!mapFeed?.items) return []
    
    let items = mapFeed.items

    // Distance filter - only apply if user location is available and distance is not "Any"
    if (userLocation && distanceFilter < 100) {
      items = items.filter((item) => {
        if (item.is_remote) return true // Always show remote items
        if (!item.distance_km) return true // Show items without distance calculation
        return item.distance_km <= distanceFilter
      })
    }

    // Search filter (local text search - includes title, description, username, location)
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      items = items.filter(
        (item) =>
          item.title.toLowerCase().includes(query) ||
          (item.description && item.description.toLowerCase().includes(query)) ||
          (item.creator?.username && item.creator.username.toLowerCase().includes(query)) ||
          (item.creator?.full_name && item.creator.full_name.toLowerCase().includes(query)) ||
          (item.location_name && item.location_name.toLowerCase().includes(query)) ||
          (item.tags && item.tags.some((tag) => tag.name.toLowerCase().includes(query)))
      )
    }

    // Tag filter is now handled by backend with semantic expansion
    // No need for local filtering when selectedTags is set

    // Sort
    if (sortBy === 'recent') {
      items = [...items].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
    } else if (sortBy === 'distance' && userLocation) {
      items = [...items].sort((a, b) => {
        // Remote items go to end
        if (a.is_remote && !b.is_remote) return 1
        if (!a.is_remote && b.is_remote) return -1
        // Sort by distance
        const distA = a.distance_km ?? Infinity
        const distB = b.distance_km ?? Infinity
        return distA - distB
      })
    } else if (sortBy === 'rating') {
      items = [...items].sort((a, b) => {
        const ratingA = a.creator?.overall_rating ?? 0
        const ratingB = b.creator?.overall_rating ?? 0
        return ratingB - ratingA // Higher ratings first
      })
    }

    return items
  }, [mapFeed?.items, searchQuery, selectedTags, sortBy, distanceFilter, userLocation])

  // Extract all unique tags from items
  const availableTags = useMemo(() => {
    if (!mapFeed?.items) return []
    const tagSet = new Set<string>()
    mapFeed.items.forEach((item) => {
      if (item.tags) {
        item.tags.forEach((tag) => tagSet.add(tag.name))
      }
    })
    return Array.from(tagSet).sort()
  }, [mapFeed?.items])

  const handleItemClick = (item: MapFeedItem) => {
    // Navigate to detail page when card is clicked
    if (item.type === 'offer') {
      navigate(`/offers/${item.id}`)
    } else {
      navigate(`/needs/${item.id}`)
    }
  }

  const handleMarkerClick = (item: MapFeedItem) => {
    // Only highlight and center map when marker is clicked
    setSelectedItem(item)
    if (item.approximate_lat && item.approximate_lon) {
      setMapCenter([item.approximate_lat, item.approximate_lon])
    }
  }

  const handleViewDetails = (item: MapFeedItem) => {
    if (item.type === 'offer') {
      navigate(`/offers/${item.id}`)
    } else {
      navigate(`/needs/${item.id}`)
    }
  }

  const handleClearFilters = () => {
    setSearchQuery('')
    setTypeFilter('all')
    setSelectedTags([])
    setRemoteOnly(false)
    setDistanceFilter(50)
    setSortBy('recent')
  }

  return (
    <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      {/* Top Filter Bar */}
      <Box sx={{ p: 2 }}>
        <Container maxWidth={false} sx={{ px: 2 }}>
          <Card sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            {/* Search Input */}
            <TextField
              placeholder="Search by title, user or location..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              size="small"
              sx={{ flexGrow: 1, minWidth: 200 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
                endAdornment: searchQuery && (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => setSearchQuery('')}>
                      <CloseIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            {/* Tag Search with Autocomplete - Supports prefix matching + semantic expansion */}
            <Autocomplete
              freeSolo
              size="small"
              options={availableTags}
              value={null}
              inputValue={tagSearchQuery}
              onInputChange={(_, newValue) => setTagSearchQuery(newValue)}
              onChange={(_, value) => {
                if (value && typeof value === 'string' && !selectedTags.includes(value)) {
                  setSelectedTags([...selectedTags, value])
                  setTagSearchQuery('')
                }
              }}
              sx={{ minWidth: 200 }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder="Search by tag..."
                />
              )}
            />

            {/* Type Filter Toggle */}
            <ToggleButtonGroup
              value={typeFilter}
              exclusive
              onChange={(_, value) => value && setTypeFilter(value)}
              size="small"
              sx={{ '& .MuiToggleButton-root': { textTransform: 'none' } }}
            >
              <ToggleButton value="all">All</ToggleButton>
              <ToggleButton value="offers">
                <OfferIcon sx={{ mr: 0.5, fontSize: 18 }} />
                Offers
              </ToggleButton>
              <ToggleButton value="needs">
                <NeedIcon sx={{ mr: 0.5, fontSize: 18 }} />
                Needs
              </ToggleButton>
            </ToggleButtonGroup>

            {/* Remote/Not Remote Toggle */}
            <ToggleButton
              value="remote"
              selected={remoteOnly}
              onChange={() => setRemoteOnly(!remoteOnly)}
              size="small"
              sx={{ textTransform: 'none' }}
            >
              Remote
            </ToggleButton>

            {/* More Filters Button */}
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={() => setFilterDrawerOpen(true)}
              sx={{ minHeight: 40 }}
              endIcon={
                selectedTags.length > 0 && (
                  <Badge badgeContent={selectedTags.length} color="primary" />
                )
              }
            >
              More Filters
            </Button>

            {/* Location Status - Square Box */}
            {locationError && (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  px: 2,
                  py: 1,
                  border: 1,
                  borderColor: 'warning.main',
                  borderRadius: 1,
                  bgcolor: 'warning.lighter',
                  minHeight: 40,
                }}
              >
                <LocationIcon color="warning" fontSize="small" />
                <Typography variant="body2" color="warning.main">
                  Location unavailable
                </Typography>
              </Box>
            )}
            {userLocation && !locationError && (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  px: 2,
                  py: 1,
                  border: 1,
                  borderColor: 'success.main',
                  borderRadius: 1,
                  bgcolor: 'success.lighter',
                  minHeight: 40,
                }}
              >
                <LocationIcon color="success" fontSize="small" />
                <Typography variant="body2" color="success.main">
                  {locationName || 'Loading location...'}
                </Typography>
              </Box>
            )}
          </Box>
          </Card>
        </Container>
      </Box>

      {/* Main Content Area */}
      <Box sx={{ flexGrow: 1, display: 'flex', overflow: 'hidden', pt: 2 }}>
        <Container maxWidth={false} sx={{ height: '100%', py: 0, px: 2 }}>
          <Grid container spacing={2} sx={{ height: '100%' }}>
            {/* Map Column */}
            <Grid item xs={12} md={7} sx={{ height: '100%', position: 'relative' }}>
              <Card sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
                {isLoading ? (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      height: '100%',
                      bgcolor: 'grey.100',
                    }}
                  >
                    <CircularProgress />
                  </Box>
                ) : error ? (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      height: '100%',
                      p: 2,
                    }}
                  >
                    <Alert severity="error">Unable to load map data. Please try again.</Alert>
                  </Box>
                ) : (
                  <MapContainer
                    center={mapCenter}
                    zoom={12}
                    style={{ height: '100%', width: '100%' }}
                    scrollWheelZoom={true}
                  >
                    <TileLayer
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
                      url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                      subdomains="abcd"
                      maxZoom={20}
                    />
                    <MapCenterUpdater center={mapCenter} />
                    
                    {/* Markers for filtered items */}
                    {filteredItems
                          .filter((item) => item.approximate_lat && item.approximate_lon)
                      .map((item) => (
                        <Marker
                          key={`${item.type}-${item.id}`}
                          position={[item.approximate_lat!, item.approximate_lon!]}
                          icon={item.type === 'offer' ? offerIcon : needIcon}
                          eventHandlers={{
                            click: () => handleMarkerClick(item),
                          }}
                        >
                        <Popup>
                          <Box sx={{ minWidth: 200 }}>
                            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                              {item.title}
                            </Typography>
                            <Chip
                              label={item.type === 'offer' ? 'Offer' : 'Need'}
                              size="small"
                              color={item.type === 'offer' ? 'success' : 'info'}
                              sx={{ mb: 1 }}
                            />
                            {item.description && (
                              <Typography variant="body2" color="text.secondary" paragraph>
                                {item.description.substring(0, 100)}
                                {item.description.length > 100 ? '...' : ''}
                              </Typography>
                            )}
                            <Button
                              size="small"
                              variant="contained"
                              fullWidth
                              onClick={() => handleViewDetails(item)}
                            >
                              View Details
                            </Button>
                          </Box>
                        </Popup>
                      </Marker>
                    ))}
                  </MapContainer>
                )}

                {/* Map Legend */}
                <Box
                  sx={{
                    position: 'absolute',
                    bottom: 16,
                    left: 16,
                    bgcolor: 'white',
                    p: 1.5,
                    borderRadius: 1,
                    boxShadow: 2,
                    zIndex: 1000,
                  }}
                >
                  <Typography variant="caption" fontWeight={600} display="block" mb={0.5}>
                    Legend
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          bgcolor: '#4CAF50',
                        }}
                      />
                      <Typography variant="caption">Offers</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          bgcolor: '#2196F3',
                        }}
                      />
                      <Typography variant="caption">Needs</Typography>
                    </Box>
                  </Box>
                </Box>
              </Card>
            </Grid>

            {/* List Column */}
            <Grid item xs={12} md={5} sx={{ height: '100%', overflow: 'auto' }}>
              <Box sx={{ pb: 2 }}>
                {/* Results Header */}
                <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6" fontWeight={600}>
                    {filteredItems.length} {filteredItems.length === 1 ? 'Result' : 'Results'}
                  </Typography>
                  {(searchQuery || selectedTags.length > 0 || remoteOnly) && (
                    <Button size="small" onClick={handleClearFilters}>
                      Clear Filters
                    </Button>
                  )}
                </Box>

                {/* Active Tags */}
                {selectedTags.length > 0 && (
                  <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {selectedTags.map((tag) => (
                      <Chip
                        key={tag}
                        label={tag}
                        size="small"
                        onDelete={() =>
                          setSelectedTags(selectedTags.filter((t) => t !== tag))
                        }
                      />
                    ))}
                  </Box>
                )}

                {/* Item Cards */}
                {isLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : filteredItems.length === 0 ? (
                  <Alert severity="info">
                    No {typeFilter === 'all' ? 'items' : typeFilter} found matching your criteria.
                  </Alert>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {filteredItems.map((item) => (
                      <Card
                        key={`${item.type}-${item.id}`}
                        sx={{
                          cursor: 'pointer',
                          border: selectedItem?.id === item.id ? 2 : 1,
                          borderColor:
                            selectedItem?.id === item.id ? 'primary.main' : 'divider',
                          '&:hover': {
                            boxShadow: 3,
                          },
                        }}
                        onClick={() => handleItemClick(item)}
                      >
                        <CardContent>
                          {/* Header with Type Badge */}
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Chip
                              icon={item.type === 'offer' ? <OfferIcon /> : <NeedIcon />}
                              label={item.type === 'offer' ? 'Offer' : 'Need'}
                              size="small"
                              color={item.type === 'offer' ? 'success' : 'info'}
                            />
                            {item.capacity && (
                              <Chip
                                label={`${item.accepted_count || 0}/${item.capacity}`}
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </Box>

                          {/* Title */}
                          <Typography variant="h6" gutterBottom fontWeight={600}>
                            {item.title}
                          </Typography>

                          {/* Description */}
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{
                              mb: 1,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                            }}
                          >
                            {item.description || 'No description available'}
                          </Typography>

                          {/* Location */}
                          {item.location_name && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                              <LocationIcon fontSize="small" color="action" />
                              <Typography variant="caption" color="text.secondary">
                                {item.location_name}
                              </Typography>
                            </Box>
                          )}

                          {/* Tags */}
                          {item.tags && item.tags.length > 0 && (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                              {item.tags.slice(0, 3).map((tag) => (
                                <Chip key={tag.id} label={tag.name} size="small" variant="outlined" />
                              ))}
                              {item.tags.length > 3 && (
                                <Chip
                                  label={`+${item.tags.length - 3}`}
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                            </Box>
                          )}

                          {/* Creator Info with Accepted Participants on Right */}
                          {item.creator && (
                            <Box sx={{ mt: 2, mb: 1 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
                                {/* Creator (Left) */}
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Avatar 
                                    sx={{ 
                                      width: 28, 
                                      height: 28, 
                                      bgcolor: 'primary.main',
                                      fontSize: '1rem'
                                    }}
                                  >
                                    {item.creator.profile_image_type === 'preset' && item.creator.profile_image
                                      ? AVATAR_EMOJIS[item.creator.profile_image] || item.creator.profile_image
                                      : item.creator.username.charAt(0).toUpperCase()}
                                  </Avatar>
                                  <Box>
                                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                      @{item.creator.username}
                                    </Typography>
                                    {item.creator.overall_rating !== undefined && item.creator.overall_rating !== null && (
                                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                        <StarIcon sx={{ fontSize: 14, color: 'warning.main' }} />
                                        <Typography variant="caption" fontWeight={600}>
                                          {item.creator.overall_rating.toFixed(1)}
                                        </Typography>
                                      </Box>
                                    )}
                                  </Box>
                                </Box>

                                {/* Accepted Participants (Right) */}
                                {item.accepted_participants && item.accepted_participants.length > 0 && (
                                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                    {item.accepted_participants.map((participant) => (
                                      <Tooltip key={participant.id} title={`@${participant.username}`}>
                                        <Avatar
                                          sx={{
                                            width: 24,
                                            height: 24,
                                            fontSize: '0.75rem',
                                            bgcolor: 'secondary.main'
                                          }}
                                        >
                                          {participant.profile_image_type === 'preset' && participant.profile_image
                                            ? AVATAR_EMOJIS[participant.profile_image] || participant.profile_image
                                            : participant.username.charAt(0).toUpperCase()}
                                        </Avatar>
                                      </Tooltip>
                                    ))}
                                  </Box>
                                )}
                              </Box>
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </Box>
                )}
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* More Filters Drawer */}
      <Drawer
        anchor="right"
        open={filterDrawerOpen}
        onClose={() => setFilterDrawerOpen(false)}
        PaperProps={{
          sx: { width: { xs: '100%', sm: 400 }, p: 3 },
        }}
      >
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" fontWeight={600}>
            Filters
          </Typography>
          <IconButton onClick={() => setFilterDrawerOpen(false)}>
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Sort By */}
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Sort By</InputLabel>
          <Select
            value={sortBy}
            label="Sort By"
            onChange={(e) => setSortBy(e.target.value as any)}
          >
            <MenuItem value="recent">Most Recent</MenuItem>
            <MenuItem value="distance">Distance</MenuItem>
            <MenuItem value="rating">Rating</MenuItem>
            <MenuItem value="popularity">Popularity</MenuItem>
          </Select>
        </FormControl>

        {/* Distance Filter */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Typography gutterBottom>
              Distance: {distanceFilter === 100 ? 'Any' : `${distanceFilter} km`}
            </Typography>
            {!userLocation && (
              <Chip
                icon={<LocationIcon />}
                label="Requires location"
                size="small"
                color="warning"
                variant="outlined"
              />
            )}
          </Box>
          <Slider
            value={distanceFilter}
            onChange={(_, value) => setDistanceFilter(value as number)}
            min={1}
            max={100}
            disabled={!userLocation}
            marks={[
              { value: 1, label: '1km' },
              { value: 50, label: '50km' },
              { value: 100, label: 'Any' },
            ]}
          />
          {!userLocation && (
            <Typography variant="caption" color="text.secondary">
              Enable location permissions to filter by distance
            </Typography>
          )}
        </Box>

        {/* Tag Filter */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            Tags
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {availableTags.map((tag) => (
              <Chip
                key={tag}
                label={tag}
                size="small"
                color={selectedTags.includes(tag) ? 'primary' : 'default'}
                onClick={() => {
                  if (selectedTags.includes(tag)) {
                    setSelectedTags(selectedTags.filter((t) => t !== tag))
                  } else {
                    setSelectedTags([...selectedTags, tag])
                  }
                }}
              />
            ))}
            {availableTags.length === 0 && (
              <Typography variant="body2" color="text.secondary">
                No tags available
              </Typography>
            )}
          </Box>
        </Box>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button fullWidth variant="outlined" onClick={handleClearFilters}>
            Clear All
          </Button>
          <Button
            fullWidth
            variant="contained"
            onClick={() => setFilterDrawerOpen(false)}
          >
            Apply
          </Button>
        </Box>
      </Drawer>
    </Box>
  )
}

export default MapView
