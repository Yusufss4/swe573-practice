// SRS NFR-7: Privacy-focused location picker
// Allows users to select location via map or text input without forcing exact coordinates

import { useState, useCallback } from 'react'
import {
  Box,
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  InputAdornment,
  Alert,
  ToggleButtonGroup,
  ToggleButton,
  CircularProgress,
} from '@mui/material'
import {
  LocationOn as LocationIcon,
  Map as MapIcon,
  Edit as EditIcon,
  MyLocation as MyLocationIcon,
} from '@mui/icons-material'
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix Leaflet default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface LocationData {
  name: string
  lat?: number
  lon?: number
}

interface LocationPickerProps {
  value: LocationData
  onChange: (location: LocationData) => void
  disabled?: boolean
  required?: boolean
}

// Reverse geocoding function using OpenStreetMap Nominatim
async function reverseGeocode(lat: number, lon: number): Promise<string | null> {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=14&addressdetails=1`,
      {
        headers: {
          'Accept-Language': 'en',
        },
      }
    )
    if (!response.ok) return null

    const data = await response.json()

    // Build a friendly location name from address components
    const address = data.address || {}
    const parts: string[] = []

    // Prefer neighborhood/suburb, then city district, then city
    if (address.neighbourhood) parts.push(address.neighbourhood)
    else if (address.suburb) parts.push(address.suburb)
    else if (address.district) parts.push(address.district)
    else if (address.borough) parts.push(address.borough)

    // Add city/town
    if (address.city) parts.push(address.city)
    else if (address.town) parts.push(address.town)
    else if (address.municipality) parts.push(address.municipality)
    else if (address.province) parts.push(address.province)

    // If we have parts, return them joined; otherwise use display_name
    if (parts.length > 0) {
      return parts.join(', ')
    }

    // Fallback to display_name but trim it to be more readable
    if (data.display_name) {
      const displayParts = data.display_name.split(', ')
      return displayParts.slice(0, 3).join(', ')
    }

    return null
  } catch (error) {
    console.error('Reverse geocoding failed:', error)
    return null
  }
}

// Component to handle map clicks
function LocationMarker({ position, setPosition, onLocationSelect }: { 
  position: [number, number] | null
  setPosition: (pos: [number, number]) => void
  onLocationSelect: (lat: number, lon: number) => void
}) {
  useMapEvents({
    click(e) {
      const newPos: [number, number] = [e.latlng.lat, e.latlng.lng]
      setPosition(newPos)
      onLocationSelect(e.latlng.lat, e.latlng.lng)
    },
  })

  return position === null ? null : <Marker position={position} />
}

/**
 * LocationPicker Component
 * 
 * Provides two ways to specify location:
 * 1. Text input - Just type a place name (e.g., "Brooklyn, NY")
 * 2. Map picker - Click on map to select coordinates
 * 
 * Features:
 * - Text-only input for privacy (no forced coordinates)
 * - Optional map picker for those who want precision
 * - Approximate coordinates (rounded to ~1km) for privacy
 * - Auto-fills location name via reverse geocoding when clicking on map
 */
export default function LocationPicker({ value, onChange, disabled, required }: LocationPickerProps) {
  const [mapDialogOpen, setMapDialogOpen] = useState(false)
  const [inputMode, setInputMode] = useState<'text' | 'map'>('text')
  const [tempPosition, setTempPosition] = useState<[number, number] | null>(
    value.lat && value.lon ? [value.lat, value.lon] : null
  )
  const [tempLocationName, setTempLocationName] = useState(value.name || '')
  const [isGeocoding, setIsGeocoding] = useState(false)
  const [isGettingLocation, setIsGettingLocation] = useState(false)

  // Handle reverse geocoding when map is clicked
  const handleLocationSelect = useCallback(async (lat: number, lon: number) => {
    setIsGeocoding(true)
    try {
      const locationName = await reverseGeocode(lat, lon)
      if (locationName) {
        setTempLocationName(locationName)
      }
    } finally {
      setIsGeocoding(false)
    }
  }, [])

  // Get user's current location using geolocation API
  const handleGetCurrentLocation = useCallback(() => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser')
      return
    }

    setIsGettingLocation(true)
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords
        const newPos: [number, number] = [latitude, longitude]
        setTempPosition(newPos)
        
        // Auto-fill location name
        setIsGeocoding(true)
        try {
          const locationName = await reverseGeocode(latitude, longitude)
          if (locationName) {
            setTempLocationName(locationName)
          }
        } finally {
          setIsGeocoding(false)
        }
        
        setIsGettingLocation(false)
      },
      (error) => {
        console.error('Geolocation error:', error)
        alert(`Unable to get your location: ${error.message}`)
        setIsGettingLocation(false)
      },
      {
        enableHighAccuracy: false,
        timeout: 10000,
        maximumAge: 300000, // Cache for 5 minutes
      }
    )
  }, [])

  const handleOpenMapPicker = () => {
    setInputMode('map')
    setMapDialogOpen(true)
    // Initialize temp values
    if (value.lat && value.lon) {
      setTempPosition([value.lat, value.lon])
    } else {
      // Default to Istanbul if no position set
      setTempPosition([41.0082, 28.9784])
    }
    setTempLocationName(value.name || '')
  }

  const handleSaveMapSelection = () => {
    if (tempPosition) {
      // Round to 2 decimal places (~1km precision) for privacy
      const roundedLat = Math.round(tempPosition[0] * 100) / 100
      const roundedLon = Math.round(tempPosition[1] * 100) / 100
      
      onChange({
        name: tempLocationName || `Location (${roundedLat}, ${roundedLon})`,
        lat: roundedLat,
        lon: roundedLon,
      })
    }
    setMapDialogOpen(false)
  }

  const handleCancelMapSelection = () => {
    setMapDialogOpen(false)
    setTempPosition(value.lat && value.lon ? [value.lat, value.lon] : null)
    setTempLocationName(value.name || '')
  }

  const handleTextInputChange = (newName: string) => {
    onChange({
      name: newName,
      lat: undefined,
      lon: undefined,
    })
  }

  const handleClearCoordinates = () => {
    onChange({
      name: value.name,
      lat: undefined,
      lon: undefined,
    })
  }

  return (
    <Box>
      {/* Main Input Section */}
      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
        <TextField
          fullWidth
          required={required}
          label="Location Name"
          placeholder="e.g., Kadıköy, Istanbul or Taksim Square"
          value={value.name}
          onChange={(e) => handleTextInputChange(e.target.value)}
          disabled={disabled}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <LocationIcon />
              </InputAdornment>
            ),
          }}
        />
        <Button
          variant="outlined"
          onClick={handleOpenMapPicker}
          disabled={disabled}
          startIcon={<MapIcon />}
          sx={{ minWidth: 140 }}
        >
          Pick on Map
        </Button>
      </Box>

      {/* Show coordinates if set */}
      {value.lat && value.lon && (
        <Alert 
          severity="info" 
          sx={{ mt: 1 }}
          action={
            <Button size="small" onClick={handleClearCoordinates}>
              Remove
            </Button>
          }
        >
          Map coordinates: {value.lat.toFixed(2)}, {value.lon.toFixed(2)} (approximate for privacy)
        </Alert>
      )}

      {/* Map Selection Dialog */}
      <Dialog 
        open={mapDialogOpen} 
        onClose={handleCancelMapSelection}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Select Location
          <Typography variant="body2" color="text.secondary">
            Choose how you want to specify the location
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 3, mt: 1 }}>
            <ToggleButtonGroup
              value={inputMode}
              exclusive
              onChange={(_, newMode) => newMode && setInputMode(newMode)}
              fullWidth
              size="small"
            >
              <ToggleButton value="text">
                <EditIcon sx={{ mr: 1 }} />
                Text Only
              </ToggleButton>
              <ToggleButton value="map">
                <MapIcon sx={{ mr: 1 }} />
                Map Selection
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {inputMode === 'text' ? (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                You can just type a location name without providing exact coordinates. 
                This protects your privacy and gives you flexibility.
              </Alert>
              <TextField
                fullWidth
                label="Location Name"
                placeholder="e.g., Near Galata Tower or Beşiktaş, Istanbul"
                value={tempLocationName}
                onChange={(e) => setTempLocationName(e.target.value)}
                helperText="Provide as much or as little detail as you're comfortable with"
              />
            </Box>
          ) : (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                Click on the map to select a location. The location name will be filled automatically.
              </Alert>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  fullWidth
                  label="Location Name"
                  placeholder="Click on the map to auto-fill, or type manually"
                  value={tempLocationName}
                  onChange={(e) => setTempLocationName(e.target.value)}
                  InputProps={{
                    endAdornment: isGeocoding ? (
                      <InputAdornment position="end">
                        <CircularProgress size={20} />
                      </InputAdornment>
                    ) : null,
                  }}
                  helperText={isGeocoding ? "Looking up location name..." : "Auto-filled from map click, or edit manually"}
                />
                <Button
                  variant="outlined"
                  onClick={handleGetCurrentLocation}
                  disabled={isGettingLocation || isGeocoding}
                  startIcon={isGettingLocation ? <CircularProgress size={20} /> : <MyLocationIcon />}
                  sx={{ minWidth: 180 }}
                >
                  {isGettingLocation ? 'Getting...' : 'Use My Location'}
                </Button>
              </Box>
              <Box sx={{ height: 400, borderRadius: 1, overflow: 'hidden', border: 1, borderColor: 'divider' }}>
                <MapContainer
                    center={tempPosition || [41.0082, 28.9784]}
                    zoom={12}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://carto.com/">CARTO</a> contributors'
                    url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                  />
                    <LocationMarker
                      position={tempPosition}
                      setPosition={setTempPosition}
                      onLocationSelect={handleLocationSelect}
                    />
                </MapContainer>
              </Box>
              {tempPosition && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Selected: {tempPosition[0].toFixed(4)}, {tempPosition[1].toFixed(4)} 
                  (will be rounded to {Math.round(tempPosition[0] * 100) / 100}, {Math.round(tempPosition[1] * 100) / 100})
                </Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelMapSelection}>Cancel</Button>
          <Button 
            onClick={handleSaveMapSelection} 
            variant="contained"
            disabled={inputMode === 'map' && !tempPosition}
          >
            Save Location
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
