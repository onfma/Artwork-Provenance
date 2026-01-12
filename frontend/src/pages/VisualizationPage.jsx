import { useQuery } from '@tanstack/react-query'
import Plot from 'react-plotly.js'
import { 
  getOverviewStats, 
  getArtworksByType, 
  getTopArtists,
  getTopLocations,
  getArtistNetwork,
  getArtworksByMaterial
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

  const { data: materialData } = useQuery({
    queryKey: ['artworksByMaterial'],
    queryFn: () => getArtworksByMaterial().then(res => res.data)
  })

  const { data: artistsData } = useQuery({
    queryKey: ['topArtists'],
    queryFn: () => getTopArtists(10).then(res => res.data)
  })

  const { data: artistNetworkData } = useQuery({
    queryKey: ['artistNetwork'],
    queryFn: () => getArtistNetwork("5a4d2e7f-4f3e-4574-8774-75db4883e2c1").then(res => res.data)
  })

  const { data: locationsData } = useQuery({
    queryKey: ['topLocations'],
    queryFn: () => getTopLocations(10).then(res => res.data)
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

        {/* Artworks by Material */}
        {materialData && materialData.data && materialData.data.length > 0 && (
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4">{materialData.title}</h3>
            <Plot
              data={[{
                type: 'pie',
                labels: materialData.data.map(d => d.material),
                values: materialData.data.map(d => d.count),
                marker: {
                  colors: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
                }
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

      {/* Artist Network and Locations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Artist Network */}
        {artistNetworkData && artistNetworkData.nodes && artistNetworkData.nodes.length > 0 ? (
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4">Artist Network</h3>
            <Plot
              data={(() => {
                const nodes = artistNetworkData.nodes
                const edges = artistNetworkData.edges || []
                
                const nodeCount = nodes.length
                const positions = {}
                
                const sourceIndex = nodeCount - 1
                positions[nodes[sourceIndex].id] = { x: 0, y: 1 }
                
                const otherNodes = nodes.filter((_, i) => i !== sourceIndex)
                const spacing = otherNodes.length > 1 ? 2 / (otherNodes.length - 1) : 0
                nodes.forEach((node, i) => {
                  if (i !== sourceIndex) {
                    const index = otherNodes.findIndex(n => n.id === node.id)
                    positions[node.id] = {
                      x: -1 + (index * spacing),
                      y: -0.5
                    }
                  }
                })
                
                const edgeTraces = []
                edges.forEach(edge => {
                  const sourceNode = nodes[sourceIndex]
                  const targetNode = nodes.find(n => n.id === edge.target)
                  
                  if (!targetNode) return
                  
                  const sourcePos = positions[sourceNode.id]
                  const targetPos = positions[targetNode.id]
                  
                  edgeTraces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: [sourcePos.x, targetPos.x],
                    y: [sourcePos.y, targetPos.y],
                    line: { 
                      color: '#6366F1', 
                      width: 3 
                    },
                    hoverinfo: 'text',
                    hovertext: `${sourceNode.name} → ${edge.relationship.replace('_', ' ')} → ${targetNode.name}`,
                    showlegend: false
                  })
                  
                  const midX = (sourcePos.x + targetPos.x) / 2
                  const midY = (sourcePos.y + targetPos.y) / 2
                  edgeTraces.push({
                    type: 'scatter',
                    mode: 'text',
                    x: [midX],
                    y: [midY],
                    text: [edge.relationship.replace('_', ' ')],
                    textfont: { 
                      size: 11, 
                      color: '#9CA3AF',
                      family: 'Arial, sans-serif'
                    },
                    hoverinfo: 'skip',
                    showlegend: false
                  })
                })
                
                // Create node trace
                const nodeTrace = {
                  type: 'scatter',
                  mode: 'markers+text',
                  x: nodes.map(n => positions[n.id].x),
                  y: nodes.map(n => positions[n.id].y),
                  text: nodes.map(n => n.name),
                  textposition: 'top center',
                  textfont: {
                    size: nodes.map((_, i) => i === sourceIndex ? 14 : 12),
                    color: '#E5E7EB'
                  },
                  marker: {
                    size: nodes.map((_, i) => i === sourceIndex ? 30 : 20),
                    color: nodes.map((_, i) => i === sourceIndex ? '#10B981' : '#3B82F6'),
                    line: { 
                      color: nodes.map((_, i) => i === sourceIndex ? '#fff' : '#E5E7EB'),
                      width: nodes.map((_, i) => i === sourceIndex ? 3 : 2)
                    }
                  },
                  hoverinfo: 'text',
                  hovertext: nodes.map((n, i) => 
                    i === sourceIndex ? `${n.name} (Source)` : n.name
                  ),
                  showlegend: false
                }
                
                return [...edgeTraces, nodeTrace]
              })()}
              layout={{
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { color: '#E5E7EB' },
                xaxis: { 
                  visible: false,
                  range: [-1.5, 1.5]
                },
                yaxis: { 
                  visible: false,
                  range: [-1.5, 1.5]
                },
                height: 400,
                margin: { t: 40, b: 40, l: 40, r: 40 },
                hovermode: 'closest'
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </div>
        ) : (
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4">Artist Network</h3>
            <div className="h-96 flex items-center justify-center text-gray-500">
              {artistNetworkData?.message || 'Loading artist network...'}
            </div>
          </div>
        )}

        {locationsData && locationsData.data && locationsData.data.length > 0 && (
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700 lg:col-span-2">
            <h3 className="text-xl font-semibold text-white mb-4">{locationsData.title}</h3>
            <Plot
              data={[{
                type: 'bar',
                y: locationsData.data.map(d => d.name),
                x: locationsData.data.map(d => d.artwork_count),
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
    </div>
  )
}

export default VisualizationPage
