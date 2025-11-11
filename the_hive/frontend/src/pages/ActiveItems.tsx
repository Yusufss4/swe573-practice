// SRS FR-14: Active Items Dashboard
// Shows user's created posts and their applications to help others

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Tabs,
  Tab,
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
  Grid,
} from '@mui/material'
import {
  LocalOffer as OfferIcon,
  EventNote as NeedIcon,
  Person as PersonIcon,
  Message as MessageIcon,
  Check as AcceptIcon,
  Close as DeclineIcon,
  ExitToApp as WithdrawIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  )
}

// Participant/Application data structure
interface Participant {
  id: number
  user_id: number
  user: {
    id: number
    username: string
    display_name?: string
    full_name?: string
  }
  offer_id?: number
  need_id?: number
  status: 'pending' | 'accepted' | 'completed' | 'declined'
  message: string
  hours_contributed?: number
  created_at: string
}

// My Post structure (Offer or Need with participants)
interface MyPost {
  id: number
  type: 'offer' | 'need'
  title: string
  description: string
  status: string
  capacity: number
  accepted_count: number
  participants: Participant[]
  created_at: string
}

// My Application structure
interface MyApplication {
  id: number
  type: 'offer' | 'need'
  item_id: number
  item_title: string
  item_creator: {
    id: number
    username: string
    display_name?: string
  }
  status: 'pending' | 'accepted' | 'completed' | 'declined'
  message: string
  hours_contributed?: number
  created_at: string
}

/**
 * ActiveItems Component
 * 
 * Two-tab dashboard:
 * 1. My Posts - Offers/Needs user created, with pending applicants
 * 2. My Applications - User's proposals to help others
 * 
 * Actions:
 * - Post owner: Accept/Decline applicants
 * - Applicant: Withdraw application, Message creator
 * 
 * Backend APIs:
 * - GET /api/v1/participants/offers/{id} - Get participants for an offer
 * - GET /api/v1/participants/needs/{id} - Get participants for a need
 * - POST /api/v1/participants/offers/{id}/accept - Accept participant
 * - POST /api/v1/participants/needs/{id}/accept - Accept participant
 * - DELETE /api/v1/participants/{id} - Withdraw/decline
 */
export default function ActiveItems() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [activeTab, setActiveTab] = useState(0)
  const [acceptDialogOpen, setAcceptDialogOpen] = useState(false)
  const [selectedParticipant, setSelectedParticipant] = useState<Participant | null>(null)
  const [selectedPost, setSelectedPost] = useState<MyPost | null>(null)
  const [hours, setHours] = useState('2')
  const [error, setError] = useState<string | null>(null)

  // Fetch user's offers with participants
  const { data: myOffers, isLoading: offersLoading } = useQuery({
    queryKey: ['myOffers'],
    queryFn: async () => {
      const response = await apiClient.get('/offers/my')
      const offers = response.data.items || []
      
      // Fetch participants for each offer
      const offersWithParticipants = await Promise.all(
        offers.map(async (offer: any) => {
          try {
            const participantsResponse = await apiClient.get(`/participants/offers/${offer.id}`)
            return {
              ...offer,
              type: 'offer' as const,
              participants: participantsResponse.data.items || [],
            }
          } catch (error) {
            return {
              ...offer,
              type: 'offer' as const,
              participants: [],
            }
          }
        })
      )
      return offersWithParticipants
    },
    enabled: !!user,
  })

  // Fetch user's needs with participants
  const { data: myNeeds, isLoading: needsLoading } = useQuery({
    queryKey: ['myNeeds'],
    queryFn: async () => {
      const response = await apiClient.get('/needs/my')
      const needs = response.data.items || []
      
      // Fetch participants for each need
      const needsWithParticipants = await Promise.all(
        needs.map(async (need: any) => {
          try {
            const participantsResponse = await apiClient.get(`/participants/needs/${need.id}`)
            return {
              ...need,
              type: 'need' as const,
              participants: participantsResponse.data.items || [],
            }
          } catch (error) {
            return {
              ...need,
              type: 'need' as const,
              participants: [],
            }
          }
        })
      )
      return needsWithParticipants
    },
    enabled: !!user,
  })

  // Combine offers and needs into "My Posts"
  const myPosts: MyPost[] = [
    ...(myOffers || []),
    ...(myNeeds || []),
  ]

  // Fetch user's applications (proposals to help others)
  const { data: myApplicationsData, isLoading: applicationsLoading } = useQuery({
    queryKey: ['myApplications'],
    queryFn: async () => {
      // Fetch all offers and needs to find user's applications
      const [offersRes, needsRes] = await Promise.all([
        apiClient.get('/offers/'),
        apiClient.get('/needs/'),
      ])

      const allOffers = offersRes.data.items || []
      const allNeeds = needsRes.data.items || []

      // Get participants for each offer/need and filter for current user
      const applications: MyApplication[] = []

      // Check offers
      for (const offer of allOffers) {
        if (offer.creator_id !== user?.id) {
          try {
            const participantsRes = await apiClient.get(`/participants/offers/${offer.id}`)
            const userParticipation = participantsRes.data.items?.find(
              (p: Participant) => p.user_id === user?.id
            )
            if (userParticipation) {
              applications.push({
                id: userParticipation.id,
                type: 'offer',
                item_id: offer.id,
                item_title: offer.title,
                item_creator: {
                  id: offer.creator_id,
                  username: offer.creator?.username || 'Unknown',
                  display_name: offer.creator?.display_name,
                },
                status: userParticipation.status,
                message: userParticipation.message,
                hours_contributed: userParticipation.hours_contributed,
                created_at: userParticipation.created_at,
              })
            }
          } catch (error) {
            // Skip if error fetching participants
          }
        }
      }

      // Check needs
      for (const need of allNeeds) {
        if (need.creator_id !== user?.id) {
          try {
            const participantsRes = await apiClient.get(`/participants/needs/${need.id}`)
            const userParticipation = participantsRes.data.items?.find(
              (p: Participant) => p.user_id === user?.id
            )
            if (userParticipation) {
              applications.push({
                id: userParticipation.id,
                type: 'need',
                item_id: need.id,
                item_title: need.title,
                item_creator: {
                  id: need.creator_id,
                  username: need.creator?.username || 'Unknown',
                  display_name: need.creator?.display_name,
                },
                status: userParticipation.status,
                message: userParticipation.message,
                hours_contributed: userParticipation.hours_contributed,
                created_at: userParticipation.created_at,
              })
            }
          } catch (error) {
            // Skip if error fetching participants
          }
        }
      }

      return applications
    },
    enabled: !!user && activeTab === 1, // Only fetch when on applications tab
  })

  const myApplications: MyApplication[] = myApplicationsData || []

  // Accept participant mutation
  const acceptMutation = useMutation({
    mutationFn: async ({ postId, postType, participantId, hours }: {
      postId: number
      postType: 'offer' | 'need'
      participantId: number
      hours: number
    }) => {
      const endpoint = postType === 'offer'
        ? `/participants/offers/${postId}/accept`
        : `/participants/needs/${postId}/accept`
      const response = await apiClient.post(endpoint, {
        participant_id: participantId,
        hours: hours,
      })
      return response.data
    },
    onSuccess: () => {
      setAcceptDialogOpen(false)
      setHours('2')
      setError(null)
      queryClient.invalidateQueries({ queryKey: ['myOffers'] })
      queryClient.invalidateQueries({ queryKey: ['myNeeds'] })
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.detail || 'Failed to accept participant'
      setError(errorMessage)
    },
  })

  // Decline/Withdraw mutation
  const declineMutation = useMutation({
    mutationFn: async (participantId: number) => {
      const response = await apiClient.delete(`/participants/${participantId}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myOffers'] })
      queryClient.invalidateQueries({ queryKey: ['myNeeds'] })
      queryClient.invalidateQueries({ queryKey: ['myApplications'] })
    },
  })

  const handleAcceptClick = (post: MyPost, participant: Participant) => {
    setSelectedPost(post)
    setSelectedParticipant(participant)
    setAcceptDialogOpen(true)
    setError(null)
  }

  const handleAcceptSubmit = () => {
    if (!selectedPost || !selectedParticipant) return

    const hoursNum = parseFloat(hours)
    if (isNaN(hoursNum) || hoursNum <= 0) {
      setError('Hours must be a positive number')
      return
    }

    acceptMutation.mutate({
      postId: selectedPost.id,
      postType: selectedPost.type,
      participantId: selectedParticipant.id,
      hours: hoursNum,
    })
  }

  const handleDecline = (participantId: number) => {
    if (confirm('Are you sure you want to decline this application?')) {
      declineMutation.mutate(participantId)
    }
  }

  const handleWithdraw = (participantId: number) => {
    if (confirm('Are you sure you want to withdraw your application?')) {
      declineMutation.mutate(participantId)
    }
  }

  const handleViewPost = (postId: number, postType: 'offer' | 'need') => {
      const path = postType === 'offer' ? `/offers/${postId}` : `/needs/${postId}`
      console.log('Navigating to:', path)
      navigate(path)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">Please log in to view your active items.</Alert>
      </Container>
    )
  }

  const isLoading = offersLoading || needsLoading

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Active Items
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Manage your posts and applications
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="My Posts" />
          <Tab label="My Applications" />
        </Tabs>
      </Box>

      {/* Tab 1: My Posts */}
      <TabPanel value={activeTab} index={0}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : myPosts.length === 0 ? (
          <Alert severity="info">
            You haven't created any offers or needs yet.{' '}
            <Button size="small" onClick={() => navigate('/offers/create')}>
              Create one now
            </Button>
          </Alert>
        ) : (
          <Grid container spacing={2}>
            {myPosts.map((post) => (
              <Grid item xs={12} key={`${post.type}-${post.id}`}>
                <Card>
                  <CardContent>
                    {/* Post Header */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                          <Chip
                            icon={post.type === 'offer' ? <OfferIcon /> : <NeedIcon />}
                            label={post.type === 'offer' ? 'Offer' : 'Need'}
                            size="small"
                            color={post.type === 'offer' ? 'success' : 'info'}
                          />
                          <Chip
                            label={post.status.toUpperCase()}
                            size="small"
                            variant="outlined"
                          />
                          <Chip
                            label={`${post.accepted_count}/${post.capacity} filled`}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                        <Typography variant="h6" fontWeight={600}>
                          {post.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Created {formatDate(post.created_at)}
                        </Typography>
                      </Box>
                      <Button
                        startIcon={<ViewIcon />}
                        onClick={() => handleViewPost(post.id, post.type)}
                      >
                        View
                      </Button>
                    </Box>

                    {/* Applicants Section */}
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                      Applicants ({post.participants?.length || 0})
                    </Typography>

                    {!post.participants || post.participants.length === 0 ? (
                      <Typography variant="body2" color="text.secondary">
                        No applicants yet
                      </Typography>
                    ) : (
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {post.participants.map((participant) => (
                          <Box
                            key={participant.id}
                            sx={{
                              p: 2,
                              bgcolor: 'grey.50',
                              borderRadius: 1,
                              border: '1px solid',
                              borderColor: 'grey.200',
                            }}
                          >
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                              <Box sx={{ display: 'flex', gap: 2, flex: 1 }}>
                                        <Avatar
                                            sx={{ bgcolor: 'primary.main', cursor: 'pointer' }}
                                            onClick={() => navigate(`/profile/${participant.user_id}`)}
                                        >
                                  <PersonIcon />
                                </Avatar>
                                <Box sx={{ flex: 1 }}>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                                <Typography
                                                    variant="subtitle2"
                                                    fontWeight={600}
                                                    onClick={() => navigate(`/profile/${participant.user_id}`)}
                                                    sx={{
                                                        cursor: 'pointer',
                                                        '&:hover': { color: 'primary.main', textDecoration: 'underline' }
                                                    }}
                                                >
                                      {participant.user.display_name || participant.user.username}
                                    </Typography>
                                    <Chip
                                      label={participant.status}
                                      size="small"
                                      color={
                                        participant.status === 'accepted'
                                          ? 'success'
                                          : participant.status === 'pending'
                                          ? 'warning'
                                          : 'default'
                                      }
                                    />
                                  </Box>
                                            <Typography
                                                variant="caption"
                                                color="text.secondary"
                                                display="block"
                                                sx={{
                                                    mb: 1,
                                                    cursor: 'pointer',
                                                    '&:hover': { color: 'primary.main' }
                                                }}
                                                onClick={() => navigate(`/profile/${participant.user_id}`)}
                                            >
                                    @{participant.user.username}
                                  </Typography>
                                  <Typography variant="body2" sx={{ mb: 1 }}>
                                    {participant.message}
                                  </Typography>
                                  {participant.hours_contributed && (
                                    <Typography variant="caption" color="text.secondary">
                                      Hours: {participant.hours_contributed}
                                    </Typography>
                                  )}
                                </Box>
                              </Box>

                              {/* Action Buttons for Pending */}
                              {participant.status === 'pending' && (
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                  <Tooltip title="Accept">
                                    <IconButton
                                      color="success"
                                      onClick={() => handleAcceptClick(post, participant)}
                                      disabled={acceptMutation.isPending || declineMutation.isPending}
                                    >
                                      <AcceptIcon />
                                    </IconButton>
                                  </Tooltip>
                                  <Tooltip title="Decline">
                                    <IconButton
                                      color="error"
                                      onClick={() => handleDecline(participant.id)}
                                      disabled={acceptMutation.isPending || declineMutation.isPending}
                                    >
                                      <DeclineIcon />
                                    </IconButton>
                                  </Tooltip>
                                </Box>
                              )}
                            </Box>
                          </Box>
                        ))}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      {/* Tab 2: My Applications */}
      <TabPanel value={activeTab} index={1}>
        {applicationsLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : myApplications.length === 0 ? (
          <Alert severity="info">
            You haven't applied to help anyone yet.{' '}
            <Button size="small" onClick={() => { setActiveTab(0); navigate('/'); }}>
              Browse offers and needs
            </Button>
          </Alert>
        ) : (
          <Grid container spacing={2}>
            {myApplications.map((application) => (
              <Grid item xs={12} key={application.id}>
                <Card>
                  <CardContent>
                    {/* Application Header */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                          <Chip
                            icon={application.type === 'offer' ? <OfferIcon /> : <NeedIcon />}
                            label={application.type === 'offer' ? 'Offer' : 'Need'}
                            size="small"
                            color={application.type === 'offer' ? 'success' : 'info'}
                          />
                          <Chip
                            label={application.status.toUpperCase()}
                            size="small"
                            color={
                              application.status === 'accepted'
                                ? 'success'
                                : application.status === 'pending'
                                ? 'warning'
                                : application.status === 'completed'
                                ? 'primary'
                                : 'default'
                            }
                          />
                        </Box>
                        <Typography variant="h6" fontWeight={600} gutterBottom>
                          {application.item_title}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.main' }}>
                            <PersonIcon fontSize="small" />
                          </Avatar>
                          <Typography variant="caption" color="text.secondary">
                            Created by @{application.item_creator.username}
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          Applied {formatDate(application.created_at)}
                        </Typography>
                      </Box>
                      <Button
                        startIcon={<ViewIcon />}
                        onClick={() => handleViewPost(application.item_id, application.type)}
                      >
                        View
                      </Button>
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    {/* Your Message */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                        Your Message
                      </Typography>
                      <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                        <Typography variant="body2">{application.message}</Typography>
                      </Box>
                    </Box>

                    {/* Hours if accepted */}
                    {application.hours_contributed && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                          Hours Agreed
                        </Typography>
                        <Chip 
                          label={`${application.hours_contributed} hours`} 
                          color="primary" 
                          size="small" 
                        />
                      </Box>
                    )}

                    {/* Action Buttons */}
                    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                      {application.status === 'pending' && (
                        <Button
                          variant="outlined"
                          color="error"
                          startIcon={<WithdrawIcon />}
                          onClick={() => handleWithdraw(application.id)}
                          disabled={declineMutation.isPending}
                        >
                          Withdraw Application
                        </Button>
                      )}
                      {application.status === 'accepted' && (
                        <Alert severity="success" sx={{ width: '100%' }}>
                          Your application has been accepted! The creator will contact you to arrange the exchange.
                        </Alert>
                      )}
                      {application.status === 'completed' && (
                        <Alert severity="info" sx={{ width: '100%' }}>
                          This exchange has been completed. Check your TimeBank balance for the hours earned.
                        </Alert>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      {/* Accept Dialog */}
      <Dialog
        open={acceptDialogOpen}
        onClose={() => !acceptMutation.isPending && setAcceptDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Accept Application</DialogTitle>
        <DialogContent>
          {selectedParticipant && (
            <>
              <Typography variant="body2" color="text.secondary" paragraph>
                Accept <strong>{selectedParticipant.user.username}</strong>'s application and specify the hours for this exchange.
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <TextField
                autoFocus
                fullWidth
                label="Hours"
                type="number"
                value={hours}
                onChange={(e) => setHours(e.target.value)}
                disabled={acceptMutation.isPending}
                inputProps={{ min: 0.5, step: 0.5 }}
                helperText="Number of TimeBank hours for this exchange"
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setAcceptDialogOpen(false)}
            disabled={acceptMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            onClick={handleAcceptSubmit}
            variant="contained"
            disabled={acceptMutation.isPending}
          >
            {acceptMutation.isPending ? 'Accepting...' : 'Accept'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
