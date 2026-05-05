"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Send, Bot, User, Code, Terminal, 
  Settings, FolderTree, Zap, Shield, 
  Activity, Download, RefreshCw, Layers, Cpu
} from "lucide-react";
import axios from "axios";
import { cn } from "../lib/utils";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7860";

export default function DashboardContent() {
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

  useEffect(() => {
    const initializeSession = async () => {
      let savedId = localStorage.getItem("infinity_session_id");
      
      if (!savedId || savedId !== "session_ihzxrn89j") {
        savedId = "session_ihzxrn89j";
        localStorage.setItem("infinity_session_id", "session_ihzxrn89j");
      }

      if (savedId) {
        setSessionId(savedId);
        axios.get(`${API_BASE}/chat/${savedId}`).then(res => {
          if (res.data.history && res.data.history.length > 0) setMessages(res.data.history);
        }).catch(err => console.error("History fetch error:", err));

        axios.get(`${API_BASE}/status/${savedId}`).then(res => {
          if (res.data.progress) setProgress(res.data.progress);
          if (res.data.phase) setPhase(res.data.phase);
          if (res.data.state === "EXECUTION") setStatus("executing");
          else if (res.data.state === "COMPLETED") setStatus("completed");
        }).catch(err => console.error("Status fetch error:", err));
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

  useEffect(() => {
    if (!sessionId) return;
    let socket: WebSocket;
    let heartbeat: any;
    let reconnectTimeout: any;

    const connect = () => {
      const wsHost = API_BASE.replace("http", "ws");
      socket = new WebSocket(`${wsHost}/ws/${sessionId}`);

      socket.onopen = () => {
        heartbeat = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) socket.send("ping");
        }, 30000);
      };

      socket.onmessage = (event) => {
        if (event.data === "pong") return;
        try {
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
        } catch (e) {}
      };

      socket.onclose = () => {
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
      setMessages((prev) => [...prev, { role: "ai", content: "Error: Could not reach the Grandmaster Backend." }]);
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
      {/* Sidebar Left */}
      <div className="w-16 flex flex-col items-center py-6 glass border-r border-slate-800 gap-8">
        <div className="p-2 bg-indigo-600 rounded-xl shadow-lg">
          <Zap className="w-6 h-6 text-white" />
        </div>
        <div className="flex flex-col gap-6 text-slate-400">
          <Activity className="w-6 h-6 hover:text-indigo-400 cursor-pointer" />
          <Layers className="w-6 h-6 hover:text-indigo-400 cursor-pointer" />
          <FolderTree className="w-6 h-6 hover:text-indigo-400 cursor-pointer" />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        <header className="h-16 glass-card flex items-center justify-between px-8 z-10">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
              INFINITY CHAT
            </h1>
            <div className="flex items-center gap-2 px-3 py-1 bg-slate-800/50 rounded-full border border-slate-700">
              <div className={cn("w-2 h-2 rounded-full", status === "idle" ? "bg-emerald-500" : "bg-amber-500 animate-pulse")} />
              <span className="text-xs font-medium text-slate-300 capitalize">{status}</span>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex flex-col items-end">
              <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Phase</span>
              <span className="text-xs font-mono text-indigo-300">{phase}</span>
            </div>
            <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden border border-slate-700">
              <div className="h-full bg-indigo-500 transition-all duration-500" style={{ width: `${progress}%` }} />
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-8 flex flex-col gap-6 scroll-smooth">
          {messages.map((msg, idx) => (
            <div key={idx} className={cn("flex gap-4 max-w-[85%]", msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto")}>
              <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center shrink-0", msg.role === "ai" ? "bg-indigo-600" : "bg-slate-700")}>
                {msg.role === "ai" ? <Bot className="w-6 h-6" /> : <User className="w-6 h-6" />}
              </div>
              <div className={cn("p-4 rounded-2xl text-sm leading-relaxed", msg.role === "ai" ? "glass-card text-slate-200" : "bg-indigo-600 text-white")}>
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </main>

        <div className="p-8 pt-0">
          <div className="relative glass-card p-2 rounded-2xl flex items-center gap-2 border border-slate-700/50">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Requirement..."
              className="flex-1 bg-transparent border-none outline-none text-sm py-3 px-4"
            />
            <button onClick={handleSend} disabled={loading} className="p-3 bg-indigo-600 rounded-xl text-white">
              {loading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Sidebar Right */}
      <div className="w-80 glass border-l border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">System Logs</h2>
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
        </div>
        <div className="flex-1 p-6 font-mono text-[11px] overflow-y-auto flex flex-col gap-3">
          {logs.map((log, idx) => (
            <div key={idx} className={cn("flex gap-2", log.type === "error" ? "text-rose-400" : "text-indigo-300/80")}>
              <span className="text-slate-600">[{log.time}]</span>
              <span>{log.msg}</span>
            </div>
          ))}
        </div>
        <div className="p-6 border-t border-slate-800 bg-slate-900/50">
          <div 
            onClick={handleDownload}
            className="group glass-card p-4 rounded-xl border border-indigo-500/30 hover:border-indigo-400 cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <Layers className="w-5 h-5 text-indigo-400" />
              <span className="text-sm font-bold text-slate-200">Empire Build ZIP</span>
              <Download className="ml-auto w-4 h-4 text-slate-500" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
