import React, { useState } from 'react';
import TabView from './TabView';
import Chatbot from './Chatbot';

function ResultsDisplay({ results, onReset }) {
  const [activeTab, setActiveTab] = useState('explanation');
  const [copiedSection, setCopiedSection] = useState(null);

  const tabs = [
    { id: 'explanation', label: 'Overview', icon: '📖' },
    { id: 'resume', label: 'Resume', icon: '📄' },
    { id: 'viva', label: 'Viva', icon: '🎓' },
    { id: 'interview', label: 'Interview', icon: '💼' },
    { id: 'chat', label: 'Chat', icon: '💬' },
  ];

  const copyToClipboard = (text, section) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const downloadAsText = () => {
    const content = generateTextContent();
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${results.repo_owner}-${results.repo_name}-analysis.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadAsDocx = async () => {
    try {
      const response = await fetch('https://github-analyzer-ciky.onrender.com/api/export-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(results),
      });
      
      if (!response.ok) throw new Error('Export failed');
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${results.repo_owner}-${results.repo_name}-analysis.docx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert('Failed to export as DOCX');
    }
  };

  const downloadAsPdf = async () => {
    try {
      const response = await fetch('https://github-analyzer-ciky.onrender.com/api/export-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(results),
      });
      
      if (!response.ok) throw new Error('Export failed');
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${results.repo_owner}-${results.repo_name}-analysis.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert('Failed to export as PDF');
    }
  };

  const generateTextContent = () => {
    let content = `GitHub Repository Analysis\n`;
    content += `Repository: ${results.repo_owner}/${results.repo_name}\n`;
    content += `${'='.repeat(60)}\n\n`;

    // Explanation
    content += `PROJECT OVERVIEW\n${'='.repeat(60)}\n`;
    content += `${results.explanation.overview}\n\n`;
    content += `Key Features:\n`;
    results.explanation.key_features.forEach((f, i) => {
      content += `${i + 1}. ${f}\n`;
    });
    content += `\nTech Stack: ${results.explanation.tech_stack.join(', ')}\n\n`;
    content += `Architecture:\n${results.explanation.architecture}\n\n`;
    content += `Challenges Solved:\n`;
    results.explanation.challenges_solved.forEach((c, i) => {
      content += `${i + 1}. ${c}\n`;
    });
    content += `\nImpact: ${results.explanation.impact}\n\n`;

    // Resume
    content += `\nRESUME BULLET POINTS\n${'='.repeat(60)}\n`;
    results.resume_bullets.forEach((b, i) => {
      content += `• ${b.point}\n`;
    });

    // Viva
    content += `\n\nVIVA QUESTIONS\n${'='.repeat(60)}\n`;
    results.viva_questions.forEach((q, i) => {
      content += `\nQ${i + 1} [${q.difficulty.toUpperCase()}]: ${q.question}\n`;
      content += `A: ${q.answer}\n`;
    });

    // Interview
    content += `\n\nINTERVIEW Q&A\n${'='.repeat(60)}\n`;
    results.interview_qa.forEach((qa, i) => {
      content += `\nQ${i + 1} [${qa.category.toUpperCase()}]: ${qa.question}\n`;
      content += `A: ${qa.answer}\n`;
    });

    return content;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-6 border border-white/20">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">
              {results.repo_owner}/{results.repo_name}
            </h2>
            <p className="text-gray-300">Analysis Complete ✅</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <div className="flex gap-2">
              <button
                onClick={downloadAsText}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/30 text-white rounded-lg transition-all flex items-center gap-2 backdrop-blur-sm"
                title="Download as Text"
              >
                <span className="text-lg">📄</span>
                <span className="text-sm font-medium">Text</span>
              </button>
              <button
                onClick={downloadAsDocx}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/30 text-white rounded-lg transition-all flex items-center gap-2 backdrop-blur-sm"
                title="Download as Word Document"
              >
                <span className="text-lg">📘</span>
                <span className="text-sm font-medium">Word</span>
              </button>
              <button
                onClick={downloadAsPdf}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/30 text-white rounded-lg transition-all flex items-center gap-2 backdrop-blur-sm"
                title="Download as PDF"
              >
                <span className="text-lg">📕</span>
                <span className="text-sm font-medium">PDF</span>
              </button>
            </div>
            <button
              onClick={onReset}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all flex items-center gap-2"
            >
              🔄 New Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Tabs and Content */}
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-6 border border-white/20">
        <TabView activeTab={activeTab} onTabChange={setActiveTab} tabs={tabs} />

        {/* Explanation Tab */}
        {activeTab === 'explanation' && (
          <div className="space-y-6">
            <Section title="📝 Overview">
              <p className="text-gray-300 leading-relaxed">{results.explanation.overview}</p>
            </Section>

            <Section title="✨ Key Features">
              <ul className="space-y-2">
                {results.explanation.key_features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-purple-400 mr-2">▸</span>
                    <span className="text-gray-300">{feature}</span>
                  </li>
                ))}
              </ul>
            </Section>

            <Section title="🛠️ Tech Stack">
              <div className="flex flex-wrap gap-2">
                {results.explanation.tech_stack.map((tech, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-purple-600/30 text-purple-200 rounded-full text-sm"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </Section>

            <Section title="🏗️ Architecture">
              <p className="text-gray-300 leading-relaxed">{results.explanation.architecture}</p>
            </Section>

            <Section title="💡 Challenges Solved">
              <ul className="space-y-2">
                {results.explanation.challenges_solved.map((challenge, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-blue-400 mr-2">✓</span>
                    <span className="text-gray-300">{challenge}</span>
                  </li>
                ))}
              </ul>
            </Section>

            <Section title="🎯 Impact">
              <p className="text-gray-300 leading-relaxed">{results.explanation.impact}</p>
            </Section>
          </div>
        )}

        {/* Resume Tab */}
        {activeTab === 'resume' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold text-white">Resume Bullet Points</h3>
              <button
                onClick={() =>
                  copyToClipboard(
                    results.resume_bullets.map((b) => `• ${b.point}`).join('\n'),
                    'resume'
                  )
                }
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors text-sm"
              >
                {copiedSection === 'resume' ? '✓ Copied!' : '📋 Copy All'}
              </button>
            </div>
            <div className="space-y-3">
              {results.resume_bullets.map((bullet, index) => (
                <div
                  key={index}
                  className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <span className="text-purple-400 font-bold mr-2">•</span>
                      <span className="text-gray-200">{bullet.point}</span>
                    </div>
                    <button
                      onClick={() => copyToClipboard(bullet.point, `resume-${index}`)}
                      className="ml-4 text-gray-400 hover:text-white transition-colors"
                    >
                      {copiedSection === `resume-${index}` ? '✓' : '📋'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Viva Tab */}
        {activeTab === 'viva' && (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-white mb-4">Viva Questions</h3>
            <div className="space-y-4">
              {results.viva_questions.map((viva, index) => (
                <div
                  key={index}
                  className="bg-white/5 border border-white/10 rounded-lg p-5 hover:bg-white/10 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm font-semibold text-purple-400">
                          Q{index + 1}
                        </span>
                        <span
                          className={`px-2 py-1 rounded text-xs font-semibold ${
                            viva.difficulty === 'easy'
                              ? 'bg-green-600/30 text-green-300'
                              : viva.difficulty === 'medium'
                              ? 'bg-yellow-600/30 text-yellow-300'
                              : 'bg-red-600/30 text-red-300'
                          }`}
                        >
                          {viva.difficulty.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-white font-medium mb-3">{viva.question}</p>
                      <p className="text-gray-300 text-sm leading-relaxed">{viva.answer}</p>
                    </div>
                    <button
                      onClick={() =>
                        copyToClipboard(`Q: ${viva.question}\nA: ${viva.answer}`, `viva-${index}`)
                      }
                      className="ml-4 text-gray-400 hover:text-white transition-colors"
                    >
                      {copiedSection === `viva-${index}` ? '✓' : '📋'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Interview Tab */}
        {activeTab === 'interview' && (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-white mb-4">Interview Q&A</h3>
            <div className="space-y-4">
              {results.interview_qa.map((qa, index) => (
                <div
                  key={index}
                  className="bg-white/5 border border-white/10 rounded-lg p-5 hover:bg-white/10 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm font-semibold text-blue-400">Q{index + 1}</span>
                        <span className="px-2 py-1 bg-blue-600/30 text-blue-300 rounded text-xs font-semibold">
                          {qa.category.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-white font-medium mb-3">{qa.question}</p>
                      <p className="text-gray-300 text-sm leading-relaxed">{qa.answer}</p>
                    </div>
                    <button
                      onClick={() =>
                        copyToClipboard(`Q: ${qa.question}\nA: ${qa.answer}`, `interview-${index}`)
                      }
                      className="ml-4 text-gray-400 hover:text-white transition-colors"
                    >
                      {copiedSection === `interview-${index}` ? '✓' : '📋'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <Chatbot results={results} />
        )}
      </div>
    </div>
  );
}

// Helper Section Component
function Section({ title, children }) {
  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-white border-b border-white/20 pb-2">{title}</h3>
      {children}
    </div>
  );
}

export default ResultsDisplay;