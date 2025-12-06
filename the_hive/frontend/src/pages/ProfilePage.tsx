// SRS FR-2 & FR-10: User Profile with Stats, Badges, and Comments
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
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Person as PersonIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  AccountBalance as BalanceIcon,
  TrendingUp as TrendingUpIcon,
  EmojiEvents as TrophyIcon,
  Star as StarIcon,
  Verified as VerifiedIcon,
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/services/api'

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

// SRS FR-10: Comment structure
interface Comment {
  id: number
  from_user_id: number
  from_username: string
  to_user_id: number
  to_username: string
  participant_id: number
  content: string
  is_approved: boolean
  timestamp: string
}

interface CommentsResponse {
  items: Comment[]
  total: number
  skip: number
  limit: number
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
    {
      id: 'community',
      name: 'Community Star',
      icon: <StarIcon />,
      color: '#E91E63',
      description: 'Received 10+ positive comments',
      earned: profile.stats.comments_received >= 10,
    },
  ]

  return badges
}

/**
 * ProfilePage Component
 * 
 * SRS FR-2: Profile Management
 * SRS FR-10: Comments and Feedback System
 * 
 * Features:
 * - Display user profile information (avatar, name, bio, location)
 * - Show badge collection based on achievements
 * - Display TimeBank statistics (balance, hours given/received)
 * - Two tabs:
 *   1. Completed Exchanges - summary of user's activity
 *   2. Comments - feedback from other users
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

  // Fetch comments by username
  const { data: commentsData, isLoading: commentsLoading } = useQuery<CommentsResponse>({
    queryKey: ['userComments', username],
    queryFn: async () => {
      const response = await apiClient.get(`/comments/username/${username}`)
      return response.data
    },
    enabled: !!username && activeTab === 1, // Only fetch when on comments tab
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
                  <Grid item xs={12} sm={6}>
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

                  {/* Hours Received */}
                  <Grid item xs={12} sm={6}>
                    <Paper elevation={0} sx={{ p: 2, bgcolor: 'info.50', border: '1px solid', borderColor: 'info.200' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <TrendingUpIcon color="info" />
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
              </Box>

              {/* Activities */}
              <Box>
                <Typography variant="body2" color="text.secondary">
                  <strong>{profile.stats.completed_exchanges}</strong> completed exchanges •{' '}
                  <strong>{profile.stats.comments_received}</strong> comments received
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
            <Tab label={`Comments (${profile.stats.comments_received})`} />
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

        {/* Tab 2: Comments */}
        <TabPanel value={activeTab} index={1}>
          {commentsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : !commentsData || commentsData.items.length === 0 ? (
            <Alert severity="info">
              No comments yet. Comments will appear here after completed exchanges.
            </Alert>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {commentsData.items.map((comment) => (
                <Card key={comment.id} variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'secondary.main' }}>
                        {comment.from_username[0].toUpperCase()}
                      </Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="subtitle2" fontWeight={600}>
                            @{comment.from_username}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatCommentDate(comment.timestamp)}
                          </Typography>
                        </Box>
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                          {comment.content}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </TabPanel>
      </Card>
    </Container>
  )
}
