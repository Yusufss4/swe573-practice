import { createTheme } from '@mui/material/styles'

// SRS: Theme configuration for The Hive platform
// Follows clean, accessible layout principles per SRS Section 3.3.1
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#FFA726', // Warm orange/amber - represents community warmth
      light: '#FFB74D',
      dark: '#F57C00',
      contrastText: '#000',
    },
    secondary: {
      main: '#42A5F5', // Blue - trust and reliability
      light: '#64B5F6',
      dark: '#1E88E5',
      contrastText: '#fff',
    },
    success: {
      main: '#66BB6A', // Green for positive actions
    },
    warning: {
      main: '#FFA726',
    },
    error: {
      main: '#EF5350',
    },
    background: {
      default: '#FAFAFA',
      paper: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
})

export default theme
