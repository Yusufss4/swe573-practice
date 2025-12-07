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
  Tabs,
  Tab,
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
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Report as ReportIcon,
  Person as PersonIcon,
  Work as WorkIcon,
  Forum as ForumIcon,
  Visibility as ViewIcon,
  CheckCircle as ResolveIcon,
  CheckCircle,
  Delete as DeleteIcon,
  Block as BlockIcon,
  Refresh as RefreshIcon,
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

const ModeratorDashboard = () => {
  const { user, isLoading: authLoading } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [activeTab, setActiveTab] = useState(0)
  const [statusFilter, setStatusFilter] = useState<string>('pending')
  const [selectedReport, setSelectedReport] = useState<Report | null>(null)
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false)
  const [moderatorAction, setModeratorAction] = useState('none')
  const [moderatorNotes, setModeratorNotes] = useState('')
  const [resolveStatus, setResolveStatus] = useState('resolved')

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
      await apiClient.delete(`/moderation/${type}s/${id}`, {
        data: { reason },
      })
    },
    onSuccess: () => {
      refetchReports()
    },
  })

  // Suspend user mutation
  const suspendUserMutation = useMutation({
    mutationFn: async ({ userId, days, reason }: { userId: number; days: number; reason: string }) => {
      await apiClient.put(`/moderation/users/${userId}/suspend`, {
        days,
        reason,
      })
    },
    onSuccess: () => {
      refetchReports()
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

  const handleRemoveContent = (report: Report) => {
    if (window.confirm(`Remove this ${report.reported_item.type}?`)) {
      removeContentMutation.mutate({
        type: report.reported_item.type,
        id: report.reported_item.id,
        reason: `Reported: ${report.reason}`,
      })
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
      case 'under_review':
        return 'info'
      case 'resolved':
        return 'success'
      case 'dismissed':
        return 'default'
      default:
        return 'default'
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
              Review reports and manage content
            </Typography>
          </Box>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => {
            refetchReports()
            queryClient.invalidateQueries({ queryKey: ['reportStats'] })
          }}
        >
          Refresh
        </Button>
      </Box>

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
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

          <Grid item xs={12} sm={6} md={3}>
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

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'info.light' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <ViewIcon sx={{ fontSize: 40, color: 'info.dark' }} />
                  <Box>
                    <Typography variant="h4" fontWeight={700}>
                      {stats.under_review}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Under Review
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'success.light' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <CheckCircle sx={{ fontSize: 40, color: 'success.dark' }} />
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
      )}

      {/* Reports List */}
      <Card>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
              <Tab label="All Reports" />
              <Tab
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    Pending
                    {stats && stats.pending > 0 && (
                      <Chip label={stats.pending} size="small" color="warning" />
                    )}
                  </Box>
                }
                onClick={() => setStatusFilter('pending')}
              />
              <Tab label="Under Review" onClick={() => setStatusFilter('under_review')} />
              <Tab label="Resolved" onClick={() => setStatusFilter('resolved')} />
            </Tabs>
          </Box>

          <FormControl size="small" sx={{ mb: 2, minWidth: 200 }}>
            <InputLabel>Filter by Status</InputLabel>
            <Select
              value={statusFilter}
              label="Filter by Status"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="under_review">Under Review</MenuItem>
              <MenuItem value="resolved">Resolved</MenuItem>
              <MenuItem value="dismissed">Dismissed</MenuItem>
            </Select>
          </FormControl>

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
                          label={report.status}
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
                            {report.reported_item.type !== 'user' && (
                              <Tooltip title="Remove Content">
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => handleRemoveContent(report)}
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
                  <MenuItem value="under_review">Under Review</MenuItem>
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
    </Container>
  )
}

export default ModeratorDashboard
