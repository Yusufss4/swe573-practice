// SRS FR-3.1: Create Offer Form
// Allows users to create service offerings with tags, location, and capacity

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControlLabel,
  Switch,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  InputAdornment,
  IconButton,
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Close as CloseIcon,
  LocationOn as LocationIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import { useMutation } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'
import LocationPicker from '@/components/LocationPicker'
import TimeSlotPicker from '@/components/TimeSlotPicker'

interface TimeRange {
  start_time: string
  end_time: string
}

interface TimeSlot {
  date: string
  time_ranges: TimeRange[]
}

interface CreateOfferRequest {
  title: string
  description: string
  is_remote: boolean
  location_name?: string
  location_lat?: number
  location_lon?: number
  capacity?: number
  hours?: number
  tags: string[]
  available_slots?: TimeSlot[]
}

/**
 * CreateOffer Component
 * 
 * Form to create a new offer with:
 * - Title and description
 * - Remote/In-person toggle
 * - Location fields (for in-person)
 * - Capacity (optional)
 * - Tags for discovery
 * 
 * Backend API: POST /api/v1/offers/
 */
export default function CreateOffer() {
  const navigate = useNavigate()
  const { user } = useAuth()

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [isRemote, setIsRemote] = useState(true)
  const [location, setLocation] = useState<{ name: string; lat?: number; lon?: number }>({
    name: '',
  })
  const [capacity, setCapacity] = useState('3')
  const [hours, setHours] = useState('1')
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([])
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Create offer mutation
  const createMutation = useMutation({
    mutationFn: async (data: CreateOfferRequest) => {
      const response = await apiClient.post('/offers/', data)
      return response.data
    },
    onSuccess: (data) => {
      // Navigate to the newly created offer
      navigate(`/offers/${data.id}`)
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.detail || 'Failed to create offer. Please try again.'
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage))
    },
  })

  const handleAddTag = () => {
    const trimmedTag = tagInput.trim().toLowerCase()
    if (trimmedTag && !tags.includes(trimmedTag)) {
      setTags([...tags, trimmedTag])
      setTagInput('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove))
  }

  const handleTagInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTag()
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validation
    if (!title.trim()) {
      setError('Title is required')
      return
    }
    if (!description.trim()) {
      setError('Description is required')
      return
    }
    if (!isRemote && !location.name.trim()) {
      setError('Location is required for in-person offers')
      return
    }
    if (tags.length === 0) {
      setError('Please add at least one tag')
      return
    }

    const capacityNum = parseInt(capacity)
    if (isNaN(capacityNum) || capacityNum < 1) {
      setError('Capacity must be at least 1')
      return
    }

    const hoursNum = parseFloat(hours)
    if (isNaN(hoursNum) || hoursNum <= 0) {
      setError('Hours must be greater than 0')
      return
    }

    // Build request
    const requestData: CreateOfferRequest = {
      title: title.trim(),
      description: description.trim(),
      is_remote: isRemote,
      capacity: capacityNum,
      hours: hoursNum,
      tags: tags,
    }

    // Add location for in-person offers
    if (!isRemote && location.name.trim()) {
      requestData.location_name = location.name.trim()
      
      // Add coordinates if provided
      if (location.lat !== undefined && location.lon !== undefined) {
        requestData.location_lat = location.lat
        requestData.location_lon = location.lon
      }
    }

    // Add time slots if specified
    if (timeSlots.length > 0) {
      requestData.available_slots = timeSlots
    }

    createMutation.mutate(requestData)
  }

  if (!user) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="warning">
          Please log in to create an offer.
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Back Button */}
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate(-1)}
        sx={{ mb: 3 }}
      >
        Back
      </Button>

      <Card>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom fontWeight={600}>
            Create an Offer
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Share a service or skill you can provide to help others in the community.
          </Typography>

          <Divider sx={{ my: 3 }} />

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            {/* Title */}
            <TextField
              fullWidth
              required
              label="Title"
              placeholder="e.g., Web Development Tutoring, Garden Help, etc."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={createMutation.isPending}
              sx={{ mb: 3 }}
            />

            {/* Description */}
            <TextField
              fullWidth
              required
              multiline
              rows={4}
              label="Description"
              placeholder="Describe what you're offering, your experience, and what helpers can expect..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={createMutation.isPending}
              sx={{ mb: 3 }}
            />

            {/* Remote Toggle */}
            <Box sx={{ mb: 3 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={isRemote}
                    onChange={(e) => setIsRemote(e.target.checked)}
                    disabled={createMutation.isPending}
                  />
                }
                label={
                  <Box>
                    <Typography variant="body2" fontWeight={500}>
                      Remote Service
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Can this service be provided online/remotely?
                    </Typography>
                  </Box>
                }
              />
            </Box>

            {/* Location Fields (only for in-person) */}
            {!isRemote && (
              <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                  Location Details
                </Typography>
                <Typography variant="caption" color="text.secondary" gutterBottom display="block" sx={{ mb: 2 }}>
                  You can provide just a place name (e.g., "Brooklyn, NY") or use the map picker for more precision.
                  Coordinates are optional and will be rounded for privacy.
                </Typography>
                <LocationPicker
                  value={location}
                  onChange={setLocation}
                  disabled={createMutation.isPending}
                  required={!isRemote}
                />
              </Box>
            )}

            {/* Capacity */}
            <TextField
              fullWidth
              label="Capacity"
              placeholder="How many people can you help?"
              value={capacity}
              onChange={(e) => setCapacity(e.target.value)}
              disabled={createMutation.isPending}
              type="number"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <PeopleIcon />
                  </InputAdornment>
                ),
              }}
              helperText="Maximum number of people you can help with this offer"
              sx={{ mb: 3 }}
            />

            {/* Hours */}
            <TextField
              fullWidth
              required
              label="Hours Required"
              placeholder="How many TimeBank hours is this worth?"
              value={hours}
              onChange={(e) => setHours(e.target.value)}
              disabled={createMutation.isPending}
              type="number"
              inputProps={{
                min: "0.5",
                step: "0.5"
              }}
              helperText="TimeBank hours for this service (e.g., 1.0, 2.5, etc.)"
              sx={{ mb: 3 }}
            />

            {/* Tags */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                Tags *
              </Typography>
              <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                Add tags to help others discover your offer (e.g., tutoring, python, gardening)
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Add a tag and press Enter"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={handleTagInputKeyPress}
                  disabled={createMutation.isPending}
                />
                <Button
                  variant="outlined"
                  onClick={handleAddTag}
                  disabled={createMutation.isPending || !tagInput.trim()}
                  startIcon={<AddIcon />}
                >
                  Add
                </Button>
              </Box>

              {tags.length > 0 && (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {tags.map((tag) => (
                    <Chip
                      key={tag}
                      label={tag}
                      onDelete={() => handleRemoveTag(tag)}
                      deleteIcon={<CloseIcon />}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              )}
            </Box>

            {/* Time Slots */}
            <Box sx={{ mb: 3 }}>
              <TimeSlotPicker
                value={timeSlots}
                onChange={setTimeSlots}
                disabled={createMutation.isPending}
              />
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                onClick={() => navigate(-1)}
                disabled={createMutation.isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={createMutation.isPending}
                startIcon={createMutation.isPending ? <CircularProgress size={20} /> : null}
              >
                {createMutation.isPending ? 'Creating...' : 'Create Offer'}
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Container>
  )
}
