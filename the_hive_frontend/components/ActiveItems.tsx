import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, X, MessageSquare, Trash2 } from 'lucide-react';
import AuthNavbar from './AuthNavbar';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Avatar, AvatarFallback } from './ui/avatar';
import { offersNeeds, applications, users, currentUser } from '../lib/mock-data';
import { toast } from 'sonner@2.0.3';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from './ui/alert-dialog';

export default function ActiveItems() {
  const navigate = useNavigate();
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    action: 'accept' | 'decline' | 'withdraw' | null;
    applicationId: string | null;
  }>({ open: false, action: null, applicationId: null });

  // Get user's active posts
  const myPosts = Object.values(offersNeeds).filter(
    (post) => post.creatorId === currentUser.id && post.status === 'active'
  );

  // Get applications for user's posts
  const applicationsForMyPosts = applications.filter((app) =>
    myPosts.some((post) => post.id === app.postId)
  );

  // Get user's applications
  const myApplications = applications.filter((app) => app.applicantId === currentUser.id);

  const handleAccept = (applicationId: string) => {
    toast.success('Application accepted! You can now message this person.');
    setConfirmDialog({ open: false, action: null, applicationId: null });
  };

  const handleDecline = (applicationId: string) => {
    toast.success('Application declined');
    setConfirmDialog({ open: false, action: null, applicationId: null });
  };

  const handleWithdraw = (applicationId: string) => {
    toast.success('Application withdrawn');
    setConfirmDialog({ open: false, action: null, applicationId: null });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <AuthNavbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-gray-900 mb-6">My Active Items</h1>

        <Tabs defaultValue="posts" className="w-full">
          <TabsList className="w-full justify-start">
            <TabsTrigger value="posts">
              My Posts ({applicationsForMyPosts.length})
            </TabsTrigger>
            <TabsTrigger value="applications">
              My Applications ({myApplications.length})
            </TabsTrigger>
          </TabsList>

          {/* My Posts Tab */}
          <TabsContent value="posts" className="mt-6">
            <div className="space-y-6">
              {myPosts.length > 0 ? (
                myPosts.map((post) => {
                  const postApplications = applicationsForMyPosts.filter(
                    (app) => app.postId === post.id
                  );

                  return (
                    <Card key={post.id}>
                      <CardHeader>
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
                            </div>
                            <CardTitle className="cursor-pointer hover:text-blue-600" onClick={() => navigate(`/${post.type}/${post.id}`)}>
                              {post.title}
                            </CardTitle>
                          </div>
                          <Badge variant="outline">
                            {postApplications.length} applicant(s)
                          </Badge>
                        </div>
                      </CardHeader>

                      {postApplications.length > 0 && (
                        <CardContent>
                          <div className="space-y-3">
                            {postApplications.map((application) => {
                              const applicant = users[application.applicantId];
                              return (
                                <div
                                  key={application.id}
                                  className="border rounded-lg p-4 bg-white"
                                >
                                  <div className="flex items-start justify-between gap-3">
                                    <div className="flex items-start gap-3 flex-1">
                                      <Avatar
                                        className="w-10 h-10 cursor-pointer"
                                        onClick={() => navigate(`/profile/${applicant.id}`)}
                                      >
                                        <AvatarFallback className="bg-blue-500 text-white">
                                          {applicant.initials}
                                        </AvatarFallback>
                                      </Avatar>
                                      <div className="flex-1">
                                        <div
                                          className="text-gray-900 cursor-pointer hover:text-blue-600"
                                          onClick={() => navigate(`/profile/${applicant.id}`)}
                                        >
                                          {applicant.name}
                                        </div>
                                        {application.message && (
                                          <p className="text-sm text-gray-600 mt-1">
                                            {application.message}
                                          </p>
                                        )}
                                        <div className="text-xs text-gray-500 mt-1">
                                          Applied {new Date(application.createdAt).toLocaleDateString()}
                                        </div>
                                      </div>
                                    </div>

                                    {application.status === 'pending' && (
                                      <div className="flex gap-2">
                                        <Button
                                          size="sm"
                                          variant="outline"
                                          className="gap-1 text-green-600 hover:text-green-700"
                                          onClick={() =>
                                            setConfirmDialog({
                                              open: true,
                                              action: 'accept',
                                              applicationId: application.id,
                                            })
                                          }
                                        >
                                          <Check className="w-4 h-4" />
                                          Accept
                                        </Button>
                                        <Button
                                          size="sm"
                                          variant="outline"
                                          className="gap-1 text-red-600 hover:text-red-700"
                                          onClick={() =>
                                            setConfirmDialog({
                                              open: true,
                                              action: 'decline',
                                              applicationId: application.id,
                                            })
                                          }
                                        >
                                          <X className="w-4 h-4" />
                                          Decline
                                        </Button>
                                      </div>
                                    )}

                                    {application.status === 'accepted' && (
                                      <div className="flex gap-2 items-center">
                                        <Badge className="bg-green-500">Accepted</Badge>
                                        <Button
                                          size="sm"
                                          variant="outline"
                                          className="gap-1"
                                          onClick={() =>
                                            navigate(`/messages/exchange-${application.id}`)
                                          }
                                        >
                                          <MessageSquare className="w-4 h-4" />
                                          Message
                                        </Button>
                                      </div>
                                    )}

                                    {application.status === 'declined' && (
                                      <Badge variant="destructive">Declined</Badge>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </CardContent>
                      )}

                      {postApplications.length === 0 && (
                        <CardContent>
                          <p className="text-sm text-gray-500 text-center py-4">
                            No applications yet
                          </p>
                        </CardContent>
                      )}
                    </Card>
                  );
                })
              ) : (
                <Card>
                  <CardContent className="p-12 text-center">
                    <p className="text-gray-500">You don't have any active posts</p>
                    <Button className="mt-4" onClick={() => navigate('/')}>
                      Create a Post
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* My Applications Tab */}
          <TabsContent value="applications" className="mt-6">
            <div className="space-y-4">
              {myApplications.length > 0 ? (
                myApplications.map((application) => {
                  const post = offersNeeds[application.postId];
                  const creator = users[post.creatorId];

                  return (
                    <Card key={application.id}>
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
                              {application.status === 'pending' && (
                                <Badge variant="outline" className="bg-yellow-50 text-yellow-700">
                                  Pending
                                </Badge>
                              )}
                              {application.status === 'accepted' && (
                                <Badge className="bg-green-500">Accepted</Badge>
                              )}
                              {application.status === 'declined' && (
                                <Badge variant="destructive">Declined</Badge>
                              )}
                            </div>

                            <h3
                              className="text-gray-900 mb-1 cursor-pointer hover:text-blue-600"
                              onClick={() => navigate(`/${post.type}/${post.id}`)}
                            >
                              {post.title}
                            </h3>

                            <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                              <Avatar className="w-6 h-6">
                                <AvatarFallback className="text-xs bg-gray-200">
                                  {creator.initials}
                                </AvatarFallback>
                              </Avatar>
                              <span>by {creator.name}</span>
                            </div>

                            {application.message && (
                              <p className="text-sm text-gray-600 mt-2">
                                Your message: "{application.message}"
                              </p>
                            )}

                            <div className="text-xs text-gray-500 mt-2">
                              Applied {new Date(application.createdAt).toLocaleDateString()}
                            </div>
                          </div>

                          <div className="flex gap-2">
                            {application.status === 'accepted' && (
                              <Button
                                size="sm"
                                variant="outline"
                                className="gap-1"
                                onClick={() =>
                                  navigate(`/messages/exchange-${application.id}`)
                                }
                              >
                                <MessageSquare className="w-4 h-4" />
                                Message
                              </Button>
                            )}

                            {application.status === 'pending' && (
                              <Button
                                size="sm"
                                variant="outline"
                                className="gap-1 text-red-600 hover:text-red-700"
                                onClick={() =>
                                  setConfirmDialog({
                                    open: true,
                                    action: 'withdraw',
                                    applicationId: application.id,
                                  })
                                }
                              >
                                <Trash2 className="w-4 h-4" />
                                Withdraw
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })
              ) : (
                <Card>
                  <CardContent className="p-12 text-center">
                    <p className="text-gray-500">You haven't applied to any posts yet</p>
                    <Button className="mt-4" onClick={() => navigate('/')}>
                      Browse Posts
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Confirmation Dialog */}
      <AlertDialog open={confirmDialog.open} onOpenChange={(open) => !open && setConfirmDialog({ open: false, action: null, applicationId: null })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {confirmDialog.action === 'accept' && 'Accept Application?'}
              {confirmDialog.action === 'decline' && 'Decline Application?'}
              {confirmDialog.action === 'withdraw' && 'Withdraw Application?'}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {confirmDialog.action === 'accept' &&
                'This will notify the applicant and allow you to start messaging.'}
              {confirmDialog.action === 'decline' &&
                'This will notify the applicant that their application was not accepted.'}
              {confirmDialog.action === 'withdraw' &&
                'This will remove your application from this post.'}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (confirmDialog.applicationId) {
                  if (confirmDialog.action === 'accept') handleAccept(confirmDialog.applicationId);
                  if (confirmDialog.action === 'decline') handleDecline(confirmDialog.applicationId);
                  if (confirmDialog.action === 'withdraw') handleWithdraw(confirmDialog.applicationId);
                }
              }}
            >
              Confirm
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
