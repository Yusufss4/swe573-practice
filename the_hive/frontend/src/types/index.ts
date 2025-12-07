// SRS: Base types matching backend API models
// These types align with the FastAPI backend schemas

// SRS FR-1: User types
export interface User {
  id: number
  username: string
  email: string
  display_name?: string
  description?: string
  profile_image?: string
  profile_image_type?: 'preset' | 'custom'
  balance: number // SRS FR-7: TimeBank balance
  location_lat?: number
  location_lon?: number
  location_name?: string
  role: 'user' | 'moderator' | 'admin'
  is_active: boolean
  created_at: string
  badges?: Badge[] // SRS FR-13: Badges
  tags?: string[] // Profile tags
}

// User profile with stats
export interface UserProfile {
  id: number
  username: string
  display_name?: string
  description?: string
  profile_image?: string
  profile_image_type: string
  location_name?: string
  balance: number
  stats: UserStats
  tags: string[]
  created_at: string
}

export interface UserStats {
  balance: number
  hours_given: number
  hours_received: number
  completed_exchanges: number
  ratings_received: number
}

// Profile update request
export interface UserProfileUpdate {
  full_name?: string
  description?: string
  profile_image?: string
  profile_image_type?: 'preset' | 'custom'
  location_lat?: number
  location_lon?: number
  location_name?: string
  tags?: string[]
}

// SRS FR-13: Badge types
export interface Badge {
  code: string
  name: string
  description: string
  earned_at?: string
}

// SRS FR-3: Offer types
export interface Offer {
  id: number
  title: string
  description: string
  duration_hours: number
  is_remote: boolean
  location_lat?: number
  location_lon?: number
  location_name?: string
  capacity: number // SRS FR-3.6: Maximum participants
  accepted_count: number
  hours: number // SRS FR-7: TimeBank hours for this offer
  status: 'ACTIVE' | 'FULL' | 'EXPIRED' | 'ARCHIVED'
  expires_at: string
  created_at: string
  owner_id: number
  owner?: User
  tags?: Tag[]
  time_slots?: TimeSlot[] // SRS FR-4: Calendar availability
}

// SRS FR-3: Need types
export interface Need {
  id: number
  title: string
  description: string
  duration_hours: number
  is_remote: boolean
  location_lat?: number
  location_lon?: number
  location_name?: string
  capacity: number
  accepted_count: number
  hours: number // SRS FR-7: TimeBank hours for this need
  status: 'ACTIVE' | 'FULL' | 'EXPIRED' | 'ARCHIVED'
  expires_at: string
  created_at: string
  owner_id: number
  owner?: User
  tags?: Tag[]
}

// SRS FR-8: Tag types
export interface Tag {
  id: number
  name: string
  description?: string
  parent_id?: number
  usage_count: number
}

// SRS FR-4: TimeSlot for calendar availability
export interface TimeSlot {
  id: number
  start_time: string // ISO datetime
  end_time: string
  is_booked: boolean
}

// SRS FR-5: Participant/Handshake types
export interface Participant {
  id: number
  user_id: number
  user?: User
  offer_id?: number
  need_id?: number
  status: 'PENDING' | 'ACCEPTED' | 'COMPLETED'
  message?: string
  created_at: string
  accepted_at?: string
  completed_at?: string
}

// SRS FR-6: Message types
export interface Message {
  id: number
  sender_id: number
  sender?: User
  recipient_id: number
  recipient?: User
  content: string
  is_read: boolean
  created_at: string
}

// SRS FR-10: Comment types
export interface Comment {
  id: number
  author_id: number
  author?: User
  target_user_id: number
  content: string
  exchange_id?: number
  is_moderated: boolean
  created_at: string
}

// SRS FR-7: Ledger entry types
export interface LedgerEntry {
  id: number
  user_id: number
  user?: User
  debit: number
  credit: number
  balance_after: number
  description?: string
  created_at: string
}

// SRS FR-15: Forum types
export interface ForumTopic {
  id: number
  topic_type: 'discussion' | 'event'
  creator_id: number
  creator_username?: string
  creator_profile_image?: string
  creator_profile_image_type?: string
  title: string
  content: string
  tags: string[]
  
  // Event-specific fields
  event_start_time?: string
  event_end_time?: string
  event_location?: string
  
  // Linked items
  linked_offer_id?: number
  linked_need_id?: number
  linked_item?: {
    id: number
    type: 'offer' | 'need'
    title: string
    creator_id: number
    creator_username?: string
  }
  
  // Moderation
  is_approved: boolean
  is_visible: boolean
  is_pinned: boolean
  
  // Engagement
  view_count: number
  comment_count: number
  
  // Timestamps
  created_at: string
  updated_at: string
}

// Legacy alias for backward compatibility
export interface ForumPost extends ForumTopic {}

export interface ForumComment {
  id: number
  topic_id: number
  author_id: number
  author_username?: string
  author_profile_image?: string
  author_profile_image_type?: string
  content: string
  is_approved: boolean
  is_visible: boolean
  created_at: string
  updated_at: string
}

export interface ForumTopicCreate {
  topic_type: 'discussion' | 'event'
  title: string
  content: string
  tags?: string[]
  event_start_time?: string
  event_end_time?: string
  event_location?: string
  linked_offer_id?: number
  linked_need_id?: number
}

// SRS FR-11: Report types
export interface Report {
  id: number
  reporter_id: number
  reporter?: User
  content_type: 'offer' | 'need' | 'comment' | 'user' | 'forum_post'
  content_id: number
  reason: string
  status: 'PENDING' | 'REVIEWED' | 'RESOLVED' | 'DISMISSED'
  moderator_id?: number
  moderator?: User
  resolution_note?: string
  created_at: string
  resolved_at?: string
}

// SRS FR-N: Notification types
export interface Notification {
  id: number
  user_id: number
  type: NotificationType
  title: string
  message: string
  related_offer_id?: number
  related_need_id?: number
  related_user_id?: number
  related_participant_id?: number
  related_rating_id?: number
  is_read: boolean
  created_at: string
  read_at?: string
}

export type NotificationType =
  | 'application_received'
  | 'application_accepted'
  | 'application_declined'
  | 'participant_cancelled'
  | 'exchange_awaiting_confirmation'
  | 'exchange_completed'
  | 'rating_received'

export interface NotificationListResponse {
  notifications: Notification[]
  total: number
  unread_count: number
}

// API Response wrappers
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ApiError {
  detail: string
  status?: number
}
