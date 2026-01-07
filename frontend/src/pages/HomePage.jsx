import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getOverviewStats, getArtworksByType } from '../api'
import { 
  RectangleStackIcon, 
  UserGroupIcon, 
  MapPinIcon, 
  ClockIcon 
} from '@heroicons/react/24/outline'

const HomePage = () => {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['overviewStats'],
    queryFn: () => getOverviewStats().then(res => res.data)
  })

  const { data: typeDistribution } = useQuery({
    queryKey: ['artworksByType'],
    queryFn: () => getArtworksByType().then(res => res.data)
  })

  const statCards = [
    {
      name: 'Total Artworks',
      value: stats?.total_artworks || 0,
      icon: RectangleStackIcon,
      color: 'bg-blue-500'
    },
    {
      name: 'Artists',
      value: stats?.total_artists || 0,
      icon: UserGroupIcon,
      color: 'bg-green-500'
    },
    {
      name: 'Locations',
      value: stats?.total_locations || 0,
      icon: MapPinIcon,
      color: 'bg-purple-500'
    },
    {
      name: 'Provenance Events',
      value: stats?.total_events || 0,
      icon: ClockIcon,
      color: 'bg-orange-500'
    }
  ]

  const features = [
    {
      title: 'Browse Artworks',
      description: 'Explore our collection of artworks with detailed provenance information',
      link: '/artworks',
      icon: '🎨'
    },
    {
      title: 'SPARQL Queries',
      description: 'Run custom SPARQL queries against our RDF knowledge base',
      link: '/sparql',
      icon: '🔍'
    },
    {
      title: 'Visualizations',
      description: 'Interactive charts, networks, and maps of artwork data',
      link: '/visualization',
      icon: '📊'
    },
    {
      title: 'Romanian Heritage',
      description: 'Discover Romanian cultural heritage and artworks',
      link: '/romanian-heritage',
      icon: '🏛️'
    }
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg shadow-xl p-8 text-white">
        <h2 className="text-4xl font-bold mb-4">
          Heritage Provenance System
        </h2>
        <p className="text-xl opacity-90 max-w-3xl">
          A comprehensive platform for modeling and managing artwork provenance with 
          integration to DBpedia, Wikidata, Getty vocabularies, Europeana, and Romanian heritage.
        </p>
        <div className="mt-6 flex space-x-4">
          <Link
            to="/artworks"
            className="px-6 py-3 bg-white text-indigo-600 rounded-lg font-semibold hover:bg-gray-100 transition"
          >
            Browse Artworks
          </Link>
          <Link
            to="/sparql"
            className="px-6 py-3 bg-indigo-700 text-white rounded-lg font-semibold hover:bg-indigo-800 transition border border-white/20"
          >
            Try SPARQL
          </Link>
        </div>
      </div>

      {/* Statistics */}
      <div>
        <h3 className="text-2xl font-bold text-white mb-4">Collection Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat) => {
            const Icon = stat.icon
            return (
              <div
                key={stat.name}
                className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm font-medium">{stat.name}</p>
                    <p className="text-3xl font-bold text-white mt-2">
                      {statsLoading ? '...' : stat.value.toLocaleString()}
                    </p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="h-8 w-8 text-white" />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Features */}
      <div>
        <h3 className="text-2xl font-bold text-white mb-4">Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature) => (
            <Link
              key={feature.title}
              to={feature.link}
              className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700 hover:border-indigo-500 transition group"
            >
              <div className="flex items-start space-x-4">
                <div className="text-4xl">{feature.icon}</div>
                <div>
                  <h4 className="text-xl font-semibold text-white group-hover:text-indigo-400 transition">
                    {feature.title}
                  </h4>
                  <p className="text-gray-400 mt-2">{feature.description}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Integrations */}
      <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
        <h3 className="text-2xl font-bold text-white mb-4">External Integrations</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {['DBpedia', 'Wikidata', 'Getty AAT', 'Getty ULAN', 'Europeana'].map((integration) => (
            <div
              key={integration}
              className="bg-gray-700 rounded-lg p-4 text-center"
            >
              <p className="text-white font-medium">{integration}</p>
            </div>
          ))}
        </div>
        <p className="text-gray-400 mt-4">
          Access rich linked data from multiple authoritative sources to enrich artwork provenance records.
        </p>
      </div>

      {/* About */}
      <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
        <h3 className="text-2xl font-bold text-white mb-4">About</h3>
        <div className="text-gray-300 space-y-3">
          <p>
            The Heritage Provenance System provides a comprehensive platform for managing the 
            complete lifecycle and ownership history of artistic works. Built on semantic web 
            technologies and CIDOC-CRM ontology, it enables:
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Complete provenance chain tracking with events, agents, and locations</li>
            <li>Integration with major linked data sources (DBpedia, Wikidata, Getty)</li>
            <li>SPARQL endpoint for advanced querying and federated queries</li>
            <li>Interactive visualizations including network graphs and maps</li>
            <li>Recommendation engine for discovering similar artworks</li>
            <li>Special focus on Romanian cultural heritage</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default HomePage
