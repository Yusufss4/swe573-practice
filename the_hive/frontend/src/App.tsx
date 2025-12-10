import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import HomePage from './pages/HomePage'
import MapView from './pages/MapView'
import OfferDetail from './pages/OfferDetail'
import NeedDetail from './pages/NeedDetail'
import CreateOffer from './pages/CreateOffer'
import CreateNeed from './pages/CreateNeed'
import ActiveItems from './pages/ActiveItems'
import ProfilePage from './pages/ProfilePage'
import MyProfile from './pages/MyProfile'
import Search from './pages/Search'
import Forum from './pages/Forum'
import ForumTopicDetail from './pages/ForumTopicDetail'
import CreateForumTopic from './pages/CreateForumTopic'
import TagsPage from './pages/TagsPage'
import ModeratorDashboard from './pages/ModeratorDashboard'

// SRS: Main application component
// Provides routing structure for all pages defined in SRS Section 3.3.1
function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        {/* Landing Page / Home Screen */}
        <Route index element={<HomePage />} />

        {/* SRS FR-9: Map-Based Visualization - Map view */}
        <Route path="map" element={<MapView />} />

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
        <Route path="forum" element={<Forum />} />
        <Route path="forum/topic/:topicId" element={<ForumTopicDetail />} />
        <Route path="forum/create" element={<CreateForumTopic />} />
        <Route path="forum/discussions" element={<Forum />} />
        <Route path="forum/events" element={<Forum />} />
        
        {/* SRS FR-8: Tagging and Search */}
        <Route path="search" element={<Search />} />
        
        {/* SRS FR-8.4: Tags Hierarchy Visualization */}
        <Route path="tags" element={<TagsPage />} />
        
        {/* SRS FR-11: Reporting and Moderation - Admin/Moderator dashboards */}
        <Route path="admin" element={<div>Admin Dashboard - To be implemented</div>} />
        <Route path="moderator" element={<ModeratorDashboard />} />
      </Route>
    </Routes>
  )
}

export default App
