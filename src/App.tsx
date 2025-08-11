import React, { useState, useEffect, useRef } from 'react';
import { Loader2 } from 'lucide-react';

// --- Remove Supabase Auth imports ---
// import { useAuth, AuthProvider } from './lib/supabase';
// import AuthModal from './components/AuthModal';

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
  scrapedData?: string;
}

export default function App() {
  // --- Remove Supabase Auth logic ---
  // const { user, loading, signOut } = useAuth();
  // const isAuthenticated = !!user;

  // --- For demo, assume user is always authenticated ---
  const isAuthenticated = true;

  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [actualTheme, setActualTheme] = useState<'light' | 'dark'>('light');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pendingApproval, setPendingApproval] = useState<Message | null>(null);
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

  // Welcome message
  useEffect(() => {
    if (isAuthenticated && messages.length === 0) {
      setMessages([{
        id: '1',
        text: "Welcome to Lazulite AI PPT Generator! Enter your event details and products to generate a PowerPoint. Make sure to include:\n• Event Name\n• Event Date\n• Event Location\n• Salesperson Name\n• Products\n\nFor example:\n" + referencePrompt,
        sender: 'ai',
        timestamp: new Date(),
      }]);
    }
  }, [isAuthenticated, messages.length]);

  // --- Simulated Web Scraping Function ---
  async function scrapeProductData(productNames: string[]): Promise<string> {
    // Simulate scraping with a delay and dummy data
    await new Promise(res => setTimeout(res, 1500));
    return productNames.map(p => 
      `Product: ${p}\nOverview: This is a simulated overview for ${p}.\nSpecifications: Simulated specs for ${p}.\nContent Integration: Simulated specs for ${p}.\nInfrastructure Requirements: Simulated specs for ${p}.\nImages: [Simulated image URLs]\n`
    ).join('\n');
  }

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
      setIsLoading(false);
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

    // Simulate scraping product data
    const scrapedData = await scrapeProductData(details.products);

    // Ask for user approval
    const approvalMsg: Message = {
      id: (Date.now() + 1).toString(),
      text: `Here is the extracted data for your products:\n\n${scrapedData}\n\nDo you approve this content to be used for PPT generation?`,
      sender: 'ai',
      timestamp: new Date(),
      approvalRequired: true,
      scrapedData,
    };
    setMessages(prev => [...prev, approvalMsg]);
    setPendingApproval(approvalMsg);
    setIsLoading(false);
  };

  // --- Handle User Approval ---
  const handleApproval = (approved: boolean) => {
    if (!pendingApproval) return;
    if (approved) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 2).toString(),
          text: "✅ Content approved! Generating your PowerPoint presentation...",
          sender: 'ai',
          timestamp: new Date(),
        },
        {
          id: (Date.now() + 3).toString(),
          text: "✨ Your presentation has been generated successfully!\n\n📑 The PowerPoint includes:\n• Product overview\n• Specifications\n• Images\n• Content integration\n• Infrastructure requirements\n\n(Download functionality would connect to backend API.)",
          sender: 'ai',
          timestamp: new Date(),
          pptDownloadUrl: '#',
        }
      ]);
    } else {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 2).toString(),
          text: "❌ Content not approved. Please modify your prompt or contact support.",
          sender: 'ai',
          timestamp: new Date(),
        }
      ]);
    }
    setPendingApproval(null);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleDownload = (url: string) => {
    // For demo, open the URL in a new tab (replace with actual download logic)
    window.open(url, '_blank');
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
            <span className="font-bold text-xl">Lazulite AI PPT Generator</span>
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
                  {msg.approvalRequired && (
                    <div className="mt-3 flex space-x-2">
                      <button
                        className="px-4 py-2 rounded bg-green-600 text-white text-xs font-semibold hover:bg-green-700"
                        onClick={() => handleApproval(true)}
                      >
                        Approve
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
              disabled={isLoading || !!pendingApproval}
            />
            <button
              type="submit"
              className={`px-6 py-3 rounded-xl font-semibold transition ${
                isLoading || !!pendingApproval
                  ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
              disabled={isLoading || !!pendingApproval}
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