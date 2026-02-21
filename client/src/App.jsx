import { useState, useRef, useEffect } from 'react'

const SourceItem = ({ source }) => (
  <div className="mb-3 pl-3 border-l-2 border-indigo-500/50">
    <div className="font-semibold text-gray-200 text-sm">{source.policyTitle}</div>
    <div className="text-xs text-indigo-400 font-mono mb-1">ID: {source.clauseId}</div>
    <div className="text-sm text-gray-400 italic">"{source.text}"</div>
  </div>
)

const EligibilityModal = ({ isOpen, onClose, onSubmit, loading, results }) => {
  const [formData, setFormData] = useState({
    attendance: '',
    cgpa: '',
    internship_completed: false
  })

  if (!isOpen) return null

  const handleSubmit = () => {
    onSubmit({
      attendance: parseFloat(formData.attendance),
      cgpa: parseFloat(formData.cgpa),
      internship_completed: formData.internship_completed
    })
  }

  const getStatusColor = (status) => {
    if (status === 'yes') return 'bg-green-500/20 text-green-300 border-green-500/50'
    if (status === 'warning') return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50'
    return 'bg-red-500/20 text-red-300 border-red-500/50'
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="p-6 border-b border-gray-800 flex justify-between items-center">
          <h2 className="text-xl font-bold text-white">Check Eligibility</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {!results ? (
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Attendance (%)</label>
              <input 
                type="number" 
                step="0.1"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                value={formData.attendance}
                onChange={e => setFormData({...formData, attendance: e.target.value})}
                placeholder="e.g. 75.5"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">CGPA</label>
              <input 
                type="number" 
                step="0.01"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                value={formData.cgpa}
                onChange={e => setFormData({...formData, cgpa: e.target.value})}
                placeholder="e.g. 8.5"
              />
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg border border-gray-700/50">
              <span className="text-sm font-medium text-gray-300">Internship Completed?</span>
              <button 
                onClick={() => setFormData({...formData, internship_completed: !formData.internship_completed})}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${formData.internship_completed ? 'bg-indigo-600' : 'bg-gray-600'}`}
              >
                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${formData.internship_completed ? 'translate-x-6' : 'translate-x-1'}`} />
              </button>
            </div>
            <button 
              onClick={handleSubmit}
              disabled={loading || !formData.attendance || !formData.cgpa}
              className="w-full mt-4 bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : 'Check Status'}
            </button>
          </div>
        ) : (
          <div className="p-6 space-y-4">
            <div className={`p-4 rounded-xl border ${getStatusColor(results.exam_eligibility.status)}`}>
              <div className="font-bold mb-1 flex justify-between">
                Exam Eligibility
                <span className="uppercase text-xs px-2 py-0.5 rounded bg-black/20">{results.exam_eligibility.status}</span>
              </div>
              <div className="text-sm opacity-90">{results.exam_eligibility.reason}</div>
            </div>

            <div className={`p-4 rounded-xl border ${getStatusColor(results.merit_scholarship.status)}`}>
              <div className="font-bold mb-1 flex justify-between">
                Merit Scholarship
                <span className="uppercase text-xs px-2 py-0.5 rounded bg-black/20">{results.merit_scholarship.status}</span>
              </div>
              <div className="text-sm opacity-90">{results.merit_scholarship.reason}</div>
            </div>

            <div className={`p-4 rounded-xl border ${getStatusColor(results.graduation.status)}`}>
              <div className="font-bold mb-1 flex justify-between">
                Graduation
                <span className="uppercase text-xs px-2 py-0.5 rounded bg-black/20">{results.graduation.status}</span>
              </div>
              <div className="text-sm opacity-90">{results.graduation.reason}</div>
            </div>

            <button 
              onClick={onClose}
              className="w-full mt-4 bg-gray-700 hover:bg-gray-600 text-white font-medium py-2.5 rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

const BotMessage = ({ text, confidence, sources, debug, needs_clarification, clarification_question, clarification_options, onOptionClick }) => {
  const [showSources, setShowSources] = useState(false)
  const [showDebug, setShowDebug] = useState(false)
  const [selectedOption, setSelectedOption] = useState(null)
  
  // Strip any remaining clause tags from answer
  const cleanText = text.replace(/^\[Policy:.*?\]\s*/gm, '');
  
  let confidenceColor = 'bg-red-500/20 text-red-300 ring-red-500/50'
  if (confidence >= 0.75) confidenceColor = 'bg-emerald-500/20 text-emerald-300 ring-emerald-500/50'
  else if (confidence >= 0.40) confidenceColor = 'bg-amber-500/20 text-amber-300 ring-amber-500/50'

  return (
    <div className="flex flex-col space-y-3 max-w-[85%]">
      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-5 shadow-lg text-gray-100 leading-relaxed">
        {cleanText}
        
        {needs_clarification && (
          <div className="mt-4">
            <p className="text-indigo-300 text-sm font-medium mb-2">
                {selectedOption ? "Selection sent:" : (clarification_question || "Please choose a topic:")}
            </p>
            <div className="flex flex-col gap-2">
              {clarification_options && clarification_options.map((opt, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                      if (selectedOption) return;
                      setSelectedOption(opt.id)
                      onOptionClick(opt)
                  }}
                  disabled={!!selectedOption}
                  className={`px-4 py-3 text-sm border rounded-lg transition-all text-left flex items-center group
                    ${selectedOption === opt.id 
                        ? 'bg-indigo-900/50 border-indigo-500 text-indigo-200' 
                        : selectedOption 
                            ? 'bg-gray-800/50 border-gray-700 text-gray-500 cursor-not-allowed opacity-50' 
                            : 'bg-gray-700 hover:bg-indigo-900/40 border-gray-600 hover:border-indigo-500/50 text-gray-200 hover:text-indigo-200'
                    }`}
                >
                  <span className={`w-2 h-2 rounded-full mr-3 transition-transform ${selectedOption === opt.id ? 'bg-indigo-400 scale-125' : 'bg-indigo-500 group-hover:scale-125'}`} />
                  {opt.label}
                  {selectedOption === opt.id && <span className="ml-auto text-xs opacity-70 animate-pulse">Processing...</span>}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Policy Sources Section - Only show if retrieval was actually performed (not ambiguous) */}
      {!needs_clarification && (confidence !== undefined || (sources && sources.length > 0)) && (
        <div className="flex flex-col space-y-2 ml-2">
          {confidence !== undefined && (
             <div className="flex items-center space-x-2">
               <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ring-1 ring-inset ${confidenceColor}`}>
                 Confidence: {Math.round(confidence * 100)}%
               </span>
             </div>
          )}

          {sources && sources.length > 0 && (
            <div className="mt-1">
              <button 
                onClick={() => setShowSources(!showSources)}
                className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center transition-colors"
              >
                {showSources ? 'Hide Policy Sources' : 'View Policy Sources'}
                <svg 
                  className={`w-3 h-3 ml-1 transform transition-transform ${showSources ? 'rotate-180' : ''}`} 
                  fill="none" viewBox="0 0 24 24" stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {showSources && (
                <div className="mt-3 p-3 bg-gray-800/50 rounded-xl border border-gray-700/50 backdrop-blur-sm animate-fade-in">
                  {sources.map((s, i) => <SourceItem key={i} source={s} />)}
                </div>
              )}
            </div>
          )}

          {debug && (
            <div className="mt-1">
              <button 
                onClick={() => setShowDebug(!showDebug)}
                className="text-xs font-medium text-orange-400 hover:text-orange-300 flex items-center transition-colors"
              >
                {showDebug ? 'Hide Debug Info' : 'View Debug Info'}
                <svg 
                  className={`w-3 h-3 ml-1 transform transition-transform ${showDebug ? 'rotate-180' : ''}`} 
                  fill="none" viewBox="0 0 24 24" stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {showDebug && (
                <div className="mt-3 p-3 bg-gray-800/50 rounded-xl border border-gray-700/50 backdrop-blur-sm animate-fade-in">
                  <pre className="text-xs text-gray-300 whitespace-pre-wrap">{JSON.stringify(debug, null, 2)}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [debug, setDebug] = useState(false)
  const abortControllerRef = useRef(null)
  
  // Eligibility State
  const [showEligibility, setShowEligibility] = useState(false)
  const [simLoading, setSimLoading] = useState(false)
  const [simResults, setSimResults] = useState(null)
  
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSimulate = async (data) => {
    setSimLoading(true)
    try {
      const response = await fetch('/simulate/eligibility', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      const result = await response.json()
      setSimResults(result.results)
    } catch (e) {
      console.error(e)
    } finally {
      setSimLoading(false)
    }
  }

  const sendMessage = async (textOverride = null, topic = null) => {
    const textToSend = textOverride || input
    if (!textToSend.trim()) return

    // If it's a new user message (not a clarification retry), add it to UI
    if (!topic) {
        setMessages(prev => [...prev, { role: 'user', text: textToSend }])
    }
    
    setInput('')
    setLoading(true)
    
    // Abort previous request if active
    if (abortControllerRef.current) {
        abortControllerRef.current.abort()
    }
    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch(`/ask${debug ? '?debug=1' : ''}`, {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ 
             question: textToSend,
             topic: topic // Add topic if present
         }),
         signal: abortControllerRef.current.signal
      });
      
      const data = await response.json();
      
      setMessages(prev => [...prev, {
        role: 'bot',
        text: data.answer,
        confidence: data.confidence,
        sources: data.sources,
        debug: data.debug, // server handles this logic if extended
        needs_clarification: data.needs_clarification,
        clarification_question: data.clarification_question,
        clarification_options: data.clarification_options,
        original_question: textToSend // Store for retries
      }])
    } catch (error) {
      if (error.name === 'AbortError') return
      
      setMessages(prev => [...prev, {
        role: 'bot',
        text: 'Sorry, I encountered an error connecting to the server. Please try again later.',
        error: true
      }])
    } finally {
      // Only unset loading if this is the current request
      if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
          setLoading(false)
          abortControllerRef.current = null
      }
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100 font-sans selection:bg-indigo-500/30">
        <EligibilityModal 
          isOpen={showEligibility} 
          onClose={() => { setShowEligibility(false); setSimResults(null); }}
          onSubmit={handleSimulate}
          loading={simLoading}
          results={simResults}
        />

        {/* Header */}
        <header className="bg-gray-900 border-b border-gray-800 p-4 shadow-sm z-10">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-indigo-500/20 shadow-lg">
                 <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                 </svg>
              </div>
              <h1 className="text-lg font-bold tracking-tight text-white">
                UniPolicy <span className="text-indigo-500">Assistant</span>
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowEligibility(true)}
                className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm font-medium text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Check Eligibility
              </button>
              
            </div>
          </div>
        </header>

        {/* Chat Container */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scroll-smooth">
          <div className="max-w-3xl mx-auto space-y-6 pb-4">
             {messages.length === 0 && (
               <div className="text-center text-gray-500 mt-20">
                  <div className="w-16 h-16 bg-gray-900 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-gray-800">
                    <svg className="w-8 h-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <p className="text-lg font-medium text-gray-400">How can I help you today?</p>
                  <p className="text-sm mt-2 max-w-xs mx-auto">Ask about attendance, exams, scholarships, or hostel regulations.</p>
               </div>
             )}

             {messages.map((msg, idx) => (
               <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                 {msg.role === 'user' ? (
                   <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-5 py-3.5 max-w-[80%] shadow-md">
                     {msg.text}
                   </div>
                 ) : (
                   <BotMessage 
                     text={msg.text} 
                     confidence={msg.confidence} 
                     sources={msg.sources} 
                     debug={msg.debug}
                     needs_clarification={msg.needs_clarification}
                     clarification_question={msg.clarification_question}
                     clarification_options={msg.clarification_options}
                     onOptionClick={(opt) => {
                       // Resend the original question with the selected topic
                       const originalQ = msg.original_question || "Is this allowed?"; // fallback
                       sendMessage(originalQ, opt.id);
                     }}
                   />
                 )}
               </div>
             ))}
             
             {loading && (
               <div className="flex justify-start">
                  <div className="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm flex items-center space-x-2">
                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"></div>
                  </div>
               </div>
             )}
             <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-gray-900 border-t border-gray-800 p-4">
          <div className="max-w-3xl mx-auto relative">
             <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask a question about university policies..."
                disabled={loading}
                className="w-full bg-gray-950 text-gray-200 placeholder-gray-500 border border-gray-700 rounded-xl py-3.5 pl-4 pr-12 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all shadow-sm disabled:opacity-50"
             />
             <button
               onClick={() => sendMessage()}
               disabled={!input.trim() || loading}
               className="absolute right-2 top-2 p-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
             >
               <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
               </svg>
             </button>
          </div>
          <div className="text-center mt-2">
             <span className="text-xs text-gray-600">AI responses can be inaccurate. Always verify important information.</span>
          </div>
        </div>
    </div>
  )
}

export default App