import { useQuery } from '@tanstack/react-query';
import { offersApi, needsApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Dashboard() {
  const { user, logout } = useAuth();

  // Fetch offers from API
  const { data: offers, isLoading: offersLoading } = useQuery({
    queryKey: ['offers'],
    queryFn: () => offersApi.list(),
  });

  // Fetch needs from API
  const { data: needs, isLoading: needsLoading } = useQuery({
    queryKey: ['needs'],
    queryFn: () => needsApi.list(),
  });

  const isLoading = offersLoading || needsLoading;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">The Hive</h1>
              <p className="text-sm text-gray-600">Time Banking Community</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.username}</p>
                <p className="text-xs text-gray-600">Balance: {user?.balance}h</p>
              </div>
              <Button variant="outline" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Your Balance</CardTitle>
              <CardDescription>Available hours</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{user?.balance}h</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Active Offers</CardTitle>
              <CardDescription>Services available</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{offers?.length || 0}</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Active Needs</CardTitle>
              <CardDescription>Help requested</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{needs?.length || 0}</p>
            </CardContent>
          </Card>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-gray-600">Loading...</p>
          </div>
        )}

        {/* Offers Section */}
        {!isLoading && (
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4">Available Offers</h2>
            {offers && offers.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {offers.map((offer) => (
                  <Card key={offer.id}>
                    <CardHeader>
                      <CardTitle className="text-lg">{offer.title}</CardTitle>
                      <CardDescription>
                        {offer.hours_estimated}h • {offer.status}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 line-clamp-3">
                        {offer.description}
                      </p>
                      <div className="mt-4">
                        <Button size="sm" className="w-full">
                          View Details
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="py-8 text-center">
                  <p className="text-gray-600">No offers available yet</p>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Needs Section */}
        {!isLoading && (
          <div>
            <h2 className="text-xl font-bold mb-4">Help Needed</h2>
            {needs && needs.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {needs.map((need) => (
                  <Card key={need.id}>
                    <CardHeader>
                      <CardTitle className="text-lg">{need.title}</CardTitle>
                      <CardDescription>
                        {need.hours_estimated}h • {need.status}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 line-clamp-3">
                        {need.description}
                      </p>
                      <div className="mt-4">
                        <Button size="sm" className="w-full" variant="outline">
                          Offer Help
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="py-8 text-center">
                  <p className="text-gray-600">No needs posted yet</p>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
