import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { executeSPARQL, getSPARQLExamples } from '../api'

const SPARQLPage = () => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [isExecuting, setIsExecuting] = useState(false)
  const [error, setError] = useState(null)


  const executeQuery = async () => {
    setIsExecuting(true)
    setError(null)
    try {
      const response = await executeSPARQL({ query})
      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-white">SPARQL Query Interface</h2>
        <a
          href="https://www.w3.org/TR/sparql11-query/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-indigo-400 hover:text-indigo-300 text-sm"
        >
          SPARQL Documentation →
        </a>
      </div>

        {/* Query Editor */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              SPARQL Query
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your SPARQL query here..."
              rows={12}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <div className="mt-4 flex space-x-3">
              <button
                onClick={executeQuery}
                disabled={!query || isExecuting}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium"
              >
                {isExecuting ? 'Executing...' : 'Execute Query'}
              </button>
              <button
                onClick={() => { setQuery(''); setResults(null); setError(null); }}
                className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Results */}
          {error && (
            <div className="bg-red-900/20 border border-red-500 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-red-400 mb-2">Error</h3>
              <pre className="text-red-300 text-sm overflow-x-auto">{error}</pre>
            </div>
          )}

          {results && (
            <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-white">Results</h3>
                <div className="text-sm text-gray-400">
                  {results.result_count} results in {results.query_time_ms.toFixed(2)}ms
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                  <thead>
                    <tr>
                      {results.results?.bindings?.[0] && Object.keys(results.results.bindings[0]).map(key => (
                        <th key={key} className="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {results.results?.bindings?.map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-700/50">
                        {Object.values(row).map((cell, cellIdx) => (
                          <td key={cellIdx} className="px-4 py-2 text-sm text-gray-300">
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
      </div>
    </div>
  )
}

export default SPARQLPage
