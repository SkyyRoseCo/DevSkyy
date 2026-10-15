'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { X, Send, ShoppingBag, Sparkles, ArrowRight } from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type MascotState = 'minimized' | 'walking-out' | 'open' | 'walking-back';

interface ChatMessage {
  role: 'mascot' | 'user';
  text: string;
}

// ---------------------------------------------------------------------------
// Collection awareness
// ---------------------------------------------------------------------------

const COLLECTION_GREETINGS: Record<string, { greeting: string; outfit: string; suggestions: string[] }> = {
  'black-rose': {
    greeting: "Welcome to the BLACK Rose collection — where darkness blooms into luxury.",
    outfit: 'black-rose',
    suggestions: [
      'Tell me about BLACK Rose Crewneck',
      'What makes this collection special?',
      'Show me the Sherpa Jacket',
    ],
  },
  'love-hurts': {
    greeting: "Feel the fire of Love Hurts — Oakland grit meets luxury passion.",
    outfit: 'love-hurts',
    suggestions: [
      'What is The Fannie?',
      'Tell me about the Varsity Jacket',
      'How do I pre-order?',
    ],
  },
  'signature': {
    greeting: "The Signature collection — timeless essentials in rose gold.",
    outfit: 'signature',
    suggestions: [
      'Tell me about The Bay Set',
      'What sizes are available?',
      'When does pre-order ship?',
    ],
  },
  default: {
    greeting: "Hey! I'm Skyy, your personal style guide. What can I help you with?",
    outfit: 'casual',
    suggestions: [
      'Show me the collections',
      'How do pre-orders work?',
      'Tell me about SkyyRose',
    ],
  },
};

function getCollectionFromPath(pathname: string): string {
  if (pathname.includes('black-rose')) return 'black-rose';
  if (pathname.includes('love-hurts')) return 'love-hurts';
  if (pathname.includes('signature')) return 'signature';
  return 'default';
}

const MASCOT_RESPONSES: Record<string, string> = {
  'show me the collections': "We have three collections: BLACK Rose (gothic luxury), Love Hurts (Oakland soul), and Signature (rose gold essentials). Each tells a unique story!",
  'how do pre-orders work?': "Pre-orders lock in your exclusive early-adopter pricing with up to 25% off retail. Limited numbered pieces — once they're claimed, they're gone!",
  'tell me about skyyrose': "Born in Oakland, we craft premium streetwear that tells stories through gothic romance, Bay Area grit, and timeless elegance.",
  'how do i pre-order?': "Head to the Pre-Order page and pick your favorites! Each piece comes with exclusive packaging, a signed certificate, and lifetime Inner Circle membership.",
};

function getMascotReply(input: string): string {
  const lower = input.toLowerCase().trim();
  for (const [key, response] of Object.entries(MASCOT_RESPONSES)) {
    if (lower.includes(key) || key.includes(lower)) return response;
  }
  return "Great question! For the best experience, check out our collections or head to the pre-order page. I'm here if you need anything!";
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function MascotBubble() {
  const pathname = usePathname();
  const [state, setState] = useState<MascotState>('minimized');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [hasGreeted, setHasGreeted] = useState(false);

  const collection = getCollectionFromPath(pathname);
  const context = COLLECTION_GREETINGS[collection] ?? COLLECTION_GREETINGS['default'];

  // Don't show on admin pages
  const isAdmin = pathname.startsWith('/admin');
  const isLogin = pathname === '/login';

  const handleOpen = useCallback(() => {
    setState('walking-out');
    setTimeout(() => {
      setState('open');
      if (!hasGreeted) {
        setMessages([{ role: 'mascot', text: context.greeting }]);
        setHasGreeted(true);
      }
    }, 600);
  }, [context.greeting, hasGreeted]);

  const handleClose = useCallback(() => {
    setState('walking-back');
    setTimeout(() => setState('minimized'), 600);
  }, []);

  const handleSend = useCallback(() => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages((prev) => [...prev, { role: 'user', text: userMsg }]);
    setInput('');

    setTimeout(() => {
      const reply = getMascotReply(userMsg);
      setMessages((prev) => [...prev, { role: 'mascot', text: reply }]);
    }, 800);
  }, [input]);

  const handleSuggestion = useCallback((text: string) => {
    setMessages((prev) => [...prev, { role: 'user', text }]);
    setTimeout(() => {
      const reply = getMascotReply(text);
      setMessages((prev) => [...prev, { role: 'mascot', text: reply }]);
    }, 800);
  }, []);

  // Reset greeting when collection changes
  useEffect(() => {
    if (state === 'open') {
      setMessages([{ role: 'mascot', text: context.greeting }]);
    }
  }, [collection]);

  if (isAdmin || isLogin) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50" style={{ fontFamily: 'system-ui, sans-serif' }}>
      {/* Chat Panel — visible when open */}
      {(state === 'open' || state === 'walking-out' || state === 'walking-back') && (
        <div
          className={`
            mb-4 w-80 rounded-2xl bg-[#0A0A0A] border border-gray-800 shadow-2xl shadow-black/50
            overflow-hidden transition-all duration-500
            ${state === 'open' ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-4 scale-95'}
          `}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-[#B76E79] to-rose-600 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-white font-semibold text-sm">Skyy</p>
                <p className="text-white/70 text-xs">Your Style Guide</p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="h-8 w-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
              aria-label="Close mascot chat"
            >
              <X className="h-4 w-4 text-white" />
            </button>
          </div>

          {/* Messages */}
          <div className="p-4 h-64 overflow-y-auto space-y-3 scrollbar-thin scrollbar-thumb-gray-800">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`
                    max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed
                    ${msg.role === 'mascot'
                      ? 'bg-gray-800 text-gray-200 rounded-bl-md'
                      : 'bg-[#B76E79] text-white rounded-br-md'
                    }
                  `}
                >
                  {msg.text}
                </div>
              </div>
            ))}
          </div>

          {/* Suggestions */}
          {messages.length <= 1 && (
            <div className="px-4 pb-2 flex flex-wrap gap-2">
              {context.suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => handleSuggestion(s)}
                  className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-full px-3 py-1.5 transition-colors border border-gray-700"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Quick Actions */}
          <div className="px-4 pb-2 flex gap-2">
            <Link
              href="/collections"
              className="flex items-center gap-1.5 text-xs bg-gray-800 hover:bg-gray-700 text-[#B76E79] rounded-full px-3 py-1.5 transition-colors border border-[#B76E79]/30"
            >
              <ShoppingBag className="h-3 w-3" />
              Collections
            </Link>
            <Link
              href="/pre-order"
              className="flex items-center gap-1.5 text-xs bg-[#B76E79]/10 hover:bg-[#B76E79]/20 text-[#B76E79] rounded-full px-3 py-1.5 transition-colors border border-[#B76E79]/30"
            >
              <ArrowRight className="h-3 w-3" />
              Pre-Order
            </Link>
          </div>

          {/* Input */}
          <div className="p-3 border-t border-gray-800">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask me anything..."
                className="flex-1 bg-gray-800 border border-gray-700 rounded-full px-4 py-2 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#B76E79]/50"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="h-9 w-9 rounded-full bg-[#B76E79] hover:bg-rose-500 disabled:opacity-30 flex items-center justify-center transition-colors"
                aria-label="Send message"
              >
                <Send className="h-4 w-4 text-white" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Face Bubble — always visible when not on admin/login */}
      <button
        onClick={state === 'minimized' ? handleOpen : handleClose}
        className={`
          relative h-14 w-14 rounded-full
          bg-gradient-to-br from-[#B76E79] to-rose-600
          shadow-lg shadow-[#B76E79]/30
          flex items-center justify-center
          transition-all duration-300 hover:scale-110 hover:shadow-xl hover:shadow-[#B76E79]/40
          ${state === 'minimized' ? 'animate-mascot-breathe' : ''}
          ${state === 'walking-out' ? 'animate-mascot-expand' : ''}
          ${state === 'walking-back' ? 'animate-mascot-shrink' : ''}
        `}
        aria-label={state === 'minimized' ? 'Open Skyy mascot chat' : 'Close Skyy mascot chat'}
      >
        {/* Inner face circle */}
        <div className="h-11 w-11 rounded-full bg-[#0A0A0A] border-2 border-[#B76E79]/60 flex items-center justify-center overflow-hidden">
          <div className="text-center">
            <Sparkles className="h-5 w-5 text-[#B76E79] mx-auto" />
            <span className="text-[8px] text-[#B76E79]/80 font-bold tracking-wider">SKYY</span>
          </div>
        </div>

        {/* Online indicator */}
        <div className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-green-500 border-2 border-[#0A0A0A]">
          <div className="h-full w-full rounded-full bg-green-500 animate-ping opacity-75" />
        </div>
      </button>

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes mascot-breathe {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
        @keyframes mascot-expand {
          0% { transform: scale(1); }
          50% { transform: scale(1.2); }
          100% { transform: scale(1); }
        }
        @keyframes mascot-shrink {
          0% { transform: scale(1); }
          50% { transform: scale(0.9); }
          100% { transform: scale(1); }
        }
        .animate-mascot-breathe {
          animation: mascot-breathe 3s ease-in-out infinite;
        }
        .animate-mascot-expand {
          animation: mascot-expand 0.6s ease-out;
        }
        .animate-mascot-shrink {
          animation: mascot-shrink 0.6s ease-out;
        }
      `}</style>
    </div>
  );
}
