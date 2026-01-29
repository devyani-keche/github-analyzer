import React from 'react';

function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="relative">
        {/* Outer spinning circle */}
        <div className="w-24 h-24 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin"></div>
        
        {/* Inner pulsing circle */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="w-12 h-12 bg-purple-500 rounded-full animate-pulse"></div>
        </div>
      </div>

      <div className="mt-8 text-center">
        <h3 className="text-2xl font-bold text-white mb-2">
          Analyzing Repository...
        </h3>
        <p className="text-gray-300 mb-4">
          This may take 30-60 seconds
        </p>
        
        {/* Progress steps */}
        <div className="space-y-2 text-left max-w-md mx-auto">
          {[
            '📦 Fetching repository data from GitHub',
            '🔍 Extracting key files and structure',
            '🤖 Running AI analysis with Groq LLM',
            '✨ Generating interview materials',
          ].map((step, index) => (
            <div
              key={index}
              className="flex items-center space-x-2 text-gray-300 animate-pulse"
              style={{ animationDelay: `${index * 0.2}s` }}
            >
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span className="text-sm">{step}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Decorative elements */}
      <div className="mt-12 flex space-x-3">
        <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce"></div>
        <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-3 h-3 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
    </div>
  );
}

export default LoadingSpinner;