import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ArtworksPage from './pages/ArtworksPage'
import ArtworkDetailPage from './pages/ArtworkDetailPage'
import ProvenancePage from './pages/ProvenancePage'
import SPARQLPage from './pages/SPARQLPage'
import VisualizationPage from './pages/VisualizationPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/artworks" element={<ArtworksPage />} />
        <Route path="/artworks/:id" element={<ArtworkDetailPage />} />
        <Route path="/provenance/:id" element={<ProvenancePage />} />
        <Route path="/sparql" element={<SPARQLPage />} />
        <Route path="/visualization" element={<VisualizationPage />} />
      </Routes>
    </Layout>
  )
}

export default App
