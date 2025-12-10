// The Hive - Landing Page / Home Screen
// A welcoming introduction to the community time-banking platform

import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  Avatar,
  Chip,
  Paper,
  Stack,
} from '@mui/material'
import {
  Handshake as HandshakeIcon,
  LocalOffer as OfferIcon,
  EventNote as NeedIcon,
  AccessTime as TimeIcon,
  Security as SecurityIcon,
  Favorite as HeartIcon,
  Groups as CommunityIcon,
  Verified as VerifiedIcon,
  EmojiEvents as BadgeIcon,
  Tag as TagIcon,
  ArrowForward as ArrowForwardIcon,
  AccountCircle as AccountIcon,
} from '@mui/icons-material'
import { useAuth } from '@/contexts/AuthContext'

// How It Works Steps
const howItWorksSteps = [
  {
    step: 1,
    title: 'Create Your Profile',
    description: 'Join The Hive with your profile. Start with 5 hours credit.',
    icon: <AccountIcon fontSize="large" />,
    color: '#FFA726',
  },
  {
    step: 2,
    title: 'Post Offers or Needs',
    description: 'Share what you can offer or what help you need from the community.',
    icon: <OfferIcon fontSize="large" />,
    color: '#66BB6A',
  },
  {
    step: 3,
    title: 'Find Matches',
    description: 'Browse the map, search by tags, and discover opportunities near you.',
    icon: <TagIcon fontSize="large" />,
    color: '#42A5F5',
  },
  {
    step: 4,
    title: 'Handshake & Exchange',
    description: 'Send proposals, agree on details, and complete the exchange.',
    icon: <HandshakeIcon fontSize="large" />,
    color: '#AB47BC',
  },
  {
    step: 5,
    title: 'Earn Time Credits',
    description: 'Gain hours when you help, spend hours when you receive help.',
    icon: <TimeIcon fontSize="large" />,
    color: '#FF7043',
  },
]

// Core Concepts
const coreConcepts = [
  {
    title: 'Offers',
    description: 'Skills, services, or items you can provide to help others in your community.',
    icon: <OfferIcon sx={{ fontSize: 40, color: 'success.main' }} />,
    example: 'Gardening, tutoring, carpentry',
  },
  {
    title: 'Needs',
    description: 'Things you\'re looking for - help, services, or skills from community members.',
    icon: <NeedIcon sx={{ fontSize: 40, color: 'info.main' }} />,
    example: 'Moving help, language practice',
  },
  {
    title: 'Handshakes',
    description: 'The agreement process where both parties confirm exchange details and timing.',
    icon: <HandshakeIcon sx={{ fontSize: 40, color: 'secondary.main' }} />,
    example: 'Propose, accept, complete',
  },
  {
    title: 'TimeBank',
    description: 'Your hour balance. Everyone\'s time is valued equally - one hour equals one hour.',
    icon: <TimeIcon sx={{ fontSize: 40, color: 'warning.main' }} />,
    example: 'Start with 5h, earn or spend',
  },
]

// Community Values
const communityValues = [
  {
    title: 'Everyone\'s Time is Equal',
    description: 'Whether you\'re teaching physics or mowing lawns, one hour equals one hour.',
    icon: '⚖️',
  },
  {
    title: 'Give & Receive',
    description: 'Start with 5 hours credit. Give to earn more, receive when you need help.',
    icon: '🔄',
  },
  {
    title: 'Trust & Safety',
    description: 'Verified profiles, mutual ratings, and community moderation keep everyone safe.',
    icon: '🛡️',
  },
  {
    title: 'Local & Remote',
    description: 'Connect with neighbors nearby or help someone across the world remotely.',
    icon: '🌍',
  },
]

// Example Categories
const exampleCategories = [
  { name: 'Gardening', emoji: '🌱', count: 24, tag: 'gardening' },
  { name: 'Tech Support', emoji: '💻', count: 18, tag: 'tech support' },
  { name: 'Tutoring', emoji: '📚', count: 31, tag: 'tutoring' },
  { name: 'Pet Care', emoji: '🐕', count: 14, tag: 'pet' },
  { name: 'Home Repair', emoji: '🔧', count: 27, tag: 'home repair' },
  { name: 'Transportation', emoji: '🚗', count: 19, tag: 'transportation' },
  { name: 'Arts & Crafts', emoji: '🎨', count: 17, tag: 'art' },
  { name: 'Health & Wellness', emoji: '🧘', count: 15, tag: 'health' },
  { name: 'Food & Cooking', emoji: '🍳', count: 22, tag: 'food' },
]

const HomePage = () => {
  const navigate = useNavigate()
  const { user } = useAuth()

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 4, md: 6 } }}>
        <Card
          elevation={3}
          sx={{
            background: 'linear-gradient(135deg, #FFF8E1 0%, #FFECB3 50%, #FFE0B2 100%)',
            p: { xs: 4, md: 6 },
            borderRadius: 3,
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Decorative elements */}
          <Box
            sx={{
              position: 'absolute',
              top: -50,
              right: -50,
              width: 200,
              height: 200,
              borderRadius: '50%',
              bgcolor: 'rgba(255, 167, 38, 0.1)',
              filter: 'blur(40px)',
            }}
          />
          <Box
            sx={{
              position: 'absolute',
              bottom: -30,
              left: -30,
              width: 150,
              height: 150,
              borderRadius: '50%',
              bgcolor: 'rgba(66, 165, 245, 0.1)',
              filter: 'blur(40px)',
            }}
          />

          <Box sx={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
            <Typography
              variant="h2"
              component="h1"
              sx={{
                fontWeight: 700,
                mb: 2,
                fontSize: { xs: '2.5rem', md: '3.5rem' },
              }}
            >
              Welcome to{' '}
              <Box component="span" sx={{ color: 'primary.main' }}>
                The Hive
              </Box>
              {' '}🐝
            </Typography>
            <Typography
              variant="h5"
              sx={{
                color: 'text.secondary',
                mb: 4,
                fontWeight: 400,
                lineHeight: 1.6,
                maxWidth: 800,
                mx: 'auto',
              }}
            >
              A community where your time is valued. Exchange skills, help neighbors, 
              and build meaningful connections – one hour at a time.
            </Typography>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
              {!user ? (
                <>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => navigate('/register')}
                    startIcon={<CommunityIcon />}
                    sx={{
                      px: 4,
                      py: 1.5,
                      borderRadius: 3,
                      textTransform: 'none',
                      fontSize: '1.1rem',
                    }}
                  >
                    Join The Hive
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={() => navigate('/login')}
                    sx={{
                      px: 4,
                      py: 1.5,
                      borderRadius: 3,
                      textTransform: 'none',
                      fontSize: '1.1rem',
                    }}
                  >
                    Sign In
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => navigate('/offers/create')}
                    startIcon={<OfferIcon />}
                    sx={{
                      px: 4,
                      py: 1.5,
                      borderRadius: 3,
                      textTransform: 'none',
                      fontSize: '1.1rem',
                    }}
                  >
                    Create Offer
                  </Button>
                  <Button
                    variant="contained"
                    color="secondary"
                    size="large"
                    onClick={() => navigate('/needs/create')}
                    startIcon={<NeedIcon />}
                    sx={{
                      px: 4,
                      py: 1.5,
                      borderRadius: 3,
                      textTransform: 'none',
                      fontSize: '1.1rem',
                    }}
                  >
                    Create Need
                  </Button>
                </>
              )}
            </Stack>
          </Box>
        </Card>
      </Container>

      {/* How It Works Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
        <Typography
          variant="h3"
          align="center"
          sx={{ mb: 2, fontWeight: 600 }}
        >
          How It Works
        </Typography>
        <Typography
          variant="h6"
          align="center"
          color="text.secondary"
          sx={{ mb: 6, maxWidth: 700, mx: 'auto' }}
        >
          Getting started is simple. Join our community and start exchanging in minutes.
        </Typography>

        <Grid container spacing={3}>
          {howItWorksSteps.map((step) => (
            <Grid item xs={12} sm={6} md={2.4} key={step.step}>
              <Card
                sx={{
                  height: '100%',
                  textAlign: 'center',
                  p: 2,
                  border: '2px solid transparent',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: 'primary.main',
                    transform: 'translateY(-4px)',
                    boxShadow: 3,
                  },
                }}
              >
                <Avatar
                  sx={{
                    width: 70,
                    height: 70,
                    bgcolor: step.color,
                    mx: 'auto',
                    mb: 2,
                  }}
                >
                  {step.icon}
                </Avatar>
                <Chip
                  label={`Step ${step.step}`}
                  size="small"
                  sx={{ mb: 1, fontWeight: 600 }}
                />
                <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                  {step.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {step.description}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Core Concepts Section */}
      <Box sx={{ bgcolor: '#F5F5F5', py: { xs: 6, md: 10 } }}>
        <Container maxWidth="lg">
          <Typography
            variant="h3"
            align="center"
            sx={{ mb: 2, fontWeight: 600 }}
          >
            Core Concepts
          </Typography>
          <Typography
            variant="h6"
            align="center"
            color="text.secondary"
            sx={{ mb: 6, maxWidth: 700, mx: 'auto' }}
          >
            Understanding the building blocks of our time-banking community.
          </Typography>

          <Grid container spacing={3}>
            {coreConcepts.map((concept) => (
              <Grid item xs={12} sm={6} md={3} key={concept.title}>
                <Card
                  sx={{
                    height: '100%',
                    p: 3,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4,
                    },
                  }}
                >
                  <Box sx={{ mb: 2 }}>{concept.icon}</Box>
                  <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                    {concept.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {concept.description}
                  </Typography>
                  <Chip
                    label={concept.example}
                    size="small"
                    variant="outlined"
                    sx={{ fontSize: '0.75rem' }}
                  />
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Community Values Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
        <Typography
          variant="h3"
          align="center"
          sx={{ mb: 2, fontWeight: 600 }}
        >
          Our Values
        </Typography>
        <Typography
          variant="h6"
          align="center"
          color="text.secondary"
          sx={{ mb: 6, maxWidth: 700, mx: 'auto' }}
        >
          The principles that make The Hive a thriving, cooperative community.
        </Typography>

        <Grid container spacing={4}>
          {communityValues.map((value) => (
            <Grid item xs={12} sm={6} md={3} key={value.title}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h2" sx={{ mb: 2 }}>
                  {value.icon}
                </Typography>
                <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                  {value.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {value.description}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Categories Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
        <Typography
          variant="h3"
          align="center"
          sx={{ mb: 2, fontWeight: 600 }}
        >
          Popular Categories
        </Typography>
        <Typography
          variant="h6"
          align="center"
          color="text.secondary"
          sx={{ mb: 6, maxWidth: 600, mx: 'auto' }}
        >
          Explore what our community is sharing and requesting.
        </Typography>

        <Grid container spacing={2}>
          {exampleCategories.map((category) => (
            <Grid item xs={6} sm={4} md={3} key={category.name}>
              <Card
                sx={{
                  p: 2,
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    bgcolor: 'primary.light',
                    transform: 'scale(1.05)',
                    boxShadow: 3,
                  },
                }}
                onClick={() => navigate(`/map?tag=${encodeURIComponent(category.tag)}`)}
              >
                <Typography variant="h3" sx={{ mb: 1 }}>
                  {category.emoji}
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>
                  {category.name}
                </Typography>
                <Chip
                  label={`${category.count} active`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Trust & Safety Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 8 } }}>
        <Card
          elevation={3}
          sx={{
            p: { xs: 4, md: 6 },
            textAlign: 'center',
            borderRadius: 3,
          }}
        >
          <SecurityIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
          <Typography variant="h3" sx={{ mb: 2, fontWeight: 600 }}>
            Your Safety Matters
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, lineHeight: 1.8 }}>
            We take community safety seriously. All members are verified, exchanges are rated, 
            and our moderation team ensures a respectful environment for everyone. 
            Meet in public places for in-person exchanges and always communicate through the platform.
          </Typography>
          <Stack direction="row" spacing={2} justifyContent="center" flexWrap="wrap">
            <Chip icon={<VerifiedIcon />} label="Verified Profiles" variant="outlined" />
            <Chip icon={<BadgeIcon />} label="Trust Ratings" variant="outlined" />
            <Chip icon={<SecurityIcon />} label="Active Moderation" variant="outlined" />
          </Stack>
        </Card>
      </Container>

      {/* Final CTA Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 8 } }}>
        <Card
          elevation={3}
          sx={{
            background: 'linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%)',
            p: { xs: 4, md: 6 },
            textAlign: 'center',
            borderRadius: 3,
          }}
        >
          <Typography variant="h2" sx={{ mb: 2, fontWeight: 600 }}>
            Ready to Join?
          </Typography>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ mb: 4, lineHeight: 1.7 }}
          >
            Become part of a community where every skill matters and every hour counts. 
            Start giving, receiving, and building connections today.
          </Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
            {!user ? (
              <>
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/register')}
                  startIcon={<HeartIcon />}
                  sx={{
                    px: 5,
                    py: 2,
                    borderRadius: 3,
                    textTransform: 'none',
                    fontSize: '1.1rem',
                  }}
                >
                  Get Started Free
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/map')}
                  endIcon={<ArrowForwardIcon />}
                  sx={{
                    px: 5,
                    py: 2,
                    borderRadius: 3,
                    textTransform: 'none',
                    fontSize: '1.1rem',
                  }}
                >
                  Explore First
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/map')}
                  startIcon={<OfferIcon />}
                  sx={{
                    px: 5,
                    py: 2,
                    borderRadius: 3,
                    textTransform: 'none',
                    fontSize: '1.1rem',
                  }}
                >
                  Browse Map
                </Button>
                <Button
                  variant="contained"
                  color="secondary"
                  size="large"
                  onClick={() => navigate('/active-items')}
                  startIcon={<TimeIcon />}
                  sx={{
                    px: 5,
                    py: 2,
                    borderRadius: 3,
                    textTransform: 'none',
                    fontSize: '1.1rem',
                  }}
                >
                  My Active Items
                </Button>
              </>
            )}
          </Stack>
        </Card>
      </Container>
    </Box>
  )
}

export default HomePage
