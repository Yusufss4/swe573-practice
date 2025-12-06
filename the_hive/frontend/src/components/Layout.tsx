// SRS: Main layout component
// Provides consistent navigation structure per SRS Section 3.3.1

import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import {
  AppBar,
  Box,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Container,
} from '@mui/material'
import {
  AccountCircle,
  Hive as HiveIcon,
  AccessTime,
  Add as AddIcon,
  Notifications as NotificationsIcon,
  Inbox as InboxIcon,
} from '@mui/icons-material'
import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'

/**
 * SRS Section 3.3.1: Clean, accessible layout with consistent navigation
 */
const Layout = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [createMenuAnchor, setCreateMenuAnchor] = useState<null | HTMLElement>(null)
  const [notificationsAnchor, setNotificationsAnchor] = useState<null | HTMLElement>(null)

  // Don't show navbar on login/register pages
  const hideNavbar = ['/login', '/register'].includes(location.pathname)

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleCreateMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setCreateMenuAnchor(event.currentTarget)
  }

  const handleCreateMenuClose = () => {
    setCreateMenuAnchor(null)
  }

  const handleNotificationsOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationsAnchor(event.currentTarget)
  }

  const handleNotificationsClose = () => {
    setNotificationsAnchor(null)
  }

  const handleLogout = () => {
    logout()
    handleClose()
    navigate('/login')
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* SRS Section 3.3.1: Enhanced Navigation header - hide on auth pages */}
      {!hideNavbar && (
        <AppBar 
          position="sticky" 
          sx={{ 
            bgcolor: 'background.paper',
            color: 'text.primary',
            boxShadow: 1,
          }}
        >
          <Toolbar sx={{ gap: 2 }}>
            {/* Logo and Brand */}
            <Box
              component={Link}
              to="/"
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                textDecoration: 'none',
                color: 'primary.main',
                mr: 2,
              }}
            >
              <HiveIcon sx={{ fontSize: 32 }} />
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  color: 'primary.main',
                  display: { xs: 'none', sm: 'block' },
                }}
              >
                The Hive
              </Typography>
            </Box>

            {/* Navigation Links - Desktop */}
            {isAuthenticated && (
              <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1, flexGrow: 1 }}>
                <Button 
                  color="inherit" 
                  component={Link} 
                  to="/home"
                  sx={{ color: 'text.primary' }}
                >
                  Home
                </Button>
                <Button 
                  color="inherit" 
                  component={Link} 
                  to="/"
                  sx={{ color: 'text.primary' }}
                >
                  Map
                </Button>
                <Button 
                  color="inherit" 
                  component={Link} 
                  to="/forum"
                  sx={{ color: 'text.primary' }}
                >
                  Forum
                </Button>
              </Box>
            )}

            {/* Spacer for non-authenticated users */}
            {!isAuthenticated && <Box sx={{ flexGrow: 1 }} />}

            {/* Right side - Authenticated user actions */}
            {isAuthenticated ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {/* Create Button with Dropdown */}
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleCreateMenuOpen}
                  sx={{
                    borderRadius: 2,
                    textTransform: 'none',
                    fontWeight: 600,
                    display: { xs: 'none', sm: 'flex' },
                  }}
                >
                  Create
                </Button>
                <IconButton
                  color="primary"
                  onClick={handleCreateMenuOpen}
                  sx={{ display: { xs: 'flex', sm: 'none' } }}
                >
                  <AddIcon />
                </IconButton>
                <Menu
                  anchorEl={createMenuAnchor}
                  open={Boolean(createMenuAnchor)}
                  onClose={handleCreateMenuClose}
                  transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                  anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                >
                  <MenuItem 
                    onClick={() => { 
                      handleCreateMenuClose(); 
                      navigate('/offers/create'); 
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <AddIcon fontSize="small" color="primary" />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          Create Offer
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Offer a service you can provide
                        </Typography>
                      </Box>
                    </Box>
                  </MenuItem>
                  <MenuItem 
                    onClick={() => { 
                      handleCreateMenuClose(); 
                      navigate('/needs/create'); 
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <AddIcon fontSize="small" color="secondary" />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          Create Need
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Request a service you need
                        </Typography>
                      </Box>
                    </Box>
                  </MenuItem>
                </Menu>

                {/* Active Items Link */}
                <Button
                  component={Link}
                  to="/active-items"
                  startIcon={<InboxIcon />}
                  sx={{
                    color: 'text.primary',
                    textTransform: 'none',
                    fontWeight: 500,
                    display: { xs: 'none', md: 'flex' },
                  }}
                >
                  Active Items
                </Button>

                {/* Notifications Bell */}
                <IconButton
                  color="inherit"
                  onClick={handleNotificationsOpen}
                  sx={{ color: 'text.primary' }}
                >
                  <NotificationsIcon />
                </IconButton>
                <Menu
                  anchorEl={notificationsAnchor}
                  open={Boolean(notificationsAnchor)}
                  onClose={handleNotificationsClose}
                  transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                  anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                  PaperProps={{
                    sx: { width: 320, maxHeight: 400 },
                  }}
                >
                  <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                    <Typography variant="h6" fontWeight={600}>
                      Notifications
                    </Typography>
                  </Box>
                  <MenuItem onClick={handleNotificationsClose}>
                    <Typography variant="body2" color="text.secondary">
                      No new notifications
                    </Typography>
                  </MenuItem>
                </Menu>

                {/* SRS FR-7.2: TimeBank Balance Indicator */}
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.75,
                    px: 2,
                    py: 1,
                    bgcolor: 'primary.50',
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'primary.200',
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'primary.100',
                    },
                  }}
                  onClick={() => navigate('/profile/me')}
                >
                  <AccessTime fontSize="small" sx={{ color: 'primary.main' }} />
                  <Typography 
                    variant="body2" 
                    fontWeight={700}
                    sx={{ color: 'primary.main' }}
                  >
                    {user?.balance?.toFixed(1) || '0.0'}h
                  </Typography>
                </Box>

                {/* User Avatar Dropdown */}
                <IconButton
                  aria-label="account of current user"
                  aria-controls="menu-appbar"
                  aria-haspopup="true"
                  onClick={handleMenu}
                  sx={{ p: 0.5 }}
                >
                  <Avatar 
                    sx={{ 
                      width: 36, 
                      height: 36, 
                      bgcolor: 'secondary.main',
                      fontWeight: 600,
                      fontSize: '1rem',
                    }}
                  >
                    {user?.display_name 
                      ? user.display_name[0].toUpperCase()
                      : user?.username?.[0].toUpperCase() || 'U'}
                  </Avatar>
                </IconButton>
                <Menu
                  id="menu-appbar"
                  anchorEl={anchorEl}
                  anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'right',
                  }}
                  keepMounted
                  transformOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                  }}
                  open={Boolean(anchorEl)}
                  onClose={handleClose}
                  PaperProps={{
                    sx: { mt: 1, minWidth: 200 },
                  }}
                >
                  {/* User Info Header */}
                  <Box sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: 'divider' }}>
                    <Typography variant="body2" fontWeight={600}>
                      {user?.display_name || user?.username}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {user?.email}
                    </Typography>
                  </Box>

                  <MenuItem onClick={() => { handleClose(); navigate('/profile/me'); }}>
                    <AccountCircle fontSize="small" sx={{ mr: 1 }} />
                    My Profile
                  </MenuItem>
                  <MenuItem onClick={() => { handleClose(); navigate('/messages'); }}>
                    <InboxIcon fontSize="small" sx={{ mr: 1 }} />
                    Messages
                  </MenuItem>
                  <MenuItem 
                    onClick={() => { handleClose(); navigate('/active-items'); }}
                    sx={{ display: { xs: 'flex', md: 'none' } }}
                  >
                    <InboxIcon fontSize="small" sx={{ mr: 1 }} />
                    Active Items
                  </MenuItem>
                  
                  {/* Admin/Moderator options */}
                  {user?.role === 'admin' && (
                    <MenuItem onClick={() => { handleClose(); navigate('/admin'); }}>
                      Admin Dashboard
                    </MenuItem>
                  )}
                  {(user?.role === 'moderator' || user?.role === 'admin') && (
                    <MenuItem onClick={() => { handleClose(); navigate('/moderator'); }}>
                      Moderator Dashboard
                    </MenuItem>
                  )}
                  
                  <Box sx={{ borderTop: 1, borderColor: 'divider', mt: 1 }} />
                  <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
                    Logout
                  </MenuItem>
                </Menu>
              </Box>
            ) : (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button 
                  variant="outlined" 
                  component={Link} 
                  to="/login"
                  sx={{ textTransform: 'none', borderRadius: 2 }}
                >
                  Login
                </Button>
                <Button 
                  variant="contained" 
                  component={Link} 
                  to="/register"
                  sx={{ textTransform: 'none', borderRadius: 2 }}
                >
                  Register
                </Button>
              </Box>
            )}
          </Toolbar>
        </AppBar>
      )}

      {/* Main content area */}
      <Container 
        component="main" 
        sx={{ 
          flexGrow: 1, 
          py: hideNavbar ? 0 : 3,
          px: hideNavbar ? 0 : undefined,
        }} 
        maxWidth={hideNavbar ? false : 'lg'}
      >
        <Outlet />
      </Container>

      {/* Footer - hide on auth pages */}
      {!hideNavbar && (
        <Box
          component="footer"
          sx={{
            py: 3,
            px: 2,
            mt: 'auto',
            backgroundColor: (theme) => theme.palette.grey[200],
          }}
        >
          <Container maxWidth="lg">
            <Typography variant="body2" color="text.secondary" align="center">
              © 2024 The Hive - Time Banking Platform
            </Typography>
          </Container>
        </Box>
      )}
    </Box>
  )
}

export default Layout
