// SRS FR-10.4: Rating Display Component for User Profiles
// Shows individual ratings with peace-oriented presentation

import { useState } from 'react'
import {
  Box,
  Typography,
  Rating as MuiRating,
  Paper,
  Chip,
  Avatar,
  Button,
  Skeleton,
  Collapse,
} from '@mui/material'
import {
  Schedule as ScheduleIcon,
  Favorite as FavoriteIcon,
  Support as SupportIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  FormatQuote as QuoteIcon,
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import apiClient from '@/services/api'

// Rating labels
const RATING_LABELS: Record<number, string> = {
  1: 'Needs Improvement',
  2: 'Below Expectations',
  3: 'Met Expectations',
  4: 'Above Expectations',
  5: 'Exceptional',
}

interface RatingItem {
  id: number
  from_user_id: number
  from_username: string | null
  to_user_id: number
  to_username: string | null
  participant_id: number
  general_rating: number
  general_rating_label: string
  reliability_rating: number
  reliability_rating_label: string
  kindness_rating: number
  kindness_rating_label: string
  helpfulness_rating: number
  helpfulness_rating_label: string
  average_rating: number
  public_comment: string | null
  visibility: string
  is_visible: boolean
  created_at: string
}

// Individual rating card
function RatingCard({ rating }: { rating: RatingItem }) {
  const navigate = useNavigate()
  const [expanded, setExpanded] = useState(false)
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }
  
  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
        <Avatar
          sx={{ bgcolor: 'primary.main', cursor: 'pointer' }}
          onClick={() => rating.from_username && navigate(`/profile/${rating.from_username}`)}
        >
          {rating.from_username?.[0]?.toUpperCase() || '?'}
        </Avatar>
        
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography
              variant="subtitle2"
              sx={{
                cursor: 'pointer',
                '&:hover': { color: 'primary.main' },
              }}
              onClick={() => rating.from_username && navigate(`/profile/${rating.from_username}`)}
            >
              {rating.from_username || 'Anonymous'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              • {formatDate(rating.created_at)}
            </Typography>
          </Box>
          
          {/* Overall rating */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
            <MuiRating value={rating.average_rating} readOnly precision={0.1} size="small" />
            <Chip
              label={rating.general_rating_label}
              size="small"
              color={rating.general_rating >= 4 ? 'success' : rating.general_rating >= 3 ? 'primary' : 'warning'}
              variant="outlined"
            />
          </Box>
        </Box>
      </Box>
      
      {/* Public comment */}
      {rating.public_comment && (
        <Box sx={{ mt: 2, pl: 7 }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <QuoteIcon sx={{ color: 'text.disabled', fontSize: 20 }} />
            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
              {rating.public_comment}
            </Typography>
          </Box>
        </Box>
      )}
      
      {/* Category ratings (expandable) - all three are always present */}
      <Button
        size="small"
        onClick={() => setExpanded(!expanded)}
        endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        sx={{ mt: 1, ml: 6 }}
      >
        {expanded ? 'Hide details' : 'View details'}
      </Button>
      
      <Collapse in={expanded}>
        <Box sx={{ mt: 1, pl: 7 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <ScheduleIcon fontSize="small" color="action" />
            <Typography variant="caption">Reliability:</Typography>
            <MuiRating value={rating.reliability_rating} readOnly size="small" />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <FavoriteIcon fontSize="small" color="action" />
            <Typography variant="caption">Kindness:</Typography>
            <MuiRating value={rating.kindness_rating} readOnly size="small" />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <SupportIcon fontSize="small" color="action" />
            <Typography variant="caption">Helpfulness:</Typography>
            <MuiRating value={rating.helpfulness_rating} readOnly size="small" />
          </Box>
        </Box>
      </Collapse>
    </Paper>
  )
}

// Ratings list component
interface RatingsListProps {
  userId: number
  limit?: number
}

export function RatingsList({ userId, limit = 10 }: RatingsListProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['user-ratings', userId],
    queryFn: async () => {
      const response = await apiClient.get(`/ratings/user/${userId}`, {
        params: { limit },
      })
      return response.data
    },
  })
  
  if (isLoading) {
    return (
      <Box>
        {[1, 2, 3].map((i) => (
          <Paper key={i} sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Skeleton variant="circular" width={40} height={40} />
              <Box sx={{ flex: 1 }}>
                <Skeleton variant="text" width="40%" />
                <Skeleton variant="text" width="60%" />
              </Box>
            </Box>
          </Paper>
        ))}
      </Box>
    )
  }
  
  if (!data?.items?.length) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          No ratings to display yet
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Ratings will appear here after exchanges are completed and both parties have shared feedback
        </Typography>
      </Paper>
    )
  }
  
  return (
    <Box>
      {data.items.map((rating: RatingItem) => (
        <RatingCard key={rating.id} rating={rating} />
      ))}
      
      {data.total > limit && (
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Showing {data.items.length} of {data.total} ratings
          </Typography>
        </Box>
      )}
    </Box>
  )
}

export { RATING_LABELS }
