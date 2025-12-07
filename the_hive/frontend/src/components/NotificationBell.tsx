import React, { useState, useEffect, useRef } from 'react'
import {
  IconButton,
  Badge,
  Popover,
  List,
  ListItem,
  ListItemText,
  Typography,
  Box,
  Divider,
  Button,
  CircularProgress,
} from '@mui/material'
import NotificationsIcon from '@mui/icons-material/Notifications'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Notification, NotificationListResponse } from '../types'
import api from '../services/api'

// SRS FR-N.1: Notification bell component with badge and dropdown

const NotificationBell: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery<NotificationListResponse>({
    queryKey: ['notifications'],
    queryFn: async () => {
      const response = await api.get('/notifications')
      return response.data
    },
    refetchInterval: 30000, // Poll every 30 seconds
  })

  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      await api.post(`/notifications/${notificationId}/read`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const markAllAsReadMutation = useMutation({
    mutationFn: async () => {
      await api.post('/notifications/read-all')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleNotificationClick = (notification: Notification) => {
    // Mark as read
    if (!notification.is_read) {
      markAsReadMutation.mutate(notification.id)
    }

    // Navigate to relevant page
    if (notification.related_offer_id) {
      navigate(`/offers/${notification.related_offer_id}`)
    } else if (notification.related_need_id) {
      navigate(`/needs/${notification.related_need_id}`)
    } else if (notification.related_user_id) {
      navigate(`/profile/${notification.related_user_id}`)
    }

    handleClose()
  }

  const handleMarkAllRead = () => {
    markAllAsReadMutation.mutate()
  }

  const getNotificationIcon = (type: string): string => {
    switch (type) {
      case 'application_received':
        return '📨'
      case 'application_accepted':
        return '✅'
      case 'application_declined':
        return '❌'
      case 'participant_cancelled':
        return '🚫'
      case 'exchange_awaiting_confirmation':
        return '⏳'
      case 'exchange_completed':
        return '🎉'
      case 'rating_received':
        return '⭐'
      default:
        return '🔔'
    }
  }

  const formatRelativeTime = (timestamp: string): string => {
    const now = new Date()
    const past = new Date(timestamp)
    const diffMs = now.getTime() - past.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return past.toLocaleDateString()
  }

  const open = Boolean(anchorEl)

  return (
    <>
      <IconButton color="inherit" onClick={handleClick}>
        <Badge badgeContent={data?.unread_count || 0} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Box sx={{ width: 400, maxHeight: 600 }}>
          <Box
            sx={{
              p: 2,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Typography variant="h6">Notifications</Typography>
            {data && data.unread_count > 0 && (
              <Button size="small" onClick={handleMarkAllRead}>
                Mark all read
              </Button>
            )}
          </Box>
          <Divider />

          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : data && data.notifications.length > 0 ? (
            <List sx={{ maxHeight: 500, overflow: 'auto', p: 0 }}>
              {data.notifications.map((notification) => (
                <React.Fragment key={notification.id}>
                  <ListItem
                    button
                    onClick={() => handleNotificationClick(notification)}
                    sx={{
                      bgcolor: notification.is_read ? 'transparent' : 'action.hover',
                      '&:hover': { bgcolor: 'action.selected' },
                    }}
                  >
                    <Box sx={{ mr: 2, fontSize: '1.5rem' }}>
                      {getNotificationIcon(notification.type)}
                    </Box>
                    <ListItemText
                      primary={
                        <Typography
                          variant="body2"
                          fontWeight={notification.is_read ? 'normal' : 'bold'}
                        >
                          {notification.title}
                        </Typography>
                      }
                      secondary={
                        <>
                          <Typography variant="body2" color="text.secondary">
                            {notification.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatRelativeTime(notification.created_at)}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          ) : (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No notifications
              </Typography>
            </Box>
          )}
        </Box>
      </Popover>
    </>
  )
}

export default NotificationBell
