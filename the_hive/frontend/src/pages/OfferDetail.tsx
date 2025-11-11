// SRS FR-3 & FR-5: Offer Detail View with Handshake Mechanism
// Shows complete offer information and allows users to propose help

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Avatar,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Divider,
  IconButton,
  Tooltip,
  Paper,
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  AccessTime as ClockIcon,
  LocalOffer as TagIcon,
  Person as PersonIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  People as PeopleIcon,
  CheckCircle as CheckIcon,
  Schedule as ScheduleIcon,
  Language as RemoteIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'

// SRS FR-3: Offer data structure
interface OfferDetail {
  id: number
  creator_id: number
  creator: {
    id: number
    username: string
    display_name?: string
    full_name?: string
  }
  title: string
  description: string
  is_remote: boolean
  location_name?: string
  location_lat?: number
  location_lon?: number
  capacity: number
  accepted_count: number
  status: string
  tags: string[]
  time_slots?: Array<{
    id: number
    start_time: string
    end_time: string
    day_of_week?: string
  }>
  start_date: string
  end_date: string
  created_at: string
}

// SRS FR-5.1: Propose help with message
interface ProposeHelpRequest {
  message: string
  selected_time_slot_id?: number
}

/**
 * OfferDetail Component
 * 
 * Displays complete offer information including:
 * - Offer type badge (Offer/Remote)
 * - Creator information with avatar
 * - Description
 * - Available time slots
 * - Capacity and tags
 * - Request Service button with proposal modal
 * 
 * Backend APIs:
 * - GET /api/v1/offers/{id} - Fetch offer details
 * - POST /api/v1/handshake/propose - Propose to help
 */
export default function OfferDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [proposeDialogOpen, setProposeDialogOpen] = useState(false)
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<number | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Fetch offer details
  const { data: offer, isLoading, error: fetchError } = useQuery<OfferDetail>({
    queryKey: ['offer', id],
    queryFn: async () => {
      const response = await apiClient.get(`/offers/${id}`)
      return response.data
    },
  })

  // Propose help mutation
  const proposeMutation = useMutation({
    mutationFn: async (data: ProposeHelpRequest) => {
      const params = new URLSearchParams({
        item_type: 'offer',
        item_id: id!,
        message: data.message,
      })
      if (data.selected_time_slot_id) {
        params.append('time_slot_id', data.selected_time_slot_id.toString())
      }
      const response = await apiClient.post('/handshake/propose', null, { params })
      return response.data
    },
    onSuccess: () => {
      setProposeDialogOpen(false)
      setMessage('')
      setSelectedTimeSlot(null)
      setError(null)
      queryClient.invalidateQueries({ queryKey: ['offer', id] })
      // Show success message or navigate
      alert('Your proposal has been sent! The creator will review it soon.')
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.detail || 'Failed to send proposal. Please try again.'
      setError(errorMessage)
    },
  })

  const handleProposeClick = () => {
    if (!user) {
      navigate('/login')
      return
    }
    setProposeDialogOpen(true)
    setError(null)
  }

  const handleSubmitProposal = () => {
    if (!message.trim()) {
      setError('Please write a message explaining why you want to help')
      return
    }
    proposeMutation.mutate({
      message: message.trim(),
      selected_time_slot_id: selectedTimeSlot || undefined,
    })
  }

  const handleTimeSlotClick = (slotId: number) => {
    setSelectedTimeSlot(selectedTimeSlot === slotId ? null : slotId)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const formatTimeSlot = (slot: { start_time: string; end_time: string; day_of_week?: string }) => {
    const start = new Date(slot.start_time).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    })
    const end = new Date(slot.end_time).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    })
    return slot.day_of_week
      ? `${slot.day_of_week}: ${start} - ${end}`
      : `${start} - ${end}`
  }

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (fetchError || !offer) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Failed to load offer details. {fetchError?.message || 'Please try again later.'}
        </Alert>
      </Container>
    )
  }

  const isCreator = user?.id === offer.creator_id
  const isFull = offer.accepted_count >= offer.capacity
  const canPropose = user && !isCreator && !isFull && offer.status === 'active'

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Back Button */}
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate(-1)}
        sx={{ mb: 3 }}
      >
        Back
      </Button>

      <Grid container spacing={3}>
        {/* Main Content */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              {/* Header with Badges */}
              <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                <Chip
                  label="Offer"
                  color="success"
                  size="small"
                />
                {offer.is_remote && (
                  <Chip
                    icon={<RemoteIcon />}
                    label="Remote"
                    color="primary"
                    size="small"
                    variant="outlined"
                  />
                )}
                <Chip
                  label={offer.status.toUpperCase()}
                  color={offer.status === 'active' ? 'success' : 'default'}
                  size="small"
                  variant="outlined"
                />
              </Box>

              {/* Title */}
              <Typography variant="h4" gutterBottom fontWeight={600}>
                {offer.title}
              </Typography>

              {/* Creator Info */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Avatar
                  sx={{
                    bgcolor: 'primary.main',
                    width: 48,
                    height: 48,
                    cursor: 'pointer'
                  }}
                  onClick={() => navigate(`/profile/${offer.creator_id}`)}
                >
                  <PersonIcon />
                </Avatar>
                <Box
                  onClick={() => navigate(`/profile/${offer.creator_id}`)}
                  sx={{
                    cursor: 'pointer',
                    '&:hover': { opacity: 0.8 }
                  }}
                >
                  <Typography
                    variant="subtitle1"
                    fontWeight={500}
                    sx={{
                      '&:hover': { color: 'primary.main' }
                    }}
                  >
                    {offer.creator.display_name || offer.creator.full_name || offer.creator.username}
                  </Typography>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{
                      '&:hover': { color: 'primary.main' }
                    }}
                  >
                    @{offer.creator.username}
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* Description */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom fontWeight={600}>
                  Description
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                  {offer.description}
                </Typography>
              </Box>

              {/* Location (if not remote) */}
              {!offer.is_remote && offer.location_name && (
                <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LocationIcon color="action" />
                  <Typography variant="body2" color="text.secondary">
                    {offer.location_name}
                  </Typography>
                </Box>
              )}

              {/* Date Range */}
              <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                <CalendarIcon color="action" />
                <Typography variant="body2" color="text.secondary">
                  Available: {formatDate(offer.start_date)} - {formatDate(offer.end_date)}
                </Typography>
              </Box>

              {/* Time Slots Section */}
              {offer.time_slots && offer.time_slots.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <ScheduleIcon color="action" />
                    <Typography variant="h6" fontWeight={600}>
                      Available Time Slots
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Select a time slot when proposing to help (optional)
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {offer.time_slots.map((slot) => (
                      <Chip
                        key={slot.id}
                        icon={<ClockIcon />}
                        label={formatTimeSlot(slot)}
                        onClick={() => proposeDialogOpen && handleTimeSlotClick(slot.id)}
                        color={selectedTimeSlot === slot.id ? 'primary' : 'default'}
                        variant={selectedTimeSlot === slot.id ? 'filled' : 'outlined'}
                        sx={{ cursor: proposeDialogOpen ? 'pointer' : 'default' }}
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {/* Action Button */}
              {canPropose && (
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  onClick={handleProposeClick}
                  disabled={proposeMutation.isPending}
                  sx={{ mt: 2 }}
                >
                  Request Service
                </Button>
              )}

              {isFull && !isCreator && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  This offer is currently full. Check back later if spots become available.
                </Alert>
              )}

              {isCreator && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  This is your offer. You can view proposals in your Active Items dashboard.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Sidebar - Details Card */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, position: 'sticky', top: 80 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Details
            </Typography>

            <Divider sx={{ my: 2 }} />

            {/* Capacity */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <PeopleIcon color="action" fontSize="small" />
                <Typography variant="subtitle2" fontWeight={500}>
                  Capacity
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box
                  sx={{
                    flexGrow: 1,
                    height: 8,
                    bgcolor: 'grey.200',
                    borderRadius: 1,
                    overflow: 'hidden',
                  }}
                >
                  <Box
                    sx={{
                      width: `${(offer.accepted_count / offer.capacity) * 100}%`,
                      height: '100%',
                      bgcolor: isFull ? 'error.main' : 'success.main',
                      transition: 'width 0.3s',
                    }}
                  />
                </Box>
                <Typography variant="body2" fontWeight={600}>
                  {offer.accepted_count}/{offer.capacity}
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {offer.capacity - offer.accepted_count} slot{offer.capacity - offer.accepted_count !== 1 ? 's' : ''} available
              </Typography>
            </Box>

            {/* Tags */}
            {offer.tags.length > 0 && (
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TagIcon color="action" fontSize="small" />
                  <Typography variant="subtitle2" fontWeight={500}>
                    Tags
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {offer.tags.map((tag) => (
                    <Chip
                      key={tag}
                      label={tag}
                      size="small"
                      variant="outlined"
                      onClick={() => navigate(`/search?query=${tag}&type=offer`)}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Propose Help Dialog */}
      <Dialog
        open={proposeDialogOpen}
        onClose={() => !proposeMutation.isPending && setProposeDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Propose to Help</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Tell {offer.creator.username} why you want to help and what makes you a good fit for this offer.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <TextField
            autoFocus
            multiline
            rows={4}
            fullWidth
            label="Your Message"
            placeholder="Hi! I'd love to help with this. I have experience in..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            disabled={proposeMutation.isPending}
            sx={{ mb: 2 }}
          />

          {/* Time Slots in Dialog */}
          {offer.time_slots && offer.time_slots.length > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Select a preferred time slot (optional)
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {offer.time_slots.map((slot) => (
                  <Chip
                    key={slot.id}
                    icon={<ClockIcon />}
                    label={formatTimeSlot(slot)}
                    onClick={() => handleTimeSlotClick(slot.id)}
                    color={selectedTimeSlot === slot.id ? 'primary' : 'default'}
                    variant={selectedTimeSlot === slot.id ? 'filled' : 'outlined'}
                    clickable
                  />
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setProposeDialogOpen(false)}
            disabled={proposeMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmitProposal}
            variant="contained"
            disabled={proposeMutation.isPending || !message.trim()}
          >
            {proposeMutation.isPending ? 'Sending...' : 'Send Proposal'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
