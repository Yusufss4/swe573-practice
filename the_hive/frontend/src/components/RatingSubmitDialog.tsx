// SRS FR-10.4 & FR-10.5: Rating Component with Multi-Category System and Blind Ratings
// Peace-oriented, community-focused rating interface

import { useState, useEffect } from 'react'
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Rating as MuiRating,
  TextField,
  Alert,
  Chip,
  Divider,
  CircularProgress,
  Collapse,
  IconButton,
  Paper,
} from '@mui/material'
import {
  Star as StarIcon,
  Schedule as ScheduleIcon,
  Favorite as FavoriteIcon,
  Support as SupportIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'

// Human-friendly rating labels
const RATING_LABELS: Record<number, string> = {
  1: 'Needs Improvement',
  2: 'Below Expectations',
  3: 'Met Expectations',
  4: 'Above Expectations',
  5: 'Exceptional',
}

// Category information - All three are required, general is calculated
interface CategoryInfo {
  name: string
  description: string
  icon: React.ReactNode
  required: boolean
}

const CATEGORIES: Record<string, CategoryInfo> = {
  reliability: {
    name: 'Reliability & Commitment',
    description: 'Did they show up as agreed, communicate clearly, and follow through?',
    icon: <ScheduleIcon />,
    required: true,
  },
  kindness: {
    name: 'Kindness & Respect',
    description: 'Was the interaction warm, respectful, and comfortable?',
    icon: <FavoriteIcon />,
    required: true,
  },
  helpfulness: {
    name: 'Helpfulness & Support',
    description: 'Did the exchange feel meaningful and genuinely supportive?',
    icon: <SupportIcon />,
    required: true,
  },
}

interface RatingSubmitProps {
  open: boolean
  onClose: () => void
  participantId: number
  recipientId: number
  recipientName: string
  exchangeTitle: string
}

interface RatingData {
  recipient_id: number
  participant_id: number
  reliability_rating: number
  kindness_rating: number
  helpfulness_rating: number
  public_comment?: string
}

// Single category rating component
function CategoryRating({
  category,
  info,
  value,
  onChange,
  disabled,
}: {
  category: string
  info: CategoryInfo
  value: number | null
  onChange: (value: number | null) => void
  disabled: boolean
}) {
  const [hover, setHover] = useState(-1)

  const getLabelText = (value: number) => {
    return RATING_LABELS[value] || ''
  }

  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Box sx={{ color: 'primary.main' }}>{info.icon}</Box>
        <Typography variant="subtitle1" fontWeight={600}>
          {info.name}
          {info.required && (
            <Typography component="span" color="error" sx={{ ml: 0.5 }}>*</Typography>
          )}
        </Typography>
      </Box>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
        {info.description}
      </Typography>
      
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <MuiRating
          name={`rating-${category}`}
          value={value}
          onChange={(_, newValue) => onChange(newValue)}
          onChangeActive={(_, newHover) => setHover(newHover)}
          disabled={disabled}
          size="large"
          sx={{
            '& .MuiRating-iconFilled': {
              color: 'primary.main',
            },
            '& .MuiRating-iconHover': {
              color: 'primary.light',
            },
          }}
        />
        <Box sx={{ minWidth: 140 }}>
          {(hover !== -1 || value) && (
            <Chip
              label={getLabelText(hover !== -1 ? hover : value || 0)}
              size="small"
              color={
                (hover !== -1 ? hover : value || 0) >= 4
                  ? 'success'
                  : (hover !== -1 ? hover : value || 0) >= 3
                  ? 'primary'
                  : 'warning'
              }
              variant="outlined"
            />
          )}
        </Box>
      </Box>
    </Box>
  )
}

// Blind rating explanation component
function BlindRatingInfo() {
  const [expanded, setExpanded] = useState(false)

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        mb: 3,
        bgcolor: 'info.50',
        border: '1px solid',
        borderColor: 'info.200',
        borderRadius: 2,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <InfoIcon color="info" fontSize="small" />
          <Typography variant="subtitle2" color="info.main">
            How do ratings work?
          </Typography>
        </Box>
        <IconButton size="small">
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>
      
      <Collapse in={expanded}>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary" paragraph>
            To encourage honest and thoughtful feedback, ratings remain private
            until both parties have submitted their reviews, or until 7 days have passed.
          </Typography>
          <Typography variant="body2" color="text.secondary" fontWeight={500}>
            This helps:
          </Typography>
          <Box component="ul" sx={{ pl: 2, mt: 1, mb: 0 }}>
            <Typography component="li" variant="body2" color="text.secondary">
              Encourage honest, unbiased feedback
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Allow both parties to share their true experience
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Build trust within our community
            </Typography>
          </Box>
        </Box>
      </Collapse>
    </Paper>
  )
}

export default function RatingSubmitDialog({
  open,
  onClose,
  participantId,
  recipientId,
  recipientName,
  exchangeTitle,
}: RatingSubmitProps) {
  const queryClient = useQueryClient()
  
  // Rating values - all three required
  const [reliabilityRating, setReliabilityRating] = useState<number | null>(null)
  const [kindnessRating, setKindnessRating] = useState<number | null>(null)
  const [helpfulnessRating, setHelpfulnessRating] = useState<number | null>(null)
  const [publicComment, setPublicComment] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  // Check rating status
  const { data: ratingStatus } = useQuery({
    queryKey: ['rating-status', participantId],
    queryFn: async () => {
      const response = await apiClient.get(`/ratings/status/${participantId}`)
      return response.data
    },
    enabled: open && !!participantId,
  })

  // Submit rating mutation
  const submitMutation = useMutation({
    mutationFn: async (data: RatingData) => {
      const response = await apiClient.post('/ratings/', data)
      return response.data
    },
    onSuccess: () => {
      setSuccess(true)
      queryClient.invalidateQueries({ queryKey: ['rating-status', participantId] })
      queryClient.invalidateQueries({ queryKey: ['ratings'] })
      // Close after showing success message
      setTimeout(() => {
        onClose()
        resetForm()
      }, 2000)
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to submit rating. Please try again.')
    },
  })

  const resetForm = () => {
    setReliabilityRating(null)
    setKindnessRating(null)
    setHelpfulnessRating(null)
    setPublicComment('')
    setError(null)
    setSuccess(false)
  }

  useEffect(() => {
    if (!open) {
      resetForm()
    }
  }, [open])

  const handleSubmit = () => {
    // All three ratings are required
    if (!reliabilityRating || !kindnessRating || !helpfulnessRating) {
      setError('Please provide ratings for all three categories')
      return
    }

    const data: RatingData = {
      recipient_id: recipientId,
      participant_id: participantId,
      reliability_rating: reliabilityRating,
      kindness_rating: kindnessRating,
      helpfulness_rating: helpfulnessRating,
    }

    if (publicComment.trim()) data.public_comment = publicComment.trim()

    setError(null)
    submitMutation.mutate(data)
  }

  // Calculate overall rating for preview
  const calculatedOverall = (reliabilityRating && kindnessRating && helpfulnessRating)
    ? Math.round((reliabilityRating + kindnessRating + helpfulnessRating) / 3)
    : null

  const canSubmit = ratingStatus?.can_submit_rating && !ratingStatus?.has_submitted_rating
  const allRatingsProvided = reliabilityRating && kindnessRating && helpfulnessRating

  // If already submitted, show status
  if (ratingStatus?.has_submitted_rating) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
        <DialogTitle>Rating Submitted</DialogTitle>
        <DialogContent>
          <Alert severity="success" sx={{ mb: 2 }}>
            <Typography variant="body2">
              You've already shared your feedback for this exchange. Thank you!
            </Typography>
          </Alert>
          
          {!ratingStatus.is_visible && (
            <Alert severity="info">
              <Typography variant="body2">
                {ratingStatus.message}
              </Typography>
              {ratingStatus.days_until_visible && ratingStatus.days_until_visible > 0 && (
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Your rating will become visible in {ratingStatus.days_until_visible} day
                  {ratingStatus.days_until_visible !== 1 ? 's' : ''}.
                </Typography>
              )}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <StarIcon color="primary" />
          <Typography variant="h6">Share Your Experience</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {/* Exchange context */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary">
            How was your exchange with <strong>{recipientName}</strong>?
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {exchangeTitle}
          </Typography>
        </Box>

        {/* Blind rating explanation */}
        <BlindRatingInfo />

        {/* Success message */}
        {success && (
          <Alert
            severity="success"
            icon={<CheckCircleIcon />}
            sx={{ mb: 3 }}
          >
            <Typography variant="body2" fontWeight={500}>
              Thank you for your feedback!
            </Typography>
            <Typography variant="caption">
              Your rating helps build a trusting community.
            </Typography>
          </Alert>
        )}

        {/* Error message */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Can't rate yet */}
        {!canSubmit && !ratingStatus?.has_submitted_rating && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            {ratingStatus?.message || 'This exchange must be completed before you can leave a rating.'}
          </Alert>
        )}

        {/* Rating form */}
        {canSubmit && !success && (
          <>
            {/* Info about how overall is calculated */}
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                Rate your exchange partner in three categories below. Your overall rating will be
                automatically calculated as the average of these three scores.
              </Typography>
            </Alert>

            {/* Required: Reliability Rating */}
            <CategoryRating
              category="reliability"
              info={CATEGORIES.reliability}
              value={reliabilityRating}
              onChange={setReliabilityRating}
              disabled={submitMutation.isPending}
            />

            {/* Required: Kindness Rating */}
            <CategoryRating
              category="kindness"
              info={CATEGORIES.kindness}
              value={kindnessRating}
              onChange={setKindnessRating}
              disabled={submitMutation.isPending}
            />

            {/* Required: Helpfulness Rating */}
            <CategoryRating
              category="helpfulness"
              info={CATEGORIES.helpfulness}
              value={helpfulnessRating}
              onChange={setHelpfulnessRating}
              disabled={submitMutation.isPending}
            />

            {/* Show calculated overall rating */}
            {allRatingsProvided && calculatedOverall && (
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  mt: 2,
                  bgcolor: 'success.50',
                  border: '1px solid',
                  borderColor: 'success.200',
                  borderRadius: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <StarIcon color="success" />
                  <Box>
                    <Typography variant="subtitle2" color="success.main">
                      Overall Rating: {calculatedOverall}/5 - {RATING_LABELS[calculatedOverall]}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Calculated from your three category ratings
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            )}

            <Divider sx={{ my: 3 }} />

            {/* Public comment */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Share a public comment (optional)
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Your comment will be visible on {recipientName}'s profile. Please keep it
                constructive and kind.
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                placeholder="Share something positive about your experience..."
                value={publicComment}
                onChange={(e) => setPublicComment(e.target.value)}
                disabled={submitMutation.isPending}
                inputProps={{ maxLength: 1000 }}
                helperText={`${publicComment.length}/1000 characters`}
              />
            </Box>
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={submitMutation.isPending}>
          {success ? 'Close' : 'Cancel'}
        </Button>
        {canSubmit && !success && (
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={!allRatingsProvided || submitMutation.isPending}
            startIcon={submitMutation.isPending ? <CircularProgress size={20} /> : <StarIcon />}
          >
            {submitMutation.isPending ? 'Submitting...' : 'Submit Rating'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}

// Export for displaying ratings
export { RATING_LABELS, CATEGORIES }
