import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes with proper precedence
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format date to relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  }
  if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  }
  if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  }
  
  return date.toLocaleDateString();
}

/**
 * Format hours as string with unit
 */
export function formatHours(hours: number): string {
  if (hours === 1) return '1 hour';
  return `${hours} hours`;
}

/**
 * Get status badge color classes
 */
export function getStatusColor(status: string): string {
  const colors = {
    ACTIVE: 'bg-green-100 text-green-800',
    FULL: 'bg-yellow-100 text-yellow-800',
    EXPIRED: 'bg-gray-100 text-gray-800',
    ARCHIVED: 'bg-gray-100 text-gray-800',
    PENDING: 'bg-blue-100 text-blue-800',
    ACCEPTED: 'bg-green-100 text-green-800',
    REJECTED: 'bg-red-100 text-red-800',
    COMPLETED: 'bg-purple-100 text-purple-800',
  };
  return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
}

/**
 * Calculate distance between two coordinates (Haversine formula)
 */
export function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371; // Earth's radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Format distance with unit
 */
export function formatDistance(km: number): string {
  if (km < 1) return `${Math.round(km * 1000)}m`;
  return `${km.toFixed(1)}km`;
}

/**
 * Check if user can accept more participants (capacity check)
 */
export function canAcceptMore(acceptedCount: number = 0, capacity: number): boolean {
  return acceptedCount < capacity;
}

/**
 * Get user initials for avatar
 */
export function getUserInitials(username?: string, fullName?: string): string {
  if (fullName) {
    const parts = fullName.trim().split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return fullName.substring(0, 2).toUpperCase();
  }
  if (username) {
    return username.substring(0, 2).toUpperCase();
  }
  return 'U';
}

/**
 * Format TimeBank balance with color
 */
export function getBalanceColor(balance: number): string {
  if (balance < 0) return 'text-red-600';
  if (balance < 2) return 'text-orange-600';
  if (balance >= 10) return 'text-green-600';
  return 'text-gray-900';
}

/**
 * Check if user is in debt danger zone
 */
export function isInDebtDanger(balance: number): boolean {
  return balance < -8; // Close to -10 reciprocity limit
}

/**
 * Validate time slot format
 */
export function isValidTimeSlot(startTime: string, endTime: string): boolean {
  const start = new Date(`2000-01-01T${startTime}`);
  const end = new Date(`2000-01-01T${endTime}`);
  return start < end;
}

/**
 * Convert day of week number to name
 */
export function getDayName(dayOfWeek: number): string {
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  return days[dayOfWeek] || 'Unknown';
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}
