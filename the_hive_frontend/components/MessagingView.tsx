import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Send, ArrowLeft, Users } from 'lucide-react';
import AuthNavbar from './AuthNavbar';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { messages, currentUser, users } from '../lib/mock-data';

export default function MessagingView() {
  const { exchangeId } = useParams();
  const navigate = useNavigate();
  const [messageText, setMessageText] = useState('');

  // Mock exchange data
  const exchange = {
    id: exchangeId || 'exchange-1',
    title: 'Web Development Tutoring',
    participants: ['user-1', 'user-2'],
  };

  const conversationMessages = messages.filter((msg) => msg.exchangeId === exchange.id);
  const otherParticipants = exchange.participants.filter((id) => id !== currentUser.id);

  const handleSendMessage = () => {
    if (!messageText.trim()) return;

    // In a real app, this would send the message to the backend
    console.log('Sending message:', messageText);
    setMessageText('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <AuthNavbar />

      <div className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 flex flex-col">
        {/* Header */}
        <Card className="mb-4">
          <CardHeader className="p-4">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/active-items')}
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>

              <div className="flex-1">
                <CardTitle className="text-lg">{exchange.title}</CardTitle>
                <div className="flex items-center gap-2 mt-1">
                  <Users className="w-4 h-4 text-gray-500" />
                  <div className="flex items-center gap-1">
                    {otherParticipants.map((userId) => {
                      const user = users[userId];
                      return (
                        <Badge
                          key={userId}
                          variant="secondary"
                          className="cursor-pointer"
                          onClick={() => navigate(`/profile/${userId}`)}
                        >
                          {user.name}
                        </Badge>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Messages */}
        <Card className="flex-1 flex flex-col min-h-0">
          <CardContent className="p-4 flex-1 flex flex-col min-h-0">
            <ScrollArea className="flex-1 pr-4">
              <div className="space-y-4">
                {conversationMessages.map((message) => {
                  const sender = users[message.senderId];
                  const isCurrentUser = message.senderId === currentUser.id;

                  return (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${isCurrentUser ? 'flex-row-reverse' : ''}`}
                    >
                      <Avatar className="w-8 h-8 flex-shrink-0">
                        <AvatarFallback
                          className={
                            isCurrentUser ? 'bg-blue-500 text-white' : 'bg-gray-300'
                          }
                        >
                          {sender.initials}
                        </AvatarFallback>
                      </Avatar>

                      <div
                        className={`flex flex-col ${
                          isCurrentUser ? 'items-end' : 'items-start'
                        } max-w-[70%]`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs text-gray-500">
                            {isCurrentUser ? 'You' : sender.name}
                          </span>
                          <span className="text-xs text-gray-400">
                            {new Date(message.timestamp).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </span>
                        </div>

                        <div
                          className={`rounded-lg px-4 py-2 ${
                            isCurrentUser
                              ? 'bg-blue-500 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}

                {conversationMessages.length === 0 && (
                  <div className="text-center py-12">
                    <p className="text-gray-500">No messages yet. Start the conversation!</p>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Message Input */}
            <div className="flex gap-2 mt-4 pt-4 border-t">
              <Input
                placeholder="Type your message..."
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                onKeyDown={handleKeyPress}
                className="flex-1"
              />
              <Button onClick={handleSendMessage} disabled={!messageText.trim()} className="gap-2">
                <Send className="w-4 h-4" />
                Send
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
