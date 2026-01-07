import React from 'react'
import { useQuery } from '@tanstack/react-query'
import Plot from 'react-plotly.js'
import { 
  getOverviewStats, 
  getArtworksByType, 
  getArtworksByCentury,
  getTopArtists,
  getTopLocations
} from '../api'

const VisualizationPage = () => {
  const { data: stats } = useQuery({
    queryKey: ['overviewStats'],
    queryFn: () => getOverviewStats().then(res => res.data)
  })

  const { data: typeData } = useQuery({
    queryKey: ['artworksByType'],
    queryFn: () => getArtworksByType().then(res => res.data)
  })

  const { data: centuryData } = useQuery({
    queryKey: ['artworksByCentury'],
    queryFn: () => getArtworksByCentury().then(res => res.data)
  })

  const { data: artistsData } = useQuery({
    queryKey: ['topArtists'],
    queryFn: () => getTopArtists(10).then(res => res.data)
  })

  return (
    <div className="space-y-8">
      <h2 className="text-3xl font-bold text-white">Data Visualizations</h2>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {stats && [
          { label: 'Artworks', value: stats.total_artworks, color: 'bg-blue-500' },
          { label: 'Artists', value: stats.total_artists, color: 'bg-green-500' },
          { label: 'Locations', value: stats.total_locations, color: 'bg-purple-500' },
          { label: 'Events', value: stats.total_events, color: 'bg-orange-500' }
        ].map(stat => (
          <div key={stat.label} className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
            <p className="text-gray-400 text-sm">{stat.label}</p>
            <p className="text-3xl font-bold text-white mt-2">{stat.value.toLocaleString()}</p>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Artworks by Type */}
        {typeData && typeData.data && typeData.data.length > 0 && (
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4">{typeData.title}</h3>
            <Plot
              data={[{
                type: 'pie',
                labels: typeData.data.map(d => d.type),
                values: typeData.data.map(d => d.count),
                marker: {
                  colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
                }
              }]}
              layout={{
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { color: '#E5E7EB' },
                showlegend: true,
                height: 350
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </div>
        )}

        {/* Artworks by Century */}
        {centuryData && centuryData.data && centuryData.data.length > 0 && (
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4">{centuryData.title}</h3>
            <Plot
              data={[{
                type: 'bar',
                x: centuryData.data.map(d => d.century),
                y: centuryData.data.map(d => d.count),
                marker: { color: '#6366F1' }
              }]}
              layout={{
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { color: '#E5E7EB' },
                xaxis: { gridcolor: '#374151' },
                yaxis: { gridcolor: '#374151' },
                height: 350
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </div>
        )}

        {/* Top Artists */}
        {artistsData && artistsData.data && artistsData.data.length > 0 && (
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700 lg:col-span-2">
            <h3 className="text-xl font-semibold text-white mb-4">{artistsData.title}</h3>
            <Plot
              data={[{
                type: 'bar',
                y: artistsData.data.map(d => d.name),
                x: artistsData.data.map(d => d.artwork_count),
                orientation: 'h',
                marker: { color: '#10B981' }
              }]}
              layout={{
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { color: '#E5E7EB' },
                xaxis: { gridcolor: '#374151', title: 'Number of Artworks' },
                yaxis: { gridcolor: '#374151' },
                height: 400,
                margin: { l: 150 }
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </div>
        )}
      </div>

      {/* Placeholder for Network and Map */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold text-white mb-4">Provenance Network</h3>
          <div className="h-64 flex items-center justify-center text-gray-500">
            Network visualization (select an artwork to view)
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold text-white mb-4">Geographic Distribution</h3>
          <div className="h-64 flex items-center justify-center text-gray-500">
            Map visualization (implementation in progress)
          </div>
        </div>
      </div>
    </div>
  )
}

export default VisualizationPage
