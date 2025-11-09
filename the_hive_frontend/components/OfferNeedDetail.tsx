import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MapPin, Calendar as CalendarIcon, Users, Tag as TagIcon, Edit, Archive } from 'lucide-react';
import AuthNavbar from './AuthNavbar';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { offersNeeds, users, currentUser } from '../lib/mock-data';
import { toast } from 'sonner@2.0.3';

export default function OfferNeedDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [applicationModalOpen, setApplicationModalOpen] = useState(false);
  const [applicationMessage, setApplicationMessage] = useState('');
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);

  const post = id ? offersNeeds[id] : null;
  const creator = post ? users[post.creatorId] : null;
  const isOwnPost = post?.creatorId === currentUser.id;
  const isFull = post ? post.filledSlots >= post.capacity : false;

  if (!post || !creator) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AuthNavbar />
        <div className="max-w-4xl mx-auto px-4 py-12 text-center">
          <p className="text-gray-500">Post not found</p>
          <Button onClick={() => navigate('/')} className="mt-4">
            Back to Home
          </Button>
        </div>
      </div>
    );
  }

  const handleApplication = () => {
    toast.success('Application sent successfully!');
    setApplicationModalOpen(false);
    setApplicationMessage('');
    setSelectedSlot(null);
  };

  const handleArchive = () => {
    toast.success('Post archived successfully');
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <AuthNavbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-start justify-between gap-4 mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
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
                {post.isRemote && (
                  <Badge variant="outline">Remote</Badge>
                )}
                {isFull && (
                  <Badge variant="destructive">Capacity Full</Badge>
                )}
              </div>
              <h1 className="text-gray-900 mb-2">{post.title}</h1>
            </div>

            {isOwnPost && (
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="gap-2">
                  <Edit className="w-4 h-4" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-2 text-red-600"
                  onClick={handleArchive}
                >
                  <Archive className="w-4 h-4" />
                  Archive
                </Button>
              </div>
            )}
          </div>

          {/* Creator Info */}
          <div
            className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
            onClick={() => navigate(`/profile/${creator.id}`)}
          >
            <Avatar className="w-12 h-12">
              <AvatarFallback className="bg-blue-500 text-white">
                {creator.initials}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="text-gray-900">{creator.name}</div>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {creator.badges.slice(0, 3).map((badge) => (
                  <Badge key={badge} variant="secondary" className="text-xs">
                    {badge}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            <Card>
              <CardHeader>
                <CardTitle>Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 whitespace-pre-wrap">{post.description}</p>
              </CardContent>
            </Card>

            {/* Location */}
            {!post.isRemote && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="w-5 h-5" />
                    Location
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 mb-3">{post.location.address}</p>
                  <div className="w-full h-48 bg-gradient-to-br from-blue-50 to-green-50 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <MapPin className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                      <span className="text-gray-500 text-sm">Approximate area shown</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Availability Calendar (for Offers) */}
            {post.type === 'offer' && post.availability && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CalendarIcon className="w-5 h-5" />
                    Available Time Slots
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {post.availability.map((avail) => (
                      <div key={avail.date} className="border rounded-lg p-3">
                        <div className="text-sm text-gray-600 mb-2">
                          {new Date(avail.date).toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'long',
                            day: 'numeric',
                          })}
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {avail.slots.map((slot) => (
                            <Button
                              key={slot}
                              variant={selectedSlot === `${avail.date}-${slot}` ? 'default' : 'outline'}
                              size="sm"
                              onClick={() => setSelectedSlot(`${avail.date}-${slot}`)}
                              disabled={isOwnPost}
                            >
                              {slot}
                            </Button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Details Card */}
            <Card>
              <CardHeader>
                <CardTitle>Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Capacity</div>
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-gray-400" />
                    <span>
                      {post.filledSlots} / {post.capacity} slots filled
                    </span>
                  </div>
                </div>

                {post.tags.length > 0 && (
                  <div>
                    <div className="text-sm text-gray-600 mb-2">Tags</div>
                    <div className="flex flex-wrap gap-1.5">
                      {post.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="gap-1">
                          <TagIcon className="w-3 h-3" />
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* CTA Card */}
            {!isOwnPost && (
              <Card>
                <CardContent className="p-6">
                  <Button
                    className="w-full"
                    disabled={isFull}
                    onClick={() => setApplicationModalOpen(true)}
                  >
                    {isFull
                      ? 'Capacity Full'
                      : post.type === 'offer'
                      ? 'Request Service'
                      : 'Offer Help'}
                  </Button>
                  {!isFull && (
                    <p className="text-xs text-gray-500 mt-2 text-center">
                      {post.capacity - post.filledSlots} spot(s) remaining
                    </p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* Application Modal */}
      <Dialog open={applicationModalOpen} onOpenChange={setApplicationModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {post.type === 'offer' ? 'Request Service' : 'Offer Help'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label htmlFor="message">Add a message (optional)</Label>
              <Textarea
                id="message"
                placeholder="Introduce yourself or add any relevant details..."
                value={applicationMessage}
                onChange={(e) => setApplicationMessage(e.target.value)}
                rows={4}
                className="mt-2"
              />
            </div>

            {post.type === 'offer' && selectedSlot && (
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="text-sm text-gray-600">Selected time slot:</div>
                <div className="text-sm text-gray-900 mt-1">{selectedSlot}</div>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setApplicationModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleApplication}>Send Application</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
