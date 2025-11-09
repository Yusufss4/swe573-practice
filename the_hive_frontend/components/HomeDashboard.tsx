import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, MapPin, Tag as TagIcon } from 'lucide-react';
import AuthNavbar from './AuthNavbar';
import CreateOfferNeedModal from './CreateOfferNeedModal';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Card, CardContent } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { offersApi, needsApi } from '../src/lib/api';
import type { Offer, Need } from '../src/lib/types';

export default function HomeDashboard() {
  const navigate = useNavigate();
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<'all' | 'offer' | 'need'>('all');
  const [selectedPin, setSelectedPin] = useState<string | null>(null);

  // Fetch offers and needs from API
  const { data: offers = [], isLoading: offersLoading } = useQuery({
    queryKey: ['offers'],
    queryFn: () => offersApi.list(),
  });

  const { data: needs = [], isLoading: needsLoading } = useQuery({
    queryKey: ['needs'],
    queryFn: () => needsApi.list(),
  });

  const isLoading = offersLoading || needsLoading;

  // Combine offers and needs into a unified format for display
  type Post = (Offer | Need) & { type: 'offer' | 'need' };
  
  const posts: Post[] = [
    ...offers.filter((o) => o.status === 'active').map((o) => ({ ...o, type: 'offer' as const })),
    ...needs.filter((n) => n.status === 'active').map((n) => ({ ...n, type: 'need' as const })),
  ];

  const filteredPosts = posts.filter((post) => {
    const matchesSearch =
      post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter === 'all' || post.type === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <AuthNavbar onCreateClick={() => setCreateModalOpen(true)} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-gray-600">Loading...</p>
          </div>
        )}

        {/* Content */}
        {!isLoading && (
          <>
            {/* Search & Filter Bar */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
              <div className="flex flex-col md:flex-row gap-3">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    placeholder="Search offers and needs..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>

                <Select value={typeFilter} onValueChange={(v) => setTypeFilter(v as any)}>
                  <SelectTrigger className="w-full md:w-40">
                    <SelectValue placeholder="Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="offer">Offers</SelectItem>
                    <SelectItem value="need">Needs</SelectItem>
                  </SelectContent>
                </Select>

                <Button variant="outline" className="gap-2">
                  <Filter className="w-4 h-4" />
                  More Filters
                </Button>
              </div>
            </div>

        {/* Map and List */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Map View */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden h-[600px] relative">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
              <div className="text-center">
                <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">Interactive Map View</p>
                <p className="text-sm text-gray-400 mt-1">
                  Showing {filteredPosts.length} items
                </p>
              </div>

              {/* Mock map pins */}
              <div className="absolute inset-0">
                {filteredPosts.slice(0, 6).map((post, index) => (
                  <div
                    key={post.id}
                    className={`absolute w-8 h-8 rounded-full flex items-center justify-center cursor-pointer transform transition-transform hover:scale-110 ${
                      post.type === 'offer' ? 'bg-green-500' : 'bg-blue-500'
                    } ${selectedPin === post.id ? 'ring-4 ring-white scale-125' : ''}`}
                    style={{
                      left: `${20 + index * 15}%`,
                      top: `${30 + (index % 3) * 20}%`,
                    }}
                    onClick={() => setSelectedPin(post.id)}
                  >
                    <div className="w-2 h-2 bg-white rounded-full" />
                  </div>
                ))}
              </div>
            </div>

            {/* Map Legend */}
            <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-green-500" />
                <span className="text-sm">Offers</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-blue-500" />
                <span className="text-sm">Needs</span>
              </div>
            </div>
          </div>

          {/* List View */}
          <div className="space-y-4 h-[600px] overflow-y-auto pr-2">
            {filteredPosts.map((post) => {
              // Get initials from creator_id (simplified - in real app, fetch user data)
              const initials = `U${post.creator_id}`;
              
              return (
                <Card
                  key={post.id}
                  className={`cursor-pointer transition-shadow hover:shadow-md ${
                    selectedPin === String(post.id) ? 'ring-2 ring-blue-500' : ''
                  }`}
                  onClick={() => navigate(`/${post.type}/${post.id}`)}
                  onMouseEnter={() => setSelectedPin(String(post.id))}
                  onMouseLeave={() => setSelectedPin(null)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge
                            variant={post.type === 'offer' ? 'default' : 'secondary'}
                            className={
                              post.type === 'offer'
                                ? 'bg-green-500 hover:bg-green-600'
                                : 'bg-blue-500 hover:bg-blue-600 text-white'
                            }
                          >
                            {post.type === 'offer' ? 'Offer' : 'Need'}
                          </Badge>
                          {!post.is_remote && post.location_name && (
                            <span className="text-xs text-gray-500 flex items-center gap-1">
                              <MapPin className="w-3 h-3" />
                              {post.location_name}
                            </span>
                          )}
                          {post.is_remote && (
                            <Badge variant="outline" className="text-xs">
                              Remote
                            </Badge>
                          )}
                        </div>

                        <h3 className="font-semibold text-gray-900 mb-1">{post.title}</h3>
                        <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                          {post.description}
                        </p>

                        <div className="flex flex-wrap gap-1.5 mb-3">
                          {post.tags?.slice(0, 3).map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              <TagIcon className="w-3 h-3 mr-1" />
                              {tag}
                            </Badge>
                          ))}
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Avatar className="w-6 h-6">
                              <AvatarFallback className="text-xs bg-gray-200">
                                {initials}
                              </AvatarFallback>
                            </Avatar>
                            <span className="text-sm text-gray-600">Creator #{post.creator_id}</span>
                          </div>

                          <div className="text-xs text-gray-500">
                            {post.accepted_count} / {post.capacity} slots filled
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}

            {filteredPosts.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500">No items found matching your filters</p>
              </div>
            )}
          </div>
        </div>
        </>
        )}
      </div>

      <CreateOfferNeedModal open={createModalOpen} onClose={() => setCreateModalOpen(false)} />
    </div>
  );
}
