"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Send, Bot, User, Code, Terminal, 
  Settings, FolderTree, Zap, Shield, 
  Activity, Download, RefreshCw, Layers, Cpu
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { cn } from "@/lib/utils";
import dynamic from "next/dynamic";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7860";

function DashboardContent() {
  const [messages, setMessages] = useState([
    { role: "ai", content: "Infinity Core v5.0 Online. Systems Nominal. How can I assist you in your industrial build today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [logs, setLogs] = useState<{msg: string, time: string, type: string}[]>([]);
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState("Standby");
  const [status, setStatus] = useState("idle"); // idle, thinking, executing, completed
  const [files, setFiles] = useState<{name: string, path: string, type: string}[]>([]);
  
  const chatEndRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const initializeSession = async () => {
      let savedId = localStorage.getItem("infinity_session_id");
      
      // FORCE RECOVERY: For this specific debug, prioritize the known active session
      if (!savedId || savedId !== "session_ihzxrn89j") {
        savedId = "session_ihzxrn89j";
        localStorage.setItem("infinity_session_id", "session_ihzxrn89j");
      }

      if (savedId) {
        setSessionId(savedId);
        // Fetch history
        axios.get(`${API_BASE}/chat/${savedId}`).then(res => {
          if (res.data.history && res.data.history.length > 0) setMessages(res.data.history);
        }).catch(err => console.error("History fetch error:", err));

        // Fetch status (This will also trigger auto-resume on backend!)
        axios.get(`${API_BASE}/status/${savedId}`).then(res => {
          if (res.data.progress) setProgress(res.data.progress);
          if (res.data.phase) setPhase(res.data.phase);
          if (res.data.state === "EXECUTION") setStatus("executing");
          else if (res.data.state === "COMPLETED") setStatus("completed");
        }).catch(err => console.error("Status fetch error:", err));
      } else {
        const newId = `session_${Math.random().toString(36).substr(2, 9)}`;
        setSessionId(newId);
        localStorage.setItem("infinity_session_id", newId);
      }
    };

    initializeSession();
  }, []);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // WebSocket for Real-time Streaming (With Heartbeat & Auto-Reconnect)
  useEffect(() => {
    if (!sessionId) return;
    let socket: WebSocket;
    let heartbeat: any;
    let reconnectTimeout: any;

    const connect = () => {
      const wsHost = API_BASE.replace("http", "ws");
      socket = new WebSocket(`${wsHost}/ws/${sessionId}`);

      socket.onopen = () => {
        console.log("WebSocket Heartbeat Started.");
        heartbeat = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) socket.send("ping");
        }, 30000); // 30s Heartbeat
      };

      socket.onmessage = (event) => {
        if (event.data === "pong") return;
        const data = JSON.parse(event.data);
        if (data.type === "status") {
          setProgress(data.progress);
          setPhase(data.phase);
          if (data.state === "COMPLETED") setStatus("completed");
        } else if (data.type === "log") {
          setLogs(prev => [{
            msg: data.message,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            type: data.log_type
          }, ...prev].slice(0, 50));
        }
      };

      socket.onclose = () => {
        console.log("WebSocket connection lost. Reconnecting in 5s...");
        clearInterval(heartbeat);
        reconnectTimeout = setTimeout(connect, 5000);
      };
    };

    connect();
    return () => {
      if (socket) socket.close();
      clearInterval(heartbeat);
      clearTimeout(reconnectTimeout);
    };
  }, [sessionId]);

  // Fetch files every 5 seconds if a session is active
  useEffect(() => {
    const fetchFiles = async () => {
      if (!sessionId) return;
      try {
        const res = await axios.get(`${API_BASE}/files/${sessionId}`);
        setFiles(res.data.files || []);
      } catch (err) {
        console.error("File sync error:", err);
      }
    };
    
    fetchFiles();
    const interval = setInterval(fetchFiles, 5000);
    return () => clearInterval(interval);
  }, [sessionId]);

  const handleSend = async () => {
    if (!input.trim() || loading || !sessionId) return;

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

  const handleDownload = () => {
    if (!sessionId) return;
    window.open(`${API_BASE}/download/${sessionId}`, "_blank");
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
        
        <div className="flex-1 p-6 font-mono text-[11px] overflow-y-auto flex flex-col gap-3">
          {logs.length > 0 ? logs.map((log, idx) => (
            <div key={idx} className={cn("flex gap-2", 
              log.type === "success" ? "text-emerald-400" : 
              log.type === "error" ? "text-rose-400" : "text-indigo-300/80")}>
              <span className="text-slate-600">[{log.time}]</span>
              <span>{log.msg}</span>
            </div>
          )) : (
            <>
              <div className="flex gap-2 text-indigo-300/80">
                <span className="text-slate-600">[00:00:01]</span>
                <span>Kernel initialized.</span>
              </div>
              <div className="flex gap-2 text-indigo-300/80">
                <span className="text-slate-600">[00:00:02]</span>
                <span>Redis persistence handshake successful.</span>
              </div>
              <div className="flex gap-2 text-indigo-300/80">
                <span className="text-slate-600">[00:00:05]</span>
                <span>Swarm agents synchronized.</span>
              </div>
            </>
          )}
          {loading && (
            <div className="flex gap-2 text-amber-400 animate-pulse">
              <span className="text-slate-600">[NOW]</span>
              <span>Agent is scavenging information...</span>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-slate-800 bg-slate-900/50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500">Project Package</h2>
          </div>
          
          <div 
            onClick={handleDownload}
            className="group glass-card p-4 rounded-xl border border-indigo-500/30 hover:border-indigo-400 transition-all cursor-pointer bg-indigo-500/5 hover:bg-indigo-500/10"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-indigo-600/20 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                <Layers className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-bold text-slate-200">Empire Build ZIP</span>
                <span className="text-[10px] text-slate-500 font-mono">Ready for deployment</span>
              </div>
              <Download className="ml-auto w-4 h-4 text-slate-500 group-hover:text-indigo-400 group-hover:animate-bounce" />
            </div>
            
            <div className="mt-4 flex items-center justify-between">
              <span className="text-[9px] text-slate-600 uppercase tracking-tighter">Full Source Code</span>
              <span className="text-[9px] py-0.5 px-2 bg-emerald-500/20 text-emerald-400 rounded-full border border-emerald-500/30">Stable</span>
            </div>
          </div>

          <p className="text-[9px] text-slate-600 mt-4 italic text-center">
            Click to download the entire autonomous construction package.
          </p>
        </div>
      </div>
    </div>
  );
}


const DynamicDashboard = dynamic(() => Promise.resolve(DashboardContent), {
  ssr: false,
  loading: () => (
    <div className="h-screen w-full bg-[#020617] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Cpu className="w-12 h-12 text-indigo-500 animate-spin" />
        <p className="text-slate-400 text-sm font-mono animate-pulse">Initializing Neural Swarm...</p>
      </div>
    </div>
  )
});

export default function Dashboard() {
  return <DynamicDashboard />;
}
