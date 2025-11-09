// Base API types matching backend schemas

export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  balance: number;
  timezone: string;
  role: 'USER' | 'MODERATOR' | 'ADMIN';
  location_lat?: number;
  location_lon?: number;
  location_name?: string;
  bio?: string;
  avatar_url?: string;
  created_at: string;
}

export interface Tag {
  id: string;
  name: string;
}

export interface TimeSlot {
  day_of_week: number; // 0-6 (Monday-Sunday)
  start_time: string;   // HH:MM format
  end_time: string;     // HH:MM format
}

export interface Offer {
  id: string;
  title: string;
  description: string;
  hours_estimated: number;
  capacity: number;
  status: 'ACTIVE' | 'FULL' | 'EXPIRED' | 'ARCHIVED';
  is_remote: boolean;
  location_lat?: number;
  location_lon?: number;
  location_name?: string;
  time_slots?: TimeSlot[];
  expires_at: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  user?: User;
  tags?: Tag[];
  accepted_count?: number;
}

export interface Need {
  id: string;
  title: string;
  description: string;
  hours_estimated: number;
  capacity: number;
  status: 'ACTIVE' | 'FULL' | 'EXPIRED' | 'ARCHIVED';
  is_remote: boolean;
  location_lat?: number;
  location_lon?: number;
  location_name?: string;
  time_slots?: TimeSlot[];
  expires_at: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  user?: User;
  tags?: Tag[];
  accepted_count?: number;
}

export interface Participant {
  id: string;
  user_id: string;
  offer_id?: string;
  need_id?: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'COMPLETED';
  hours_contributed?: number;
  created_at: string;
  updated_at: string;
  user?: User;
  offer?: Offer;
  need?: Need;
}

export interface Comment {
  id: string;
  content: string;
  rating?: number;
  author_id: string;
  recipient_id: string;
  participant_id: string;
  created_at: string;
  author?: User;
  recipient?: User;
}

export interface LedgerEntry {
  id: string;
  user_id: string;
  debit: number;
  credit: number;
  balance: number;
  description?: string;
  created_at: string;
}

export interface ForumPost {
  id: string;
  title: string;
  content: string;
  author_id: string;
  created_at: string;
  updated_at: string;
  author?: User;
  reply_count?: number;
}

export interface ForumReply {
  id: string;
  content: string;
  post_id: string;
  author_id: string;
  created_at: string;
  author?: User;
}

export interface MapItem {
  id: string;
  type: 'offer' | 'need';
  title: string;
  description: string;
  location_lat: number;
  location_lon: number;
  location_name: string;
  user_id: string;
  username: string;
  created_at: string;
}

// Request/Response types

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  timezone: string;
  location_lat?: number;
  location_lon?: number;
  location_name?: string;
}

export interface CreateOfferRequest {
  title: string;
  description: string;
  hours_estimated: number;
  capacity: number;
  is_remote: boolean;
  location_lat?: number;
  location_lon?: number;
  location_name?: string;
  time_slots?: TimeSlot[];
  tags: string[];
}

export interface CreateNeedRequest {
  title: string;
  description: string;
  hours_estimated: number;
  capacity: number;
  is_remote: boolean;
  location_lat?: number;
  location_lon?: number;
  location_name?: string;
  time_slots?: TimeSlot[];
  tags: string[];
}

export interface CreateCommentRequest {
  content: string;
  rating?: number;
  recipient_id: string;
  participant_id: string;
}

export interface AcceptParticipantRequest {
  hours: number;
}

export interface SearchParams {
  query?: string;
  type?: 'offer' | 'need';
  tags?: string;
  is_remote?: boolean;
  location_lat?: number;
  location_lon?: number;
  radius_km?: number;
}

export interface DashboardStats {
  active_offers_count: number;
  active_needs_count: number;
  pending_requests_count: number;
  completed_exchanges_count: number;
}
