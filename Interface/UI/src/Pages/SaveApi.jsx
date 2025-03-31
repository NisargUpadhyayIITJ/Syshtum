import { useState } from 'react'
import { ChevronDown } from 'lucide-react';
import { SaveApiKey } from '../../server/server.js';
import { useNavigate } from 'react-router-dom';

function SaveApi() {
    const [selectedModel, setSelectedModel] = useState('GPT-4o')
    const [command, setCommand] = useState('')
    const [isDropdownOpen, setIsDropdownOpen] = useState(false)
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    
    const navigate = useNavigate() // Missing navigate initialization
    const models = ['GPT-4o', 'Gemini']
  
    const handleExecuteCommand = async () => {
      console.log('Executing command:- ', command);
      
      if (command.trim() === '') {
        setError('API Key cannot be empty')
        return
      }
      
      try {
        setIsLoading(true)
        setError('') // Clear previous errors
        
        const response = await SaveApiKey({ 
          api_key: command, 
          model: selectedModel 
        })
        
        console.log(response)
        setCommand('')
        navigate('/')
      } catch (error) {
        console.error(error)
        setError('Error saving API Key')
      } finally {
        setIsLoading(false)
      }
    }
    
    const handleKeyDown = (e) => {
      if (e.key === 'Enter') {
        handleExecuteCommand()
      }
    }
    
    return (
      <div className="flex flex-col w-full min-h-screen bg-gradient-to-b from-neutral-900 to-neutral-950 text-neutral-200 p-6">
        <div className="flex flex-col items-center justify-center flex-grow max-w-3xl mx-auto w-full">
          <div className="w-full mb-12 text-center">
            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
              Enter your API Key
            </h1>
            {error && (
              <div className="text-red-600 text-xl rounded-lg mt-4">
                {error}
              </div>
            )}
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
                  placeholder="Enter your API key..."
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={isLoading}
                />
              </div>
              
              <button 
                className={`bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium py-4 px-6 rounded-lg 
                transition-all duration-200 flex items-center justify-center ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                onClick={handleExecuteCommand}
                disabled={isLoading}
              >
                {isLoading ? 'Saving...' : 'Save API Key'}
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }
  
export default SaveApi;