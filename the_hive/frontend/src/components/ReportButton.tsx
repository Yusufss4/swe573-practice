import { useState } from 'react'
import {
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tooltip,
  SelectChangeEvent,
} from '@mui/material'
import { Flag as FlagIcon } from '@mui/icons-material'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

interface ReportButtonProps {
  itemType: 'user' | 'offer' | 'need' | 'comment' | 'forum_topic'
  itemId: number
  itemTitle?: string
  size?: 'small' | 'medium' | 'large'
}

interface ReportData {
  reported_user_id?: number
  reported_offer_id?: number
  reported_need_id?: number
  reported_comment_id?: number
  reported_forum_topic_id?: number
  reason: string
  description: string
}

const ReportButton = ({ itemType, itemId, itemTitle, size = 'small' }: ReportButtonProps) => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const [open, setOpen] = useState(false)
  const [reason, setReason] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const reportMutation = useMutation({
    mutationFn: async (data: ReportData) => {
      const response = await apiClient.post('/reports/', data)
      return response.data
    },
    onSuccess: () => {
      setSuccess(true)
      setError(null)
      // Auto-close after 2 seconds
      setTimeout(() => {
        handleClose()
      }, 2000)
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to submit report')
    },
  })

  const handleOpen = () => {
    if (!user) {
      navigate('/login')
      return
    }
    setOpen(true)
    setError(null)
    setSuccess(false)
  }

  const handleClose = () => {
    setOpen(false)
    setReason('')
    setDescription('')
    setError(null)
    setSuccess(false)
  }

  const handleSubmit = () => {
    if (!reason) {
      setError('Please select a reason')
      return
    }
    if (!description.trim()) {
      setError('Please provide a description')
      return
    }

    const reportData: ReportData = {
      reason,
      description: description.trim(),
    }

    // Set the appropriate item ID field
    switch (itemType) {
      case 'user':
        reportData.reported_user_id = itemId
        break
      case 'offer':
        reportData.reported_offer_id = itemId
        break
      case 'need':
        reportData.reported_need_id = itemId
        break
      case 'comment':
        reportData.reported_comment_id = itemId
        break
      case 'forum_topic':
        reportData.reported_forum_topic_id = itemId
        break
    }

    reportMutation.mutate(reportData)
  }

  const getItemTypeLabel = () => {
    switch (itemType) {
      case 'user':
        return 'User'
      case 'offer':
        return 'Offer'
      case 'need':
        return 'Need'
      case 'comment':
        return 'Comment'
      case 'forum_topic':
        return 'Forum Topic'
    }
  }

  return (
    <>
      <Tooltip title={`Report ${getItemTypeLabel()}`}>
        <IconButton
          size={size}
          onClick={handleOpen}
          sx={{
            color: 'text.secondary',
            '&:hover': {
              color: 'error.main',
              bgcolor: 'error.light',
              opacity: 0.1,
            },
          }}
        >
          <FlagIcon fontSize={size} />
        </IconButton>
      </Tooltip>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          Report {getItemTypeLabel()}
          {itemTitle && `: "${itemTitle}"`}
        </DialogTitle>
        
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Report submitted successfully. Our moderators will review it soon.
            </Alert>
          )}

          {!success && (
            <>
              <FormControl fullWidth sx={{ mb: 3, mt: 1 }}>
                <InputLabel>Reason for Report</InputLabel>
                <Select
                  value={reason}
                  label="Reason for Report"
                  onChange={(e: SelectChangeEvent) => setReason(e.target.value)}
                >
                  <MenuItem value="spam">Spam</MenuItem>
                  <MenuItem value="harassment">Harassment</MenuItem>
                  <MenuItem value="inappropriate">Inappropriate Content</MenuItem>
                  <MenuItem value="scam">Scam or Fraud</MenuItem>
                  <MenuItem value="misinformation">Misinformation</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                multiline
                rows={4}
                label="Description"
                placeholder="Please provide details about why you're reporting this..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                helperText="Help us understand the issue"
              />
            </>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose}>
            {success ? 'Close' : 'Cancel'}
          </Button>
          {!success && (
            <Button
              variant="contained"
              color="error"
              onClick={handleSubmit}
              disabled={reportMutation.isPending}
            >
              {reportMutation.isPending ? 'Submitting...' : 'Submit Report'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </>
  )
}

export default ReportButton
