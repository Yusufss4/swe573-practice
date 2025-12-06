// SRS FR-2 & FR-10: User Profile with Stats, Badges, and Ratings
// Public profile view displaying user info, TimeBank stats, and feedback

import { useState } from 'react'
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
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { RatingsList } from '@/components/RatingDisplay'

// SRS FR-2: User profile data structure
interface UserProfile {
  id: number
  username: string
  display_name?: string | null
  description?: string | null
  location_name?: string | null
  balance: number
  stats: {
    balance: number
    hours_given: number
    hours_received: number
    completed_exchanges: number
    comments_received: number
  }
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
 * - Two tabs:
 *   1. Activities - completed exchanges
 *   2. Recent Ratings - feedback from other users
 */
export default function ProfilePage() {
  const { username } = useParams<{ username: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState(0)

  // Fetch user profile by username
  const { data: profile, isLoading: profileLoading, error: profileError } = useQuery<UserProfile>({
    queryKey: ['userProfile', username],
    queryFn: async () => {
      const response = await apiClient.get(`/users/username/${username}`)
      return response.data
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
    queryKey: ['userCompletedExchanges', username],
    queryFn: async () => {
      const response = await apiClient.get(`/users/username/${username}/completed-exchanges`)
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
          Failed to load profile. User may not exist.
        </Alert>
      </Container>
    )
  }

  const badges = getBadges(profile)
  const earnedBadges = badges.filter((b) => b.earned)

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
                <Avatar
                  sx={{
                    width: 120,
                    height: 120,
                    bgcolor: 'primary.main',
                    fontSize: '3rem',
                    mb: 2,
                  }}
                >
                  {profile.display_name?.[0]?.toUpperCase() || profile.username[0].toUpperCase()}
                </Avatar>
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
              </Box>
            </Grid>

            {/* Bio and Stats */}
            <Grid item xs={12} md={8}>
              {/* Bio */}
              {profile.description && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    About
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                    {profile.description}
                  </Typography>
                </Box>
              )}

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
                        {profile.stats.balance.toFixed(1)}h
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
                        {profile.stats.hours_given.toFixed(1)}h
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
                        {profile.stats.hours_received.toFixed(1)}h
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
            <Tab label="Recent Ratings" />
          </Tabs>
        </Box>

        {/* Tab 1: Activities */}
        <TabPanel value={activeTab} index={0}>
          {exchangesLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : !exchangesData || exchangesData.items.length === 0 ? (
            <Alert severity="info">
              No completed exchanges yet. Exchanges will appear here after they are completed.
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
                            label={`${exchange.hours.toFixed(1)}h`}
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

        {/* Tab 2: Recent Ratings */}
        <TabPanel value={activeTab} index={1}>
          <RatingsList userId={profile.id} limit={10} />
        </TabPanel>
      </Card>
    </Container>
  )
}
