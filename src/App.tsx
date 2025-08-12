import React, { useState, useEffect, useRef } from 'react';
import { Loader2, AlertCircle, CheckCircle, Edit3, Trash2, Plus } from 'lucide-react';
import { APIService, ProductContent, MultiProductResponse } from './services/api';

// --- Helper function to extract required details from the prompt ---
function extractPromptDetails(prompt: string) {
  const eventNameMatch = prompt.match(/(?:for|event|Event)\s*["']?([^"']+)["']?/i);
  const eventDateMatch = prompt.match(/(?:on|date)\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})/i);
  const eventLocationMatch = prompt.match(/(?:in|at)\s*([A-Za-z\s]+)/i);
  const salespersonMatch = prompt.match(/(?:salesperson|featuring)\s*([A-Za-z\s]+)/i);
  const productsMatch = prompt.match(/products?:\s*([A-Za-z0-9,\s]+)/i);

  return {
    eventName: eventNameMatch ? eventNameMatch[1].trim() : '',
    eventDate: eventDateMatch ? eventDateMatch[1].trim() : '',
    eventLocation: eventLocationMatch ? eventLocationMatch[1].trim() : '',
    salesperson: salespersonMatch ? salespersonMatch[1].trim() : '',
    products: productsMatch ? productsMatch[1].split(',').map(p => p.trim()).filter(Boolean) : [],
  };
}

const REQUIRED_FIELDS = [
  { key: 'eventName', label: 'Event Name' },
  { key: 'eventDate', label: 'Event Date' },
  { key: 'eventLocation', label: 'Event Location' },
  { key: 'salesperson', label: 'Salesperson Name' },
  { key: 'products', label: 'Products' },
];

const referencePrompt = `Generate a PowerPoint for the "Open House Event" on August 11, 2025 in Dubai featuring salesperson Jasmeet Kaur and slides on the products: AI Photobooth, Kinetic Ceiling, and Kinetic Blooming Flower.`;

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isTyping?: boolean;
  pptDownloadUrl?: string;
  approvalRequired?: boolean;
  multiProductData?: MultiProductResponse;
  taskId?: string;
  isGenerating?: boolean;
}

export default function App() {
  const isAuthenticated = true; // For demo

  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [actualTheme, setActualTheme] = useState<'light' | 'dark'>('light');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pendingApproval, setPendingApproval] = useState<Message | null>(null);
  const [editingProductIndex, setEditingProductIndex] = useState<number | null>(null);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'available' | 'unavailable'>('checking');
  const [editingContent, setEditingContent] = useState<ProductContent | null>(null);
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Theme management
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'system' | null;
    if (savedTheme) setTheme(savedTheme);
  }, []);

  useEffect(() => {
    const updateTheme = () => {
      let newTheme: 'light' | 'dark';
      if (theme === 'system') {
        newTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      } else {
        newTheme = theme as 'light' | 'dark';
      }
      setActualTheme(newTheme);
      document.documentElement.classList.toggle('dark', newTheme === 'dark');
      localStorage.setItem('theme', theme);
    };
    updateTheme();
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', updateTheme);
      return () => mediaQuery.removeEventListener('change', updateTheme);
    }
  }, [theme]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Check backend status on mount
  useEffect(() => {
    checkBackendHealth();
    initializeChatSession();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const health = await APIService.healthCheck();
      setBackendStatus(health.backend_available ? 'available' : 'unavailable');
    } catch (error) {
      setBackendStatus('unavailable');
    }
  };

  const initializeChatSession = async () => {
    try {
      if (backendStatus === 'available') {
        const session = await APIService.createChatSession();
        setChatSessionId(session.session_id);
      }
    } catch (error) {
      console.error('Failed to create chat session:', error);
    }
  };

  // Welcome message
  useEffect(() => {
    if (isAuthenticated && messages.length === 0) {
      const statusMessage = backendStatus === 'unavailable' 
        ? "\n\n⚠️ Backend is not available. Using demo mode with simulated responses."
        : "\n\n✅ Connected to Lazulite AI backend.";

      setMessages([{
        id: '1',
        text: "Welcome to Lazulite AI PPT Generator! Enter your event details and products to generate a PowerPoint. Make sure to include:\n• Event Name\n• Event Date\n• Event Location\n• Salesperson Name\n• Products\n\nFor example:\n" + referencePrompt + statusMessage,
        sender: 'ai',
        timestamp: new Date(),
      }]);
    }
  }, [isAuthenticated, messages.length, backendStatus]);

  // --- Real Content Extraction ---
  const extractProductContent = async (productNames: string[]): Promise<MultiProductResponse> => {
    if (backendStatus === 'unavailable') {
      // Fallback to simulated data
      await new Promise(res => setTimeout(res, 2000));
      return {
        overview: `${productNames.join(', ')} offer cutting-edge interactive technology solutions. These products combine advanced AI capabilities with stunning visual displays for enhanced user engagement.`,
        specifications: [
          "High-resolution 4K display with touch interface",
          "AI-powered gesture recognition and facial detection"
        ],
        content_integration: [
          "Seamless CMS integration with real-time content updates",
          "Multi-platform compatibility with cloud-based management"
        ],
        infrastructure_requirements: [
          "Stable internet connection (minimum 50 Mbps)",
          "Dedicated power supply with backup systems"
        ]
      };
    }

    return await APIService.extractProductContent(productNames);
  };

  // --- Message Send Handler ---
  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading || pendingApproval) return;

    const details = extractPromptDetails(inputText);
    const missingFields = REQUIRED_FIELDS.filter(field => {
      if (field.key === 'products') return details.products.length === 0;
      return !details[field.key as keyof typeof details];
    });

    if (missingFields.length > 0) {
      const missingLabels = missingFields.map(f => f.label).join(', ');
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          text: `⚠️ Please provide the following missing details in your prompt: ${missingLabels}.\n\nReference prompt:\n${referencePrompt}`,
          sender: 'ai',
          timestamp: new Date(),
        }
      ]);
      setInputText('');
      return;
    }

    // Add user message
    setMessages(prev => [
      ...prev,
      {
        id: Date.now().toString(),
        text: inputText,
        sender: 'user',
        timestamp: new Date(),
      }
    ]);
    setInputText('');
    setIsLoading(true);

    try {
      // Extract product content from website
      const multiProductData = await extractProductContent(details.products);

      // Ask for user approval
      const approvalMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: `I've extracted content for your products from the Lazulite website. Please review and approve:`,
        sender: 'ai',
        timestamp: new Date(),
        approvalRequired: true,
        multiProductData,
      };
      setMessages(prev => [...prev, approvalMsg]);
      setPendingApproval(approvalMsg);
    } catch (error) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          text: `❌ Failed to extract product content: ${error instanceof Error ? error.message : 'Unknown error'}`,
          sender: 'ai',
          timestamp: new Date(),
        }
      ]);
    }
    
    setIsLoading(false);
  };

  // --- Handle User Approval ---
  const handleApproval = async (approved: boolean) => {
    if (!pendingApproval || !pendingApproval.multiProductData) return;

    if (approved) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 2).toString(),
          text: "✅ Content approved! Generating your PowerPoint presentation...",
          sender: 'ai',
          timestamp: new Date(),
          isGenerating: true,
        }
      ]);

      try {
        const result = await APIService.generatePPT({
          prompt: inputText,
          approved_content: pendingApproval.multiProductData.products
        });

        // Poll for completion
        pollPPTStatus(result.task_id);
      } catch (error) {
        setMessages(prev => [
          ...prev,
          {
            id: (Date.now() + 3).toString(),
            text: `❌ Failed to start PPT generation: ${error instanceof Error ? error.message : 'Unknown error'}`,
            sender: 'ai',
            timestamp: new Date(),
          }
        ]);
      }
    } else {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 2).toString(),
          text: "❌ Content not approved. You can modify the content using the edit options above, or provide new requirements.",
          sender: 'ai',
          timestamp: new Date(),
        }
      ]);
    }
    setPendingApproval(null);
  };

  // --- Poll PPT Generation Status ---
  const pollPPTStatus = async (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await APIService.checkPPTStatus(taskId);
        
        if (status.status === 'completed' && status.download_url) {
          clearInterval(pollInterval);
          setMessages(prev => [
            ...prev.filter(m => !m.isGenerating),
            {
              id: (Date.now() + 4).toString(),
              text: "✨ Your presentation has been generated successfully!",
              sender: 'ai',
              timestamp: new Date(),
              pptDownloadUrl: status.download_url,
            }
          ]);
        } else if (status.status === 'failed') {
          clearInterval(pollInterval);
          setMessages(prev => [
            ...prev.filter(m => !m.isGenerating),
            {
              id: (Date.now() + 4).toString(),
              text: `❌ PPT generation failed: ${status.error_message || 'Unknown error'}`,
              sender: 'ai',
              timestamp: new Date(),
            }
          ]);
        }
      } catch (error) {
        clearInterval(pollInterval);
        setMessages(prev => [
          ...prev.filter(m => !m.isGenerating),
          {
            id: (Date.now() + 4).toString(),
            text: `❌ Error checking PPT status: ${error instanceof Error ? error.message : 'Unknown error'}`,
            sender: 'ai',
            timestamp: new Date(),
          }
        ]);
      }
    }, 3000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleDownload = (url: string) => {
    window.open(url, '_blank');
  };

  // --- Content Editing Functions ---
  const handleEditContent = (content: ProductContent, productIndex: number) => {
    setEditingContent({ ...content });
    setEditingProductIndex(productIndex);
  };

  const handleSaveEdit = () => {
    if (!editingContent || !pendingApproval) return;
    
    const updatedMessage = {
      ...pendingApproval,
      multiProductData: {
        ...pendingApproval.multiProductData!,
        products: pendingApproval.multiProductData!.products.map((product, index) => 
          index === editingProductIndex ? editingContent : product
        )
      }
    };
    
    setMessages(prev => prev.map(msg => 
      msg.id === pendingApproval.id ? updatedMessage : msg
    ));
    
    setPendingApproval(updatedMessage);
    setEditingContent(null);
    setEditingProductIndex(null);
  };

  const handleCancelEdit = () => {
    setEditingContent(null);
    setEditingProductIndex(null);
  };

  // --- Content Display Component ---
  const MultiProductDisplay: React.FC<{ 
    multiProductData: MultiProductResponse; 
    isEditing?: boolean;
    editingProductIndex?: number | null;
  }> = ({ 
    multiProductData, 
    isEditing = false 
  }) => {
    return (
      <div className={`mt-3 p-4 rounded-lg border ${
        actualTheme === 'dark' ? 'bg-gray-800 border-gray-600' : 'bg-gray-50 border-gray-200'
      }`}>
        <h3 className="font-bold text-lg mb-4">
          Extracted Content for {multiProductData.total_products} Product{multiProductData.total_products > 1 ? 's' : ''}
        </h3>
        
        <div className="space-y-6">
          {multiProductData.products.map((product, productIndex) => {
            const currentContent = (isEditing && editingProductIndex === productIndex) ? editingContent! : product;
            const isEditingThisProduct = isEditing && editingProductIndex === productIndex;
            
            return (
              <div key={productIndex} className={`p-4 rounded-lg border ${
                actualTheme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'
              }`}>
                <h4 className="font-bold text-md mb-3 text-blue-600 dark:text-blue-400">
                  {product.product_name}
                </h4>
                
                <div className="space-y-4">
                  {/* Overview */}
                  <div>
                    <h5 className="font-semibold text-sm mb-2 flex items-center">
                      📋 Overview
                      {isEditingThisProduct && (
                        <Edit3 className="w-3 h-3 ml-1 text-blue-500" />
                      )}
                    </h5>
                    {isEditingThisProduct ? (
                      <textarea
                        value={currentContent.overview}
                        onChange={(e) => setEditingContent(prev => prev ? {...prev, overview: e.target.value} : null)}
                        className="w-full p-2 text-xs rounded border resize-none"
                        rows={2}
                      />
                    ) : (
                      <p className="text-xs text-gray-600 dark:text-gray-300">{currentContent.overview}</p>
                    )}
                  </div>

                  {/* Specifications */}
                  <div>
                    <h5 className="font-semibold text-sm mb-2">⚙️ Specifications</h5>
                    <ul className="space-y-1">
                      {currentContent.specifications.map((spec, idx) => (
                        <li key={idx} className="text-xs text-gray-600 dark:text-gray-300 flex items-start">
                          <span className="mr-2">•</span>
                          {isEditingThisProduct ? (
                            <input
                              value={spec}
                              onChange={(e) => {
                                const newSpecs = [...currentContent.specifications];
                                newSpecs[idx] = e.target.value;
                                setEditingContent(prev => prev ? {...prev, specifications: newSpecs} : null);
                              }}
                              className="flex-1 p-1 text-xs rounded border"
                            />
                          ) : (
                            <span>{spec}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Content Integration */}
                  <div>
                    <h5 className="font-semibold text-sm mb-2">🔗 Content Integration</h5>
                    <ul className="space-y-1">
                      {currentContent.content_integration.map((item, idx) => (
                        <li key={idx} className="text-xs text-gray-600 dark:text-gray-300 flex items-start">
                          <span className="mr-2">•</span>
                          {isEditingThisProduct ? (
                            <input
                              value={item}
                              onChange={(e) => {
                                const newItems = [...currentContent.content_integration];
                                newItems[idx] = e.target.value;
                                setEditingContent(prev => prev ? {...prev, content_integration: newItems} : null);
                              }}
                              className="flex-1 p-1 text-xs rounded border"
                            />
                          ) : (
                            <span>{item}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Infrastructure Requirements */}
                  <div>
                    <h5 className="font-semibold text-sm mb-2">🏗️ Infrastructure Requirements</h5>
                    <ul className="space-y-1">
                      {currentContent.infrastructure_requirements.map((req, idx) => (
                        <li key={idx} className="text-xs text-gray-600 dark:text-gray-300 flex items-start">
                          <span className="mr-2">•</span>
                          {isEditingThisProduct ? (
                            <input
                              value={req}
                              onChange={(e) => {
                                const newReqs = [...currentContent.infrastructure_requirements];
                                newReqs[idx] = e.target.value;
                                setEditingContent(prev => prev ? {...prev, infrastructure_requirements: newReqs} : null);
                              }}
                              className="flex-1 p-1 text-xs rounded border"
                            />
                          ) : (
                            <span>{req}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Images Preview */}
                  {currentContent.images && currentContent.images.length > 0 && (
                    <div>
                      <h5 className="font-semibold text-sm mb-2">🖼️ Images ({currentContent.image_layout})</h5>
                      <div className="text-xs text-gray-600 dark:text-gray-300">
                        {currentContent.images.length} image{currentContent.images.length > 1 ? 's' : ''} processed for PPT
                      </div>
                    </div>
                  )}
                </div>

                {/* Edit Controls for each product */}
                {isEditingThisProduct ? (
                  <div className="mt-4 flex space-x-2">
                    <button
                      onClick={handleSaveEdit}
                      className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                    >
                      <CheckCircle className="w-3 h-3 inline mr-1" />
                      Save Changes
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      className="px-3 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <div className="mt-4">
                    <button
                      onClick={() => handleEditContent(product, productIndex)}
                      className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                    >
                      <Edit3 className="w-3 h-3 inline mr-1" />
                      Edit {product.product_name}
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // --- Settings Modal ---
  const SettingsModal = () => (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className={`w-full max-w-lg rounded-2xl shadow-2xl border ${
        actualTheme === 'dark' 
          ? 'bg-gray-900 border-gray-700' 
          : 'bg-white border-gray-200'
      }`}>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold">Settings</h2>
            <button
              className="text-gray-500 hover:text-gray-900 dark:hover:text-white"
              onClick={() => setSettingsOpen(false)}
            >
              ✕
            </button>
          </div>
          <div className="space-y-6">
            <div>
              <label className="block font-medium mb-2">Theme</label>
              <select
                value={theme}
                onChange={e => setTheme(e.target.value as 'light' | 'dark' | 'system')}
                className="w-full rounded-lg border px-3 py-2"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="system">System</option>
              </select>
            </div>
            <div>
              <label className="block font-medium mb-2">Backend Status</label>
              <div className="flex items-center space-x-2">
                {backendStatus === 'checking' && <Loader2 className="w-4 h-4 animate-spin" />}
                {backendStatus === 'available' && <CheckCircle className="w-4 h-4 text-green-500" />}
                {backendStatus === 'unavailable' && <AlertCircle className="w-4 h-4 text-red-500" />}
                <span className="text-sm">
                  {backendStatus === 'checking' && 'Checking...'}
                  {backendStatus === 'available' && 'Connected'}
                  {backendStatus === 'unavailable' && 'Disconnected (Demo Mode)'}
                </span>
              </div>
              <button
                onClick={checkBackendHealth}
                className="mt-2 px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
              >
                Retry Connection
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // --- Main Render ---
  return (
    <div className={`min-h-screen transition-all duration-500 ${
      actualTheme === 'dark' 
        ? 'bg-gray-900 text-white' 
        : 'bg-gray-50 text-gray-900'
    }`}>
      {/* Aurora Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute inset-0 opacity-40 ${
          actualTheme === 'dark' 
            ? 'bg-gradient-to-br from-blue-900/30 via-purple-900/30 to-teal-900/30' 
            : 'bg-gradient-to-br from-blue-100/60 via-purple-100/60 to-teal-100/60'
        }`}></div>
        <div className="absolute top-0 left-0 w-full h-full">
          <div className={`absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-20 animate-pulse ${
            actualTheme === 'dark' ? 'bg-blue-500' : 'bg-blue-400'
          }`} style={{ animationDuration: '4s' }}></div>
          <div className={`absolute top-3/4 right-1/4 w-80 h-80 rounded-full blur-3xl opacity-25 animate-pulse ${
            actualTheme === 'dark' ? 'bg-purple-500' : 'bg-purple-400'
          }`} style={{ animationDuration: '6s', animationDelay: '1s' }}></div>
        </div>
      </div>

      {/* Main Content */}
      <div>
        <header className={`relative z-10 border-b transition-all duration-300 backdrop-blur-xl ${
          actualTheme === 'dark' 
            ? 'border-gray-800/50 bg-gray-900/80' 
            : 'border-gray-200/50 bg-white/80'
        }`}>
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center space-x-3">
              <span className="font-bold text-xl">Lazulite AI PPT Generator</span>
              {backendStatus === 'unavailable' && (
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                  Demo Mode
                </span>
              )}
            </div>
            <button
              className="text-gray-500 hover:text-blue-600"
              onClick={() => setSettingsOpen(true)}
            >
              Settings
            </button>
          </div>
        </header>
        <main className="relative z-10 px-4 py-6 flex flex-col h-[calc(100vh-88px)]">
          {/* Reference Prompt UI above input area */}
          <div className="max-w-4xl mx-auto w-full mb-4">
            <div className={`rounded-xl p-4 text-xs font-medium ${
              actualTheme === 'dark' ? 'bg-gray-800/70 text-gray-300' : 'bg-blue-50 text-blue-700'
            }`}>
              <span className="font-semibold">Reference Prompt:</span> {referencePrompt}
            </div>
          </div>
          
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto max-w-4xl mx-auto w-full mb-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex mb-4 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] rounded-xl px-4 py-3 shadow ${
                  msg.sender === 'user'
                    ? actualTheme === 'dark'
                      ? 'bg-blue-700 text-white'
                      : 'bg-blue-100 text-blue-900'
                    : actualTheme === 'dark'
                      ? 'bg-gray-800 text-gray-100'
                      : 'bg-white text-gray-900'
                }`}>
                  <div className="text-sm whitespace-pre-line">{msg.text}</div>
                  
                  {/* Show scraped content */}
                  {msg.multiProductData && (
                    <MultiProductDisplay 
                      multiProductData={msg.multiProductData} 
                      isEditing={editingContent !== null && msg.id === pendingApproval?.id}
                      editingProductIndex={editingProductIndex}
                    />
                  )}
                  
                  {/* Loading indicator for generation */}
                  {msg.isGenerating && (
                    <div className="mt-3 flex items-center space-x-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-xs">Generating presentation...</span>
                    </div>
                  )}
                  
                  {/* Download button */}
                  {msg.pptDownloadUrl && (
                    <button
                      className="mt-2 px-4 py-2 rounded bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700"
                      onClick={() => handleDownload(msg.pptDownloadUrl!)}
                    >
                      Download PPT
                    </button>
                  )}
                  
                  <div className="text-xs text-gray-400 mt-1">
                    {msg.sender === 'user' ? 'You' : 'AI'} • {msg.timestamp.toLocaleTimeString()}
                  </div>
                  
                  {/* Approval Buttons */}
                  {msg.approvalRequired && !editingContent && (
                    <div className="mt-3 flex space-x-2">
                      <button
                        className="px-4 py-2 rounded bg-green-600 text-white text-xs font-semibold hover:bg-green-700"
                        onClick={() => handleApproval(true)}
                      >
                        Approve & Generate PPT
                      </button>
                      <button
                        className="px-4 py-2 rounded bg-red-600 text-white text-xs font-semibold hover:bg-red-700"
                        onClick={() => handleApproval(false)}
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          
          {/* Chat Input */}
          <form
            className="max-w-4xl mx-auto w-full flex items-center space-x-2"
            onSubmit={e => {
              e.preventDefault();
              handleSendMessage();
            }}
          >
            <textarea
              className={`flex-1 rounded-xl border px-4 py-3 resize-none transition ${
                actualTheme === 'dark'
                  ? 'bg-gray-800 border-gray-700 text-white'
                  : 'bg-white border-gray-300 text-gray-900'
              }`}
              rows={2}
              placeholder='Type your prompt here...'
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading || !!pendingApproval || !!editingContent}
            />
            <button
              type="submit"
              className={`px-6 py-3 rounded-xl font-semibold transition ${
                isLoading || !!pendingApproval || !!editingContent
                  ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
              disabled={isLoading || !!pendingApproval || !!editingContent}
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Send'}
            </button>
          </form>
        </main>
      </div>
      {settingsOpen && <SettingsModal />}
    </div>
  );
}