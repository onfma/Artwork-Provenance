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
export const createArtwork = (data) => api.post('/artworks', data)
export const updateArtwork = (id, data) => api.put(`/artworks/${id}`, data)
export const deleteArtwork = (id) => api.delete(`/artworks/${id}`)
export const enrichArtwork = (id, source) => api.get(`/artworks/${id}/enrich`, { params: { source } })

// Provenance
export const getProvenanceChain = (artworkId) => api.get(`/provenance/${artworkId}/chain`)
export const addProvenanceEvent = (artworkId, data) => api.post(`/provenance/${artworkId}/events`, data)
export const getProvenanceTimeline = (artworkId) => api.get(`/provenance/timeline/${artworkId}`)
export const searchProvenanceEvents = (params) => api.get('/provenance/events/search', { params })

// SPARQL
export const executeSPARQL = (data) => api.post('/sparql/query', data)
export const getSPARQLExamples = () => api.get('/sparql/examples')
export const getStatistics = () => api.get('/sparql/statistics')
export const queryDBpedia = (query) => api.get('/sparql/federated/dbpedia', { params: { query } })
export const queryWikidata = (query) => api.get('/sparql/federated/wikidata', { params: { query } })
export const queryGetty = (query) => api.get('/sparql/federated/getty', { params: { query } })

// Recommendations
export const getRecommendations = (artworkId, params) => api.get(`/recommendations/${artworkId}`, { params })
export const getSimilarProvenance = (artworkId, params) => api.get(`/recommendations/${artworkId}/similar-provenance`, { params })

// Visualization
export const getOverviewStats = () => api.get('/visualization/statistics/overview')
export const getArtworksByType = () => api.get('/visualization/statistics/by-type')
export const getArtworksByCentury = () => api.get('/visualization/statistics/by-century')
export const getTopArtists = (limit) => api.get('/visualization/statistics/top-artists', { params: { limit } })
export const getTopLocations = (limit) => api.get('/visualization/statistics/top-locations', { params: { limit } })
export const getProvenanceNetwork = (artworkId) => api.get(`/visualization/network/provenance/${artworkId}`)
export const getLocationMap = () => api.get('/visualization/map/locations')

export default api
