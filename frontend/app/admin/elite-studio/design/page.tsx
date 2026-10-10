'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Send,
  RefreshCw,
  Image,
  Lightbulb,
  Palette,
  FileText,
  Wrench,
  ChevronDown,
  ChevronUp,
  Loader2,
  Sparkles,
  Plus,
} from 'lucide-react';
import { eliteStudioClient, type CreativeOperation } from '@/lib/elite-studio-client';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  operation?: CreativeOperation;
  timestamp: Date;
}

interface DesignResult {
  concept_name?: string;
  description?: string;
  colorways?: string[];
  tech_notes?: string;
  materials?: string[];
  inspiration?: string;
}

// ---------------------------------------------------------------------------
// Prompt suggestions
// ---------------------------------------------------------------------------

const PROMPT_SUGGESTIONS = [
  'Design a cropped hoodie for the Black Rose collection — urban gothic, East Bay inspired',
  'Create a bay-bridge varsity jacket concept for Signature — gold and navy colorway',
  'Love Hurts cargo shorts — B&B rose motif, crimson and black, streetwear edge',
  'Kids Capsule mini tracksuit — playful rose gold with SkyyRose branding',
  'Signature limited-edition tee with Oakland skyline graphic, luxury street aesthetic',
] as const;

// ---------------------------------------------------------------------------
// Result display component
// ---------------------------------------------------------------------------

function DesignResultDisplay({ result }: { result: DesignResult }) {
  const [showTechNotes, setShowTechNotes] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5"
    >
      {result.concept_name && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="h-4 w-4 text-[#B76E79]" aria-hidden="true" />
            <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">Concept</p>
          </div>
          <h3 className="text-xl font-bold text-white">{result.concept_name}</h3>
        </div>
      )}

      {result.description && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <FileText className="h-4 w-4 text-gray-500" aria-hidden="true" />
            <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">Description</p>
          </div>
          <p className="text-gray-300 text-sm leading-relaxed">{result.description}</p>
        </div>
      )}

      {result.inspiration && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Lightbulb className="h-4 w-4 text-[#D4AF37]" aria-hidden="true" />
            <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">Inspiration</p>
          </div>
          <p className="text-gray-400 text-sm leading-relaxed italic">{result.inspiration}</p>
        </div>
      )}

      {result.colorways && result.colorways.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Palette className="h-4 w-4 text-purple-400" aria-hidden="true" />
            <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">Colorways</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {result.colorways.map((c) => (
              <Badge key={c} variant="outline" className="border-gray-700 text-gray-300 text-xs">
                {c}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {result.materials && result.materials.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">Materials</p>
          <div className="flex flex-wrap gap-2">
            {result.materials.map((m) => (
              <Badge key={m} variant="outline" className="border-gray-700 text-gray-400 text-xs">
                {m}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {result.tech_notes && (
        <div>
          <button
            className="flex items-center gap-2 text-xs text-gray-500 uppercase tracking-wide font-medium hover:text-gray-300 transition-colors w-full text-left"
            onClick={() => setShowTechNotes((v) => !v)}
            aria-expanded={showTechNotes}
          >
            <Wrench className="h-4 w-4" aria-hidden="true" />
            Technical Notes
            {showTechNotes ? (
              <ChevronUp className="h-3.5 w-3.5 ml-auto" aria-hidden="true" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5 ml-auto" aria-hidden="true" />
            )}
          </button>
          <AnimatePresence>
            {showTechNotes && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <p className="text-gray-400 text-sm leading-relaxed mt-2 pl-6">
                  {result.tech_notes}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Chat bubble
// ---------------------------------------------------------------------------

function ChatBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  const result = message.operation?.result as DesignResult | undefined;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-[#B76E79]/20 border border-[#B76E79]/30 text-white'
            : 'bg-gray-800 border border-gray-700 text-gray-200'
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        {result && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <DesignResultDisplay result={result} />
          </div>
        )}
        <p className="text-xs text-gray-600 mt-2">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function DesignCoPilotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [lastOperation, setLastOperation] = useState<CreativeOperation | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Poll for operation completion
  const { data: polledOperation } = useQuery({
    queryKey: ['elite-studio', 'design-poll', lastOperation?.operation_id],
    queryFn: () =>
      lastOperation ? eliteStudioClient.getOperation(lastOperation.operation_id) : null,
    enabled:
      !!lastOperation &&
      (lastOperation.status === 'queued' || lastOperation.status === 'running'),
    refetchInterval: 3000,
  });

  // Update messages when operation completes
  useEffect(() => {
    if (polledOperation && polledOperation.status === 'completed' && polledOperation.result) {
      setLastOperation(polledOperation);
      setMessages((prev) => {
        const idx = prev.findLastIndex((m) => m.operation?.operation_id === polledOperation.operation_id);
        if (idx === -1) return prev;
        const updated = [...prev];
        updated[idx] = {
          ...updated[idx],
          operation: polledOperation,
          content: extractConceptName(polledOperation.result as DesignResult) ?? updated[idx].content,
        };
        return updated;
      });
    }
  }, [polledOperation]);

  const ideationMutation = useMutation({
    mutationFn: async (prompt: string) => {
      return eliteStudioClient.createOperation('design-ideation', 'concept', {
        prompt,
        brand: 'SkyyRose',
        style: 'luxury streetwear',
      });
    },
    onSuccess: (operation) => {
      setLastOperation(operation);
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content:
          operation.status === 'completed' && operation.result
            ? extractConceptName(operation.result as DesignResult) ?? 'Here is your design concept...'
            : 'Working on your design concept...',
        operation,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    },
    onError: (err: Error) => {
      const errorMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Failed to generate design: ${err.message}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    },
  });

  const mockupMutation = useMutation({
    mutationFn: async (sku: string) => {
      return eliteStudioClient.createOperation('mockup', sku, {
        source: 'design-ideation',
        concept_id: lastOperation?.operation_id,
      });
    },
    onSuccess: (operation) => {
      const msg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Generating mockup for SKU: ${operation.sku}. Check Operations for the result.`,
        operation,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, msg]);
    },
    onError: (err: Error) => {
      const msg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Mockup generation failed: ${err.message}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, msg]);
    },
  });

  const handleSend = useCallback(() => {
    const trimmed = inputValue.trim();
    if (!trimmed || ideationMutation.isPending) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    ideationMutation.mutate(trimmed);
  }, [inputValue, ideationMutation]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleSuggestion = useCallback(
    (suggestion: string) => {
      setInputValue(suggestion);
      textareaRef.current?.focus();
    },
    []
  );

  const handleRefine = useCallback(() => {
    if (!lastOperation?.result) return;
    const conceptName = extractConceptName(lastOperation.result as DesignResult);
    const refinePrompt = `Refine the "${conceptName ?? 'design'}" concept — push it further with more luxury detail and brand-specific elements.`;
    setInputValue(refinePrompt);
    textareaRef.current?.focus();
  }, [lastOperation]);

  const handleGenerateMockups = useCallback(() => {
    if (!lastOperation) return;
    mockupMutation.mutate(lastOperation.sku);
  }, [lastOperation, mockupMutation]);

  const isLoading = ideationMutation.isPending || mockupMutation.isPending;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Design Co-Pilot</h1>
        <p className="text-gray-400 mt-1">
          AI-powered design ideation for SkyyRose luxury streetwear
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left: Chat interface */}
        <Card className="bg-gray-900 border-gray-800 flex flex-col h-[680px]">
          <CardHeader className="shrink-0 border-b border-gray-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-[#B76E79] to-[#D4AF37]">
                <Sparkles className="h-5 w-5 text-white" aria-hidden="true" />
              </div>
              <div>
                <CardTitle className="text-white text-base">Design Studio</CardTitle>
                <CardDescription className="text-gray-500 text-xs">
                  Describe your vision.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
            <AnimatePresence initial={false}>
              {messages.length === 0 ? (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center justify-center h-full text-center py-8"
                >
                  <div className="rounded-2xl bg-gradient-to-br from-[#B76E79]/10 to-[#D4AF37]/10 border border-[#B76E79]/20 p-6 max-w-xs">
                    <Lightbulb className="h-10 w-10 text-[#D4AF37] mx-auto mb-3" aria-hidden="true" />
                    <p className="text-gray-300 font-medium">Start with a design idea</p>
                    <p className="text-gray-500 text-xs mt-2">
                      Describe the piece, collection, inspiration, or vibe — the AI will generate a full concept.
                    </p>
                  </div>

                  <div className="mt-6 space-y-2 w-full max-w-sm">
                    <p className="text-xs text-gray-600 uppercase tracking-wide">Suggestions</p>
                    {PROMPT_SUGGESTIONS.slice(0, 3).map((s, i) => (
                      <button
                        key={i}
                        onClick={() => handleSuggestion(s)}
                        className="block w-full text-left text-xs text-gray-400 hover:text-[#B76E79] bg-gray-800/50 hover:bg-gray-800 rounded-lg px-3 py-2 transition-colors border border-transparent hover:border-[#B76E79]/20"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </motion.div>
              ) : (
                messages.map((msg) => <ChatBubble key={msg.id} message={msg} />)
              )}

              {isLoading && (
                <motion.div
                  key="typing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3">
                    <div className="flex items-center gap-2 text-gray-400 text-sm">
                      <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                      Generating design concept...
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="shrink-0 border-t border-gray-800 p-4 space-y-3">
            <div className="flex gap-2">
              <Textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe a design concept... (Shift+Enter for new line)"
                className="resize-none min-h-[80px] bg-gray-800 border-gray-700 text-white placeholder:text-gray-500 focus-visible:ring-[#B76E79] text-sm"
                aria-label="Design concept input"
                disabled={isLoading}
              />
              <Button
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                className="self-end bg-gradient-to-r from-[#B76E79] to-[#D4AF37] text-white hover:opacity-90 transition-opacity disabled:opacity-40"
                aria-label="Send message"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                ) : (
                  <Send className="h-4 w-4" aria-hidden="true" />
                )}
              </Button>
            </div>

            {/* Action buttons */}
            {lastOperation && (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefine}
                  disabled={isLoading}
                  className="border-gray-700 text-gray-400 hover:text-[#B76E79] hover:border-[#B76E79]/50 text-xs gap-1.5"
                  aria-label="Refine the last design concept"
                >
                  <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />
                  Refine
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleGenerateMockups}
                  disabled={isLoading || mockupMutation.isPending}
                  className="border-gray-700 text-gray-400 hover:text-[#D4AF37] hover:border-[#D4AF37]/50 text-xs gap-1.5"
                  aria-label="Generate mockup images from this concept"
                >
                  <Image className="h-3.5 w-3.5" aria-hidden="true" />
                  Generate Mockups
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setMessages([]);
                    setLastOperation(null);
                    setInputValue('');
                  }}
                  className="text-gray-600 hover:text-gray-400 text-xs gap-1.5 ml-auto"
                  aria-label="Start a new conversation"
                >
                  <Plus className="h-3.5 w-3.5" aria-hidden="true" />
                  New
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* Right: Result display */}
        <Card className="bg-gray-900 border-gray-800 flex flex-col h-[680px]">
          <CardHeader className="shrink-0 border-b border-gray-800 pb-4">
            <CardTitle className="text-white text-base flex items-center gap-2">
              <Palette className="h-5 w-5 text-[#B76E79]" aria-hidden="true" />
              Design Concept
            </CardTitle>
            <CardDescription className="text-gray-500 text-xs">
              AI-generated design details will appear here
            </CardDescription>
          </CardHeader>

          <div className="flex-1 overflow-y-auto p-6 min-h-0">
            {!lastOperation && !isLoading ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="rounded-2xl bg-gray-800/50 border border-gray-700 p-8 max-w-xs">
                  <Palette className="h-12 w-12 text-gray-700 mx-auto mb-4" aria-hidden="true" />
                  <p className="text-gray-400 font-medium">No concept yet</p>
                  <p className="text-gray-600 text-sm mt-2">
                    Send a design idea in the chat to generate a full concept with colorways, materials, and technical notes.
                  </p>
                </div>

                {/* Brand color swatches for reference */}
                <div className="mt-6 w-full max-w-xs">
                  <p className="text-xs text-gray-600 uppercase tracking-wide text-center mb-3">Brand Palette</p>
                  <div className="grid grid-cols-4 gap-2">
                    {[
                      { name: 'Rose Gold', hex: '#B76E79' },
                      { name: 'Dark', hex: '#0A0A0A' },
                      { name: 'Gold', hex: '#D4AF37' },
                      { name: 'Crimson', hex: '#DC143C' },
                    ].map((color) => (
                      <div key={color.hex} className="flex flex-col items-center gap-1.5">
                        <div
                          className="h-10 w-10 rounded-lg border border-gray-700"
                          style={{ backgroundColor: color.hex }}
                          aria-label={`${color.name}: ${color.hex}`}
                        />
                        <p className="text-xs text-gray-600">{color.name}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : isLoading && !lastOperation?.result ? (
              <div className="space-y-4">
                <Skeleton className="h-6 w-48 bg-gray-800" />
                <Skeleton className="h-4 w-full bg-gray-800" />
                <Skeleton className="h-4 w-3/4 bg-gray-800" />
                <Skeleton className="h-4 w-5/6 bg-gray-800" />
                <div className="flex gap-2 pt-2">
                  <Skeleton className="h-6 w-20 bg-gray-800 rounded-full" />
                  <Skeleton className="h-6 w-24 bg-gray-800 rounded-full" />
                  <Skeleton className="h-6 w-16 bg-gray-800 rounded-full" />
                </div>
              </div>
            ) : lastOperation?.result ? (
              <DesignResultDisplay result={lastOperation.result as DesignResult} />
            ) : null}
          </div>

          {/* Operation metadata footer */}
          {lastOperation && (
            <div className="shrink-0 border-t border-gray-800 px-6 py-3">
              <div className="flex items-center justify-between text-xs text-gray-600">
                <span className="font-mono truncate max-w-[200px]">{lastOperation.operation_id}</span>
                <div className="flex items-center gap-3 shrink-0">
                  <Badge
                    variant="outline"
                    className={`text-xs ${
                      lastOperation.status === 'completed'
                        ? 'border-green-700 text-green-500'
                        : lastOperation.status === 'running'
                          ? 'border-blue-700 text-blue-400'
                          : 'border-gray-700 text-gray-400'
                    }`}
                  >
                    {lastOperation.status}
                  </Badge>
                  <span>${lastOperation.cost_usd.toFixed(4)}</span>
                </div>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function extractConceptName(result: DesignResult): string | null {
  return result.concept_name ?? null;
}
