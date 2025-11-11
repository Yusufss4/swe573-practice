// Redirect component for My Profile route
// Redirects to /profile/:id using current user's ID

import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Box, CircularProgress } from '@mui/material'
import { useAuth } from '@/contexts/AuthContext'

export default function MyProfile() {
  const { user, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading) {
      if (user) {
        navigate(`/profile/${user.id}`, { replace: true })
      } else {
        navigate('/login', { replace: true })
      }
    }
  }, [user, isLoading, navigate])

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    </Container>
  )
}
