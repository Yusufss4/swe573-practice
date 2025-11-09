// SRS FR-1.3: User Login Page
// Provides secure login functionality with JWT token management

import { useState } from 'react'
import { useNavigate, Link as RouterLink, useLocation } from 'react-router-dom'
import {
  Box,
  Container,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Link,
  InputAdornment,
  IconButton,
  Divider,
} from '@mui/material'
import { Visibility, VisibilityOff, Hive as HiveIcon } from '@mui/icons-material'
import { useAuth } from '@/contexts/AuthContext'

/**
 * SRS FR-1.3: User login functionality
 * SRS FR-1.5: Session-based authentication with JWT
 */
const Login = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  // Get the redirect path from location state, or default to home
  const from = (location.state as any)?.from?.pathname || '/'

  const handleChange = (field: string) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData({ ...formData, [field]: event.target.value })
    setError('')
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    
    // Basic validation
    if (!formData.username || !formData.password) {
      setError('Please enter both username and password')
      return
    }

    setIsSubmitting(true)
    setError('')

    try {
      // SRS FR-1.3: Login with username and password
      await login(formData.username, formData.password)

      // Redirect to the page they tried to visit or home
      navigate(from, { replace: true })
    } catch (error: any) {
      // Handle different error formats
      let errorMessage = 'Invalid username or password'
      
      if (error.response?.data) {
        // FastAPI validation error format
        if (error.response.data.detail) {
          if (typeof error.response.data.detail === 'string') {
            errorMessage = error.response.data.detail
          } else if (Array.isArray(error.response.data.detail)) {
            // Validation errors array
            errorMessage = error.response.data.detail
              .map((err: any) => err.msg || JSON.stringify(err))
              .join(', ')
          }
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      setError(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '80vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4,
        }}
      >
        <Card sx={{ width: '100%', boxShadow: 3 }}>
          <CardContent sx={{ p: 4 }}>
            {/* Header with Logo */}
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <HiveIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" component="h1" gutterBottom fontWeight={600}>
                Welcome Back
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Sign in to continue to The Hive
              </Typography>
            </Box>

            {/* Error Alert */}
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {/* Login Form */}
            <Box component="form" onSubmit={handleSubmit} noValidate>
              <TextField
                fullWidth
                label="Username or Email"
                name="username"
                value={formData.username}
                onChange={handleChange('username')}
                margin="normal"
                required
                autoComplete="username"
                autoFocus
              />

              <TextField
                fullWidth
                label="Password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange('password')}
                margin="normal"
                required
                autoComplete="current-password"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={isSubmitting}
                sx={{ mt: 3, mb: 2, py: 1.5 }}
              >
                {isSubmitting ? 'Signing In...' : 'Sign In'}
              </Button>

              <Divider sx={{ my: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  OR
                </Typography>
              </Divider>

              <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Don't have an account?{' '}
                  <Link
                    component={RouterLink}
                    to="/register"
                    sx={{ fontWeight: 600, textDecoration: 'none' }}
                  >
                    Create Account
                  </Link>
                </Typography>
              </Box>
            </Box>

            {/* Info Box */}
            <Box
              sx={{
                mt: 3,
                p: 2,
                bgcolor: 'primary.50',
                borderRadius: 1,
                border: '1px solid',
                borderColor: 'primary.200',
              }}
            >
              <Typography variant="body2" color="text.secondary">
                💡 <strong>New to The Hive?</strong> Start with 5 hours in your TimeBank.
                Exchange services based on time, not money!
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

export default Login
