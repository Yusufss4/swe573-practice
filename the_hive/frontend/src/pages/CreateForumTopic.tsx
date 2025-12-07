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
  const [eventStartTime, setEventStartTime] = useState('')
  const [eventEndTime, setEventEndTime] = useState('')
  const [eventLocation, setEventLocation] = useState('')

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
        if (eventStartTime) {
          payload.event_start_time = new Date(eventStartTime).toISOString()
        }
        if (eventEndTime) {
          payload.event_end_time = new Date(eventEndTime).toISOString()
        }
        if (eventLocation.trim()) {
          payload.event_location = eventLocation.trim()
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

    if (topicType === 'event' && !eventStartTime) {
      newErrors.eventStartTime = 'Event start time is required'
    }

    if (eventEndTime && eventStartTime && new Date(eventEndTime) <= new Date(eventStartTime)) {
      newErrors.eventEndTime = 'End time must be after start time'
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

                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
                  <TextField
                    type="datetime-local"
                    label="Start Date & Time"
                    value={eventStartTime}
                    onChange={(e) => setEventStartTime(e.target.value)}
                    error={!!errors.eventStartTime}
                    helperText={errors.eventStartTime}
                    InputLabelProps={{ shrink: true }}
                    sx={{ minWidth: 220 }}
                    required
                  />
                  <TextField
                    type="datetime-local"
                    label="End Date & Time (optional)"
                    value={eventEndTime}
                    onChange={(e) => setEventEndTime(e.target.value)}
                    error={!!errors.eventEndTime}
                    helperText={errors.eventEndTime}
                    InputLabelProps={{ shrink: true }}
                    sx={{ minWidth: 220 }}
                  />
                </Box>

                <TextField
                  fullWidth
                  label="Location (optional)"
                  value={eventLocation}
                  onChange={(e) => setEventLocation(e.target.value)}
                  placeholder="e.g., Community Center, Online, etc."
                  helperText="Where will the event take place?"
                />
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
