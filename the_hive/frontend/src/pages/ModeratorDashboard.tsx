// SRS FR-11: Moderator Dashboard for Reports and Content Moderation
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Divider,
  Snackbar,
  Tabs,
  Tab,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Report as ReportIcon,
  Person as PersonIcon,
  Work as WorkIcon,
  Forum as ForumIcon,
  Visibility as ViewIcon,
  CheckCircle as ResolveIcon,
  Delete as DeleteIcon,
  Block as BlockIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingIcon,
  SwapHoriz as ExchangeIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'

// Types
interface ReportStats {
  total_reports: number
  pending: number
  under_review: number
  resolved: number
  dismissed: number
  user_reports: number
  offer_reports: number
  need_reports: number
  comment_reports: number
  forum_topic_reports: number
  spam_reports: number
  harassment_reports: number
  inappropriate_reports: number
  scam_reports: number
  misinformation_reports: number
  other_reports: number
}

interface Report {
  id: number
  reporter: {
    id: number
    username: string
    full_name: string | null
  }
  reported_item: {
    type: string
    id: number
    title: string | null
    content: string | null
    creator_username: string | null
  }
  reason: string
  description: string
  status: string
  moderator_action: string
  moderator_notes: string | null
  created_at: string
  reviewed_at: string | null
  resolved_at: string | null
}

interface ReportListResponse {
  reports: Report[]
  total: number
  pending_count: number
  under_review_count: number
  resolved_count: number
  page: number
  page_size: number
}

interface DashboardStats {
  total_offers: number
  total_needs: number
  active_offers: number
  active_needs: number
  completed_exchanges: number
  total_hours_exchanged: number
  active_users: number
}

const ModeratorDashboard = () => {
  const { user, isLoading: authLoading } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [statusFilter, setStatusFilter] = useState<string>('pending')
  const [selectedReport, setSelectedReport] = useState<Report | null>(null)
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false)
  const [removeDialogOpen, setRemoveDialogOpen] = useState(false)
  const [userActionDialogOpen, setUserActionDialogOpen] = useState(false)
  const [userActionType, setUserActionType] = useState<'suspend' | 'ban' | 'warning'>('warning')
  const [suspensionDays, setSuspensionDays] = useState(7)
  const [actionReason, setActionReason] = useState('')
  const [moderatorAction, setModeratorAction] = useState('none')
  const [moderatorNotes, setModeratorNotes] = useState('')
  const [resolveStatus, setResolveStatus] = useState('resolved')
  const [successMessage, setSuccessMessage] = useState('')

  // Show loading while auth is initializing
  if (authLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  // Check if user is moderator after auth is loaded
  if (!user || (user.role !== 'moderator' && user.role !== 'admin')) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          You do not have permission to access the moderator dashboard.
        </Alert>
      </Container>
    )
  }

  // Fetch report statistics
  const { data: stats, isLoading: statsLoading } = useQuery<ReportStats>({
    queryKey: ['reportStats'],
    queryFn: async () => {
      const response = await apiClient.get('/reports/stats')
      return response.data
    },
  })

  // Fetch dashboard statistics
  const {
    data: dashboardStats,
    isLoading: dashboardStatsLoading,
    isError: dashboardStatsError
  } = useQuery<DashboardStats>({
    queryKey: ['dashboardStats'],
    queryFn: async () => {
      const response = await apiClient.get('/dashboard/stats')
      return response.data
    },
    retry: false, // Don't retry if endpoint doesn't exist yet
  })

  // Fetch reports list
  const {
    data: reportsData,
    isLoading: reportsLoading,
    refetch: refetchReports,
  } = useQuery<ReportListResponse>({
    queryKey: ['reports', statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') {
        params.append('status', statusFilter)
      }
      params.append('limit', '50')
      const response = await apiClient.get(`/reports/?${params}`)
      return response.data
    },
  })

  // Resolve report mutation
  const resolveReportMutation = useMutation({
    mutationFn: async ({
      reportId,
      status,
      action,
      notes,
    }: {
      reportId: number
      status: string
      action: string
      notes: string
    }) => {
      await apiClient.put(`/reports/${reportId}`, {
        status,
        moderator_action: action,
        moderator_notes: notes,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      queryClient.invalidateQueries({ queryKey: ['reportStats'] })
      setResolveDialogOpen(false)
      setSelectedReport(null)
      setModeratorNotes('')
      setModeratorAction('none')
    },
  })

  // Remove content mutation
  const removeContentMutation = useMutation({
    mutationFn: async ({ type, id, reason }: { type: string; id: number; reason: string }) => {
      console.log('Removing content:', { type, id, reason })
      const response = await apiClient.delete(`/moderation/${type}s/${id}`, {
        data: { reason },
      })
      console.log('Remove content response:', response)
      return response.data
    },
    onSuccess: (data, variables) => {
      console.log('Content removed successfully')
      setSuccessMessage(`${variables.type.charAt(0).toUpperCase() + variables.type.slice(1)} removed successfully`)
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] })
      queryClient.invalidateQueries({ queryKey: ['mapFeed'] })
      setRemoveDialogOpen(false)
      setSelectedReport(null)
      setActionReason('')
    },
    onError: (error: any) => {
      console.error('Error removing content:', error)
      alert(`Failed to remove content: ${error.response?.data?.detail || error.message}`)
    },
  })

  // User action mutations
  const suspendUserMutation = useMutation({
    mutationFn: async ({ userId, days, reason }: { userId: number; days: number; reason: string }) => {
      await apiClient.put(`/moderation/users/${userId}/suspend`, {
        days,
        reason,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      setUserActionDialogOpen(false)
      setSelectedReport(null)
      setActionReason('')
    },
  })

  const banUserMutation = useMutation({
    mutationFn: async ({ userId, reason }: { userId: number; reason: string }) => {
      await apiClient.put(`/moderation/users/${userId}/ban`, {
        reason,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      setUserActionDialogOpen(false)
      setSelectedReport(null)
      setActionReason('')
    },
  })

  const handleResolveReport = () => {
    if (!selectedReport) return
    resolveReportMutation.mutate({
      reportId: selectedReport.id,
      status: resolveStatus,
      action: moderatorAction,
      notes: moderatorNotes,
    })
  }

  const handleConfirmRemoveContent = () => {
    if (!selectedReport) return

    console.log('handleConfirmRemoveContent called with report:', selectedReport)

    removeContentMutation.mutate({
      type: selectedReport.reported_item.type,
      id: selectedReport.reported_item.id,
      reason: actionReason || `Reported: ${selectedReport.reason}`,
    })
  }

  const handleUserAction = () => {
    if (!selectedReport || selectedReport.reported_item.type !== 'user') return

    const userId = selectedReport.reported_item.id

    if (userActionType === 'suspend') {
      suspendUserMutation.mutate({
        userId,
        days: suspensionDays,
        reason: actionReason,
      })
    } else if (userActionType === 'ban') {
      banUserMutation.mutate({
        userId,
        reason: actionReason,
      })
    } else {
      // Warning - just resolve the report with warning action
      resolveReportMutation.mutate({
        reportId: selectedReport.id,
        status: 'resolved',
        action: 'warning',
        notes: actionReason,
      })
      setUserActionDialogOpen(false)
      setSelectedReport(null)
    }
  }

  const handleViewItem = (report: Report) => {
    const { type, id } = report.reported_item
    if (type === 'offer') navigate(`/offers/${id}`)
    else if (type === 'need') navigate(`/needs/${id}`)
    else if (type === 'user') navigate(`/profile/${report.reported_item.creator_username}`)
    else if (type === 'forum_topic') navigate(`/forum/${id}`)
  }

  const getReasonColor = (reason: string) => {
    switch (reason) {
      case 'spam':
        return 'warning'
      case 'harassment':
        return 'error'
      case 'inappropriate':
        return 'error'
      case 'scam':
        return 'error'
      case 'misinformation':
        return 'warning'
      default:
        return 'default'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'warning'
      case 'resolved':
        return 'success'
      case 'dismissed':
        return 'default'
      default:
        return 'default'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Pending'
      case 'under_review':
        return 'Under Review'
      case 'resolved':
        return 'Resolved'
      case 'dismissed':
        return 'Dismissed'
      default:
        return status.charAt(0).toUpperCase() + status.slice(1)
    }
  }

  if (statsLoading || reportsLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <DashboardIcon sx={{ fontSize: 40, color: 'primary.main' }} />
          <Box>
            <Typography variant="h4" fontWeight={700}>
              Moderator Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Review reports and monitor platform activity
            </Typography>
          </Box>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => {
            refetchReports()
            queryClient.invalidateQueries({ queryKey: ['reportStats'] })
            queryClient.invalidateQueries({ queryKey: ['dashboardStats'] })
          }}
        >
          Refresh
        </Button>
      </Box>

      {/* Platform Overview Statistics */}
      {dashboardStatsLoading && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
            Platform Overview
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={40} />
          </Box>
        </Box>
      )}

      {dashboardStatsError && (
        <Alert severity="info" sx={{ mb: 4 }}>
          <Typography variant="body2" fontWeight={600}>
            Platform statistics are not available
          </Typography>
          <Typography variant="caption">
            The backend server may need to be restarted to enable this feature.
            Restart the backend and refresh this page.
          </Typography>
        </Alert>
      )}

      {dashboardStats && (
        <>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
            Platform Overview
          </Typography>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <TrendingIcon color="primary" sx={{ fontSize: 40 }} />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {dashboardStats.active_offers + dashboardStats.active_needs}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Active Exchanges
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <ExchangeIcon color="success" sx={{ fontSize: 40 }} />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {dashboardStats.completed_exchanges}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Completed
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ bgcolor: 'primary.light' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <ExchangeIcon sx={{ fontSize: 40, color: 'primary.dark' }} />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {dashboardStats.total_hours_exchanged.toFixed(1)}h
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Hours Exchanged
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <PersonIcon color="info" sx={{ fontSize: 40 }} />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {dashboardStats.active_users}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Active Users
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Service Types Breakdown */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom fontWeight={600}>
                    Service Types
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <WorkIcon fontSize="small" color="primary" />
                        <Typography>Active Offers</Typography>
                      </Box>
                      <Chip label={dashboardStats.active_offers} size="small" color="primary" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <WorkIcon fontSize="small" color="secondary" />
                        <Typography>Active Needs</Typography>
                      </Box>
                      <Chip label={dashboardStats.active_needs} size="small" color="secondary" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <WorkIcon fontSize="small" />
                        <Typography>Total Offers</Typography>
                      </Box>
                      <Chip label={dashboardStats.total_offers} size="small" variant="outlined" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <WorkIcon fontSize="small" />
                        <Typography>Total Needs</Typography>
                      </Box>
                      <Chip label={dashboardStats.total_needs} size="small" variant="outlined" />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Activity Metrics */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom fontWeight={600}>
                    Activity Metrics
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Completion Rate</Typography>
                      <Chip
                        label={`${((dashboardStats.completed_exchanges / (dashboardStats.total_offers + dashboardStats.total_needs || 1)) * 100).toFixed(1)}%`}
                        size="small"
                        color="success"
                      />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Avg Hours/Exchange</Typography>
                      <Chip
                        label={`${(dashboardStats.total_hours_exchanged / (dashboardStats.completed_exchanges || 1)).toFixed(1)}h`}
                        size="small"
                      />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Avg Activity/User</Typography>
                      <Chip
                        label={`${((dashboardStats.total_offers + dashboardStats.total_needs) / (dashboardStats.active_users || 1)).toFixed(1)}`}
                        size="small"
                      />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Divider sx={{ my: 4 }} />
        </>
      )}

      {/* Report Statistics */}
      {stats && (
        <>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
            Moderation Reports
          </Typography>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={4}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <ReportIcon color="primary" sx={{ fontSize: 40 }} />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {stats.total_reports}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Reports
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ bgcolor: 'warning.light' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <ReportIcon sx={{ fontSize: 40, color: 'warning.dark' }} />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {stats.pending}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Pending Review
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ bgcolor: 'success.light' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <ResolveIcon sx={{ fontSize: 40, color: 'success.dark' }} />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {stats.resolved}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Resolved
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Report Type Breakdown */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom fontWeight={600}>
                    Reports by Type
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <PersonIcon fontSize="small" />
                        <Typography>Users</Typography>
                      </Box>
                      <Chip label={stats.user_reports} size="small" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <WorkIcon fontSize="small" />
                        <Typography>Offers</Typography>
                      </Box>
                      <Chip label={stats.offer_reports} size="small" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <WorkIcon fontSize="small" />
                        <Typography>Needs</Typography>
                      </Box>
                      <Chip label={stats.need_reports} size="small" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <ForumIcon fontSize="small" />
                        <Typography>Comments</Typography>
                      </Box>
                      <Chip label={stats.comment_reports} size="small" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <ForumIcon fontSize="small" />
                        <Typography>Forum Topics</Typography>
                      </Box>
                      <Chip label={stats.forum_topic_reports} size="small" />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Report Reason Breakdown */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom fontWeight={600}>
                    Reports by Reason
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Spam</Typography>
                      <Chip label={stats.spam_reports} size="small" color="warning" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Harassment</Typography>
                      <Chip label={stats.harassment_reports} size="small" color="error" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Inappropriate</Typography>
                      <Chip label={stats.inappropriate_reports} size="small" color="error" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Scam</Typography>
                      <Chip label={stats.scam_reports} size="small" color="error" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Misinformation</Typography>
                      <Chip label={stats.misinformation_reports} size="small" color="warning" />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Other</Typography>
                      <Chip label={stats.other_reports} size="small" />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}

      {/* Reports List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Report Queue
          </Typography>

          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs
              value={statusFilter}
              onChange={(_, newValue) => setStatusFilter(newValue)}
              aria-label="report status tabs"
            >
              <Tab label="Pending" value="pending" />
              <Tab label="Resolved" value="resolved" />
              <Tab label="Dismissed" value="dismissed" />
            </Tabs>
          </Box>

          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Reason</TableCell>
                  <TableCell>Reporter</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reportsData?.reports.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                        No reports found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  reportsData?.reports.map((report) => (
                    <TableRow key={report.id}>
                      <TableCell>{report.id}</TableCell>
                      <TableCell>
                        <Chip
                          label={report.reported_item.type}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={report.reason}
                          size="small"
                          color={getReasonColor(report.reason)}
                        />
                      </TableCell>
                      <TableCell>{report.reporter.username}</TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                          {report.description}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getStatusLabel(report.status)}
                          size="small"
                          color={getStatusColor(report.status)}
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(report.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Item">
                          <IconButton
                            size="small"
                            onClick={() => handleViewItem(report)}
                          >
                            <ViewIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {report.status === 'pending' && (
                          <>
                            <Tooltip title="Resolve Report">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => {
                                  setSelectedReport(report)
                                  setResolveDialogOpen(true)
                                }}
                              >
                                <ResolveIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            {report.reported_item.type === 'user' ? (
                              <Tooltip title="User Actions">
                                <IconButton
                                  size="small"
                                  color="warning"
                                  onClick={() => {
                                    setSelectedReport(report)
                                    setUserActionDialogOpen(true)
                                  }}
                                >
                                  <BlockIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            ) : (
                              <Tooltip title="Remove Content">
                                <IconButton
                                  size="small"
                                  color="error"
                                    onClick={() => {
                                      setSelectedReport(report)
                                      setRemoveDialogOpen(true)
                                    }}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                          </>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {reportsData && reportsData.total > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Showing {reportsData.reports.length} of {reportsData.total} reports
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Resolve Report Dialog */}
      <Dialog
        open={resolveDialogOpen}
        onClose={() => setResolveDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Resolve Report #{selectedReport?.id}</DialogTitle>
        <DialogContent>
          {selectedReport && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
              <Alert severity="info">
                <Typography variant="body2" fontWeight={600}>
                  Reported Item: {selectedReport.reported_item.type}
                </Typography>
                <Typography variant="body2">
                  {selectedReport.reported_item.title || selectedReport.reported_item.content}
                </Typography>
              </Alert>

              <FormControl fullWidth>
                <InputLabel>Resolution Status</InputLabel>
                <Select
                  value={resolveStatus}
                  label="Resolution Status"
                  onChange={(e) => setResolveStatus(e.target.value)}
                >
                  <MenuItem value="resolved">Resolved</MenuItem>
                  <MenuItem value="dismissed">Dismissed</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Moderator Action</InputLabel>
                <Select
                  value={moderatorAction}
                  label="Moderator Action"
                  onChange={(e) => setModeratorAction(e.target.value)}
                >
                  <MenuItem value="none">No Action</MenuItem>
                  <MenuItem value="warning">Warning Issued</MenuItem>
                  <MenuItem value="content_removed">Content Removed</MenuItem>
                  <MenuItem value="user_suspended">User Suspended</MenuItem>
                  <MenuItem value="user_banned">User Banned</MenuItem>
                </Select>
              </FormControl>

              <TextField
                label="Moderator Notes"
                multiline
                rows={4}
                fullWidth
                value={moderatorNotes}
                onChange={(e) => setModeratorNotes(e.target.value)}
                placeholder="Add notes about your decision..."
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResolveDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleResolveReport}
            disabled={resolveReportMutation.isPending}
          >
            {resolveReportMutation.isPending ? 'Resolving...' : 'Resolve Report'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Remove Content Dialog */}
      <Dialog
        open={removeDialogOpen}
        onClose={() => setRemoveDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Remove Content</DialogTitle>
        <DialogContent>
          {selectedReport && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
              <Alert severity="warning">
                <Typography variant="body2" fontWeight={600}>
                  Are you sure you want to remove this {selectedReport.reported_item.type}?
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {selectedReport.reported_item.title || selectedReport.reported_item.content?.substring(0, 100)}
                </Typography>
              </Alert>

              <TextField
                label="Reason for Removal"
                multiline
                rows={3}
                fullWidth
                value={actionReason}
                onChange={(e) => setActionReason(e.target.value)}
                placeholder="Explain why this content is being removed..."
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemoveDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleConfirmRemoveContent}
            disabled={removeContentMutation.isPending}
          >
            {removeContentMutation.isPending ? 'Removing...' : 'Remove Content'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* User Action Dialog (Suspend/Ban/Warning) */}
      <Dialog
        open={userActionDialogOpen}
        onClose={() => setUserActionDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>User Moderation Action</DialogTitle>
        <DialogContent>
          {selectedReport && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
              <Alert severity="info">
                <Typography variant="body2" fontWeight={600}>
                  User: @{selectedReport.reported_item.creator_username}
                </Typography>
                <Typography variant="body2">
                  Reported for: {selectedReport.reason}
                </Typography>
              </Alert>

              <FormControl fullWidth>
                <InputLabel>Action Type</InputLabel>
                <Select
                  value={userActionType}
                  label="Action Type"
                  onChange={(e) => setUserActionType(e.target.value as any)}
                >
                  <MenuItem value="warning">Issue Warning</MenuItem>
                  <MenuItem value="suspend">Temporary Suspension</MenuItem>
                  <MenuItem value="ban">Permanent Ban</MenuItem>
                </Select>
              </FormControl>

              {userActionType === 'suspend' && (
                <TextField
                  label="Suspension Duration (days)"
                  type="number"
                  fullWidth
                  value={suspensionDays}
                  onChange={(e) => setSuspensionDays(parseInt(e.target.value) || 7)}
                  inputProps={{ min: 1, max: 365 }}
                />
              )}

              <TextField
                label="Reason"
                multiline
                rows={4}
                fullWidth
                required
                value={actionReason}
                onChange={(e) => setActionReason(e.target.value)}
                placeholder="Explain the reason for this action..."
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUserActionDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color={userActionType === 'ban' ? 'error' : 'warning'}
            onClick={handleUserAction}
            disabled={!actionReason || suspendUserMutation.isPending || banUserMutation.isPending}
          >
            {(suspendUserMutation.isPending || banUserMutation.isPending)
              ? 'Processing...'
              : userActionType === 'warning'
                ? 'Issue Warning'
                : userActionType === 'suspend'
                  ? 'Suspend User'
                  : 'Ban User'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Notification */}
      <Snackbar
        open={!!successMessage}
        autoHideDuration={4000}
        onClose={() => setSuccessMessage('')}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSuccessMessage('')} severity="success" sx={{ width: '100%' }}>
          {successMessage}
        </Alert>
      </Snackbar>
    </Container>
  )
}

export default ModeratorDashboard
