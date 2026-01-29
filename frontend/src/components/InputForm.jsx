import React, { useState } from 'react';

function InputForm({ onAnalyze }) {
  const [repoUrl, setRepoUrl] = useState('');
  const [focus, setFocus] = useState('all');
  const [isValidUrl, setIsValidUrl] = useState(true);

  const validateGitHubUrl = (url) => {
    const pattern = /^https?:\/\/github\.com\/[\w\-\.]+\/[\w\-\.]+\/?$/;
    return pattern.test(url.trim());
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const trimmedUrl = repoUrl.trim();
    
    if (!validateGitHubUrl(trimmedUrl)) {
      setIsValidUrl(false);
      return;
    }

    setIsValidUrl(true);
    onAnalyze(trimmedUrl, focus);
  };

  const handleUrlChange = (e) => {
    setRepoUrl(e.target.value);
    setIsValidUrl(true);
  };

  const exampleRepos = [
    'https://github.com/openai/whisper',
    'https://github.com/vercel/next.js',
    'https://github.com/facebook/react',
  ];

  const handleExampleClick = (url) => {
    setRepoUrl(url);
    setIsValidUrl(true);
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Repository URL Input */}
        <div>
          <label className="block text-white font-semibold mb-3 text-lg">
            📦 GitHub Repository URL
          </label>
          <input
            type="text"
            value={repoUrl}
            onChange={handleUrlChange}
            placeholder="https://github.com/username/repository"
            className={`w-full px-4 py-3 rounded-lg bg-white/10 border ${
              isValidUrl ? 'border-white/30' : 'border-red-500'
            } text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all`}
            required
          />
          {!isValidUrl && (
            <p className="text-red-400 text-sm mt-2">
              Please enter a valid GitHub repository URL
            </p>
          )}
          
          {/* Example repositories */}
          <div className="mt-3">
            <p className="text-gray-400 text-sm mb-2">Try these examples:</p>
            <div className="flex flex-wrap gap-2">
              {exampleRepos.map((url, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleExampleClick(url)}
                  className="px-3 py-1 bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 text-sm rounded-full transition-colors"
                >
                  {url.split('/').slice(-2).join('/')}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Focus Selection */}
        <div>
          <label className="block text-white font-semibold mb-3 text-lg">
            🎯 Analysis Focus
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { value: 'all', label: '✨ All', desc: 'Complete analysis' },
              { value: 'resume', label: '📄 Resume', desc: 'Bullet points' },
              { value: 'interview', label: '💼 Interview', desc: 'Q&A prep' },
              { value: 'viva', label: '🎓 Viva', desc: 'Exam questions' },
            ].map((option) => (
              <label
                key={option.value}
                className={`relative cursor-pointer rounded-lg p-4 border-2 transition-all ${
                  focus === option.value
                    ? 'border-purple-500 bg-purple-500/20'
                    : 'border-white/20 bg-white/5 hover:border-white/40'
                }`}
              >
                <input
                  type="radio"
                  name="focus"
                  value={option.value}
                  checked={focus === option.value}
                  onChange={(e) => setFocus(e.target.value)}
                  className="sr-only"
                />
                <div className="text-center">
                  <div className="text-2xl mb-1">{option.label.split(' ')[0]}</div>
                  <div className="text-white font-medium text-sm">
                    {option.label.split(' ').slice(1).join(' ')}
                  </div>
                  <div className="text-gray-400 text-xs mt-1">{option.desc}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold text-lg rounded-lg shadow-lg transform hover:scale-105 transition-all duration-200"
        >
          🔍 Analyze Repository
        </button>
      </form>

      {/* Info Box */}
      <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
        <p className="text-blue-200 text-sm">
          <span className="font-semibold">💡 Tip:</span> Analysis typically takes 30-60 seconds. 
          Make sure the repository is public and has a README file for best results.
        </p>
      </div>
    </div>
  );
}

export default InputForm;