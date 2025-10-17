import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Machines from './pages/Machines'
import Images from './pages/Images'
import Writebacks from './pages/Writebacks'
import Snapshots from './pages/Snapshots'
import Network from './pages/Network'
import Storage from './pages/Storage'
import Settings from './pages/Settings'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="machines" element={<Machines />} />
        <Route path="images" element={<Images />} />
        <Route path="writebacks" element={<Writebacks />} />
        <Route path="snapshots" element={<Snapshots />} />
        <Route path="storage" element={<Storage />} />
        <Route path="network" element={<Network />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App

