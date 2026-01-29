import React from 'react';

function TabView({ activeTab, onTabChange, tabs }) {
  return (
    <div className="border-b border-white/20 mb-6">
      <div className="flex space-x-2 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-6 py-3 rounded-t-lg font-semibold transition-all whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-white/20 text-white border-b-2 border-purple-500'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default TabView;