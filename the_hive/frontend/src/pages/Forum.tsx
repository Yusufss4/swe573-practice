// SRS FR-15: Community Forum
// Main forum page with Discussions and Events tabs

import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  CardActionArea,
  Button,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
  Avatar,
  Stack,
} from '@mui/material'
import {
  Add as AddIcon,
  Forum as ForumIcon,
  Event as EventIcon,
  Search as SearchIcon,
  Comment as CommentIcon,
  Visibility as ViewIcon,
  Schedule as ScheduleIcon,
  LocationOn as LocationIcon,
  PushPin as PinIcon,
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'
import { getAvatarDisplay } from '@/utils/avatars'

// Types
interface ForumTopic {
  id: number
  topic_type: 'discussion' | 'event'
  creator_id: number
  creator_username: string | null
  creator_display_name: string | null
  creator_profile_image?: string | null
  creator_profile_image_type?: string | null
  title: string
  content: string
  tags: string[]
  event_start_time: string | null
  event_end_time: string | null
  event_location: string | null
  is_pinned: boolean
  view_count: number
  comment_count: number
  created_at: string
  updated_at: string
}

interface ForumTopicListResponse {
  items: ForumTopic[]
  total: number
  skip: number
  limit: number
}

// Tab panel component
function TabPanel({
  children,
  value,
  index,
}: {
  children: React.ReactNode
  value: number
  index: number
}) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

// Topic card component
function TopicCard({ topic, onClick }: { topic: ForumTopic; onClick: () => void }) {
  const avatarDisplay = getAvatarDisplay(
    topic.creator_profile_image,
    topic.creator_profile_image_type
  )

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const formatEventTime = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  return (
    <Card
      sx={{
        mb: 2,
        border: topic.is_pinned ? 2 : 1,
        borderColor: topic.is_pinned ? 'primary.main' : 'divider',
        bgcolor: topic.is_pinned ? 'primary.50' : 'background.paper',
      }}
    >
      <CardActionArea onClick={onClick}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            {/* Avatar */}
            {avatarDisplay?.isCustomImage ? (
              <Avatar src={avatarDisplay.src} sx={{ width: 40, height: 40 }} />
            ) : avatarDisplay?.emoji ? (
              <Avatar
                sx={{
                  width: 40,
                  height: 40,
                  bgcolor: avatarDisplay.bgcolor,
                  fontSize: '1.25rem',
                }}
              >
                {avatarDisplay.emoji}
              </Avatar>
            ) : (
              <Avatar sx={{ width: 40, height: 40, bgcolor: 'grey.400' }}>
                {topic.creator_username?.[0]?.toUpperCase() || 'U'}
              </Avatar>
            )}

            {/* Content */}
            <Box sx={{ flex: 1, minWidth: 0 }}>
              {/* Header */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                {topic.is_pinned && (
                  <PinIcon fontSize="small" color="primary" sx={{ transform: 'rotate(45deg)' }} />
                )}
                <Typography variant="h6" component="h2" noWrap sx={{ fontWeight: 600 }}>
                  {topic.title}
                </Typography>
              </Box>

              {/* Meta info */}
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                by {topic.creator_display_name || topic.creator_username}{' '}
                <Typography component="span" variant="body2" color="text.disabled">
                  @{topic.creator_username}
                </Typography>
                {' · '}{formatDate(topic.created_at)}
              </Typography>

              {/* Event-specific info */}
              {topic.topic_type === 'event' && topic.event_start_time && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <ScheduleIcon fontSize="small" color="primary" />
                    <Typography variant="body2" color="primary.main" fontWeight={500}>
                      {formatEventTime(topic.event_start_time)}
                    </Typography>
                  </Box>
                  {topic.event_location && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <LocationIcon fontSize="small" color="action" />
                      <Typography variant="body2" color="text.secondary" noWrap>
                        {topic.event_location}
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}

              {/* Content preview */}
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  mb: 1,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                }}
              >
                {topic.content}
              </Typography>

              {/* Tags */}
              {topic.tags.length > 0 && (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                  {topic.tags.slice(0, 5).map((tag) => (
                    <Chip key={tag} label={tag} size="small" variant="outlined" />
                  ))}
                  {topic.tags.length > 5 && (
                    <Chip label={`+${topic.tags.length - 5}`} size="small" />
                  )}
                </Box>
              )}

              {/* Stats */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <ViewIcon fontSize="small" color="action" />
                  <Typography variant="caption" color="text.secondary">
                    {topic.view_count}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <CommentIcon fontSize="small" color="action" />
                  <Typography variant="caption" color="text.secondary">
                    {topic.comment_count}
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  )
}

// Main Forum component
export default function Forum() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { isAuthenticated } = useAuth()

  // State
  const tabFromUrl = searchParams.get('tab') === 'events' ? 1 : 0
  const [tabValue, setTabValue] = useState(tabFromUrl)
  const [tagFilter, setTagFilter] = useState(searchParams.get('tag') || '')
  const [searchKeyword, setSearchKeyword] = useState('')

  // Get current topic type
  const topicType = tabValue === 0 ? 'discussion' : 'event'

  // Fetch topics
  const {
    data: topicsData,
    isLoading,
    error,
  } = useQuery<ForumTopicListResponse>({
    queryKey: ['forumTopics', topicType, tagFilter, searchKeyword],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.set('topic_type', topicType)
      if (tagFilter) params.set('tags', tagFilter)
      if (searchKeyword) params.set('keyword', searchKeyword)
      params.set('limit', '50')

      const response = await apiClient.get(`/forum/topics?${params.toString()}`)
      return response.data
    },
  })

  // Handle tab change
  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
    const newParams = new URLSearchParams(searchParams)
    newParams.set('tab', newValue === 1 ? 'events' : 'discussions')
    setSearchParams(newParams)
  }

  // Handle tag filter
  const handleTagFilter = (tag: string) => {
    setTagFilter(tag)
    const newParams = new URLSearchParams(searchParams)
    if (tag) {
      newParams.set('tag', tag)
    } else {
      newParams.delete('tag')
    }
    setSearchParams(newParams)
  }

  // Handle search
  const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      // Search is applied via queryKey change
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Box>
          <Typography variant="h4" gutterBottom fontWeight={700}>
            Community Forum
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Share ideas, discuss topics, and discover community events
          </Typography>
        </Box>
        {isAuthenticated && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() =>
              navigate(`/forum/create?type=${topicType}`)
            }
            sx={{ borderRadius: 2 }}
          >
            {tabValue === 0 ? 'New Discussion' : 'New Event'}
          </Button>
        )}
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab
            icon={<ForumIcon />}
            iconPosition="start"
            label="Discussions"
            sx={{ textTransform: 'none', fontWeight: 600 }}
          />
          <Tab
            icon={<EventIcon />}
            iconPosition="start"
            label="Events"
            sx={{ textTransform: 'none', fontWeight: 600 }}
          />
        </Tabs>
      </Box>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search topics..."
          size="small"
          value={searchKeyword}
          onChange={(e) => setSearchKeyword(e.target.value)}
          onKeyDown={handleSearch}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 250 }}
        />
        <TextField
          placeholder="Filter by tag"
          size="small"
          value={tagFilter}
          onChange={(e) => handleTagFilter(e.target.value)}
          sx={{ minWidth: 150 }}
        />
        {tagFilter && (
          <Chip
            label={`Tag: ${tagFilter}`}
            onDelete={() => handleTagFilter('')}
            color="primary"
            size="small"
          />
        )}
      </Box>

      {/* Content */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          Unable to load forum topics. Please try again.
        </Alert>
      ) : topicsData?.items.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No {topicType === 'discussion' ? 'discussions' : 'events'} found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {tagFilter || searchKeyword
              ? 'Try adjusting your filters'
              : 'Be the first to start one!'}
          </Typography>
          {isAuthenticated && (
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => navigate(`/forum/create?type=${topicType}`)}
            >
              Create {topicType === 'discussion' ? 'Discussion' : 'Event'}
            </Button>
          )}
        </Box>
      ) : (
        <>
          {/* Discussions Tab */}
          <TabPanel value={tabValue} index={0}>
            <Stack spacing={0}>
              {topicsData?.items.map((topic) => (
                <TopicCard
                  key={topic.id}
                  topic={topic}
                  onClick={() => navigate(`/forum/topic/${topic.id}`)}
                />
              ))}
            </Stack>
          </TabPanel>

          {/* Events Tab */}
          <TabPanel value={tabValue} index={1}>
            <Stack spacing={0}>
              {topicsData?.items.map((topic) => (
                <TopicCard
                  key={topic.id}
                  topic={topic}
                  onClick={() => navigate(`/forum/topic/${topic.id}`)}
                />
              ))}
            </Stack>
          </TabPanel>
        </>
      )}

      {/* Total count */}
      {topicsData && topicsData.total > 0 && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Showing {topicsData.items.length} of {topicsData.total}{' '}
            {topicType === 'discussion' ? 'discussions' : 'events'}
          </Typography>
        </Box>
      )}
    </Container>
  )
}
