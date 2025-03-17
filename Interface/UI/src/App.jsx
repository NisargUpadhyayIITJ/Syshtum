import { useState } from 'react'
import { Mic, Send, ChevronDown } from 'lucide-react';
import { getData } from '../server/server';

function App() {
  const [selectedModel, setSelectedModel] = useState('GPT-4o')
  const [command, setCommand] = useState('')
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [recent, setRecent] = useState([])
  
  const models = ['GPT-4o', 'Gemini']

  const handleExecuteCommand = async () => {
    console.log('Executing command:- ', command);
    
    if (command === '') return
    
    const response = await getData({ 
      prompt: command, 
      model: selectedModel })
    console.log(response)
    
    setRecent([command, ...recent])
    setCommand('')
  }
  
  return (
    <div className="flex flex-col w-full min-h-screen bg-gradient-to-b from-neutral-900 to-neutral-950 text-neutral-200 p-6">
      <div className="flex flex-col items-center justify-center flex-grow max-w-3xl mx-auto w-full">
        <div className="w-full mb-12 text-center">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
            Self Operating Computer
          </h1>
          <p className="text-neutral-400">
            Control your computer with natural language commands
          </p>
        </div>
        
        <div className="w-full bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-lg">
          <div className="relative mb-5">
            <div 
              className="flex items-center justify-between w-full p-3 border border-neutral-700 rounded-lg bg-neutral-800 cursor-pointer"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full mr-3 bg-green-500"></div>
                <span>{selectedModel}</span>
              </div>
              <ChevronDown className="h-5 w-5 text-neutral-400" />
            </div>
            
            {isDropdownOpen && (
              <div className="absolute top-full left-0 mt-1 w-full bg-neutral-800 border border-neutral-700 rounded-lg shadow-xl z-10">
                {models.map((model) => (
                  <div 
                    key={model}
                    className="p-3 hover:bg-neutral-700 cursor-pointer flex items-center"
                    onClick={() => {
                      setSelectedModel(model)
                      setIsDropdownOpen(false)
                    }}
                  >
                    <div className={`w-3 h-3 rounded-full mr-3 ${selectedModel === model ? 'bg-green-500' : 'bg-neutral-600'}`}></div>
                    {model}
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="flex flex-col space-y-4">
            <div className="flex items-center bg-neutral-800 border border-neutral-700 rounded-lg overflow-hidden pl-4">
              <input 
                type="text"
                className="flex-grow bg-transparent py-4 focus:outline-none text-neutral-200 placeholder-neutral-500"
                placeholder="Enter your command..."
                value={command}
                onChange={(e) => setCommand(e.target.value)}
              />
              <button className="p-4 text-neutral-400 hover:text-neutral-200 transition-colors">
                <Mic className="h-5 w-5" />
              </button>
            </div>
            
            <button className="bg-gradient-to-r from-blue-600 to-purple-600 cursor-pointer text-white font-medium py-4 px-6 rounded-lg 
            transition-all duration-200 flex items-center justify-center"
            onClick={handleExecuteCommand}>
              <Send className="h-5 w-5 mr-2" />
              Execute Command
            </button>
          </div>
          
          <div className="mt-6 pt-6 border-t border-neutral-800">
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-500">Recent commands</span>
              <span className="text-xs text-neutral-600 bg-neutral-800 px-2 py-1 rounded">History</span>
            </div>
            <div className="mt-3 text-neutral-400 text-sm">
              {recent.length === 0 && (
                <p>No recent commands</p>
              )}
              {recent.map((command, index) => (
                <div key={index} className="flex items-center justify-between py-2 border-b border-neutral-800">
                  <span>{command}</span>
                  <button className="text-neutral-500 hover:text-neutral-400 transition-colors">Run</button>
                </div>
              ))}
            </div>
          </div>
        </div>
        
      </div>
    </div>
  )
}

export default App