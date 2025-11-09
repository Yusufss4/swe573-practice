import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, Menu, Bell, Check } from 'lucide-react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Sheet, SheetContent, SheetTrigger } from './ui/sheet';
import { useAuth } from '../src/contexts/AuthContext';

interface AuthNavbarProps {
  onCreateClick?: () => void;
}

export default function AuthNavbar({ onCreateClick }: AuthNavbarProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [notificationsList, setNotificationsList] = useState<any[]>([]);

  const unreadCount = notificationsList.filter((n) => !n.isRead).length;

  const markAsRead = (notificationId: string) => {
    setNotificationsList((prev) =>
      prev.map((n) => (n.id === notificationId ? { ...n, isRead: true } : n))
    );
  };

  const markAllAsRead = () => {
    setNotificationsList((prev) => prev.map((n) => ({ ...n, isRead: true })));
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'application':
        return '📝';
      case 'acceptance':
        return '✅';
      case 'message':
        return '💬';
      case 'comment':
        return '💭';
      case 'system':
        return '🔔';
      default:
        return '📌';
    }
  };

  const handleNotificationClick = (notification: any) => {
    markAsRead(notification.id);
    // Navigate based on notification type
    if (notification.relatedType === 'application') {
      navigate('/active-items');
    } else if (notification.relatedType === 'exchange') {
      navigate(`/messages/${notification.relatedId}`);
    } else if (notification.relatedType === 'user') {
      navigate(`/profile/${notification.relatedId}`);
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInMins = Math.floor(diffInMs / 60000);
    const diffInHours = Math.floor(diffInMs / 3600000);
    const diffInDays = Math.floor(diffInMs / 86400000);

    if (diffInMins < 60) {
      return `${diffInMins}m ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      return `${diffInDays}d ago`;
    }
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-white">
                <path
                  d="M12 2L2 7L12 12L22 7L12 2Z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M2 17L12 22L22 17"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M2 12L12 17L22 12"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <span className="text-gray-900">The Hive</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-4">
            <Button onClick={onCreateClick} className="gap-2">
              <Plus className="w-4 h-4" />
              Create
            </Button>

            <Link to="/active-items">
              <Button variant="ghost">Active Items</Button>
            </Link>

            <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-50 rounded-lg border border-amber-200">
              <span className="text-sm text-gray-600">Balance:</span>
              <span className="text-amber-600">{user?.balance?.toFixed(1) || '0.0'}h</span>
            </div>

            {/* Notifications Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="relative">
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-96">
                <div className="flex items-center justify-between px-4 py-3 border-b">
                  <span className="text-gray-900">Notifications</span>
                  {unreadCount > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={markAllAsRead}
                      className="h-auto py-1 text-xs"
                    >
                      <Check className="w-3 h-3 mr-1" />
                      Mark all read
                    </Button>
                  )}
                </div>
                <ScrollArea className="h-96">
                  {notificationsList.length > 0 ? (
                    <div className="py-2">
                      {notificationsList.map((notification) => (
                        <div
                          key={notification.id}
                          className={`px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors border-b border-gray-100 ${
                            !notification.isRead ? 'bg-blue-50' : ''
                          }`}
                          onClick={() => handleNotificationClick(notification)}
                        >
                          <div className="flex gap-3">
                            <div className="text-2xl flex-shrink-0">
                              {getNotificationIcon(notification.type)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between gap-2 mb-1">
                                <span className="text-sm text-gray-900">
                                  {notification.title}
                                </span>
                                {!notification.isRead && (
                                  <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1" />
                                )}
                              </div>
                              <p className="text-sm text-gray-600 line-clamp-2">
                                {notification.message}
                              </p>
                              <span className="text-xs text-gray-400 mt-1 inline-block">
                                {formatTimeAgo(notification.createdAt)}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="py-12 text-center text-gray-500 text-sm">
                      No notifications
                    </div>
                  )}
                </ScrollArea>
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="gap-2">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="bg-blue-500 text-white">
                      {user?.username?.substring(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden lg:inline">{user?.full_name || user?.username}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={() => navigate(`/profile/${user?.id}`)}>
                  My Profile
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-red-600">Log Out</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Mobile Navigation */}
          <div className="md:hidden flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-2 py-1 bg-amber-50 rounded border border-amber-200">
              <span className="text-xs text-gray-600">Balance:</span>
              <span className="text-xs text-amber-600">{user?.balance.toFixed(1)}h</span>
            </div>

            {/* Mobile Notifications */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="relative">
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80">
                <div className="flex items-center justify-between px-4 py-3 border-b">
                  <span className="text-gray-900">Notifications</span>
                  {unreadCount > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={markAllAsRead}
                      className="h-auto py-1 text-xs"
                    >
                      <Check className="w-3 h-3 mr-1" />
                      Mark all
                    </Button>
                  )}
                </div>
                <ScrollArea className="h-96">
                  {notificationsList.length > 0 ? (
                    <div className="py-2">
                      {notificationsList.map((notification) => (
                        <div
                          key={notification.id}
                          className={`px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors border-b border-gray-100 ${
                            !notification.isRead ? 'bg-blue-50' : ''
                          }`}
                          onClick={() => handleNotificationClick(notification)}
                        >
                          <div className="flex gap-3">
                            <div className="text-2xl flex-shrink-0">
                              {getNotificationIcon(notification.type)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between gap-2 mb-1">
                                <span className="text-sm text-gray-900">
                                  {notification.title}
                                </span>
                                {!notification.isRead && (
                                  <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1" />
                                )}
                              </div>
                              <p className="text-sm text-gray-600 line-clamp-2">
                                {notification.message}
                              </p>
                              <span className="text-xs text-gray-400 mt-1 inline-block">
                                {formatTimeAgo(notification.createdAt)}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="py-12 text-center text-gray-500 text-sm">
                      No notifications
                    </div>
                  )}
                </ScrollArea>
              </DropdownMenuContent>
            </DropdownMenu>

            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Menu className="w-5 h-5" />
                </Button>
              </SheetTrigger>
              <SheetContent>
                <div className="flex flex-col gap-4 mt-8">
                  <div className="flex items-center gap-3 pb-4 border-b">
                    <Avatar className="w-10 h-10">
                      <AvatarFallback className="bg-blue-500 text-white">
                        {user?.username?.substring(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div>{user?.full_name || user?.username}</div>
                      <div className="text-sm text-gray-500">
                        {user?.balance.toFixed(1)}h balance
                      </div>
                    </div>
                  </div>

                  <Button onClick={onCreateClick} className="gap-2 w-full">
                    <Plus className="w-4 h-4" />
                    Create
                  </Button>

                  <Link to="/active-items">
                    <Button variant="outline" className="w-full">
                      Active Items
                    </Button>
                  </Link>

                  <Link to={`/profile/${user?.id}`}>
                    <Button variant="outline" className="w-full">
                      My Profile
                    </Button>
                  </Link>

                  <Button variant="ghost" className="text-red-600 w-full">
                    Log Out
                  </Button>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </nav>
  );
}
