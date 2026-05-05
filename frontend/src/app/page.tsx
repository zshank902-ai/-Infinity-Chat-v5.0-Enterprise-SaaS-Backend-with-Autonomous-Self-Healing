"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Send, Bot, User, Code, Terminal, 
  Settings, FolderTree, Zap, Shield, 
  Activity, Download, RefreshCw, Layers 
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { cn } from "@/lib/utils";

const API_BASE = "http://localhost:8000";

export default function Dashboard() {
  const [messages, setMessages] = useState([
    { role: "ai", content: "Infinity Core v5.0 Online. Systems Nominal. How can I assist you in your industrial build today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(`session_${Math.random().toString(36).substr(2, 9)}`);
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState("Standby");
  const [status, setStatus] = useState("idle"); // idle, thinking, executing, completed
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);
    setStatus("thinking");

    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        message: userMessage,
        session_id: sessionId
      });

      setMessages((prev) => [...prev, { role: "ai", content: res.data.response }]);
      setProgress(res.data.progress || 0);
      setPhase(res.data.phase || "Processing");
      
      if (res.data.state === "EXECUTION") setStatus("executing");
      else if (res.data.state === "COMPLETED") setStatus("completed");
      else setStatus("idle");

    } catch (error) {
      setMessages((prev) => [...prev, { role: "ai", content: "Error: Could not reach the Grandmaster Backend. Please check your connection." }]);
      setStatus("idle");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#0f172a] text-slate-100 overflow-hidden font-sans">
      {/* Sidebar Left - Navigation */}
      <div className="w-16 flex flex-col items-center py-6 glass border-r border-slate-800 gap-8">
        <div className="p-2 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-500/20">
          <Zap className="w-6 h-6 text-white" />
        </div>
        <div className="flex flex-col gap-6 text-slate-400">
          <Activity className="w-6 h-6 hover:text-indigo-400 cursor-pointer transition-colors" />
          <Layers className="w-6 h-6 hover:text-indigo-400 cursor-pointer transition-colors" />
          <FolderTree className="w-6 h-6 hover:text-indigo-400 cursor-pointer transition-colors" />
          <div className="mt-auto mb-4 flex flex-col gap-6">
            <Shield className="w-6 h-6 hover:text-indigo-400 cursor-pointer transition-colors" />
            <Settings className="w-6 h-6 hover:text-indigo-400 cursor-pointer transition-colors" />
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Top Header */}
        <header className="h-16 glass-card flex items-center justify-between px-8 z-10">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
              INFINITY CHAT <span className="text-xs font-mono text-slate-500 ml-2">V5.0 ENT</span>
            </h1>
            <div className="flex items-center gap-2 px-3 py-1 bg-slate-800/50 rounded-full border border-slate-700">
              <div className={cn("w-2 h-2 rounded-full", status === "idle" ? "bg-emerald-500" : "bg-amber-500 animate-pulse")} />
              <span className="text-xs font-medium text-slate-300 capitalize">{status}</span>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex flex-col items-end">
              <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">System Phase</span>
              <span className="text-xs font-mono text-indigo-300">{phase}</span>
            </div>
            <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden border border-slate-700">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
              />
            </div>
          </div>
        </header>

        {/* Chat / Viewport */}
        <main className="flex-1 overflow-y-auto p-8 flex flex-col gap-6 scroll-smooth">
          <AnimatePresence>
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                  "flex gap-4 max-w-[85%]",
                  msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                )}
              >
                <div className={cn(
                  "w-10 h-10 rounded-xl flex items-center justify-center shadow-lg shrink-0",
                  msg.role === "ai" ? "bg-indigo-600 shadow-indigo-500/20" : "bg-slate-700 shadow-slate-900/40"
                )}>
                  {msg.role === "ai" ? <Bot className="w-6 h-6" /> : <User className="w-6 h-6" />}
                </div>
                <div className={cn(
                  "p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap",
                  msg.role === "ai" ? "glass-card text-slate-200" : "bg-indigo-600 text-white"
                )}>
                  {msg.content}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={chatEndRef} />
        </main>

        {/* Bottom Input Area */}
        <div className="p-8 pt-0">
          <div className="relative glass-card p-2 rounded-2xl flex items-center gap-2 border border-slate-700/50 shadow-2xl">
            <button className="p-3 hover:bg-slate-800 rounded-xl transition-colors text-slate-400">
              <Layers className="w-5 h-5" />
            </button>
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Give requirement to your Grandmaster Agent..."
              className="flex-1 bg-transparent border-none outline-none text-sm py-3 px-2 placeholder:text-slate-500"
            />
            <button 
              onClick={handleSend}
              disabled={loading}
              className={cn(
                "p-3 rounded-xl transition-all shadow-lg",
                loading ? "bg-slate-800 text-slate-600" : "bg-indigo-600 text-white hover:bg-indigo-500 hover:scale-105 active:scale-95"
              )}
            >
              {loading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </div>
          <p className="text-[10px] text-center mt-3 text-slate-600 uppercase tracking-[0.2em] font-bold">
            Autonomous Industrial Construction Swarm Active
          </p>
        </div>
      </div>

      {/* Sidebar Right - System Logs / Files */}
      <div className="w-80 glass border-l border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
            <Terminal className="w-4 h-4" /> System Logs
          </h2>
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
        </div>
        
        <div className="flex-1 p-6 font-mono text-[11px] text-indigo-300/80 overflow-y-auto flex flex-col gap-3">
          <div className="flex gap-2">
            <span className="text-slate-600">[00:00:01]</span>
            <span>Kernel initialized.</span>
          </div>
          <div className="flex gap-2">
            <span className="text-slate-600">[00:00:02]</span>
            <span>Redis persistence handshake successful.</span>
          </div>
          <div className="flex gap-2">
            <span className="text-slate-600">[00:00:05]</span>
            <span>Swarm agents synchronized.</span>
          </div>
          {loading && (
            <div className="flex gap-2 text-amber-400 animate-pulse">
              <span className="text-slate-600">[NOW]</span>
              <span>Agent is scavenging information...</span>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-slate-800 bg-slate-900/50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500">Workspace</h2>
            <Download className="w-4 h-4 text-slate-500 hover:text-indigo-400 cursor-pointer" />
          </div>
          <div className="space-y-2 overflow-y-auto max-h-48">
            {files.length > 0 ? files.map((file, idx) => (
              <div key={idx} className="flex items-center gap-2 text-xs text-slate-400 hover:bg-slate-800/50 p-2 rounded cursor-pointer transition-colors group">
                <Code className="w-4 h-4 text-indigo-400 group-hover:text-indigo-300" />
                <div className="flex flex-col">
                  <span className="text-slate-300">{file.name}</span>
                  <span className="text-[9px] text-slate-600 font-mono">{file.path}</span>
                </div>
              </div>
            )) : (
              <div className="text-[10px] text-slate-600 text-center py-4 italic">No files generated yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
