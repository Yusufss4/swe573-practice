// SRS FR-2 & FR-10: User Profile with Stats, Badges, and Ratings
// Public profile view displaying user info, TimeBank stats, and feedback

import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  Chip,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  IconButton,
  Divider,
  Paper,
  Rating as MuiRating,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Person as PersonIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  AccountBalance as BalanceIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  EmojiEvents as TrophyIcon,
  Star as StarIcon,
  Verified as VerifiedIcon,
  Schedule as ScheduleIcon,
  Favorite as FavoriteIcon,
  Support as SupportIcon,
  Edit as EditIcon,
  PhotoCamera as PhotoCameraIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { RatingsList } from '@/components/RatingDisplay'
import { useAuth } from '@/contexts/AuthContext'

// Preset avatar emoji mappings - expanded with more options
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

// SRS FR-2: User profile data structure
interface UserProfile {
  id: number
  username: string
  display_name?: string | null
  description?: string | null
  profile_image?: string | null
  profile_image_type: string
  location_name?: string | null
  balance: number
  stats: {
    balance: number
    hours_given: number
    hours_received: number
    completed_exchanges: number
    ratings_received: number
  }
  tags: string[]
  created_at: string
}

// Rating summary for category averages
interface RatingSummary {
  user_id: number
  total_ratings: number
  average_general: number | null
  average_reliability: number | null
  average_kindness: number | null
  average_helpfulness: number | null
  overall_average: number | null
  rating_distribution: Record<number, number>
}

// Completed exchange structure
interface CompletedExchange {
  id: number
  offer_id?: number | null
  need_id?: number | null
  item_title: string
  item_description: string
  item_type: 'offer' | 'need'
  other_user_id: number
  other_username: string
  role: string
  hours: number
  completed_at: string
}

interface CompletedExchangesResponse {
  items: CompletedExchange[]
  total: number
  skip: number
  limit: number
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
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  )
}

// Badge definitions based on user stats
interface Badge {
  id: string
  name: string
  icon: React.ReactNode
  color: string
  description: string
  earned: boolean
}

const getBadges = (profile: UserProfile): Badge[] => {
  const badges: Badge[] = [
    {
      id: 'newcomer',
      name: 'Newcomer',
      icon: <StarIcon />,
      color: '#9E9E9E',
      description: 'Welcome to The Hive!',
      earned: profile.stats.completed_exchanges >= 0,
    },
    {
      id: 'helper',
      name: 'Helper',
      icon: <VerifiedIcon />,
      color: '#2196F3',
      description: 'Completed 5 exchanges',
      earned: profile.stats.completed_exchanges >= 5,
    },
    {
      id: 'hero',
      name: 'Helper Hero',
      icon: <TrophyIcon />,
      color: '#FF9800',
      description: 'Completed 10 exchanges',
      earned: profile.stats.completed_exchanges >= 10,
    },
    {
      id: 'master',
      name: 'Master Helper',
      icon: <TrophyIcon />,
      color: '#FFD700',
      description: 'Completed 25 exchanges',
      earned: profile.stats.completed_exchanges >= 25,
    },
    {
      id: 'generous',
      name: 'Generous Giver',
      icon: <TrendingUpIcon />,
      color: '#4CAF50',
      description: 'Given 50+ hours',
      earned: profile.stats.hours_given >= 50,
    },
  ]

  return badges
}

// Profile Update Data
interface ProfileUpdateData {
  full_name?: string
  description?: string
  profile_image?: string
  profile_image_type?: string
  tags?: string[]
}

/**
 * ProfilePage Component
 * 
 * SRS FR-2: Profile Management
 * SRS FR-10: Ratings and Feedback System
 * 
 * Features:
 * - Display user profile information (avatar, name, bio, location)
 * - Show badge collection based on achievements
 * - Display TimeBank statistics (balance, hours given/received)
 * - Show rating category averages in stats section
 * - Edit profile for own profile (avatar, about, tags)
 * - Two tabs:
 *   1. Activities - completed exchanges
 *   2. Recent Ratings - feedback from other users
 */
export default function ProfilePage() {
  const { username } = useParams<{ username: string }>()
  const navigate = useNavigate()
  const { user: currentUser } = useAuth()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Edit mode states
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editAbout, setEditAbout] = useState('')
  const [editFullName, setEditFullName] = useState('')
  const [editTags, setEditTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')

  // Avatar selection
  const [avatarDialogOpen, setAvatarDialogOpen] = useState(false)
  const [selectedAvatar, setSelectedAvatar] = useState<string>('')
  const [uploadingImage, setUploadingImage] = useState(false)

  // Fetch user profile by username
  const { data: profile, isLoading: profileLoading, error: profileError } = useQuery<UserProfile>({
    queryKey: ['userProfile', username],
    queryFn: async () => {
      const response = await apiClient.get(`/users/username/${username}`)
      return response.data
    },
  })

  // Fetch preset avatars
  const { data: presetAvatars } = useQuery<{ avatars: string[] }>({
    queryKey: ['presetAvatars'],
    queryFn: async () => {
      const response = await apiClient.get('/users/avatars/presets')
      return response.data
    },
  })

  // Check if this is the current user's profile
  const isOwnProfile = currentUser && profile && currentUser.username === profile.username

  // Initialize edit states when profile loads
  useEffect(() => {
    if (profile) {
      setEditAbout(profile.description || '')
      setEditFullName(profile.display_name || '')
      setEditTags(profile.tags || [])
      setSelectedAvatar(profile.profile_image || '')
    }
  }, [profile])

  // Profile update mutation
  const updateProfileMutation = useMutation({
    mutationFn: async (data: ProfileUpdateData) => {
      const response = await apiClient.put('/users/me', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userProfile', username] })
      setEditDialogOpen(false)
    },
  })

  // Avatar update mutation
  const updateAvatarMutation = useMutation({
    mutationFn: async (avatar: string) => {
      const response = await apiClient.put('/users/me', {
        profile_image: avatar,
        profile_image_type: 'preset',
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userProfile', username] })
      setAvatarDialogOpen(false)
    },
  })

  // Image upload mutation
  const uploadImageMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const response = await apiClient.post('/users/me/avatar', formData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userProfile', username] })
      setAvatarDialogOpen(false)
      setUploadingImage(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    },
    onError: (error: Error) => {
      setUploadingImage(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
      alert(`Unable to upload image: ${error.message || 'Please try again.'}`)
    },
  })

  // Remove custom image mutation
  const removeImageMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.delete('/users/me/avatar')
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userProfile', username] })
    },
  })

  // Fetch rating summary for category averages
  const { data: ratingSummary } = useQuery<RatingSummary>({
    queryKey: ['rating-summary', profile?.id],
    queryFn: async () => {
      const response = await apiClient.get(`/ratings/summary/${profile!.id}`)
      return response.data
    },
    enabled: !!profile?.id,
  })

  // Fetch completed exchanges by username
  const { data: exchangesData, isLoading: exchangesLoading } = useQuery<CompletedExchangesResponse>({
    queryKey: ['userCompletedExchanges', username, 'completed'],
    queryFn: async () => {
      const response = await apiClient.get(`/users/username/${username}/completed-exchanges?status_filter=completed`)
      return response.data
    },
    enabled: !!username && activeTab === 1, // Only fetch when on completed activities tab
  })

  // Fetch active exchanges (accepted status)
  const { data: activeExchangesData, isLoading: activeExchangesLoading } = useQuery<CompletedExchangesResponse>({
    queryKey: ['userActiveExchanges', username, 'accepted'],
    queryFn: async () => {
      const response = await apiClient.get(`/users/username/${username}/completed-exchanges?status_filter=accepted`)
      return response.data
    },
    enabled: !!username && activeTab === 0, // Only fetch when on activities tab
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'long',
      year: 'numeric',
    })
  }

  const formatCommentDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  // Handle adding a tag
  const handleAddTag = () => {
    const tag = tagInput.trim().toLowerCase()
    if (tag && !editTags.includes(tag) && editTags.length < 10) {
      setEditTags([...editTags, tag])
      setTagInput('')
    }
  }

  // Handle removing a tag
  const handleRemoveTag = (tagToRemove: string) => {
    setEditTags(editTags.filter(tag => tag !== tagToRemove))
  }

  // Handle save profile
  const handleSaveProfile = () => {
    updateProfileMutation.mutate({
      full_name: editFullName,
      description: editAbout,
      tags: editTags,
    })
  }

  // Handle file upload
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file size (500KB max)
      if (file.size > 500 * 1024) {
        alert('Image too large. Maximum size is 500KB.')
        // Reset input to allow re-selecting
        if (fileInputRef.current) fileInputRef.current.value = ''
        return
      }
      // Validate file type
      if (!['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)) {
        alert('Invalid file type. Please upload a JPEG, PNG, GIF, or WebP image.')
        // Reset input to allow re-selecting
        if (fileInputRef.current) fileInputRef.current.value = ''
        return
      }
      setUploadingImage(true)
      uploadImageMutation.mutate(file)
      // Note: input is reset in onSuccess/onError callbacks
    }
  }

  // Handle tag click - navigate to map with filter (same as OfferDetail/NeedDetail)
  const handleTagClick = (tag: string) => {
    navigate(`/?tag=${encodeURIComponent(tag)}`)
  }

  // Get avatar display
  const getAvatarDisplay = (image: string | null | undefined, imageType: string) => {
    // Custom image (data URL or URL)
    if (imageType === 'custom' && image) {
      return { isCustomImage: true, src: image }
    }
    // Preset emoji avatar
    if (imageType === 'preset' && image && AVATAR_EMOJIS[image]) {
      return {
        emoji: AVATAR_EMOJIS[image],
        bgcolor: AVATAR_COLORS[image],
      }
    }
    return null
  }

  if (profileLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (profileError || !profile) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Unable to load profile. This user may not exist.
        </Alert>
      </Container>
    )
  }

  const badges = getBadges(profile)
  const earnedBadges = badges.filter((b) => b.earned)
  const avatarDisplay = getAvatarDisplay(profile.profile_image, profile.profile_image_type)

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Back Button */}
      <IconButton onClick={() => navigate(-1)} sx={{ mb: 2 }}>
        <ArrowBackIcon />
      </IconButton>

      {/* Profile Header Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            {/* Avatar and Basic Info */}
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                <Box sx={{ position: 'relative' }}>
                  {avatarDisplay && 'isCustomImage' in avatarDisplay ? (
                    // Custom uploaded image
                    <Avatar
                      src={avatarDisplay.src}
                      sx={{
                        width: 120,
                        height: 120,
                        mb: 2,
                        cursor: isOwnProfile ? 'pointer' : 'default',
                        '&:hover': isOwnProfile ? { opacity: 0.8 } : {},
                      }}
                      onClick={() => isOwnProfile && setAvatarDialogOpen(true)}
                    />
                  ) : (
                // Preset emoji or default avatar
                      <Avatar
                        sx={{
                          width: 120,
                          height: 120,
                          bgcolor: avatarDisplay ? avatarDisplay.bgcolor : 'primary.main',
                          fontSize: avatarDisplay ? '4rem' : '3rem',
                          mb: 2,
                          cursor: isOwnProfile ? 'pointer' : 'default',
                          '&:hover': isOwnProfile ? { opacity: 0.8 } : {},
                        }}
                        onClick={() => isOwnProfile && setAvatarDialogOpen(true)}
                      >
                        {avatarDisplay
                          ? avatarDisplay.emoji
                          : (profile.display_name?.[0]?.toUpperCase() || profile.username[0].toUpperCase())
                        }
                      </Avatar>
                  )}
                  {isOwnProfile && (
                    <IconButton
                      size="small"
                      sx={{
                        position: 'absolute',
                        bottom: 16,
                        right: 0,
                        bgcolor: 'background.paper',
                        boxShadow: 1,
                        '&:hover': { bgcolor: 'grey.100' },
                      }}
                      onClick={() => setAvatarDialogOpen(true)}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                  )}
                </Box>
                <Typography variant="h5" fontWeight={600} gutterBottom>
                  {profile.display_name || profile.username}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  @{profile.username}
                </Typography>

                {/* Location */}
                {profile.location_name && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
                    <LocationIcon fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary">
                      {profile.location_name}
                    </Typography>
                  </Box>
                )}

                {/* Member Since */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
                  <CalendarIcon fontSize="small" color="action" />
                  <Typography variant="body2" color="text.secondary">
                    Member since {formatDate(profile.created_at)}
                  </Typography>
                </Box>

                {/* Profile Tags - Clickable to filter map */}
                {profile.tags && profile.tags.length > 0 && (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 2, justifyContent: 'center' }}>
                    {profile.tags.map((tag) => (
                      <Chip
                        key={tag}
                        label={tag}
                        size="small"
                        variant="outlined"
                        color="primary"
                        clickable
                        onClick={() => handleTagClick(tag)}
                        sx={{
                          borderRadius: 2,
                          '&:hover': {
                            bgcolor: 'primary.50',
                            borderColor: 'primary.main',
                          }
                        }}
                      />
                    ))}
                  </Box>
                )}

                {/* Edit Profile Button */}
                {isOwnProfile && (
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={() => setEditDialogOpen(true)}
                    sx={{ mt: 2 }}
                  >
                    Edit Profile
                  </Button>
                )}
              </Box>
            </Grid>

            {/* Bio and Stats */}
            <Grid item xs={12} md={8}>
              {/* Bio */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  About
                </Typography>
                {profile.description ? (
                  <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                    {profile.description}
                  </Typography>
                ) : (
                  <Typography variant="body2" color="text.disabled" fontStyle="italic">
                    {isOwnProfile ? 'Click "Edit Profile" to add a description about yourself.' : 'No description yet.'}
                  </Typography>
                )}
              </Box>

              {/* TimeBank Stats */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  TimeBank Stats
                </Typography>
                <Grid container spacing={2}>
                  {/* Balance */}
                  <Grid item xs={6} sm={4}>
                    <Paper elevation={0} sx={{ p: 2, bgcolor: 'primary.50', border: '1px solid', borderColor: 'primary.200' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <BalanceIcon color="primary" />
                        <Typography variant="caption" color="text.secondary">
                          Balance
                        </Typography>
                      </Box>
                      <Typography variant="h4" fontWeight={600} color="primary.main">
                        {Math.round(profile.stats.balance)}h
                      </Typography>
                    </Paper>
                  </Grid>

                  {/* Hours Given */}
                  <Grid item xs={6} sm={4}>
                    <Paper elevation={0} sx={{ p: 2, bgcolor: 'success.50', border: '1px solid', borderColor: 'success.200' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <TrendingUpIcon color="success" />
                        <Typography variant="caption" color="text.secondary">
                          Hours Given
                        </Typography>
                      </Box>
                      <Typography variant="h4" fontWeight={600} color="success.main">
                        {Math.round(profile.stats.hours_given)}h
                      </Typography>
                    </Paper>
                  </Grid>

                  {/* Hours Received */}
                  <Grid item xs={6} sm={4}>
                    <Paper elevation={0} sx={{ p: 2, bgcolor: 'info.50', border: '1px solid', borderColor: 'info.200' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <TrendingDownIcon color="info" />
                        <Typography variant="caption" color="text.secondary">
                          Hours Received
                        </Typography>
                      </Box>
                      <Typography variant="h4" fontWeight={600} color="info.main">
                        {Math.round(profile.stats.hours_received)}h
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>

                {/* Rating Categories under TimeBank Stats */}
                {ratingSummary && ratingSummary.total_ratings > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Rating Averages ({ratingSummary.total_ratings} rating{ratingSummary.total_ratings !== 1 ? 's' : ''})
                    </Typography>
                    <Grid container spacing={2}>
                      {/* Overall */}
                      <Grid item xs={6} sm={3}>
                        <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', border: '1px solid', borderColor: 'grey.200' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                            <StarIcon sx={{ fontSize: 16, color: 'warning.main' }} />
                            <Typography variant="caption" color="text.secondary">
                              Overall
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Typography variant="h6" fontWeight={600}>
                              {ratingSummary.overall_average?.toFixed(1) || '-'}
                            </Typography>
                            <MuiRating value={ratingSummary.overall_average || 0} readOnly precision={0.1} size="small" max={1} />
                          </Box>
                        </Paper>
                      </Grid>
                      {/* Reliability */}
                      <Grid item xs={6} sm={3}>
                        <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', border: '1px solid', borderColor: 'grey.200' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                            <ScheduleIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                            <Typography variant="caption" color="text.secondary">
                              Reliability
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Typography variant="h6" fontWeight={600}>
                              {ratingSummary.average_reliability?.toFixed(1) || '-'}
                            </Typography>
                            <MuiRating value={ratingSummary.average_reliability || 0} readOnly precision={0.1} size="small" max={1} />
                          </Box>
                        </Paper>
                      </Grid>
                      {/* Kindness */}
                      <Grid item xs={6} sm={3}>
                        <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', border: '1px solid', borderColor: 'grey.200' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                            <FavoriteIcon sx={{ fontSize: 16, color: 'error.light' }} />
                            <Typography variant="caption" color="text.secondary">
                              Kindness
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Typography variant="h6" fontWeight={600}>
                              {ratingSummary.average_kindness?.toFixed(1) || '-'}
                            </Typography>
                            <MuiRating value={ratingSummary.average_kindness || 0} readOnly precision={0.1} size="small" max={1} />
                          </Box>
                        </Paper>
                      </Grid>
                      {/* Helpfulness */}
                      <Grid item xs={6} sm={3}>
                        <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', border: '1px solid', borderColor: 'grey.200' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                            <SupportIcon sx={{ fontSize: 16, color: 'primary.light' }} />
                            <Typography variant="caption" color="text.secondary">
                              Helpfulness
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Typography variant="h6" fontWeight={600}>
                              {ratingSummary.average_helpfulness?.toFixed(1) || '-'}
                            </Typography>
                            <MuiRating value={ratingSummary.average_helpfulness || 0} readOnly precision={0.1} size="small" max={1} />
                          </Box>
                        </Paper>
                      </Grid>
                    </Grid>
                  </Box>
                )}
              </Box>

              {/* Activities */}
              <Box>
                <Typography variant="body2" color="text.secondary">
                  <strong>{profile.stats.completed_exchanges}</strong> completed exchanges
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Badges Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Badges
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            {earnedBadges.length} of {badges.length} badges earned
          </Typography>

          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {badges.map((badge) => (
              <Paper
                key={badge.id}
                elevation={badge.earned ? 2 : 0}
                sx={{
                  p: 2,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  minWidth: 120,
                  opacity: badge.earned ? 1 : 0.4,
                  bgcolor: badge.earned ? 'background.paper' : 'grey.100',
                  border: badge.earned ? `2px solid ${badge.color}` : '1px solid',
                  borderColor: badge.earned ? badge.color : 'grey.300',
                }}
              >
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    bgcolor: badge.earned ? badge.color : 'grey.400',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    mb: 1,
                  }}
                >
                  {badge.icon}
                </Box>
                <Typography variant="caption" fontWeight={600} textAlign="center">
                  {badge.name}
                </Typography>
                <Typography variant="caption" color="text.secondary" textAlign="center" sx={{ fontSize: '0.65rem' }}>
                  {badge.description}
                </Typography>
              </Paper>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Tabs Section */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab label="Activities" />
            <Tab label="Completed Activities" />
            <Tab label="Recent Ratings" />
          </Tabs>
        </Box>

        {/* Tab 1: Active Exchanges */}
        <TabPanel value={activeTab} index={0}>
          {activeExchangesLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : !activeExchangesData || activeExchangesData.items.length === 0 ? (
            <Alert severity="info">
              No active exchanges. Active exchanges will appear here when accepted.
            </Alert>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {activeExchangesData.items.map((exchange) => (
                <Card 
                  key={exchange.id} 
                  variant="outlined"
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': { 
                      bgcolor: 'action.hover',
                      borderColor: 'primary.main'
                    }
                  }}
                  onClick={() => {
                    const path = exchange.item_type === 'offer' 
                      ? `/offers/${exchange.offer_id}` 
                      : `/needs/${exchange.need_id}`
                    navigate(path)
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Box>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {exchange.item_title}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mt: 0.5 }}>
                          <Chip
                            label={exchange.item_type === 'offer' ? 'Offer' : 'Need'}
                            size="small"
                            color={exchange.item_type === 'offer' ? 'primary' : 'secondary'}
                            variant="outlined"
                          />
                          <Chip
                            label="Active"
                            size="small"
                            color="success"
                          />
                          <Chip
                            label={`${Math.round(exchange.hours)}h`}
                            size="small"
                          />
                        </Box>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{
                      mb: 1.5,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                    }}>
                      {exchange.item_description}
                    </Typography>
                    {/* Show location if not remote */}
                    {!exchange.is_remote && exchange.location_name && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <LocationIcon fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                          {exchange.location_name}
                        </Typography>
                      </Box>
                    )}
                    {/* Only show participant info if there's an actual participant (not waiting) */}
                    {exchange.role !== 'creator' && exchange.other_user_id && (
                      <>
                        <Divider sx={{ my: 1 }} />
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <PersonIcon fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary">
                            {exchange.role === 'provider' ? 'Providing to' : 'Receiving from'}{' '}
                            <Typography
                              component="span"
                              variant="body2"
                              color="primary"
                              sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                              onClick={(e) => {
                                e.stopPropagation()
                                navigate(`/profile/${exchange.other_username}`)
                              }}
                            >
                              @{exchange.other_username}
                            </Typography>
                          </Typography>
                        </Box>
                      </>
                    )}
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </TabPanel>

        {/* Tab 2: Completed Activities */}
        <TabPanel value={activeTab} index={1}>
          {exchangesLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : !exchangesData || exchangesData.items.length === 0 ? (
            <Alert severity="info">
              No completed exchanges yet.
            </Alert>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {exchangesData.items.map((exchange) => (
                <Card 
                  key={exchange.id} 
                  variant="outlined"
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': { 
                      bgcolor: 'action.hover',
                      borderColor: 'primary.main'
                    }
                  }}
                  onClick={() => {
                    const path = exchange.item_type === 'offer' 
                      ? `/offers/${exchange.offer_id}` 
                      : `/needs/${exchange.need_id}`
                    navigate(path)
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Box>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {exchange.item_title}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mt: 0.5 }}>
                          <Chip
                            label={exchange.item_type === 'offer' ? 'Offer' : 'Need'}
                            size="small"
                            color={exchange.item_type === 'offer' ? 'primary' : 'secondary'}
                            variant="outlined"
                          />
                          <Chip
                            label={`${Math.round(exchange.hours)}h`}
                            size="small"
                            color="success"
                          />
                        </Box>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {formatCommentDate(exchange.completed_at)}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{
                      mb: 1.5,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                    }}>
                      {exchange.item_description}
                    </Typography>
                    {/* Show location if not remote */}
                    {!exchange.is_remote && exchange.location_name && (
                      <>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <LocationIcon fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary">
                            {exchange.location_name}
                          </Typography>
                        </Box>
                      </>
                    )}
                    <Divider sx={{ my: 1 }} />
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <PersonIcon fontSize="small" color="action" />
                      <Typography variant="body2" color="text.secondary">
                        {exchange.role === 'provider' ? 'Provided to' : 'Received from'}{' '}
                        <Typography
                          component="span"
                          variant="body2"
                          color="primary"
                          sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                          onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/profile/${exchange.other_username}`)
                          }}
                        >
                          @{exchange.other_username}
                        </Typography>
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              ))}
                </Box>
          )}
        </TabPanel>

        {/* Tab 3: Recent Ratings */}
        <TabPanel value={activeTab} index={2}>
          <RatingsList userId={profile.id} limit={10} />
        </TabPanel>
      </Card>

      {/* Edit Profile Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Profile</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            {/* Display Name */}
            <TextField
              label="Display Name"
              value={editFullName}
              onChange={(e) => setEditFullName(e.target.value)}
              fullWidth
              helperText="Your name as shown to other users"
            />

            {/* About/Description */}
            <TextField
              label="About"
              value={editAbout}
              onChange={(e) => setEditAbout(e.target.value)}
              multiline
              rows={4}
              fullWidth
              helperText={`${editAbout.length}/1000 characters`}
              inputProps={{ maxLength: 1000 }}
            />

            {/* Tags */}
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Profile Tags (up to 10)
              </Typography>
              <Typography variant="caption" color="text.secondary" paragraph>
                Add tags that describe your skills, interests, or what services you can offer.
              </Typography>

              {/* Tag chips */}
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                {editTags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag}
                    size="small"
                    onDelete={() => handleRemoveTag(tag)}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>

              {/* Add tag input */}
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  size="small"
                  placeholder="Add a tag..."
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      handleAddTag()
                    }
                  }}
                  disabled={editTags.length >= 10}
                  sx={{ flex: 1 }}
                />
                <Button
                  variant="outlined"
                  onClick={handleAddTag}
                  disabled={!tagInput.trim() || editTags.length >= 10}
                >
                  Add
                </Button>
              </Box>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSaveProfile}
            disabled={updateProfileMutation.isPending}
          >
            {updateProfileMutation.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Avatar Selection Dialog */}
      <Dialog open={avatarDialogOpen} onClose={() => setAvatarDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Choose Your Avatar</DialogTitle>
        <DialogContent>
          {/* Upload Custom Image Section */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>
              Upload Your Own Image
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Upload a custom profile picture (JPEG, PNG, GIF, or WebP, max 500KB).
            </Typography>

            <input
              type="file"
              ref={fileInputRef}
              accept="image/jpeg,image/png,image/gif,image/webp"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />

            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Button
                variant="outlined"
                startIcon={<PhotoCameraIcon />}
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadingImage}
              >
                {uploadingImage ? 'Uploading...' : 'Choose Image'}
              </Button>

              {profile.profile_image_type === 'custom' && profile.profile_image && (
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={() => removeImageMutation.mutate()}
                  disabled={removeImageMutation.isPending}
                >
                  Remove Custom Image
                </Button>
              )}
            </Box>

            {/* Preview of current custom image */}
            {profile.profile_image_type === 'custom' && profile.profile_image && (
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar
                  src={profile.profile_image}
                  sx={{ width: 64, height: 64 }}
                />
                <Typography variant="caption" color="text.secondary">
                  Current custom image
                </Typography>
              </Box>
            )}
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Preset Avatars Section */}
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Or Choose a Preset Avatar
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Select an avatar that represents you in The Hive community.
          </Typography>

          <Grid container spacing={1.5}>
            {presetAvatars?.avatars.map((avatar) => (
              <Grid item xs={4} sm={3} md={2} key={avatar}>
                <Paper
                  elevation={selectedAvatar === avatar ? 4 : 1}
                  sx={{
                    p: 1.5,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    cursor: 'pointer',
                    border: selectedAvatar === avatar ? 2 : 1,
                    borderColor: selectedAvatar === avatar ? 'primary.main' : 'grey.300',
                    borderStyle: 'solid',
                    bgcolor: selectedAvatar === avatar ? 'primary.50' : 'background.paper',
                    '&:hover': { bgcolor: 'action.hover' },
                    transition: 'all 0.2s',
                  }}
                  onClick={() => setSelectedAvatar(avatar)}
                >
                  <Avatar
                    sx={{
                      width: 48,
                      height: 48,
                      bgcolor: AVATAR_COLORS[avatar] || 'primary.main',
                      fontSize: '1.75rem',
                      mb: 0.5,
                    }}
                  >
                    {AVATAR_EMOJIS[avatar] || avatar[0].toUpperCase()}
                  </Avatar>
                  <Typography variant="caption" textAlign="center" sx={{ textTransform: 'capitalize', fontSize: '0.65rem' }}>
                    {avatar}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAvatarDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => updateAvatarMutation.mutate(selectedAvatar)}
            disabled={!selectedAvatar || updateAvatarMutation.isPending}
          >
            {updateAvatarMutation.isPending ? 'Saving...' : 'Save Preset Avatar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
