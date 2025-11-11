// SRS FR-8 & FR-9: Interactive Map View with Offers/Needs Display
// Provides location-based browsing with filtering and search capabilities

import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
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
} from '@mui/material'
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  LocalOffer as OfferIcon,
  EventNote as NeedIcon,
  Person as PersonIcon,
  LocationOn as LocationIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon,
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
  location_lat?: number
  location_lon?: number
  location_name?: string
  tags?: Array<{ id: number; name: string }> | null
  creator?: {
    id: number
    username: string
    display_name?: string
  }
  capacity?: number
  accepted_count?: number
  status: string
  created_at: string
}

interface MapFeedResponse {
  items: MapFeedItem[]
  total: number
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
  
  // Filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState<'all' | 'offers' | 'needs'>('all')
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false)
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [distanceFilter, setDistanceFilter] = useState<number>(50) // km
  const [sortBy, setSortBy] = useState<'recent' | 'distance' | 'popularity'>('recent')
  
  // Map state
  const [mapCenter, setMapCenter] = useState<[number, number]>([40.7128, -74.0060]) // Default: NYC
  const [selectedItem, setSelectedItem] = useState<MapFeedItem | null>(null)

  // SRS FR-9: Fetch map feed data
  const { data: mapFeed, isLoading, error, refetch } = useQuery<MapFeedResponse>({
    queryKey: ['mapFeed', typeFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (typeFilter !== 'all') {
        params.append('type', typeFilter === 'offers' ? 'offer' : 'need')
      }
      
      const response = await apiClient.get<MapFeedResponse>(`/map/feed?${params.toString()}`)
      return response.data
    },
  })

  // Filter and search items locally (can be optimized to use backend search)
  const filteredItems = useMemo(() => {
    if (!mapFeed?.items) return []
    
    let items = mapFeed.items

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      items = items.filter(
        (item) =>
          item.title.toLowerCase().includes(query) ||
          (item.description && item.description.toLowerCase().includes(query)) ||
          (item.tags && item.tags.some((tag) => tag.name.toLowerCase().includes(query)))
      )
    }

    // Tag filter
    if (selectedTags.length > 0) {
      items = items.filter((item) =>
        item.tags && item.tags.some((tag) => selectedTags.includes(tag.name))
      )
    }

    // Sort
    if (sortBy === 'recent') {
      items = [...items].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
    }

    return items
  }, [mapFeed?.items, searchQuery, selectedTags, sortBy])

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
    if (item.location_lat && item.location_lon) {
      setMapCenter([item.location_lat, item.location_lon])
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
    setDistanceFilter(50)
    setSortBy('recent')
  }

  return (
    <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      {/* Top Filter Bar */}
      <Box
        sx={{
          p: 2,
          bgcolor: 'background.paper',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Container maxWidth="xl">
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            {/* Search Input */}
            <TextField
              placeholder="Search offers and needs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              size="small"
              sx={{ flexGrow: 1, minWidth: 250 }}
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

            {/* Type Filter Toggle */}
            <ToggleButtonGroup
              value={typeFilter}
              exclusive
              onChange={(_, value) => value && setTypeFilter(value)}
              size="small"
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

            {/* More Filters Button */}
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={() => setFilterDrawerOpen(true)}
              endIcon={
                selectedTags.length > 0 && (
                  <Badge badgeContent={selectedTags.length} color="primary" />
                )
              }
            >
              More Filters
            </Button>

            {/* Refresh Button */}
            <Tooltip title="Refresh map data">
              <IconButton onClick={() => refetch()} size="small">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Container>
      </Box>

      {/* Main Content Area */}
      <Box sx={{ flexGrow: 1, display: 'flex', overflow: 'hidden' }}>
        <Container maxWidth="xl" sx={{ height: '100%', py: 0 }}>
          <Grid container spacing={2} sx={{ height: '100%' }}>
            {/* Map Column */}
            <Grid item xs={12} md={7} sx={{ height: '100%', position: 'relative' }}>
              <Box sx={{ height: '100%', position: 'relative', borderRadius: 1, overflow: 'hidden' }}>
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
                    <Alert severity="error">Failed to load map data</Alert>
                  </Box>
                ) : (
                  <MapContainer
                    center={mapCenter}
                    zoom={12}
                    style={{ height: '100%', width: '100%' }}
                    scrollWheelZoom={true}
                  >
                    <TileLayer
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    <MapCenterUpdater center={mapCenter} />
                    
                    {/* Markers for filtered items */}
                    {filteredItems
                      .filter((item) => item.location_lat && item.location_lon)
                      .map((item) => (
                        <Marker
                          key={`${item.type}-${item.id}`}
                          position={[item.location_lat!, item.location_lon!]}
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
              </Box>
            </Grid>

            {/* List Column */}
            <Grid item xs={12} md={5} sx={{ height: '100%', overflow: 'auto' }}>
              <Box sx={{ pb: 2 }}>
                {/* Results Header */}
                <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6" fontWeight={600}>
                    {filteredItems.length} {filteredItems.length === 1 ? 'Result' : 'Results'}
                  </Typography>
                  {(searchQuery || selectedTags.length > 0) && (
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

                          {/* Creator Info */}
                          {item.creator && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
                              <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.main' }}>
                                <PersonIcon fontSize="small" />
                              </Avatar>
                              <Typography variant="caption" color="text.secondary">
                                {item.creator.display_name || item.creator.username}
                              </Typography>
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
            <MenuItem value="popularity">Popularity</MenuItem>
          </Select>
        </FormControl>

        {/* Distance Filter */}
        <Box sx={{ mb: 3 }}>
          <Typography gutterBottom>
            Distance: {distanceFilter === 100 ? 'Any' : `${distanceFilter} km`}
          </Typography>
          <Slider
            value={distanceFilter}
            onChange={(_, value) => setDistanceFilter(value as number)}
            min={1}
            max={100}
            marks={[
              { value: 1, label: '1km' },
              { value: 50, label: '50km' },
              { value: 100, label: 'Any' },
            ]}
          />
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
