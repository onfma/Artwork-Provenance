import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Artworks
export const getArtworks = (params) => api.get('/artworks', { params })
export const getArtwork = (id) => api.get(`/artworks/${id}`)
export const enrichArtwork = (id, source) => api.get(`/artworks/${id}/enrich`, { params: { source } })

// Artists
export const getArtists = (params) => api.get('/artists', { params })
export const getArtist = (id) => api.get(`/artists/${id}`)
export const enrichArtist = (id, source) => api.get(`/artists/${id}/enrich`, { params: { source } })

// Locations
export const getLocations = (params) => api.get('/locations', { params })
export const getLocation = (id) => api.get(`/locations/${id}`)

// Provenance
export const searchProvenanceEvents = (params) => api.get('/provenance', { params })
export const getProvenanceTimeline = (eventId) => api.get(`/provenance/${eventId}`)
export const getProvenanceChain = (artworkId) => api.get(`/provenance/${artworkId}/chain`)

// Visualization
export const getOverviewStats = () => api.get('/visualization/statistics/overview')
export const getArtworksByType = () => api.get('/visualization/statistics/by-type')
export const getArtworksByMaterial = () => api.get('/visualization/statistics/by-material')
export const getTopArtists = (limit) => api.get('/visualization/statistics/top-artists', { params: { limit } })
export const getTopLocations = (limit) => api.get('/visualization/statistics/top-locations', { params: { limit } })
export const getArtistNetwork = (artist_id) => api.get(`/visualization/statistics/network/artists/${artist_id}`)
// export const getLocationMap = () => api.get('/visualization/map/locations')

// SPARQL
export const executeSPARQL = (data) => api.post('/sparql/query', data)
export const getSPARQLExamples = () => api.get('/sparql/examples')
export const getStatistics = () => api.get('/sparql/statistics')

// Recommendations
export const getRecommendations = (artworkId, params) => api.get(`/recommendations/${artworkId}`, { params })
export const getSimilarProvenance = (artworkId, params) => api.get(`/recommendations/${artworkId}/similar-provenance`, { params })


export default api
