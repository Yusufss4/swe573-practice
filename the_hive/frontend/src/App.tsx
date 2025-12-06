import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import MapView from './pages/MapView'
import OfferDetail from './pages/OfferDetail'
import NeedDetail from './pages/NeedDetail'
import CreateOffer from './pages/CreateOffer'
import CreateNeed from './pages/CreateNeed'
import ActiveItems from './pages/ActiveItems'
import ProfilePage from './pages/ProfilePage'
import MyProfile from './pages/MyProfile'
import Search from './pages/Search'

// SRS: Main application component
// Provides routing structure for all pages defined in SRS Section 3.3.1
function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        {/* SRS FR-9: Map-Based Visualization - Home map view */}
        <Route index element={<MapView />} />
        
        {/* SRS FR-1: User Registration and Authentication */}
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        
        {/* SRS FR-3: Offer and Need Management */}
        <Route path="offers" element={<div>Offers List - To be implemented</div>} />
        <Route path="offers/:id" element={<OfferDetail />} />
        <Route path="offers/create" element={<CreateOffer />} />
        
        <Route path="needs" element={<div>Needs List - To be implemented</div>} />
        <Route path="needs/:id" element={<NeedDetail />} />
        <Route path="needs/create" element={<CreateNeed />} />
        
        {/* SRS FR-2: Profile Management */}
        <Route path="profile/:username" element={<ProfilePage />} />
        <Route path="profile/me" element={<MyProfile />} />
        
        {/* SRS FR-14: Active Items Management */}
        <Route path="active-items" element={<ActiveItems />} />        {/* SRS FR-6: Messaging System */}
        <Route path="messages" element={<div>Messages - To be implemented</div>} />
        
        {/* SRS FR-15: Community Forum */}
        <Route path="forum" element={<div>Forum - To be implemented</div>} />
        <Route path="forum/discussions" element={<div>Discussions - To be implemented</div>} />
        <Route path="forum/events" element={<div>Events - To be implemented</div>} />
        
        {/* SRS FR-8: Tagging and Search */}
        <Route path="search" element={<Search />} />
        
        {/* SRS FR-11: Reporting and Moderation - Admin/Moderator dashboards */}
        <Route path="admin" element={<div>Admin Dashboard - To be implemented</div>} />
        <Route path="moderator" element={<div>Moderator Dashboard - To be implemented</div>} />
      </Route>
    </Routes>
  )
}

export default App
