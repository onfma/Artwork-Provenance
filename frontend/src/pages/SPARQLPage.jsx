import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { executeSPARQL, getSPARQLExamples } from '../api'

const SPARQLPage = () => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [isExecuting, setIsExecuting] = useState(false)
  const [error, setError] = useState(null)

  const { data: examples } = useQuery({
    queryKey: ['sparqlExamples'],
    queryFn: () => getSPARQLExamples().then(res => res.data)
  })

  const executeQuery = async () => {
    setIsExecuting(true)
    setError(null)
    try {
      const response = await executeSPARQL({ query, output_format: 'json' })
      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setIsExecuting(false)
    }
  }

  const loadExample = (exampleQuery) => {
    setQuery(exampleQuery.trim())
    setResults(null)
    setError(null)
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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

        {/* Examples Sidebar */}
        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Example Queries</h3>
            {examples?.examples && (
              <div className="space-y-2">
                {Object.entries(examples.examples).map(([key, exampleQuery]) => (
                  <button
                    key={key}
                    onClick={() => loadExample(exampleQuery)}
                    className="w-full text-left px-3 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 hover:text-white transition text-sm"
                  >
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-3">Federated Queries</h3>
            <p className="text-sm text-gray-400 mb-3">
              Query external endpoints:
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex items-center space-x-2">
                <span className="text-indigo-400">•</span>
                <span className="text-gray-300">DBpedia</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-indigo-400">•</span>
                <span className="text-gray-300">Wikidata</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-indigo-400">•</span>
                <span className="text-gray-300">Getty Vocabularies</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SPARQLPage
