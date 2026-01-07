import React from 'react'

const RomanianHeritagePage = () => {
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-yellow-600 rounded-lg shadow-xl p-8 text-white">
        <h2 className="text-4xl font-bold mb-4">🇷🇴 Romanian Heritage</h2>
        <p className="text-xl opacity-90">
          Explore Romanian cultural heritage and artworks
        </p>
      </div>

      <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
        <h3 className="text-2xl font-semibold text-white mb-4">Featured Collections</h3>
        <p className="text-gray-400">Romanian heritage integration implementation in progress</p>
        
        <div className="mt-6 space-y-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-lg font-semibold text-white">Muzeul Național de Artă al României (MNAR)</h4>
            <p className="text-gray-400 mt-2">National Museum of Art of Romania</p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-lg font-semibold text-white">Muzeul Național de Artă Contemporană (MNAC)</h4>
            <p className="text-gray-400 mt-2">National Museum of Contemporary Art</p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-lg font-semibold text-white">Institutul Național al Patrimoniului (INP)</h4>
            <p className="text-gray-400 mt-2">National Heritage Institute</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RomanianHeritagePage
