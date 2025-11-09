import { useParams, useNavigate } from 'react-router-dom';
import { Award, Clock, TrendingUp, TrendingDown } from 'lucide-react';
import AuthNavbar from './AuthNavbar';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { users, offersNeeds, comments } from '../lib/mock-data';

export default function UserProfile() {
  const { userId } = useParams();
  const navigate = useNavigate();

  const user = userId ? users[userId] : null;
  const userComments = userId ? comments[userId] || [] : [];

  // Get completed/archived posts by this user
  const userPosts = Object.values(offersNeeds).filter(
    (post) => post.creatorId === userId && (post.status === 'completed' || post.status === 'archived')
  );

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AuthNavbar />
        <div className="max-w-4xl mx-auto px-4 py-12 text-center">
          <p className="text-gray-500">User not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AuthNavbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-6">
              <Avatar className="w-24 h-24">
                <AvatarFallback className="bg-blue-500 text-white text-2xl">
                  {user.initials}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1">
                <h1 className="text-gray-900 mb-2">{user.name}</h1>
                <p className="text-gray-600 mb-4">{user.bio}</p>

                {/* Badge Showcase */}
                {user.badges.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Award className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600">Badges</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {user.badges.map((badge) => (
                        <Badge key={badge} className="bg-amber-100 text-amber-800 hover:bg-amber-200">
                          <Award className="w-3 h-3 mr-1" />
                          {badge}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Statistics */}
        <div className="grid sm:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-amber-600" />
                </div>
                <div>
                  <div className="text-sm text-gray-600">TimeBank Balance</div>
                  <div className="text-2xl text-gray-900">{user.balance.toFixed(1)}h</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <div className="text-sm text-gray-600">Hours Given</div>
                  <div className="text-2xl text-gray-900">{user.hoursGiven.toFixed(1)}h</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                  <TrendingDown className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <div className="text-sm text-gray-600">Hours Received</div>
                  <div className="text-2xl text-gray-900">{user.hoursReceived.toFixed(1)}h</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabbed Content */}
        <Tabs defaultValue="exchanges" className="w-full">
          <TabsList className="w-full justify-start">
            <TabsTrigger value="exchanges">Completed Exchanges</TabsTrigger>
            <TabsTrigger value="comments">
              Comments ({userComments.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="exchanges" className="mt-6">
            <div className="space-y-4">
              {userPosts.length > 0 ? (
                userPosts.map((post) => (
                  <Card
                    key={post.id}
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => navigate(`/${post.type}/${post.id}`)}
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
                            <Badge variant="outline">{post.status}</Badge>
                          </div>
                          <h3 className="text-gray-900 mb-1">{post.title}</h3>
                          <p className="text-sm text-gray-600 line-clamp-2">
                            {post.description}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card>
                  <CardContent className="p-12 text-center">
                    <p className="text-gray-500">No completed exchanges yet</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="comments" className="mt-6">
            <div className="space-y-4">
              {userComments.length > 0 ? (
                userComments.map((comment) => {
                  const author = users[comment.authorId];
                  return (
                    <Card key={comment.id}>
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <Avatar className="w-10 h-10">
                            <AvatarFallback className="bg-gray-300">
                              {author?.initials || 'U'}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-gray-900">{author?.name || 'Unknown'}</span>
                              <span className="text-sm text-gray-500">
                                {new Date(comment.createdAt).toLocaleDateString()}
                              </span>
                            </div>
                            <p className="text-gray-700">{comment.content}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })
              ) : (
                <Card>
                  <CardContent className="p-12 text-center">
                    <p className="text-gray-500">No comments yet</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
