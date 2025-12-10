// SRS FR-15: Create Forum Topic
// Create a new discussion or event

import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Chip,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  InputLabel,
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Forum as ForumIcon,
  Event as EventIcon,
  Add as AddIcon,
} from '@mui/icons-material'
import { useMutation } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'
import LocationPicker from '@/components/LocationPicker'

export default function CreateForumTopic() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { isAuthenticated } = useAuth()

  // Get initial type from URL
  const initialType = searchParams.get('type') === 'event' ? 'event' : 'discussion'

  // Form state
  const [topicType, setTopicType] = useState<'discussion' | 'event'>(initialType)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [tagInput, setTagInput] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [eventStartDate, setEventStartDate] = useState('')
  const [eventStartTime, setEventStartTime] = useState('')
  const [eventEndDate, setEventEndDate] = useState('')
  const [eventEndTime, setEventEndTime] = useState('')
  const [eventLocation, setEventLocation] = useState<{
    name: string
    lat?: number
    lon?: number
  }>({ name: '' })

  // Generate time options (24-hour format, 30-minute intervals)
  const timeOptions = Array.from({ length: 48 }, (_, i) => {
    const hour = Math.floor(i / 2)
    const minute = i % 2 === 0 ? '00' : '30'
    return `${hour}:${minute}`
  })

  // Validation errors
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Create topic mutation
  const createTopicMutation = useMutation({
    mutationFn: async () => {
      const payload: Record<string, unknown> = {
        topic_type: topicType,
        title: title.trim(),
        content: content.trim(),
        tags,
      }

      if (topicType === 'event') {
        if (eventStartDate && eventStartTime) {
          const [hour, minute] = eventStartTime.split(':')
          const startDateTime = `${eventStartDate}T${hour.padStart(2, '0')}:${minute}:00`
          payload.event_start_time = new Date(startDateTime).toISOString()
        }
        if (eventEndDate && eventEndTime) {
          const [hour, minute] = eventEndTime.split(':')
          const endDateTime = `${eventEndDate}T${hour.padStart(2, '0')}:${minute}:00`
          payload.event_end_time = new Date(endDateTime).toISOString()
        }
        if (eventLocation.name.trim()) {
          payload.event_location = eventLocation.name.trim()
          if (eventLocation.lat && eventLocation.lon) {
            payload.event_location_lat = eventLocation.lat
            payload.event_location_lon = eventLocation.lon
          }
        }
      }

      const response = await apiClient.post('/forum/topics', payload)
      return response.data
    },
    onSuccess: (data) => {
      navigate(`/forum/topic/${data.id}`)
    },
  })

  // Handle tag input
  const handleAddTag = () => {
    const tag = tagInput.trim().toLowerCase()
    if (tag && !tags.includes(tag) && tags.length < 10) {
      setTags([...tags, tag])
      setTagInput('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove))
  }

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTag()
    }
  }

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!title.trim()) {
      newErrors.title = 'Title is required'
    } else if (title.trim().length < 3) {
      newErrors.title = 'Title must be at least 3 characters'
    } else if (title.trim().length > 200) {
      newErrors.title = 'Title must be less than 200 characters'
    }

    if (!content.trim()) {
      newErrors.content = 'Content is required'
    } else if (content.trim().length < 10) {
      newErrors.content = 'Content must be at least 10 characters'
    } else if (content.trim().length > 5000) {
      newErrors.content = 'Content must be less than 5000 characters'
    }

    if (topicType === 'event' && !eventStartDate) {
      newErrors.eventStartDate = 'Event start date is required'
    }

    if (topicType === 'event' && !eventStartTime) {
      newErrors.eventStartTime = 'Event start time is required'
    }

    if (eventEndDate && eventEndTime && eventStartDate && eventStartTime) {
      const [startHour, startMinute] = eventStartTime.split(':')
      const [endHour, endMinute] = eventEndTime.split(':')
      const startDateTime = new Date(`${eventStartDate}T${startHour.padStart(2, '0')}:${startMinute}:00`)
      const endDateTime = new Date(`${eventEndDate}T${endHour.padStart(2, '0')}:${endMinute}:00`)
      if (endDateTime <= startDateTime) {
        newErrors.eventEndTime = 'End time must be after start time'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // Handle submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (validateForm()) {
      createTopicMutation.mutate()
    }
  }

  // Redirect if not authenticated
  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="warning" sx={{ mb: 2 }}>
          Please log in to create a forum topic.
        </Alert>
        <Button onClick={() => navigate('/login')}>Go to Login</Button>
      </Container>
    )
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Back button */}
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/forum')}
        sx={{ mb: 3 }}
      >
        Back to Forum
      </Button>

      {/* Header */}
      <Typography variant="h4" gutterBottom fontWeight={700}>
        Create New {topicType === 'event' ? 'Event' : 'Discussion'}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        {topicType === 'event'
          ? 'Share an upcoming community event with date, time, and location'
          : 'Start a conversation with the community'}
      </Typography>

      <Card>
        <CardContent sx={{ p: 4 }}>
          <form onSubmit={handleSubmit}>
            {/* Topic Type */}
            <FormControl component="fieldset" sx={{ mb: 3 }}>
              <FormLabel component="legend">Topic Type</FormLabel>
              <RadioGroup
                row
                value={topicType}
                onChange={(e) => setTopicType(e.target.value as 'discussion' | 'event')}
              >
                <FormControlLabel
                  value="discussion"
                  control={<Radio />}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <ForumIcon fontSize="small" />
                      Discussion
                    </Box>
                  }
                />
                <FormControlLabel
                  value="event"
                  control={<Radio />}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <EventIcon fontSize="small" />
                      Event
                    </Box>
                  }
                />
              </RadioGroup>
            </FormControl>

            {/* Title */}
            <TextField
              fullWidth
              label="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              error={!!errors.title}
              helperText={errors.title || `${title.length}/200 characters`}
              sx={{ mb: 3 }}
              required
            />

            {/* Content */}
            <TextField
              fullWidth
              multiline
              rows={6}
              label="Content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              error={!!errors.content}
              helperText={errors.content || `${content.length}/5000 characters`}
              sx={{ mb: 3 }}
              required
            />

            {/* Event-specific fields */}
            {topicType === 'event' && (
              <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Event Details
                </Typography>

                {/* Start Date and Time */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Start Date & Time *
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <TextField
                      type="date"
                      value={eventStartDate}
                      onChange={(e) => setEventStartDate(e.target.value)}
                      error={!!errors.eventStartDate}
                      helperText={errors.eventStartDate}
                      InputLabelProps={{ shrink: true }}
                      sx={{ minWidth: 180 }}
                      required
                    />
                    <FormControl sx={{ minWidth: 120 }} error={!!errors.eventStartTime} required>
                      <InputLabel>Time</InputLabel>
                      <Select
                        value={eventStartTime}
                        onChange={(e) => setEventStartTime(e.target.value)}
                        label="Time"
                      >
                        {timeOptions.map((time) => (
                          <MenuItem key={time} value={time}>
                            {time}
                          </MenuItem>
                        ))}
                      </Select>
                      {errors.eventStartTime && (
                        <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                          {errors.eventStartTime}
                        </Typography>
                      )}
                    </FormControl>
                  </Box>
                </Box>

                {/* End Date and Time */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    End Date & Time (optional)
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <TextField
                      type="date"
                      value={eventEndDate}
                      onChange={(e) => setEventEndDate(e.target.value)}
                      error={!!errors.eventEndDate}
                      helperText={errors.eventEndDate}
                      InputLabelProps={{ shrink: true }}
                      sx={{ minWidth: 180 }}
                    />
                    <FormControl sx={{ minWidth: 120 }} error={!!errors.eventEndTime}>
                      <InputLabel>Time</InputLabel>
                      <Select
                        value={eventEndTime}
                        onChange={(e) => setEventEndTime(e.target.value)}
                        label="Time"
                      >
                        <MenuItem value="">--</MenuItem>
                        {timeOptions.map((time) => (
                          <MenuItem key={time} value={time}>
                            {time}
                          </MenuItem>
                        ))}
                      </Select>
                      {errors.eventEndTime && (
                        <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                          {errors.eventEndTime}
                        </Typography>
                      )}
                    </FormControl>
                  </Box>
                </Box>

                {/* Location */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Location (optional)
                  </Typography>
                  <LocationPicker
                    value={eventLocation}
                    onChange={setEventLocation}
                    disabled={false}
                    required={false}
                  />
                </Box>
              </Box>
            )}

            {/* Tags */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                Tags (up to 10)
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  size="small"
                  placeholder="Add a tag"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleTagKeyDown}
                  disabled={tags.length >= 10}
                  sx={{ flex: 1 }}
                />
                <Button
                  variant="outlined"
                  onClick={handleAddTag}
                  disabled={!tagInput.trim() || tags.length >= 10}
                  startIcon={<AddIcon />}
                >
                  Add
                </Button>
              </Box>
              {tags.length > 0 && (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {tags.map((tag) => (
                    <Chip
                      key={tag}
                      label={tag}
                      onDelete={() => handleRemoveTag(tag)}
                      size="small"
                    />
                  ))}
                </Box>
              )}
            </Box>

            {/* Error message */}
            {createTopicMutation.isError && (
              <Alert severity="error" sx={{ mb: 3 }}>
                Unable to create topic. Please try again.
              </Alert>
            )}

            {/* Submit button */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button
                variant="outlined"
                onClick={() => navigate('/forum')}
                disabled={createTopicMutation.isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={createTopicMutation.isPending}
                startIcon={createTopicMutation.isPending && <CircularProgress size={20} />}
              >
                {createTopicMutation.isPending
                  ? 'Creating...'
                  : `Create ${topicType === 'event' ? 'Event' : 'Discussion'}`}
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Container>
  )
}
