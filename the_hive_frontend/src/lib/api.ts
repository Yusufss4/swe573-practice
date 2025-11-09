import apiClient from './api-client';
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  User,
  Offer,
  Need,
  CreateOfferRequest,
  CreateNeedRequest,
  Tag,
  Participant,
  AcceptParticipantRequest,
  Comment,
  CreateCommentRequest,
  LedgerEntry,
  ForumPost,
  ForumReply,
  MapItem,
  SearchParams,
  DashboardStats,
} from './types';

// Authentication API
export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post('/api/v1/auth/login', data);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await apiClient.post('/api/v1/auth/register', data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get('/api/v1/auth/me');
    return response.data;
  },

  getLedger: async (): Promise<LedgerEntry[]> => {
    const response = await apiClient.get('/api/v1/auth/me/ledger');
    return response.data;
  },
};

// Users API
export const usersApi = {
  getUser: async (userId: string): Promise<User> => {
    const response = await apiClient.get(`/api/v1/users/${userId}`);
    return response.data;
  },

  getUserComments: async (userId: string): Promise<Comment[]> => {
    const response = await apiClient.get(`/api/v1/comments/user/${userId}`);
    return response.data;
  },
};

// Offers API
export const offersApi = {
  list: async (params?: { skip?: number; limit?: number }): Promise<Offer[]> => {
    const response = await apiClient.get('/api/v1/offers/', { params });
    return response.data.items || [];
  },

  get: async (offerId: string): Promise<Offer> => {
    const response = await apiClient.get(`/api/v1/offers/${offerId}`);
    return response.data;
  },

  create: async (data: CreateOfferRequest): Promise<Offer> => {
    const response = await apiClient.post('/api/v1/offers/', data);
    return response.data;
  },

  update: async (offerId: string, data: Partial<CreateOfferRequest>): Promise<Offer> => {
    const response = await apiClient.put(`/api/v1/offers/${offerId}`, data);
    return response.data;
  },

  delete: async (offerId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/offers/${offerId}`);
  },

  getMyOffers: async (): Promise<Offer[]> => {
    const response = await apiClient.get('/api/v1/offers/me/my-offers');
    return response.data;
  },
};

// Needs API
export const needsApi = {
  list: async (params?: { skip?: number; limit?: number }): Promise<Need[]> => {
    const response = await apiClient.get('/api/v1/needs/', { params });
    return response.data.items || [];
  },

  get: async (needId: string): Promise<Need> => {
    const response = await apiClient.get(`/api/v1/needs/${needId}`);
    return response.data;
  },

  create: async (data: CreateNeedRequest): Promise<Need> => {
    const response = await apiClient.post('/api/v1/needs/', data);
    return response.data;
  },

  update: async (needId: string, data: Partial<CreateNeedRequest>): Promise<Need> => {
    const response = await apiClient.put(`/api/v1/needs/${needId}`, data);
    return response.data;
  },

  delete: async (needId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/needs/${needId}`);
  },

  getMyNeeds: async (): Promise<Need[]> => {
    const response = await apiClient.get('/api/v1/needs/me/my-needs');
    return response.data;
  },
};

// Tags API
export const tagsApi = {
  list: async (): Promise<Tag[]> => {
    const response = await apiClient.get('/api/v1/offers/tags/');
    return response.data;
  },
};

// Participants API
export const participantsApi = {
  // Offer participants
  proposeForOffer: async (offerId: string): Promise<Participant> => {
    const response = await apiClient.post(`/api/v1/participants/offers/${offerId}`);
    return response.data;
  },

  getOfferParticipants: async (offerId: string): Promise<Participant[]> => {
    const response = await apiClient.get(`/api/v1/participants/offers/${offerId}`);
    return response.data;
  },

  acceptOfferParticipant: async (
    offerId: string,
    participantId: string,
    data: AcceptParticipantRequest
  ): Promise<Participant> => {
    const response = await apiClient.post(
      `/api/v1/participants/offers/${offerId}/accept`,
      { ...data, participant_id: participantId }
    );
    return response.data;
  },

  // Need participants
  proposeForNeed: async (needId: string): Promise<Participant> => {
    const response = await apiClient.post(`/api/v1/participants/needs/${needId}`);
    return response.data;
  },

  getNeedParticipants: async (needId: string): Promise<Participant[]> => {
    const response = await apiClient.get(`/api/v1/participants/needs/${needId}`);
    return response.data;
  },

  acceptNeedParticipant: async (
    needId: string,
    participantId: string,
    data: AcceptParticipantRequest
  ): Promise<Participant> => {
    const response = await apiClient.post(
      `/api/v1/participants/needs/${needId}/accept`,
      { ...data, participant_id: participantId }
    );
    return response.data;
  },

  // Complete exchange
  completeExchange: async (participantId: string): Promise<Participant> => {
    const response = await apiClient.post(
      `/api/v1/participants/exchange/${participantId}/complete`
    );
    return response.data;
  },

  // Get my participations
  getMyParticipations: async (): Promise<Participant[]> => {
    const response = await apiClient.get('/api/v1/participants/me/participations');
    return response.data;
  },
};

// Comments API
export const commentsApi = {
  create: async (data: CreateCommentRequest): Promise<Comment> => {
    const response = await apiClient.post('/api/v1/comments', data);
    return response.data;
  },

  getUserComments: async (userId: string): Promise<Comment[]> => {
    const response = await apiClient.get(`/api/v1/comments/user/${userId}`);
    return response.data;
  },
};

// Search API
export const searchApi = {
  search: async (params: SearchParams): Promise<(Offer | Need)[]> => {
    const response = await apiClient.get('/api/v1/search/', { params });
    return response.data;
  },
};

// Map API
export const mapApi = {
  getMapItems: async (): Promise<MapItem[]> => {
    const response = await apiClient.get('/api/v1/map/items');
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get('/api/v1/dashboard/stats');
    return response.data;
  },
};

// Forum API
export const forumApi = {
  listPosts: async (params?: { skip?: number; limit?: number }): Promise<ForumPost[]> => {
    const response = await apiClient.get('/api/v1/forum/posts', { params });
    return response.data;
  },

  getPost: async (postId: string): Promise<ForumPost> => {
    const response = await apiClient.get(`/api/v1/forum/posts/${postId}`);
    return response.data;
  },

  createPost: async (data: { title: string; content: string }): Promise<ForumPost> => {
    const response = await apiClient.post('/api/v1/forum/posts', data);
    return response.data;
  },

  getReplies: async (postId: string): Promise<ForumReply[]> => {
    const response = await apiClient.get(`/api/v1/forum/posts/${postId}/replies`);
    return response.data;
  },

  createReply: async (postId: string, content: string): Promise<ForumReply> => {
    const response = await apiClient.post(`/api/v1/forum/posts/${postId}/replies`, {
      content,
    });
    return response.data;
  },
};
