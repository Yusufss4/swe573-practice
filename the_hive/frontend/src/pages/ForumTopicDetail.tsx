// SRS FR-15: Forum Topic Detail Page
// View topic details and comments

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  TextField,
  CircularProgress,
  Alert,
  Avatar,
  Divider,
  IconButton,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Comment as CommentIcon,
  Visibility as ViewIcon,
  Schedule as ScheduleIcon,
  LocationOn as LocationIcon,
  PushPin as PinIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Send as SendIcon,
  Event as EventIcon,
  Forum as ForumIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'
import ReportButton from '@/components/ReportButton'
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
  linked_offer_id: number | null
  linked_need_id: number | null
  linked_item: {
    id: number
    type: 'offer' | 'need'
    title: string
    creator_username: string | null
  } | null
  is_pinned: boolean
  view_count: number
  comment_count: number
  created_at: string
  updated_at: string
}

interface ForumComment {
  id: number
  topic_id: number
  author_id: number
  author_username: string | null
  author_display_name: string | null
  author_profile_image?: string | null
  author_profile_image_type?: string | null
  content: string
  created_at: string
  updated_at: string
}

interface CommentsResponse {
  items: ForumComment[]
  total: number
  skip: number
  limit: number
}

export default function ForumTopicDetail() {
  const { topicId } = useParams<{ topicId: string }>()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuth()
  const queryClient = useQueryClient()

  // State
  const [newComment, setNewComment] = useState('')
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

  // Fetch topic
  const {
    data: topic,
    isLoading: topicLoading,
    error: topicError,
  } = useQuery<ForumTopic>({
    queryKey: ['forumTopic', topicId],
    queryFn: async () => {
      const response = await apiClient.get(`/forum/topics/${topicId}`)
      return response.data
    },
    enabled: !!topicId,
  })

  // Fetch comments
  const {
    data: commentsData,
    isLoading: commentsLoading,
  } = useQuery<CommentsResponse>({
    queryKey: ['forumComments', topicId],
    queryFn: async () => {
      const response = await apiClient.get(`/forum/topics/${topicId}/comments?limit=100`)
      return response.data
    },
    enabled: !!topicId,
  })

  // Create comment mutation
  const createCommentMutation = useMutation({
    mutationFn: async (content: string) => {
      const response = await apiClient.post(`/forum/topics/${topicId}/comments`, { content })
      return response.data
    },
    onSuccess: () => {
      setNewComment('')
      queryClient.invalidateQueries({ queryKey: ['forumComments', topicId] })
      queryClient.invalidateQueries({ queryKey: ['forumTopic', topicId] })
    },
  })

  // Delete topic mutation
  const deleteTopicMutation = useMutation({
    mutationFn: async () => {
      await apiClient.delete(`/forum/topics/${topicId}`)
    },
    onSuccess: () => {
      navigate('/forum')
    },
  })

  // Format date
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  const formatEventTime = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  // Handle submit comment
  const handleSubmitComment = (e: React.FormEvent) => {
    e.preventDefault()
    if (newComment.trim()) {
      createCommentMutation.mutate(newComment.trim())
    }
  }

  // Handle delete
  const handleDelete = () => {
    deleteTopicMutation.mutate()
    setDeleteDialogOpen(false)
  }

  // Loading state
  if (topicLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  // Error state
  if (topicError || !topic) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          Unable to load this topic. It may not exist or has been removed.
        </Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/forum')}>
          Back to Forum
        </Button>
      </Container>
    )
  }

  const isCreator = user?.id === topic.creator_id
  const topicAvatarDisplay = getAvatarDisplay(
    topic.creator_profile_image,
    topic.creator_profile_image_type
  )

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Back button */}
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/forum')}
        sx={{ mb: 3 }}
      >
        Back to Forum
      </Button>

      {/* Topic Card */}
      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 4 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={topic.topic_type === 'event' ? <EventIcon /> : <ForumIcon />}
                label={topic.topic_type === 'event' ? 'Event' : 'Discussion'}
                color={topic.topic_type === 'event' ? 'secondary' : 'primary'}
                size="small"
              />
              {topic.is_pinned && (
                <Chip
                  icon={<PinIcon sx={{ transform: 'rotate(45deg)' }} />}
                  label="Pinned"
                  size="small"
                  color="warning"
                />
              )}
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {!isCreator && (
                <ReportButton
                  itemType="forum_topic"
                  itemId={topic.id}
                  itemTitle={topic.title}
                  size="small"
                />
              )}
              {isCreator && (
                <Box>
                  <IconButton
                    size="small"
                    onClick={() => navigate(`/forum/edit/${topic.id}`)}
                    title="Edit"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => setDeleteDialogOpen(true)}
                    title="Delete"
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              )}
            </Box>
          </Box>

          {/* Title */}
          <Typography variant="h4" gutterBottom fontWeight={700}>
            {topic.title}
          </Typography>

          {/* Creator info */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              mb: 3,
              cursor: 'pointer',
            }}
            onClick={() => navigate(`/profile/${topic.creator_username}`)}
          >
            {topicAvatarDisplay?.isCustomImage ? (
              <Avatar src={topicAvatarDisplay.src} sx={{ width: 48, height: 48 }} />
            ) : topicAvatarDisplay?.emoji ? (
              <Avatar
                sx={{
                  width: 48,
                  height: 48,
                  bgcolor: topicAvatarDisplay.bgcolor,
                  fontSize: '1.5rem',
                }}
              >
                {topicAvatarDisplay.emoji}
              </Avatar>
            ) : (
              <Avatar sx={{ width: 48, height: 48 }}>
                {topic.creator_username?.[0]?.toUpperCase() || 'U'}
              </Avatar>
            )}
            <Box>
              <Typography variant="subtitle1" fontWeight={600}>
                {topic.creator_display_name || topic.creator_username}{' '}
                <Typography component="span" variant="body2" color="text.secondary">
                  @{topic.creator_username}
                </Typography>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Posted {formatDate(topic.created_at)}
              </Typography>
            </Box>
          </Box>

          {/* Event info */}
          {topic.topic_type === 'event' && topic.event_start_time && (
            <Paper
              variant="outlined"
              sx={{ p: 2, mb: 3, bgcolor: 'secondary.50', borderColor: 'secondary.200' }}
            >
              <Typography variant="subtitle2" color="secondary.main" gutterBottom fontWeight={600}>
                Event Details
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ScheduleIcon color="secondary" fontSize="small" />
                  <Typography variant="body2">
                    {formatEventTime(topic.event_start_time)}
                    {topic.event_end_time && ` - ${formatEventTime(topic.event_end_time)}`}
                  </Typography>
                </Box>
                {topic.event_location && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LocationIcon color="secondary" fontSize="small" />
                    <Typography variant="body2">{topic.event_location}</Typography>
                  </Box>
                )}
              </Box>
            </Paper>
          )}

          {/* Linked item */}
          {topic.linked_item && (
            <Paper
              variant="outlined"
              sx={{ p: 2, mb: 3, cursor: 'pointer' }}
              onClick={() =>
                navigate(`/${topic.linked_item!.type}s/${topic.linked_item!.id}`)
              }
            >
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Linked {topic.linked_item.type === 'offer' ? 'Offer' : 'Need'}
              </Typography>
              <Typography variant="body1" fontWeight={500}>
                {topic.linked_item.title}
              </Typography>
            </Paper>
          )}

          {/* Content */}
          <Typography variant="body1" sx={{ mb: 3, whiteSpace: 'pre-wrap' }}>
            {topic.content}
          </Typography>

          {/* Tags */}
          {topic.tags.length > 0 && (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
              {topic.tags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  size="small"
                  variant="outlined"
                  onClick={() => navigate(`/forum?tag=${tag}`)}
                />
              ))}
            </Box>
          )}

          <Divider sx={{ my: 2 }} />

          {/* Stats */}
          <Box sx={{ display: 'flex', gap: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <ViewIcon color="action" fontSize="small" />
              <Typography variant="body2" color="text.secondary">
                {topic.view_count} views
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <CommentIcon color="action" fontSize="small" />
              <Typography variant="body2" color="text.secondary">
                {topic.comment_count} comments
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Comments Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom fontWeight={600}>
          Comments ({commentsData?.total || 0})
        </Typography>

        {/* Comment form */}
        {isAuthenticated ? (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <form onSubmit={handleSubmitComment}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  placeholder="Write a comment..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  disabled={createCommentMutation.isPending}
                  sx={{ mb: 2 }}
                />
                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<SendIcon />}
                    disabled={!newComment.trim() || createCommentMutation.isPending}
                  >
                    {createCommentMutation.isPending ? 'Posting...' : 'Post Comment'}
                  </Button>
                </Box>
              </form>
              {createCommentMutation.isError && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  Unable to post your comment. Please try again.
                </Alert>
              )}
            </CardContent>
          </Card>
        ) : (
          <Alert severity="info" sx={{ mb: 3 }}>
            Please <Button onClick={() => navigate('/login')}>log in</Button> to comment.
          </Alert>
        )}

        {/* Comments list */}
        {commentsLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={32} />
          </Box>
        ) : commentsData?.items.length === 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
            No comments yet. Be the first to comment!
          </Typography>
        ) : (
          <Box>
            {commentsData?.items.map((comment) => {
              const commentAvatarDisplay = getAvatarDisplay(
                comment.author_profile_image,
                comment.author_profile_image_type
              )
              return (
                <Card
                  key={comment.id}
                  sx={{
                    mb: 2,
                    '&:hover .comment-report-button': {
                      opacity: 1,
                    },
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      {/* Avatar */}
                      {commentAvatarDisplay?.isCustomImage ? (
                        <Avatar
                          src={commentAvatarDisplay.src}
                          sx={{ width: 36, height: 36, cursor: 'pointer' }}
                          onClick={() => navigate(`/profile/${comment.author_username}`)}
                        />
                      ) : commentAvatarDisplay?.emoji ? (
                        <Avatar
                          sx={{
                            width: 36,
                            height: 36,
                            bgcolor: commentAvatarDisplay.bgcolor,
                            fontSize: '1rem',
                            cursor: 'pointer',
                          }}
                          onClick={() => navigate(`/profile/${comment.author_username}`)}
                        >
                          {commentAvatarDisplay.emoji}
                        </Avatar>
                      ) : (
                        <Avatar
                          sx={{ width: 36, height: 36, cursor: 'pointer' }}
                          onClick={() => navigate(`/profile/${comment.author_username}`)}
                        >
                          {comment.author_username?.[0]?.toUpperCase() || 'U'}
                        </Avatar>
                      )}

                      {/* Content */}
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography
                              variant="subtitle2"
                              fontWeight={600}
                              sx={{ cursor: 'pointer' }}
                              onClick={() => navigate(`/profile/${comment.author_username}`)}
                            >
                              {comment.author_display_name || comment.author_username}{' '}
                              <Typography component="span" variant="body2" color="text.secondary">
                                @{comment.author_username}
                              </Typography>
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {formatDate(comment.created_at)}
                            </Typography>
                          </Box>
                          {user && user.id !== comment.author_id && (
                            <Box
                              className="comment-report-button"
                              sx={{
                                opacity: 0,
                                transition: 'opacity 0.2s',
                              }}
                            >
                              <ReportButton
                                itemType="comment"
                                itemId={comment.id}
                                size="small"
                              />
                            </Box>
                          )}
                        </Box>
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                          {comment.content}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              )
            })}
          </Box>
        )}
      </Box>

      {/* Delete confirmation dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Topic?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this topic? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleDelete}
            color="error"
            variant="contained"
            disabled={deleteTopicMutation.isPending}
          >
            {deleteTopicMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
