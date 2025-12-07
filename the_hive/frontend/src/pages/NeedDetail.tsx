// SRS FR-3 & FR-5: Need Detail View with Handshake Mechanism
// Shows complete need information and allows users to propose help

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
  Paper,
  Tabs,
  Tab,
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  AccessTime as ClockIcon,
  LocalOffer as TagIcon,
  Person as PersonIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  People as PeopleIcon,
  Schedule as ScheduleIcon,
  Language as RemoteIcon,
  HelpOutline as NeedIcon,
  CheckCircle as CheckIcon,
  Map as MapIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'
import { getAvatarDisplay } from '@/utils/avatars'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix Leaflet icon issue
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
})

L.Marker.prototype.options.icon = DefaultIcon

// SRS FR-3: Need data structure
interface NeedDetail {
  id: number
  creator_id: number
  creator: {
    id: number
    username: string
    display_name?: string
    full_name?: string
    profile_image?: string
    profile_image_type?: string
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
  available_slots?: Array<{
    date: string
    time_ranges: Array<{
      start_time: string
      end_time: string
    }>
  }>
  start_date: string
  end_date: string
  created_at: string
}

// SRS FR-5.1: Propose help with message
interface ProposeHelpRequest {
  message: string
    selected_date?: string
    selected_time_range?: string
}

// Accepted participant structure
interface AcceptedParticipant {
  id: number
  user_id: number
  user: {
    id: number
    username: string
    display_name?: string
  }
  status: string
  hours_contributed?: number
  created_at: string
}

interface ParticipantListResponse {
  items: AcceptedParticipant[]
  total: number
}

/**
 * NeedDetail Component
 * 
 * Displays complete need information including:
 * - Need type badge (Need/Remote)
 * - Creator information with avatar
 * - Description
 * - Available time slots
 * - Capacity and tags
 * - Offer to Help button with proposal modal
 * 
 * Backend APIs:
 * - GET /api/v1/needs/{id} - Fetch need details
 * - POST /api/v1/handshake/propose - Propose to help
 */
export default function NeedDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [proposeDialogOpen, setProposeDialogOpen] = useState(false)
    const [selectedDate, setSelectedDate] = useState<string | null>(null)
    const [selectedTimeRange, setSelectedTimeRange] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [currentTab, setCurrentTab] = useState(0)

  // Fetch need details
  const { data: need, isLoading, error: fetchError } = useQuery<NeedDetail>({
    queryKey: ['need', id],
    queryFn: async () => {
      const response = await apiClient.get(`/needs/${id}`)
      return response.data
    },
  })

  // Fetch accepted participants
  const { data: acceptedParticipants } = useQuery<ParticipantListResponse>({
    queryKey: ['need-participants', id, 'accepted'],
    queryFn: async () => {
      const response = await apiClient.get(`/participants/needs/${id}?status_filter=accepted`)
      return response.data
    },
    enabled: !!id,
  })

  // Propose help mutation
  const proposeMutation = useMutation({
    mutationFn: async (data: ProposeHelpRequest) => {
      const params = new URLSearchParams({
        item_type: 'need',
        item_id: id!,
        message: data.message,
      })
          if (data.selected_date && data.selected_time_range) {
              params.append('selected_date', data.selected_date)
              params.append('selected_time_range', data.selected_time_range)
      }
      const response = await apiClient.post('/handshake/propose', null, { params })
      return response.data
    },
    onSuccess: () => {
      setProposeDialogOpen(false)
      setMessage('')
        setSelectedDate(null)
        setSelectedTimeRange(null)
      setError(null)
      queryClient.invalidateQueries({ queryKey: ['need', id] })
      // Navigate to My Applications tab in Active Items
      navigate('/active-items?tab=applications')
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.detail || 'Unable to send your offer. Please try again.'
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
      setError('Please write a message explaining how you can help')
      return
    }
    proposeMutation.mutate({
      message: message.trim(),
        selected_date: selectedDate || undefined,
        selected_time_range: selectedTimeRange || undefined,
    })
    }

    const handleTimeSlotClick = (date: string, timeRange: string) => {
        const key = `${date}-${timeRange}`
        const currentKey = selectedDate && selectedTimeRange ? `${selectedDate}-${selectedTimeRange}` : null

        if (currentKey === key) {
            // Deselect if clicking the same slot
            setSelectedDate(null)
            setSelectedTimeRange(null)
        } else {
            // Select new slot
            setSelectedDate(date)
            setSelectedTimeRange(timeRange)
        }
    }

    const formatSlotDate = (dateStr: string) => {
        const [year, month, day] = dateStr.split('-')
        return new Date(parseInt(year), parseInt(month) - 1, parseInt(day)).toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
    })
  }

    const formatTimeRange = (start: string, end: string) => {
        return `${start} - ${end}`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

    const formatTimeSlotOld = (slot: { start_time: string; end_time: string; day_of_week?: string }) => {
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

  if (fetchError || !need) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Unable to load this need. Please try again later.
        </Alert>
      </Container>
    )
  }

  const isCreator = user?.id === need.creator_id
  const isFull = need.accepted_count >= need.capacity
  const canPropose = user && !isCreator && !isFull && need.status === 'active'

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
                  icon={<NeedIcon />}
                  label="Need"
                  color="info"
                  size="small"
                />
                {need.is_remote && (
                  <Chip
                    icon={<RemoteIcon />}
                    label="Remote"
                    color="primary"
                    size="small"
                    variant="outlined"
                  />
                )}
                <Chip
                  label={need.status.charAt(0).toUpperCase() + need.status.slice(1)}
                  color={need.status === 'active' ? 'success' : 'default'}
                  size="small"
                  variant="outlined"
                />
              </Box>

              {/* Title */}
              <Typography variant="h4" gutterBottom fontWeight={600}>
                {need.title}
              </Typography>

              {/* Creator Info */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                {(() => {
                  const avatarDisplay = getAvatarDisplay(need.creator.profile_image, need.creator.profile_image_type)
                  if (avatarDisplay?.isCustomImage && avatarDisplay.src) {
                    return (
                      <Avatar
                        src={avatarDisplay.src}
                        sx={{
                          width: 48,
                          height: 48,
                          cursor: 'pointer'
                        }}
                        onClick={() => navigate(`/profile/${need.creator.username}`)}
                      />
                    )
                  }
                  if (avatarDisplay?.emoji) {
                    return (
                      <Avatar
                        sx={{
                          bgcolor: avatarDisplay.bgcolor || 'info.main',
                          width: 48,
                          height: 48,
                          cursor: 'pointer',
                          fontSize: '1.5rem',
                        }}
                        onClick={() => navigate(`/profile/${need.creator.username}`)}
                      >
                        {avatarDisplay.emoji}
                      </Avatar>
                    )
                  }
                  return (
                    <Avatar
                      sx={{
                        bgcolor: 'info.main',
                        width: 48,
                        height: 48,
                        cursor: 'pointer'
                      }}
                      onClick={() => navigate(`/profile/${need.creator.username}`)}
                    >
                      <PersonIcon />
                    </Avatar>
                  )
                })()}
                              <Box
                                  onClick={() => navigate(`/profile/${need.creator.username}`)}
                                  sx={{
                                      cursor: 'pointer',
                                      '&:hover': { opacity: 0.8 }
                                  }}
                              >
                                  <Typography
                                      variant="subtitle1"
                                      fontWeight={500}
                                      sx={{
                                          '&:hover': { color: 'info.main' }
                                      }}
                                  >
                    {need.creator.display_name || need.creator.full_name || need.creator.username}
                  </Typography>
                                  <Typography
                                      variant="caption"
                                      color="text.secondary"
                                      sx={{
                                          '&:hover': { color: 'info.main' }
                                      }}
                                  >
                    @{need.creator.username}
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* Tabs for Details and Location */}
              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
                  <Tab label="Details" />
                  {!need.is_remote && need.location_lat && need.location_lon && (
                    <Tab label="Location" />
                  )}
                </Tabs>
              </Box>

              {/* Details Tab */}
              {currentTab === 0 && (
                <>
                  {/* Description */}
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom fontWeight={600}>
                      Description
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                      {need.description}
                    </Typography>
                  </Box>

                  {/* Location (if not remote) */}
                  {!need.is_remote && need.location_name && (
                    <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LocationIcon color="action" />
                      <Typography variant="body2" color="text.secondary">
                        {need.location_name}
                      </Typography>
                    </Box>
                  )}

                  {/* Date Range */}
                  <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CalendarIcon color="action" />
                    <Typography variant="body2" color="text.secondary">
                      Needed by: {formatDate(need.start_date)} - {formatDate(need.end_date)}
                    </Typography>
                  </Box>

                  {/* Time Slots Section */}
                  {need.available_slots && need.available_slots.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <ScheduleIcon color="action" />
                      <Typography variant="h6" fontWeight={600}>
                        Preferred Time Slots
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {need.available_slots.map((slot, idx) => (
                          <Box key={idx}>
                            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                              {formatSlotDate(slot.date)}
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                              {slot.time_ranges.map((range, rangeIdx) => {
                                const rangeKey = `${range.start_time}-${range.end_time}`
                                const isSelected = selectedDate === slot.date && selectedTimeRange === rangeKey
                                return (
                                  <Chip
                                    key={rangeIdx}
                                    icon={<ClockIcon />}
                                    label={formatTimeRange(range.start_time, range.end_time)}
                                    onClick={() => handleTimeSlotClick(slot.date, rangeKey)}
                                    color={isSelected ? 'primary' : 'default'}
                                    variant={isSelected ? 'filled' : 'outlined'}
                                    sx={{ cursor: 'pointer' }}
                                  />
                                )
                              })}
                            </Box>
                          </Box>
                        ))}
                      </Box>
                    </Box>
                  )}
                </>
              )}

              {/* Location Map Tab */}
              {currentTab === 1 && !need.is_remote && need.location_lat && need.location_lon && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom fontWeight={600}>
                    Location
                  </Typography>
                  {need.location_name && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <LocationIcon color="action" />
                      <Typography variant="body2" color="text.secondary">
                        {need.location_name}
                      </Typography>
                    </Box>
                  )}
                  <Box sx={{ height: 400, width: '100%', borderRadius: 1, overflow: 'hidden' }}>
                    <MapContainer
                      center={[need.location_lat, need.location_lon]}
                      zoom={13}
                      style={{ height: '100%', width: '100%' }}
                    >
                      <TileLayer
                        attribution='&copy; <a href="https://carto.com/">CARTO</a> contributors'
                        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                      />
                      <Marker position={[need.location_lat, need.location_lon]}>
                        <Popup>
                          <Box>
                            <Typography variant="subtitle2" fontWeight={600}>
                              {need.title}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {need.location_name}
                            </Typography>
                          </Box>
                        </Popup>
                      </Marker>
                    </MapContainer>
                  </Box>
                </Box>
              )}

              {/* Action Button */}
              {canPropose && (
                <Button
                  variant="contained"
                  color="info"
                  size="large"
                  fullWidth
                  onClick={handleProposeClick}
                  disabled={proposeMutation.isPending}
                  sx={{ mt: 2 }}
                >
                  Offer to Help
                </Button>
              )}

              {isFull && !isCreator && need.status !== 'completed' && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  This need has enough helpers. Check back later if spots become available.
                </Alert>
              )}

              {need.status === 'completed' && !isCreator && (
                <Alert severity="success" sx={{ mt: 2 }}>
                  This need has been completed.
                </Alert>
              )}

              {isCreator && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  This is your need. You can view proposals in your Active Items dashboard.
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
                  Helpers Needed
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
                      width: `${(need.accepted_count / need.capacity) * 100}%`,
                      height: '100%',
                      bgcolor: isFull ? 'success.main' : 'info.main',
                      transition: 'width 0.3s',
                    }}
                  />
                </Box>
                <Typography variant="body2" fontWeight={600}>
                  {need.accepted_count}/{need.capacity}
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {isFull ? 'All helpers found!' : `${need.capacity - need.accepted_count} helper${need.capacity - need.accepted_count !== 1 ? 's' : ''} needed`}
              </Typography>

              {/* Accepted Participants */}
              {acceptedParticipants && acceptedParticipants.items.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                    Accepted helpers:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {acceptedParticipants.items.map((participant) => (
                      <Chip
                        key={participant.id}
                        avatar={
                          <Avatar sx={{ bgcolor: 'success.main', width: 24, height: 24 }}>
                            <CheckIcon sx={{ fontSize: 14 }} />
                          </Avatar>
                        }
                        label={participant.user.display_name || participant.user.username}
                        size="small"
                        variant="outlined"
                        color="success"
                        onClick={() => navigate(`/profile/${participant.user.username}`)}
                        sx={{ cursor: 'pointer' }}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Box>

            {/* Tags */}
            {need.tags.length > 0 && (
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TagIcon color="action" fontSize="small" />
                  <Typography variant="subtitle2" fontWeight={500}>
                    Tags
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {need.tags.map((tag) => (
                    <Chip
                      key={tag}
                      label={tag}
                      size="small"
                      variant="outlined"
                      onClick={() => navigate(`/?tag=${encodeURIComponent(tag)}&type=needs`)}
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
        <DialogTitle>Offer to Help</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Tell {need.creator.username} how you can help and what makes you qualified to assist with this need.
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
            placeholder="Hi! I can help with this. I have experience in..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            disabled={proposeMutation.isPending}
            sx={{ mb: 2 }}
          />

          {/* Time Slots in Dialog */}
                  {need.available_slots && need.available_slots.length > 0 && (
            <Box>
                          <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                Select a preferred time slot (optional)
              </Typography>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
                              {need.available_slots.map((slot, idx) => (
                                  <Box key={idx}>
                                      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
                                          {formatSlotDate(slot.date)}
                                      </Typography>
                                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                          {slot.time_ranges.map((range, rangeIdx) => {
                                              const rangeKey = `${range.start_time}-${range.end_time}`
                                              const isSelected = selectedDate === slot.date && selectedTimeRange === rangeKey
                                              return (
                                                  <Chip
                                key={rangeIdx}
                                icon={<ClockIcon />}
                                label={formatTimeRange(range.start_time, range.end_time)}
                                onClick={() => handleTimeSlotClick(slot.date, rangeKey)}
                                color={isSelected ? 'primary' : 'default'}
                                variant={isSelected ? 'filled' : 'outlined'}
                                clickable
                            />
                          )
                      })}
                        </Box>
                    </Box>
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
            color="info"
            disabled={proposeMutation.isPending || !message.trim()}
          >
            {proposeMutation.isPending ? 'Sending...' : 'Send Proposal'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
