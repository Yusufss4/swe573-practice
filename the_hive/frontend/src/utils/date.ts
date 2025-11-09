// SRS: Date and time utilities
// Handles timezone-aware date formatting per SRS requirements

import { format, formatDistanceToNow, parseISO } from 'date-fns'

/**
 * Format ISO datetime string to readable format
 * SRS: Users have timezone field (IANA format)
 */
export const formatDateTime = (isoString: string): string => {
  try {
    return format(parseISO(isoString), 'MMM d, yyyy HH:mm')
  } catch {
    return isoString
  }
}

/**
 * Format date only
 */
export const formatDate = (isoString: string): string => {
  try {
    return format(parseISO(isoString), 'MMM d, yyyy')
  } catch {
    return isoString
  }
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (isoString: string): string => {
  try {
    return formatDistanceToNow(parseISO(isoString), { addSuffix: true })
  } catch {
    return isoString
  }
}

/**
 * Check if date is expired
 */
export const isExpired = (isoString: string): boolean => {
  try {
    return parseISO(isoString) < new Date()
  } catch {
    return false
  }
}

/**
 * Format duration in hours
 * SRS FR-7: TimeBank uses hours as unit
 */
export const formatDuration = (hours: number): string => {
  if (hours === 1) return '1 hour'
  return `${hours} hours`
}
