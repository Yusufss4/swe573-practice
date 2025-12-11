// SRS FR-14: Active Items Dashboard
// Shows user's created posts and their applications to help others

import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
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
    CheckCircle as CompleteIcon,
  Star as StarIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'
import RatingSubmitDialog from '@/components/RatingSubmitDialog'

// Preset avatar emoji mappings
const AVATAR_EMOJIS: Record<string, string> = {
  // Insects
  bee: '🐝',
  butterfly: '🦋',
  ladybug: '🐞',
  ant: '🐜',
  cricket: '🦗',
  caterpillar: '🐛',
  snail: '🐌',
  spider: '🕷️',
  mosquito: '🦟',
  // Nature/animals
  bird: '🐦',
  owl: '🦉',
  turtle: '🐢',
  frog: '🐸',
  rabbit: '🐰',
  fox: '🦊',
  bear: '🐻',
  wolf: '🐺',
  deer: '🦌',
  squirrel: '🐿️',
  // Plants
  flower: '🌸',
  sunflower: '🌻',
  tree: '🌳',
  leaf: '🍃',
  mushroom: '🍄',
  cactus: '🌵',
}

// Avatar colors for presets
const AVATAR_COLORS: Record<string, string> = {
  // Insects
  bee: '#FFD700',
  butterfly: '#E91E63',
  ladybug: '#F44336',
  ant: '#795548',
  cricket: '#8BC34A',
  caterpillar: '#4CAF50',
  snail: '#9E9E9E',
  spider: '#424242',
  mosquito: '#607D8B',
  // Nature/animals
  bird: '#03A9F4',
  owl: '#8D6E63',
  turtle: '#009688',
  frog: '#8BC34A',
  rabbit: '#FFCCBC',
  fox: '#FF5722',
  bear: '#795548',
  wolf: '#78909C',
  deer: '#A1887F',
  squirrel: '#FF8A65',
  // Plants
  flower: '#F48FB1',
  sunflower: '#FFC107',
  tree: '#4CAF50',
  leaf: '#81C784',
  mushroom: '#D7CCC8',
  cactus: '#66BB6A',
}

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
    profile_image?: string
    profile_image_type?: string
  }
  offer_id?: number
  need_id?: number
  status: 'pending' | 'accepted' | 'completed' | 'declined'
  message: string
  selected_slot?: string
  hours_contributed?: number
  provider_confirmed?: boolean
  requester_confirmed?: boolean
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
  hours: number
  participants: Participant[]
  created_at: string
  creator_username?: string
  creator_profile_image?: string
  creator_profile_image_type?: string
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
    profile_image?: string
    profile_image_type?: string
  }
  status: 'pending' | 'accepted' | 'completed' | 'declined'
  message: string
  selected_slot?: string  // JSON array of selected time slots
  hours_contributed?: number
  provider_confirmed?: boolean
  requester_confirmed?: boolean
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
 * - POST /api/v1/handshake/{handshake_id}/accept - Accept participant (via handshake API)
 * - POST /api/v1/participants/exchange/{participant_id}/complete - Complete exchange
 */
export default function ActiveItems() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  // Initialize tab from URL params (tab=applications means index 1)
  const initialTab = searchParams.get('tab') === 'applications' ? 1 : 0
  const [activeTab, setActiveTab] = useState(initialTab)

  // Clear URL params after applying
  useEffect(() => {
    if (searchParams.get('tab')) {
      setSearchParams({}, { replace: true })
    }
  }, [])
  const [acceptDialogOpen, setAcceptDialogOpen] = useState(false)
    const [completeDialogOpen, setCompleteDialogOpen] = useState(false)
  const [withdrawDialogOpen, setWithdrawDialogOpen] = useState(false)
  const [declineDialogOpen, setDeclineDialogOpen] = useState(false)
  const [selectedParticipant, setSelectedParticipant] = useState<Participant | null>(null)
    const [selectedPost, setSelectedPost] = useState<MyPost | null>(null)
  const [withdrawParticipantId, setWithdrawParticipantId] = useState<number | null>(null)
  const [declineParticipantId, setDeclineParticipantId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
    const [completeSuccess, setCompleteSuccess] = useState<{
        hours: number
        newBalance: number
        isPartial?: boolean
    } | null>(null)

  // Rating dialog state
  const [ratingDialogOpen, setRatingDialogOpen] = useState(false)
  const [ratingData, setRatingData] = useState<{
    participantId: number
    recipientId: number
    recipientName: string
    exchangeTitle: string
  } | null>(null)

  // Exchange context for rating after completion
  const [completionContext, setCompletionContext] = useState<{
    participantId: number
    otherUserId: number
    otherUserName: string
    exchangeTitle: string
  } | null>(null)

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
              creator_username: offer.creator?.username || user?.username,
              creator_profile_image: offer.creator?.profile_image || user?.profile_image,
              creator_profile_image_type: offer.creator?.profile_image_type || user?.profile_image_type,
            }
          } catch (error) {
            return {
              ...offer,
              type: 'offer' as const,
              participants: [],
              creator_username: offer.creator?.username || user?.username,
              creator_profile_image: offer.creator?.profile_image || user?.profile_image,
              creator_profile_image_type: offer.creator?.profile_image_type || user?.profile_image_type,
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
              creator_username: need.creator?.username || user?.username,
              creator_profile_image: need.creator?.profile_image || user?.profile_image,
              creator_profile_image_type: need.creator?.profile_image_type || user?.profile_image_type,
            }
          } catch (error) {
            return {
              ...need,
              type: 'need' as const,
              participants: [],
              creator_username: need.creator?.username || user?.username,
              creator_profile_image: need.creator?.profile_image || user?.profile_image,
              creator_profile_image_type: need.creator?.profile_image_type || user?.profile_image_type,
            }
          }
        })
      )
      return needsWithParticipants
    },
    enabled: !!user,
  })

  // Combine offers and needs into "My Posts" and sort by creation date (newest first)
  const myPosts: MyPost[] = [
    ...(myOffers || []),
    ...(myNeeds || []),
  ].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  // Fetch user's applications (proposals to help others)
  const { data: myApplicationsData, isLoading: applicationsLoading } = useQuery({
    queryKey: ['myApplications'],
    queryFn: async () => {
        // Use the handshake API to get user's proposals
        const response = await apiClient.get('/handshake/my-proposals', {
            params: {
                status_filter: 'all', // Get all statuses
                limit: 100, // Get up to 100 proposals
            },
        })

        const proposals = response.data.items || []

        // Fetch offer/need details for each proposal
        const applications: MyApplication[] = await Promise.all(
            proposals.map(async (proposal: any) => {
          try {
              let item_title = 'Unknown'
              let item_creator = {
                  id: 0,
                  username: 'Unknown',
                  display_name: undefined,
            }
              let item_id = 0
              let type: 'offer' | 'need' = 'offer'

              if (proposal.offer_id) {
                  const offerRes = await apiClient.get(`/offers/${proposal.offer_id}`)
                  item_title = offerRes.data.title
                  item_creator = {
                      id: offerRes.data.creator_id,
                      username: offerRes.data.creator?.username || 'Unknown',
                      display_name: offerRes.data.creator?.display_name,
                    profile_image: offerRes.data.creator?.profile_image,
                    profile_image_type: offerRes.data.creator?.profile_image_type,
                  }
                item_id = proposal.offer_id
                type = 'offer'
            } else if (proposal.need_id) {
                const needRes = await apiClient.get(`/needs/${proposal.need_id}`)
                item_title = needRes.data.title
                item_creator = {
                    id: needRes.data.creator_id,
                    username: needRes.data.creator?.username || 'Unknown',
                    display_name: needRes.data.creator?.display_name,
                  profile_image: needRes.data.creator?.profile_image,
                  profile_image_type: needRes.data.creator?.profile_image_type,
              }
                item_id = proposal.need_id
                type = 'need'
            }

              return {
                  id: proposal.id,
                  type,
                  item_id,
                  item_title,
                  item_creator,
                  status: proposal.status,
                  message: proposal.message || '',
                selected_slot: proposal.selected_slot,
                  hours_contributed: proposal.hours_contributed,
                  provider_confirmed: proposal.provider_confirmed,
                  requester_confirmed: proposal.requester_confirmed,
                  created_at: proposal.created_at,
              }
          } catch (error) {
              console.error('Error fetching item details for proposal:', error)
              // Return a fallback object
              return {
                  id: proposal.id,
                  type: proposal.offer_id ? 'offer' as const : 'need' as const,
                  item_id: proposal.offer_id || proposal.need_id || 0,
                  item_title: 'Item details unavailable',
                  item_creator: {
                    id: 0,
                    username: 'Unknown',
                    display_name: undefined,
                    profile_image: undefined,
                    profile_image_type: undefined,
                },
                  status: proposal.status,
                  message: proposal.message || '',
                selected_slot: proposal.selected_slot,
                  hours_contributed: proposal.hours_contributed,
                  provider_confirmed: proposal.provider_confirmed,
                  requester_confirmed: proposal.requester_confirmed,
                  created_at: proposal.created_at,
              }
          }
        })
      )

      return applications
    },
      enabled: !!user,
  })

  const myApplications: MyApplication[] = myApplicationsData || []

  // Accept participant mutation
  const acceptMutation = useMutation({
    mutationFn: async ({ participantId, hours }: {
      participantId: number
      hours: number
    }) => {
      // Use handshake API to accept the participant
      const response = await apiClient.post(`/handshake/${participantId}/accept`, null, {
        params: { hours }
      })
      return response.data
    },
    onSuccess: () => {
        setAcceptDialogOpen(false)
      setError(null)
      queryClient.invalidateQueries({ queryKey: ['myOffers'] })
      queryClient.invalidateQueries({ queryKey: ['myNeeds'] })
    },
    onError: (err: any) => {
      const errorMessage = err.response?.data?.detail || 'Unable to accept this request. Please try again.'
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

    // Complete Exchange mutation
    const completeMutation = useMutation({
        mutationFn: async (participantId: number) => {
            const response = await apiClient.post(`/participants/exchange/${participantId}/complete`)
            return response.data
        },
        onSuccess: (data) => {
            // Check if this is a partial confirmation (only one party confirmed)
            if (data.status === 'pending_confirmation') {
                setCompleteSuccess({
                    hours: 0,
                    newBalance: 0,
                    isPartial: true,
                })
            } else {
                // Full completion - show balance update
                const isProvider = data.provider_id === user?.id
                setCompleteSuccess({
                    hours: data.hours,
                    newBalance: isProvider ? data.provider_new_balance : data.requester_new_balance,
                    isPartial: false,
                })
            }
            queryClient.invalidateQueries({ queryKey: ['myOffers'] })
            queryClient.invalidateQueries({ queryKey: ['myNeeds'] })
            queryClient.invalidateQueries({ queryKey: ['myApplications'] })
        },
        onError: (err: any) => {
            const errorMessage = err.response?.data?.detail || 'Unable to complete this exchange. Please try again.'
            setError(errorMessage)
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

    // Use handshake API - pass participant ID (which is the handshake ID) and hours
    acceptMutation.mutate({
      participantId: selectedParticipant.id,
      hours: selectedPost.hours,
    })
  }

  const handleDecline = (participantId: number) => {
    setDeclineParticipantId(participantId)
    setDeclineDialogOpen(true)
  }

  const handleDeclineConfirm = () => {
    if (declineParticipantId) {
      declineMutation.mutate(declineParticipantId)
      setDeclineDialogOpen(false)
      setDeclineParticipantId(null)
    }
  }

  const handleWithdraw = (participantId: number) => {
    setWithdrawParticipantId(participantId)
    setWithdrawDialogOpen(true)
  }

  const handleWithdrawConfirm = () => {
    if (withdrawParticipantId) {
      declineMutation.mutate(withdrawParticipantId)
      setWithdrawDialogOpen(false)
      setWithdrawParticipantId(null)
    }
  }

  const handleCompleteClick = (item: Participant | MyApplication, post?: MyPost) => {
        // For MyApplication, we only need the id for completion
        if ('item_id' in item) {
          // It's a MyApplication - the other user is the item creator
            setSelectedParticipant({ id: item.id } as Participant)
          setCompletionContext({
            participantId: item.id,
            otherUserId: item.item_creator.id,
            otherUserName: item.item_creator.display_name || item.item_creator.username,
            exchangeTitle: item.item_title,
          })
        } else {
          // It's a Participant from My Posts - the other user is the participant
            setSelectedParticipant(item)
          setCompletionContext({
            participantId: item.id,
            otherUserId: item.user_id,
            otherUserName: item.user?.display_name || item.user?.username || 'User',
            exchangeTitle: post?.title || 'Exchange',
          })
        }
        setCompleteDialogOpen(true)
        setError(null)
        setCompleteSuccess(null)
    }

    const handleCompleteSubmit = () => {
        if (!selectedParticipant) return
        completeMutation.mutate(selectedParticipant.id)
    }

  const handleCompleteDialogClose = (openRating: boolean = false) => {
        setCompleteDialogOpen(false)
        setSelectedParticipant(null)
        setError(null)

      // User can rate as soon as they confirm (even for partial confirmation)
      if (openRating && completeSuccess && completionContext) {
        setRatingData({
          participantId: completionContext.participantId,
          recipientId: completionContext.otherUserId,
          recipientName: completionContext.otherUserName,
          exchangeTitle: completionContext.exchangeTitle,
        })
        setRatingDialogOpen(true)
      }

        setCompleteSuccess(null)
      setCompletionContext(null)
    }

  const handleViewPost = (postId: number, postType: 'offer' | 'need') => {
      const path = postType === 'offer' ? `/offers/${postId}` : `/needs/${postId}`
      console.log('Navigating to:', path)
      navigate(path)
  }

  const formatStatus = (status: string) => {
    return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase()
  }

  const parseSelectedSlots = (slotString?: string): string[] => {
    if (!slotString) return []
    try {
      const parsed = JSON.parse(slotString)
      return Array.isArray(parsed) ? parsed : []
    } catch {
      return []
    }
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
                            label={formatStatus(post.status)}
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
                                  sx={{
                                    width: 48,
                                    height: 48,
                                    bgcolor: participant.user.profile_image_type === 'preset' && participant.user.profile_image
                                      ? AVATAR_COLORS[participant.user.profile_image] || 'primary.main'
                                      : 'primary.main',
                                    fontSize: '1.5rem',
                                    cursor: 'pointer'
                                  }}
                                  onClick={() => navigate(`/profile/${participant.user.username}`)}
                                >
                                  {participant.user.profile_image_type === 'preset' && participant.user.profile_image ? (
                                    AVATAR_EMOJIS[participant.user.profile_image] || participant.user.profile_image
                                  ) : participant.user.profile_image_type === 'custom' ? (
                                      <PersonIcon />
                                  ) : (
                                    <PersonIcon />
                                  )}
                                </Avatar>
                                <Box sx={{ flex: 1 }}>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                                <Typography
                                                    variant="subtitle2"
                                                    fontWeight={600}
                                                    onClick={() => navigate(`/profile/${participant.user.username}`)}
                                                    sx={{
                                                        cursor: 'pointer',
                                                        '&:hover': { color: 'primary.main', textDecoration: 'underline' }
                                                    }}
                                                >
                                      {participant.user.display_name || participant.user.username}
                                    </Typography>
                                    <Chip
                                      label={formatStatus(participant.status)}
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
                                                onClick={() => navigate(`/profile/${participant.user.username}`)}
                                            >
                                    @{participant.user.username}
                                  </Typography>

                                  {/* Application Date */}
                                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                                    Applied {formatDate(participant.created_at)}
                                  </Typography>

                                  {/* Message */}
                                  {participant.message && (
                                    <Box sx={{ mb: 1 }}>
                                      <Typography variant="caption" fontWeight={600} color="text.secondary">
                                        Message:
                                      </Typography>
                                      <Typography variant="body2" sx={{ mt: 0.5 }}>
                                        {participant.message}
                                      </Typography>
                                    </Box>
                                  )}

                                  {/* Selected Time Slots */}
                                  {participant.selected_slot && parseSelectedSlots(participant.selected_slot).length > 0 && (
                                    <Box sx={{ mb: 1 }}>
                                      <Typography variant="caption" fontWeight={600} color="text.secondary" display="block" gutterBottom>
                                        Preferred Time Slots:
                                      </Typography>
                                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                        {parseSelectedSlots(participant.selected_slot).map((slot, idx) => (
                                          <Chip
                                            key={idx}
                                            label={slot}
                                            size="small"
                                            variant="outlined"
                                            color="primary"
                                          />
                                        ))}
                                      </Box>
                                    </Box>
                                  )}

                                  {participant.hours_contributed > 0 && (
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

                                    {/* Action Button for Accepted - Complete Exchange */}
                                    {participant.status === 'accepted' && (
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, alignItems: 'flex-end' }}>
                                  {/* Show confirmation status with usernames and avatars */}
                                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                                    {/* Provider chip (for Offer: creator, for Need: participant) */}
                                                <Chip
                                      avatar={
                                        <Avatar
                                          sx={{
                                            width: 24,
                                            height: 24,
                                            bgcolor: post.type === 'offer'
                                              ? (post.creator_profile_image_type === 'preset' && post.creator_profile_image ? AVATAR_COLORS[post.creator_profile_image as keyof typeof AVATAR_COLORS] : '#1976d2')
                                              : (participant.user.profile_image_type === 'preset' && participant.user.profile_image ? AVATAR_COLORS[participant.user.profile_image as keyof typeof AVATAR_COLORS] : '#1976d2'),
                                            fontSize: '0.875rem'
                                          }}
                                        >
                                          {post.type === 'offer'
                                            ? (post.creator_profile_image_type === 'preset' && post.creator_profile_image ? AVATAR_EMOJIS[post.creator_profile_image as keyof typeof AVATAR_EMOJIS] : post.creator_username?.charAt(0).toUpperCase())
                                            : (participant.user.profile_image_type === 'preset' && participant.user.profile_image ? AVATAR_EMOJIS[participant.user.profile_image as keyof typeof AVATAR_EMOJIS] : participant.user.username?.charAt(0).toUpperCase())
                                          }
                                        </Avatar>
                                      }
                                      label={
                                        participant.provider_confirmed
                                          ? `${post.type === 'offer' ? post.creator_username : participant.user.username} ✓`
                                          : `Waiting for ${post.type === 'offer' ? post.creator_username : participant.user.username}`
                                      }
                                                    size="small"
                                      color={participant.provider_confirmed ? "success" : "warning"}
                                                    variant={participant.provider_confirmed ? "filled" : "outlined"}
                                      onClick={() => navigate(`/profile/${post.type === 'offer' ? post.creator_username : participant.user.username}`)}
                                      sx={{ cursor: 'pointer' }}
                                                />
                                    {/* Requester chip (for Offer: participant, for Need: creator) */}
                                                <Chip
                                      avatar={
                                        <Avatar
                                          sx={{
                                            width: 24,
                                            height: 24,
                                            bgcolor: post.type === 'need'
                                              ? (post.creator_profile_image_type === 'preset' && post.creator_profile_image ? AVATAR_COLORS[post.creator_profile_image as keyof typeof AVATAR_COLORS] : '#1976d2')
                                              : (participant.user.profile_image_type === 'preset' && participant.user.profile_image ? AVATAR_COLORS[participant.user.profile_image as keyof typeof AVATAR_COLORS] : '#1976d2'),
                                            fontSize: '0.875rem'
                                          }}
                                        >
                                          {post.type === 'need'
                                            ? (post.creator_profile_image_type === 'preset' && post.creator_profile_image ? AVATAR_EMOJIS[post.creator_profile_image as keyof typeof AVATAR_EMOJIS] : post.creator_username?.charAt(0).toUpperCase())
                                            : (participant.user.profile_image_type === 'preset' && participant.user.profile_image ? AVATAR_EMOJIS[participant.user.profile_image as keyof typeof AVATAR_EMOJIS] : participant.user.username?.charAt(0).toUpperCase())
                                          }
                                        </Avatar>
                                      }
                                      label={
                                        participant.requester_confirmed
                                          ? `${post.type === 'need' ? post.creator_username : participant.user.username} ✓`
                                          : `Waiting for ${post.type === 'need' ? post.creator_username : participant.user.username}`
                                      }
                                                    size="small"
                                      color={participant.requester_confirmed ? "success" : "warning"}
                                                    variant={participant.requester_confirmed ? "filled" : "outlined"}
                                      onClick={() => navigate(`/profile/${post.type === 'need' ? post.creator_username : participant.user.username}`)}
                                      sx={{ cursor: 'pointer' }}
                                                />
                                            </Box>
                                            {/* Show Rate button if current user (requester/post owner) has confirmed */}
                                            {participant.requester_confirmed ? (
                                                <Button
                                                    variant="outlined"
                                                    color="primary"
                                                    size="small"
                                                    startIcon={<StarIcon />}
                                                    onClick={() => {
                                                        setRatingData({
                                                            participantId: participant.id,
                                                            recipientId: participant.user_id,
                                                            recipientName: participant.user?.display_name || participant.user?.username || 'User',
                                                            exchangeTitle: post.title,
                                                        })
                                                        setRatingDialogOpen(true)
                                                    }}
                                                >
                                                    Rate User
                                                </Button>
                                            ) : (
                                                <Tooltip title="Confirm completion">
                                                    <Button
                                                        variant="contained"
                                                        color="primary"
                                                        size="small"
                                                        startIcon={<CompleteIcon />}
                                                        onClick={() => handleCompleteClick(participant, post)}
                                                        disabled={completeMutation.isPending}
                                                    >
                                                        Confirm Complete
                                                    </Button>
                                                </Tooltip>
                                            )}
                                        </Box>
                                    )}

                                    {/* Action Button for Completed - Rate User */}
                                    {participant.status === 'completed' && (
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, alignItems: 'flex-end' }}>
                                            <Chip
                                                label="Completed"
                                                size="small"
                                                color="success"
                                                icon={<CompleteIcon />}
                                            />
                                            <Button
                                                variant="outlined"
                                                color="primary"
                                                size="small"
                                                startIcon={<StarIcon />}
                                                onClick={() => {
                                                    setRatingData({
                                                        participantId: participant.id,
                                                        recipientId: participant.user_id,
                                                        recipientName: participant.user?.display_name || participant.user?.username || 'User',
                                                        exchangeTitle: post.title,
                                                    })
                                                    setRatingDialogOpen(true)
                                                }}
                                            >
                                                Rate User
                                            </Button>
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
                            label={formatStatus(application.status)}
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
                          <Avatar
                            sx={{
                              width: 32,
                              height: 32,
                              bgcolor: application.item_creator.profile_image_type === 'preset' && application.item_creator.profile_image
                                ? AVATAR_COLORS[application.item_creator.profile_image] || 'primary.main'
                                : 'primary.main',
                              fontSize: '1.2rem',
                              cursor: 'pointer'
                            }}
                            onClick={() => navigate(`/profile/${application.item_creator.username}`)}
                          >
                            {application.item_creator.profile_image_type === 'preset' && application.item_creator.profile_image ? (
                              AVATAR_EMOJIS[application.item_creator.profile_image] || application.item_creator.profile_image
                            ) : application.item_creator.profile_image_type === 'custom' ? (
                              <PersonIcon fontSize="small" />
                            ) : (
                              <PersonIcon fontSize="small" />
                            )}
                          </Avatar>
                          <Typography
                            variant="body2"
                            color="primary"
                            sx={{ cursor: 'pointer', fontWeight: 500, '&:hover': { textDecoration: 'underline' } }}
                            onClick={() => navigate(`/profile/${application.item_creator.username}`)}
                          >
                            {application.item_creator.display_name || application.item_creator.username}
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

                    {/* Selected Time Slots */}
                    {application.selected_slot && parseSelectedSlots(application.selected_slot).length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                          Your Preferred Time Slots
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {parseSelectedSlots(application.selected_slot).map((slot, idx) => (
                            <Chip
                              key={idx}
                              label={slot}
                              size="small"
                              variant="outlined"
                              color="primary"
                            />
                          ))}
                        </Box>
                      </Box>
                    )}

                    {/* Hours if accepted */}
                    {application.hours_contributed > 0 && (
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
                          onClick={() => {
                            console.log('Withdraw clicked for application:', application.id)
                            handleWithdraw(application.id)
                          }}
                          disabled={declineMutation.isPending}
                        >
                          Withdraw Application
                        </Button>
                      )}
                      {application.status === 'accepted' && (
                                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: '100%' }}>
                                        <Alert severity="success">
                                            Accepted! Both parties must confirm completion to finalize the exchange.
                                        </Alert>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                            {/* Show confirmation status with usernames and avatars */}
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                              {/* Provider chip (for Offer: creator, for Need: current user) */}
                                                <Chip
                                avatar={
                                  <Avatar
                                    sx={{
                                      width: 24,
                                      height: 24,
                                      bgcolor: application.type === 'offer'
                                        ? (application.item_creator.profile_image_type === 'preset' && application.item_creator.profile_image ? AVATAR_COLORS[application.item_creator.profile_image as keyof typeof AVATAR_COLORS] : '#1976d2')
                                        : (user?.profile_image_type === 'preset' && user?.profile_image ? AVATAR_COLORS[user.profile_image as keyof typeof AVATAR_COLORS] : '#1976d2'),
                                      fontSize: '0.875rem'
                                    }}
                                  >
                                    {application.type === 'offer'
                                      ? (application.item_creator.profile_image_type === 'preset' && application.item_creator.profile_image ? AVATAR_EMOJIS[application.item_creator.profile_image as keyof typeof AVATAR_EMOJIS] : application.item_creator.username?.charAt(0).toUpperCase())
                                      : (user?.profile_image_type === 'preset' && user?.profile_image ? AVATAR_EMOJIS[user.profile_image as keyof typeof AVATAR_EMOJIS] : user?.username?.charAt(0).toUpperCase())
                                    }
                                  </Avatar>
                                }
                                label={
                                  application.provider_confirmed
                                    ? `${application.type === 'offer' ? application.item_creator.username : user?.username} ✓`
                                    : `Waiting for ${application.type === 'offer' ? application.item_creator.username : user?.username}`
                                }
                                                    size="small"
                                color={application.provider_confirmed ? "success" : "warning"}
                                                    variant={application.provider_confirmed ? "filled" : "outlined"}
                                onClick={() => navigate(`/profile/${application.type === 'offer' ? application.item_creator.username : user?.username}`)}
                                sx={{ cursor: 'pointer' }}
                                                />
                              {/* Requester chip (for Offer: current user, for Need: creator) */}
                                                <Chip
                                avatar={
                                  <Avatar
                                    sx={{
                                      width: 24,
                                      height: 24,
                                      bgcolor: application.type === 'need'
                                        ? (application.item_creator.profile_image_type === 'preset' && application.item_creator.profile_image ? AVATAR_COLORS[application.item_creator.profile_image as keyof typeof AVATAR_COLORS] : '#1976d2')
                                        : (user?.profile_image_type === 'preset' && user?.profile_image ? AVATAR_COLORS[user.profile_image as keyof typeof AVATAR_COLORS] : '#1976d2'),
                                      fontSize: '0.875rem'
                                    }}
                                  >
                                    {application.type === 'need'
                                      ? (application.item_creator.profile_image_type === 'preset' && application.item_creator.profile_image ? AVATAR_EMOJIS[application.item_creator.profile_image as keyof typeof AVATAR_EMOJIS] : application.item_creator.username?.charAt(0).toUpperCase())
                                      : (user?.profile_image_type === 'preset' && user?.profile_image ? AVATAR_EMOJIS[user.profile_image as keyof typeof AVATAR_EMOJIS] : user?.username?.charAt(0).toUpperCase())
                                    }
                                  </Avatar>
                                }
                                label={
                                  application.requester_confirmed
                                    ? `${application.type === 'need' ? application.item_creator.username : user?.username} ✓`
                                    : `Waiting for ${application.type === 'need' ? application.item_creator.username : user?.username}`
                                }
                                                    size="small"
                                color={application.requester_confirmed ? "success" : "warning"}
                                                    variant={application.requester_confirmed ? "filled" : "outlined"}
                                onClick={() => navigate(`/profile/${application.type === 'need' ? application.item_creator.username : user?.username}`)}
                                sx={{ cursor: 'pointer' }}
                                                />
                                            </Box>
                                            {/* Show Rate button if current user (provider/applicant) has confirmed */}
                                            {application.provider_confirmed ? (
                                                <Button
                                                    variant="outlined"
                                                    color="primary"
                                                    startIcon={<StarIcon />}
                                                    onClick={() => {
                                                        setRatingData({
                                                            participantId: application.id,
                                                            recipientId: application.item_creator.id,
                                                            recipientName: application.item_creator.display_name || application.item_creator.username,
                                                            exchangeTitle: application.item_title,
                                                        })
                                                        setRatingDialogOpen(true)
                                                    }}
                                                >
                                                    Rate User
                                                </Button>
                                            ) : (
                                                <Button
                                                    variant="contained"
                                                    color="primary"
                                                    startIcon={<CompleteIcon />}
                                                    onClick={() => handleCompleteClick(application)}
                                                    disabled={completeMutation.isPending}
                                                >
                                                    Confirm Complete
                                                </Button>
                                            )}
                                        </Box>
                                    </Box>
                      )}
                      {application.status === 'completed' && (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: '100%' }}>
                          <Alert severity="info">
                            This exchange has been completed. Check your TimeBank balance for the hours earned.
                          </Alert>
                          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                            <Button
                              variant="outlined"
                              color="primary"
                              startIcon={<StarIcon />}
                              onClick={() => {
                                setRatingData({
                                  participantId: application.id,
                                  recipientId: application.item_creator.id,
                                  recipientName: application.item_creator.display_name || application.item_creator.username,
                                  exchangeTitle: application.item_title,
                                })
                                setRatingDialogOpen(true)
                              }}
                            >
                              Rate User
                            </Button>
                          </Box>
                        </Box>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

          <Dialog
              open={completeDialogOpen}
              onClose={() => !completeMutation.isPending && handleCompleteDialogClose()}
              maxWidth="sm"
              fullWidth
          >
              <DialogTitle>
                  {completeSuccess 
                      ? (completeSuccess.isPartial ? 'Confirmation Recorded!' : 'Exchange Completed!')
                      : 'Confirm Exchange Completion'}
              </DialogTitle>
              <DialogContent>
                  {completeSuccess ? (
                      completeSuccess.isPartial ? (
                          <>
                              <Alert severity="info" sx={{ mb: 2 }}>
                                  Your confirmation has been recorded!
                              </Alert>
                              <Typography variant="body2" color="text.secondary" paragraph>
                                  The exchange will be finalized once the other party also confirms completion.
                              </Typography>
                              <Typography variant="body2" color="text.secondary" paragraph>
                                  TimeBank hours will be transferred after both parties confirm.
                              </Typography>
                              <Alert severity="info" sx={{ mt: 2 }}>
                                  <Typography variant="body2">
                                      TimeBank hours will be transferred once the other party also confirms.
                                  </Typography>
                              </Alert>
                          </>
                      ) : (
                          <>
                              <Alert severity="success" sx={{ mb: 2 }}>
                                  The exchange has been successfully completed!
                              </Alert>
                              <Typography variant="body2" color="text.secondary" paragraph>
                                  <strong>{completeSuccess.hours}</strong> hours have been transferred.
                              </Typography>
                              <Typography variant="body2" color="text.secondary" paragraph>
                                  Your new balance: <strong>{Math.round(completeSuccess.newBalance)}</strong> hours
                              </Typography>
                          </>
                      )
                  ) : (
                      <>
                          <Typography variant="body2" color="text.secondary" paragraph>
                              Confirm that this exchange has been completed. Both parties must confirm for hours to transfer.
                          </Typography>
                          <Box component="ul" sx={{ pl: 2, mb: 2 }}>
                              <Typography component="li" variant="body2" color="text.secondary">
                                  Both provider and requester must confirm
                              </Typography>
                              <Typography component="li" variant="body2" color="text.secondary">
                                  TimeBank hours transfer when both confirm
                              </Typography>
                              <Typography component="li" variant="body2" color="text.secondary">
                                  You can rate the other party immediately after confirming
                              </Typography>
                          </Box>

                          {error && (
                              <Alert severity="error" sx={{ mb: 2 }}>
                                  {error}
                              </Alert>
                          )}

                          <Alert severity="info">
                              Make sure the real-world exchange has happened before confirming.
                          </Alert>
                      </>
                  )}
              </DialogContent>
              <DialogActions>
                  {completeSuccess ? (
                      <>
                        <Button onClick={() => handleCompleteDialogClose(false)} variant="outlined">
                          Close
                        </Button>
                        <Button
                          onClick={() => handleCompleteDialogClose(true)}
                          variant="contained"
                          color="primary"
                          startIcon={<StarIcon />}
                        >
                          Rate User
                        </Button>
                      </>
                  ) : (
                      <>
                          <Button
                              onClick={() => handleCompleteDialogClose(false)}
                              disabled={completeMutation.isPending}
                          >
                              Cancel
                          </Button>
                          <Button
                              onClick={handleCompleteSubmit}
                              variant="contained"
                              color="primary"
                              disabled={completeMutation.isPending}
                              startIcon={completeMutation.isPending ? <CircularProgress size={20} /> : <CompleteIcon />}
                          >
                              {completeMutation.isPending ? 'Confirming...' : 'Confirm Completion'}
                          </Button>
                      </>
                  )}
              </DialogActions>
          </Dialog>

      {/* Accept Dialog */}
      <Dialog
        open={acceptDialogOpen}
        onClose={() => !acceptMutation.isPending && setAcceptDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Accept Application</DialogTitle>
        <DialogContent>
                  {selectedParticipant && selectedPost && (
            <>
              <Typography variant="body2" color="text.secondary" paragraph>
                              Accept <strong>{selectedParticipant.user.username}</strong>'s application?
              </Typography>

                          <Alert severity="info" sx={{ mb: 2 }}>
                              This exchange is for <strong>{selectedPost.hours}</strong> TimeBank hour{selectedPost.hours !== 1 ? 's' : ''}.
                          </Alert>

              {error && (
                              <Alert severity="error">
                  {error}
                </Alert>
                          )}
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

      {/* Rating Dialog */}
      {ratingData && (
        <RatingSubmitDialog
          open={ratingDialogOpen}
          onClose={() => {
            setRatingDialogOpen(false)
            setRatingData(null)
          }}
          participantId={ratingData.participantId}
          recipientId={ratingData.recipientId}
          recipientName={ratingData.recipientName}
          exchangeTitle={ratingData.exchangeTitle}
        />
      )}

      {/* Withdraw Confirmation Dialog */}
      <Dialog
        open={withdrawDialogOpen}
        onClose={() => !declineMutation.isPending && setWithdrawDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Withdraw Application</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            Are you sure you want to withdraw your application? This action cannot be undone.
          </Typography>
          <Alert severity="warning">
            The creator will be notified that you have withdrawn your application.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setWithdrawDialogOpen(false)}
            disabled={declineMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            onClick={handleWithdrawConfirm}
            variant="contained"
            color="error"
            disabled={declineMutation.isPending}
          >
            {declineMutation.isPending ? 'Withdrawing...' : 'Withdraw Application'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Decline Confirmation Dialog */}
      <Dialog
        open={declineDialogOpen}
        onClose={() => !declineMutation.isPending && setDeclineDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Decline Application</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            Are you sure you want to decline this application? This action cannot be undone.
          </Typography>
          <Alert severity="warning">
            The applicant will be notified that their application has been declined.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setDeclineDialogOpen(false)}
            disabled={declineMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDeclineConfirm}
            variant="contained"
            color="error"
            disabled={declineMutation.isPending}
          >
            {declineMutation.isPending ? 'Declining...' : 'Decline Application'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
