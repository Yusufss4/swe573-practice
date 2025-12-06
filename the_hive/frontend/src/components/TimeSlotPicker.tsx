// SRS FR-3: Time Slot Management for Offers/Needs
// Allows users to specify available time slots when creating offers or needs

import { useState } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  IconButton,
  Typography,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  AccessTime as TimeIcon,
  CalendarMonth as CalendarIcon,
} from '@mui/icons-material'

interface TimeRange {
  start_time: string // HH:MM format
  end_time: string // HH:MM format
}

interface TimeSlot {
  date: string // YYYY-MM-DD format
  time_ranges: TimeRange[]
}

interface TimeSlotPickerProps {
  value: TimeSlot[]
  onChange: (slots: TimeSlot[]) => void
  disabled?: boolean
}

/**
 * TimeSlotPicker Component
 * 
 * Allows users to add multiple time slots with date and time ranges.
 * Supports:
 * - Adding multiple dates
 * - Multiple time ranges per date
 * - Validation for time format and logical ordering
 * - Edit and delete functionality
 */

// Generate time options in 30-minute increments (24-hour format)
const generateTimeOptions = (): string[] => {
  const options: string[] = []
  for (let hour = 0; hour < 24; hour++) {
    for (let minute = 0; minute < 60; minute += 30) {
      const h = hour.toString().padStart(2, '0')
      const m = minute.toString().padStart(2, '0')
      options.push(`${h}:${m}`)
    }
  }
  return options
}

export default function TimeSlotPicker({ value, onChange, disabled }: TimeSlotPickerProps) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  
  // Form state for dialog
  const [selectedDate, setSelectedDate] = useState('')
  const [timeRanges, setTimeRanges] = useState<TimeRange[]>([
    { start_time: '09:00', end_time: '10:00' }
  ])
  const [error, setError] = useState<string | null>(null)

  const handleOpenDialog = (index: number | null = null) => {
    if (index !== null) {
      // Edit existing slot
      const slot = value[index]
      setSelectedDate(slot.date)
      setTimeRanges(slot.time_ranges)
      setEditingIndex(index)
    } else {
      // Add new slot
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      setSelectedDate(tomorrow.toISOString().split('T')[0])
      setTimeRanges([{ start_time: '09:00', end_time: '10:00' }])
      setEditingIndex(null)
    }
    setError(null)
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setError(null)
  }

  const handleAddTimeRange = () => {
    setTimeRanges([...timeRanges, { start_time: '09:00', end_time: '10:00' }])
  }

  const handleRemoveTimeRange = (index: number) => {
    if (timeRanges.length > 1) {
      setTimeRanges(timeRanges.filter((_, i) => i !== index))
    }
  }

  const handleTimeRangeChange = (
    index: number,
    field: 'start_time' | 'end_time',
    value: string
  ) => {
    const newRanges = [...timeRanges]
    newRanges[index][field] = value
    setTimeRanges(newRanges)
  }

  const validateTimeSlot = (): boolean => {
    setError(null)

    // Validate date
    if (!selectedDate) {
      setError('Please select a date')
      return false
    }

    const slotDate = new Date(selectedDate)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    if (slotDate < today) {
      setError('Date cannot be in the past')
      return false
    }

    // Validate time ranges
    for (let i = 0; i < timeRanges.length; i++) {
      const range = timeRanges[i]
      
      if (!range.start_time || !range.end_time) {
        setError(`Time range ${i + 1} is incomplete`)
        return false
      }

      if (range.end_time <= range.start_time) {
        setError(`Time range ${i + 1}: End time must be after start time`)
        return false
      }

      // Check for overlaps with other ranges
      for (let j = i + 1; j < timeRanges.length; j++) {
        const other = timeRanges[j]
        if (
          (range.start_time < other.end_time && other.start_time < range.end_time)
        ) {
          setError(`Time range ${i + 1} overlaps with range ${j + 1}`)
          return false
        }
      }
    }

    return true
  }

  const handleSaveSlot = () => {
    if (!validateTimeSlot()) {
      return
    }

    const newSlot: TimeSlot = {
      date: selectedDate,
      time_ranges: timeRanges,
    }

    let newSlots = [...value]
    if (editingIndex !== null) {
      // Update existing slot
      newSlots[editingIndex] = newSlot
    } else {
      // Add new slot
      newSlots.push(newSlot)
    }

    // Sort by date
    newSlots.sort((a, b) => a.date.localeCompare(b.date))

    onChange(newSlots)
    handleCloseDialog()
  }

  const handleDeleteSlot = (index: number) => {
    onChange(value.filter((_, i) => i !== index))
  }

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr + 'T00:00:00')
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    })
  }

  const formatTimeRange = (range: TimeRange): string => {
    return `${range.start_time} - ${range.end_time}`
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle2" fontWeight={600}>
          Available Time Slots (Optional)
        </Typography>
        <Button
          size="small"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          disabled={disabled}
        >
          Add Time Slot
        </Button>
      </Box>

      {value.length === 0 ? (
        <Alert severity="info">
          No time slots specified. Add specific dates and times when you're available, 
          or leave empty if you're flexible with scheduling.
        </Alert>
      ) : (
        <Stack spacing={1}>
          {value.map((slot, index) => (
            <Card key={index} variant="outlined">
              <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <CalendarIcon fontSize="small" color="primary" />
                      <Typography variant="body2" fontWeight={600}>
                        {formatDate(slot.date)}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, ml: 3 }}>
                      {slot.time_ranges.map((range, rangeIndex) => (
                        <Chip
                          key={rangeIndex}
                          icon={<TimeIcon />}
                          label={formatTimeRange(range)}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(index)}
                      disabled={disabled}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteSlot(index)}
                      disabled={disabled}
                      color="error"
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Stack>
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingIndex !== null ? 'Edit Time Slot' : 'Add Time Slot'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <TextField
            fullWidth
            type="date"
            label="Date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ mb: 3 }}
          />

          <Typography variant="subtitle2" gutterBottom fontWeight={600}>
            Time Ranges
          </Typography>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block" sx={{ mb: 2 }}>
            Add one or more time ranges for this date
          </Typography>

          <Stack spacing={2}>
            {timeRanges.map((range, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <TextField
                  select
                  label="Start Time"
                  value={range.start_time}
                  onChange={(e) => handleTimeRangeChange(index, 'start_time', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  size="small"
                  sx={{ flex: 1, minWidth: 120 }}
                  SelectProps={{ native: true }}
                >
                  {generateTimeOptions().map((time) => (
                    <option key={time} value={time}>{time}</option>
                  ))}
                </TextField>
                <Typography variant="body2" color="text.secondary">
                  to
                </Typography>
                <TextField
                  select
                  label="End Time"
                  value={range.end_time}
                  onChange={(e) => handleTimeRangeChange(index, 'end_time', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  size="small"
                  sx={{ flex: 1, minWidth: 120 }}
                  SelectProps={{ native: true }}
                >
                  {generateTimeOptions().map((time) => (
                    <option key={time} value={time}>{time}</option>
                  ))}
                </TextField>
                {timeRanges.length > 1 && (
                  <IconButton
                    size="small"
                    onClick={() => handleRemoveTimeRange(index)}
                    color="error"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                )}
              </Box>
            ))}
          </Stack>

          <Button
            startIcon={<AddIcon />}
            onClick={handleAddTimeRange}
            sx={{ mt: 2 }}
            size="small"
          >
            Add Another Time Range
          </Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveSlot} variant="contained">
            {editingIndex !== null ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
