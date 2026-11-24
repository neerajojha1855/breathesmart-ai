import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Bot, Loader2, Send, Sparkles, User } from 'lucide-react';
import { useLocation } from '../contexts/LocationContext';
import { api } from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  followups?: string[];
}

export const AssistantPage: React.FC = () => {
  const { location } = useLocation();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `Hello! I am BreatheSmart AI, your urban air quality companion. I am grounded in live atmospheric readings for ${location.city}. How can I assist you with your routines, home ventilation, or travel decisions today?`,
      sources: ['Open-Meteo Air Quality', 'Groq openai/gpt-oss-120b'],
      followups: [
        'Is it safe for my child to play outdoors today?',
        'When is the best time to open my windows?',
        'How should I set my HEPA purifier tonight?',
      ],
    },
  ]);

  const mutation = useMutation({
    mutationFn: (msg: string) =>
      api.chatWithAssistant(msg, location.latitude, location.longitude, messages.slice(-4)),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.message,
          sources: data.context_sources,
          followups: data.suggested_followups,
        },
      ]);
    },
  });

  const handleSend = (text: string) => {
    if (!text.trim() || mutation.isPending) return;

    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    mutation.mutate(text);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      {/* Header Context Pill */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Conversational AI Assistant</h1>
          <p className="text-xs text-slate-500">
            Powered by Groq gpt-oss-120b • Strictly grounded in verified {location.city} sensor readings
          </p>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-800 text-xs font-semibold rounded-full border border-emerald-200">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
          <span>Live Context Active</span>
        </div>
      </div>

      {/* Chat Transcript Container */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs h-[520px] flex flex-col overflow-hidden">
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {m.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-emerald-600 text-white rounded-tr-xs'
                    : 'bg-slate-100 text-slate-800 rounded-tl-xs'
                }`}
              >
                <p className="whitespace-pre-wrap">{m.content}</p>

                {m.sources && m.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-200 text-[10px] text-slate-500 flex items-center gap-2">
                    <span>Grounded in:</span>
                    {m.sources.map((s, idx) => (
                      <span key={idx} className="bg-white px-1.5 py-0.5 rounded border border-slate-200">
                        {s}
                      </span>
                    ))}
                  </div>
                )}

                {m.followups && m.followups.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-slate-200/60">
                    <span className="text-[11px] font-bold text-slate-600 block mb-1.5">Suggested Questions:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {m.followups.map((q, qIdx) => (
                        <button
                          key={qIdx}
                          onClick={() => handleSend(q)}
                          className="text-left text-xs bg-white text-emerald-800 hover:bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200 transition-colors"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {m.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-800 text-white flex items-center justify-center shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {mutation.isPending && (
            <div className="flex gap-3 justify-start items-center text-xs text-slate-500 bg-slate-50 p-3 rounded-xl max-w-sm">
              <Loader2 className="w-4 h-4 animate-spin text-emerald-600" />
              <span>Analyzing atmospheric context with Groq...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-3 bg-slate-50 border-t border-slate-200">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(input);
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Ask anything about air quality in ${location.city}...`}
              className="flex-1 px-4 py-2 text-sm bg-white border border-slate-300 rounded-xl focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
            <button
              type="submit"
              disabled={!input.trim() || mutation.isPending}
              className="p-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl transition-colors focus-visible:ring-2 focus-visible:ring-emerald-500"
              aria-label="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
