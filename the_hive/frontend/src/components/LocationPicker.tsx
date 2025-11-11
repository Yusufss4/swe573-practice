// SRS NFR-7: Privacy-focused location picker
// Allows users to select location via map or text input without forcing exact coordinates

import { useState } from 'react'
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
} from '@mui/material'
import {
  LocationOn as LocationIcon,
  Map as MapIcon,
  Edit as EditIcon,
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

// Component to handle map clicks
function LocationMarker({ position, setPosition }: { 
  position: [number, number] | null
  setPosition: (pos: [number, number]) => void 
}) {
  useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng])
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
 */
export default function LocationPicker({ value, onChange, disabled, required }: LocationPickerProps) {
  const [mapDialogOpen, setMapDialogOpen] = useState(false)
  const [inputMode, setInputMode] = useState<'text' | 'map'>('text')
  const [tempPosition, setTempPosition] = useState<[number, number] | null>(
    value.lat && value.lon ? [value.lat, value.lon] : null
  )
  const [tempLocationName, setTempLocationName] = useState(value.name || '')

  const handleOpenMapPicker = () => {
    setInputMode('map')
    setMapDialogOpen(true)
    // Initialize temp values
    if (value.lat && value.lon) {
      setTempPosition([value.lat, value.lon])
    } else {
      // Default to NYC if no position set
      setTempPosition([40.7128, -74.0060])
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
          placeholder="e.g., Brooklyn, NY or Downtown Seattle"
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
                placeholder="e.g., Near Central Park, Manhattan or Portland, OR"
                value={tempLocationName}
                onChange={(e) => setTempLocationName(e.target.value)}
                helperText="Provide as much or as little detail as you're comfortable with"
              />
            </Box>
          ) : (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                Click on the map to select a location. Coordinates will be rounded to ~1km precision for privacy.
              </Alert>
              <TextField
                fullWidth
                label="Location Name (Optional)"
                placeholder="Give this location a friendly name"
                value={tempLocationName}
                onChange={(e) => setTempLocationName(e.target.value)}
                sx={{ mb: 2 }}
              />
              <Box sx={{ height: 400, borderRadius: 1, overflow: 'hidden', border: 1, borderColor: 'divider' }}>
                <MapContainer
                  center={tempPosition || [40.7128, -74.0060]}
                  zoom={10}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <LocationMarker position={tempPosition} setPosition={setTempPosition} />
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
