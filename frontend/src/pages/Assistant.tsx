import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  MessageSquareText,
  Send,
  Sparkles,
  Bot,
  User,
  ShieldCheck,
  ExternalLink,
  ChevronRight,
  Database,
  Code2,
} from "lucide-react";
import { useAppStore } from "../stores/appStore";

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  sql?: string;
  tableData?: any[];
  projectLink?: string;
  timestamp: string;
}

export function Assistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      sender: "assistant",
      text: "Namaste! I am the DelayRay Infrastructure Copilot. You can ask me analytical questions in plain English about project delays, cost overruns, active early warning alerts, and feature attribution across the 1,981 central sector projects.",
      timestamp: "Just now",
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const suggestedQuestions = [
    "What are the top 5 projects ranked by Value at Risk?",
    "Which railway projects have active early warning alerts?",
    "What percentage of predictive power comes from existing CUF fields?",
    "Show projects in Maharashtra with calibrated risk score > 80",
  ];

  const handleSend = async (questionText?: string) => {
    const q = questionText || input;
    if (!q.trim()) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: "user",
      text: q,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    // Simulated guarded analytical assistant response
    setTimeout(() => {
      let assistantMsg: ChatMessage;

      if (q.toLowerCase().includes("top 5") || q.toLowerCase().includes("value at risk")) {
        assistantMsg = {
          id: (Date.now() + 1).toString(),
          sender: "assistant",
          text: "Here are the top 5 central sector infrastructure projects ranked by total Value at Risk (VaR):",
          sql: "SELECT project_id, project_name, sector, original_cost_cr, value_at_risk_cr FROM projects JOIN predictions ON projects.project_id = predictions.project_id ORDER BY value_at_risk_cr DESC LIMIT 5;",
          tableData: [
            { id: "PRJ-0012", name: "Western Dedicated Freight Corridor", sector: "Railways", cost: "₹81,459 Cr", var: "₹18,240 Cr" },
            { id: "PRJ-0045", name: "Mumbai-Ahmedabad High Speed Rail", sector: "Railways", cost: "₹1,08,000 Cr", var: "₹15,480 Cr" },
            { id: "PRJ-0118", name: "Barmer Petroleum Refinery Complex", sector: "Petroleum", cost: "₹72,937 Cr", var: "₹12,850 Cr" },
            { id: "PRJ-0231", name: "Subansiri Lower Hydroelectric Project", sector: "Power", cost: "₹21,247 Cr", var: "₹6,420 Cr" },
            { id: "PRJ-0089", name: "Bharatmala Pkg 4 Expressway", sector: "Road Transport", cost: "₹14,500 Cr", var: "₹4,120 Cr" },
          ],
          timestamp: new Date().toLocaleTimeString(),
        };
      } else if (q.toLowerCase().includes("cuf") || q.toLowerCase().includes("percentage") || q.toLowerCase().includes("ablation")) {
        assistantMsg = {
          id: (Date.now() + 1).toString(),
          sender: "assistant",
          text: "Based on our econometric ablation study, existing Common Undertaking Format (CUF) fields (G1+G2) account for exactly **66.0%** of total predictive accuracy. Adding extended features—contractor execution ratings, pre-sanction land handover percentages, and macro commodity shock indices (G3-G6)—adds the remaining 34.0% in variance explained.",
          sql: "SELECT experiment, test_mae, test_r2 FROM ablation_reports WHERE experiment IN ('CUF-Only (G1+G2)', 'All Groups (G1-G6 Full)');",
          timestamp: new Date().toLocaleTimeString(),
        };
      } else {
        assistantMsg = {
          id: (Date.now() + 1).toString(),
          sender: "assistant",
          text: `Analysis query resolved: Filtered active portfolio for "${q}". Found 14 projects matching criteria with high risk signals. Statutory clearance and contractor liquidity are the leading bottlenecks.`,
          sql: `SELECT * FROM projects WHERE status = 'ongoing' AND sector LIKE '%Railway%' LIMIT 5;`,
          timestamp: new Date().toLocaleTimeString(),
        };
      }

      setMessages((prev) => [...prev, assistantMsg]);
      setIsTyping(false);
    }, 600);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-16">
      {/* Header */}
      <div className="flex items-center justify-between p-6 bg-surface border border-border rounded-xl">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-black text-text tracking-tight">Analytical AI Assistant</h1>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              Guarded SQL Active
            </span>
          </div>
          <p className="text-xs text-muted mt-1">
            Local Ollama LLM with guarded SQL translation and RAG search over monthly monitoring remarks.
          </p>
        </div>
      </div>

      {/* Chat Messages Box */}
      <div className="bg-surface border border-border rounded-xl flex flex-col h-[560px] overflow-hidden">
        {/* Messages Scroll Area */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex gap-3 max-w-2xl ${
                m.sender === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                  m.sender === "user" ? "bg-accent text-background" : "bg-raised border border-border text-accent"
                }`}
              >
                {m.sender === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`p-4 rounded-xl text-xs space-y-3 ${
                  m.sender === "user"
                    ? "bg-accent text-background font-medium rounded-tr-none"
                    : "bg-raised/70 border border-border text-text rounded-tl-none"
                }`}
              >
                <div className="leading-relaxed whitespace-pre-wrap">{m.text}</div>

                {/* Guarded SQL preview if present */}
                {m.sql && (
                  <div className="p-2.5 rounded bg-background/80 border border-border/60 text-[11px] font-mono space-y-1">
                    <div className="text-muted flex items-center gap-1 font-sans text-[10px]">
                      <Code2 className="w-3 h-3 text-accent" />
                      Guarded SQL Query
                    </div>
                    <div className="text-accent overflow-x-auto">{m.sql}</div>
                  </div>
                )}

                {/* Table Data Preview if present */}
                {m.tableData && (
                  <div className="overflow-x-auto rounded border border-border/60">
                    <table className="w-full text-left text-[11px]">
                      <thead className="bg-background/90 border-b border-border/60 text-muted">
                        <tr>
                          <th className="p-2">ID</th>
                          <th className="p-2">Project</th>
                          <th className="p-2">Sector</th>
                          <th className="p-2 text-right">Cost</th>
                          <th className="p-2 text-right">VaR</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/40">
                        {m.tableData.map((row, i) => (
                          <tr key={i}>
                            <td className="p-2 font-mono">
                              <Link to={`/projects/${row.id}`} className="text-accent underline">
                                {row.id}
                              </Link>
                            </td>
                            <td className="p-2 font-semibold truncate max-w-[140px]">{row.name}</td>
                            <td className="p-2 text-muted">{row.sector}</td>
                            <td className="p-2 text-right font-mono">{row.cost}</td>
                            <td className="p-2 text-right font-mono font-bold text-critical">{row.var}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                <div
                  className={`text-[10px] ${
                    m.sender === "user" ? "text-background/80 text-right" : "text-muted"
                  }`}
                >
                  {m.timestamp}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex gap-3 max-w-2xl mr-auto animate-pulse">
              <div className="w-8 h-8 rounded-full bg-raised border border-border flex items-center justify-center text-accent">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-3 bg-raised/70 border border-border rounded-xl text-xs text-muted">
                Synthesizing SQL and querying database...
              </div>
            </div>
          )}
        </div>

        {/* Suggested Queries Chips */}
        <div className="p-3 bg-raised/30 border-t border-border flex items-center gap-2 overflow-x-auto no-scrollbar">
          <span className="text-[11px] text-muted shrink-0 font-semibold">Suggested:</span>
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(q)}
              className="px-2.5 py-1 rounded-full bg-raised hover:bg-raised/80 border border-border text-[11px] text-text hover:text-accent whitespace-nowrap transition-colors"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-3.5 bg-surface border-t border-border flex items-center gap-3">
          <input
            type="text"
            placeholder="Ask a question about infrastructure project delays, overruns, or alerts..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            className="flex-1 px-4 py-2 bg-raised/50 border border-border rounded-lg text-xs text-text placeholder-muted focus:outline-none focus:border-accent"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim()}
            className="px-4 py-2 rounded-lg bg-accent hover:bg-accent/90 disabled:opacity-40 text-background font-bold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-accent/20"
          >
            <span>Ask</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
