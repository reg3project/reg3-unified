import React, { useState } from 'react';

const FeedbackLoopDiagram = () => {
  const [activeStep, setActiveStep] = useState(null);
  
  const steps = [
    { id: 1, label: 'Push IDML', desc: 'Upload catalog files to GitHub', icon: '📤' },
    { id: 2, label: 'Extract', desc: 'Claude parses IDML → XLSX', icon: '⚙️' },
    { id: 3, label: 'Compare', desc: 'Check vs reference files', icon: '🔍' },
    { id: 4, label: 'Report', desc: 'Generate accuracy metrics', icon: '📊' },
    { id: 5, label: 'Review', desc: 'Human checks errors', icon: '👁️' },
    { id: 6, label: 'Correct', desc: 'Fix rules or references', icon: '✏️' },
  ];

  const Arrow = ({ rotate = 0 }) => (
    <div className="flex items-center justify-center" style={{ transform: `rotate(${rotate}deg)` }}>
      <svg width="40" height="20" viewBox="0 0 40 20" className="text-blue-400">
        <path d="M0 10 L30 10 M25 5 L30 10 L25 15" fill="none" stroke="currentColor" strokeWidth="2"/>
      </svg>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold text-center mb-2">REG3 Unified Pipeline</h1>
      <p className="text-gray-400 text-center mb-8">Positive Learning Feedback Loop</p>
      
      {/* Main circular diagram */}
      <div className="relative w-full max-w-4xl mx-auto aspect-square">
        {/* Center hub */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center z-10 shadow-lg shadow-blue-500/30">
          <div className="text-center">
            <div className="text-2xl">📚</div>
            <div className="text-xs font-medium mt-1">Knowledge</div>
            <div className="text-xs text-blue-200">Base</div>
          </div>
        </div>
        
        {/* Steps in circular layout */}
        {steps.map((step, index) => {
          const angle = (index * 60 - 90) * (Math.PI / 180);
          const radius = 42; // percentage from center
          const x = 50 + radius * Math.cos(angle);
          const y = 50 + radius * Math.sin(angle);
          
          return (
            <div
              key={step.id}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-transform hover:scale-110"
              style={{ left: `${x}%`, top: `${y}%` }}
              onMouseEnter={() => setActiveStep(step.id)}
              onMouseLeave={() => setActiveStep(null)}
            >
              <div className={`w-24 h-24 rounded-xl flex flex-col items-center justify-center shadow-lg transition-colors ${
                activeStep === step.id 
                  ? 'bg-blue-600 shadow-blue-500/50' 
                  : index < 4 
                    ? 'bg-gray-700 hover:bg-gray-600' 
                    : 'bg-green-700 hover:bg-green-600'
              }`}>
                <span className="text-2xl">{step.icon}</span>
                <span className="text-xs font-medium mt-1">{step.label}</span>
              </div>
              {activeStep === step.id && (
                <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 bg-gray-800 px-3 py-2 rounded text-xs whitespace-nowrap z-20">
                  {step.desc}
                </div>
              )}
            </div>
          );
        })}
        
        {/* Circular arrow path */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="36"
            fill="none"
            stroke="rgba(59, 130, 246, 0.3)"
            strokeWidth="0.5"
            strokeDasharray="3 2"
          />
          {/* Arrow markers */}
          <defs>
            <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="rgba(59, 130, 246, 0.6)" />
            </marker>
          </defs>
        </svg>
      </div>
      
      {/* Legend */}
      <div className="flex justify-center gap-8 mt-8">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-700 rounded"></div>
          <span className="text-sm text-gray-400">Claude (Automated)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-700 rounded"></div>
          <span className="text-sm text-gray-400">Human (Review)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gradient-to-br from-blue-600 to-purple-600 rounded"></div>
          <span className="text-sm text-gray-400">Shared Knowledge</span>
        </div>
      </div>
      
      {/* Metrics panel */}
      <div className="max-w-2xl mx-auto mt-12 bg-gray-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">Expected Improvement Trajectory</h2>
        <div className="grid grid-cols-4 gap-4 text-center">
          <div className="bg-gray-700 p-4 rounded-lg">
            <div className="text-2xl font-bold text-red-400">85.8%</div>
            <div className="text-xs text-gray-400 mt-1">Cycle 1</div>
            <div className="text-xs text-gray-500">Initial</div>
          </div>
          <div className="bg-gray-700 p-4 rounded-lg">
            <div className="text-2xl font-bold text-yellow-400">92%</div>
            <div className="text-xs text-gray-400 mt-1">Cycle 2</div>
            <div className="text-xs text-gray-500">+6.2%</div>
          </div>
          <div className="bg-gray-700 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-400">97%</div>
            <div className="text-xs text-gray-400 mt-1">Cycle 3</div>
            <div className="text-xs text-gray-500">+5%</div>
          </div>
          <div className="bg-gray-700 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-400">99%+</div>
            <div className="text-xs text-gray-400 mt-1">Target</div>
            <div className="text-xs text-gray-500">Production</div>
          </div>
        </div>
      </div>
      
      {/* Workflow steps */}
      <div className="max-w-3xl mx-auto mt-12">
        <h2 className="text-lg font-semibold mb-4">Workflow Commands</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-blue-400 mb-2">Your Side (Local)</h3>
            <pre className="text-xs text-gray-300 font-mono bg-gray-900 p-3 rounded overflow-x-auto">
{`# Add files
cp *.idml input/idml/learning/
cp *.xlsx input/xlsx/learning/

# Push to GitHub
git add . && git commit -m "Add files"
git push

# Get results
git pull
open reports/summary.html`}
            </pre>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-purple-400 mb-2">Claude's Side (Cloud)</h3>
            <pre className="text-xs text-gray-300 font-mono bg-gray-900 p-3 rounded overflow-x-auto">
{`# Automated processing
./scripts/run_all.sh

# Or step by step
python src/import/main.py
python src/check/main.py
python src/check/reporter.py

# Commit results
git add output/ reports/
git commit && git push`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeedbackLoopDiagram;
