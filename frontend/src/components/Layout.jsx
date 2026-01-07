import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  HomeIcon, 
  RectangleStackIcon, 
  ChartBarIcon, 
  CommandLineIcon,
  MapIcon 
} from '@heroicons/react/24/outline'

const Layout = ({ children }) => {
  const location = useLocation()

  const navigation = [
    { name: 'Home', href: '/', icon: HomeIcon },
    { name: 'Artworks', href: '/artworks', icon: RectangleStackIcon },
    { name: 'Visualizations', href: '/visualization', icon: ChartBarIcon },
    { name: 'SPARQL Query', href: '/sparql', icon: CommandLineIcon },
    { name: 'Romanian Heritage', href: '/romanian-heritage', icon: MapIcon },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-white">
                Heritage Provenance System
              </h1>
            </div>
            <div className="text-sm text-gray-400">
              Artwork Provenance Management
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors
                    ${isActive(item.href)
                      ? 'border-indigo-500 text-white'
                      : 'border-transparent text-gray-300 hover:text-white hover:border-gray-500'
                    }
                  `}
                >
                  <Icon className="h-5 w-5 mr-2" />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-400 text-sm">
            <p>Integrated with DBpedia, Wikidata, Getty Vocabularies, Europeana & Romanian Heritage</p>
            <p className="mt-2">© 2026 Heritage Provenance System</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout
