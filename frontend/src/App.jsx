import React, { useState } from 'react';
import InputForm from './components/InputForm';
import ResultsDisplay from './components/ResultsDisplay';
import LoadingSpinner from './components/LoadingSpinner';

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (repoUrl, focus) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('/api/analyze-repo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          focus: focus,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Analysis failed');
      }

      if (data.success) {
        setResults(data.data);
      } else {
        throw new Error(data.message || 'Analysis failed');
      }
    } catch (err) {
      setError(err.message);
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            🚀 GitHub Repository Analyzer
          </h1>
          <p className="text-xl text-gray-300">
            AI-Powered Interview & Resume Preparation Tool
          </p>
          <p className="text-sm text-gray-400 mt-2">
            Analyze any GitHub repository to generate interview questions, resume bullets, and more
          </p>
        </header>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          {!results && !loading && (
            <InputForm onAnalyze={handleAnalyze} />
          )}

          {loading && <LoadingSpinner />}

          {error && (
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-6 mb-8">
              <h3 className="text-red-400 font-semibold text-lg mb-2">
                ⚠️ Error
              </h3>
              <p className="text-red-300">{error}</p>
              <button
                onClick={handleReset}
                className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {results && (
            <ResultsDisplay results={results} onReset={handleReset} />
          )}
        </div>

        {/* Footer */}
        <footer className="text-center mt-16 text-gray-400 text-sm">
          <p>Powered by Groq AI & GitHub API</p>
          <p className="mt-2">Built with FastAPI + React</p>
        </footer>
      </div>
    </div>
  );
}

export default App;