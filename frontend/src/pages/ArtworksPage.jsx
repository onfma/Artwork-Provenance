import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getArtworks } from '../api'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

const ArtworksPage = () => {
  const [filters, setFilters] = useState({
    type_id: '',
    material_id: '',
    subject_id: '',
    artist_id: '',
    location_id: '',
    limit: 20,
    skip: 0
  })

  const [searchTerm, setSearchTerm] = useState('')
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm)
      setFilters(prev => ({ ...prev, skip: 0 }))
    }, 500)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const queryParams = { ...filters, search: debouncedSearchTerm }

  const { data, isLoading, error } = useQuery({
    queryKey: ['artworks', queryParams],
    queryFn: () => getArtworks(queryParams).then(res => res.data.artworks)
  })

  const artworkTypes = [
    { value: '', label: 'All Types' },
    { value: 'painting', label: 'Painting' },
    { value: 'sculpture', label: 'Sculpture' },
    { value: 'drawing', label: 'Drawing' },
    { value: 'print', label: 'Print' },
    { value: 'photograph', label: 'Photograph' },
    { value: 'manuscript', label: 'Manuscript' },
    { value: 'artifact', label: 'Artifact' },
    { value: 'installation', label: 'Installation' }
  ]

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ 
      ...prev, 
      [key]: value, 
      skip: key === 'skip' ? value : 0 
    }))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-white">Artworks Collection</h2>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Search
            </label>
            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search artworks..."
                className="w-full px-4 py-2 pl-10 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            </div>
          </div>

          {/* Type Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Artwork Type
            </label>
            <select
              value={filters.type_id}
              onChange={(e) => handleFilterChange('type_id', e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {artworkTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Romanian Heritage Filter */}
          {/* <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Romanian Heritage
            </label>
            <select
              value={filters.romanian_heritage === null ? '' : filters.romanian_heritage}
              onChange={(e) => {
                const value = e.target.value === '' ? null : e.target.value === 'true'
                handleFilterChange('romanian_heritage', value)
              }}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Artworks</option>
              <option value="true">Romanian Heritage Only</option>
              <option value="false">Non-Romanian Heritage</option>
            </select>
          </div> */}
        </div>
      </div>

      {/* Artworks Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
          <p className="text-gray-400 mt-4">Loading artworks...</p>
        </div>
      ) : error ? (
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 text-center">
          <p className="text-red-400">Error loading artworks: {error.message}</p>
        </div>
      ) : data && data.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.map((artwork) => (
              <Link
                key={artwork.uri}
                to={`/artworks/${artwork.uri.split('/').pop()}`}
                className="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700 hover:border-indigo-500 transition group"
                vocab="http://schema.org/"
                typeof="VisualArtwork"
                about={artwork.uri}
              >
                {/* Image placeholder */}
                {artwork.imageURL ? (
                  <img src={artwork.imageURL} alt={artwork.title} className="w-full h-48 object-cover" property="image" />
                ) : (
                  <div className="h-48 bg-gray-700 flex items-center justify-center">
                    <span className="text-6xl">🎨</span>
                  </div>
                )}
                
                

                {/* Content */}
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition" property="name">
                    {artwork.title}
                  </h3>
                  {artwork.title_ro && (
                    <p className="text-sm text-gray-400 mt-1" property="alternateName" lang="ro">{artwork.title_ro}</p>
                  )}
                  
                  <div className="mt-3 space-y-2 text-sm text-gray-400">
                    {artwork.artist && (
                      <p property="creator" typeof={artwork.artist.type === 'Organization' ? 'Organization' : 'Person'}>Artist: <span property="name">{artwork.artist.name}</span></p>
                    )}
                    {artwork.creation_date && (
                      <p>Created: <span property="dateCreated">{artwork.creation_date}</span></p>
                    )}
                    {artwork.artwork_type && (
                      <span className="inline-block px-2 py-1 bg-gray-700 rounded text-xs" property="artform">
                        {artwork.artwork_type}
                      </span>
                    )}
                    {artwork.romanian_heritage && (
                      <span className="inline-block px-2 py-1 bg-indigo-600 rounded text-xs ml-2">
                        Romanian Heritage
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex justify-center space-x-4 mt-8">
            <button
              onClick={() => handleFilterChange('skip', Math.max(0, filters.skip - filters.limit))}
              disabled={filters.skip === 0}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Previous
            </button>
            <button
              onClick={() => handleFilterChange('skip', filters.skip + filters.limit)}
              disabled={!data || data.length < filters.limit}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Next
            </button>
          </div>
        </>
      ) : (
        <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
          <p className="text-gray-400 text-lg">No artworks found</p>
          <p className="text-gray-500 mt-2">Try adjusting your filters</p>
        </div>
      )}
    </div>
  )
}

export default ArtworksPage
