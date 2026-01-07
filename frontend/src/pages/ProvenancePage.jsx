import React from 'react'
import { useParams } from 'react-router-dom'

const ProvenancePage = () => {
  const { id } = useParams()

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Provenance Chain</h2>
      <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
        <p className="text-gray-400">Provenance for artwork {id}</p>
        <p className="text-gray-500 mt-2">Timeline visualization implementation in progress</p>
      </div>
    </div>
  )
}

export default ProvenancePage
