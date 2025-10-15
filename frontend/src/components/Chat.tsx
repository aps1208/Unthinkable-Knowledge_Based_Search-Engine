import { useState } from "react";
import ReactMarkdown from "react-markdown";
import API from "../api/client";

export default function Chat() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<{ q: string; a: string }[]>([]);

  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("query", query);
    try {
      const res = await API.post("/ask", formData);
      setAnswer(res.data.answer);
      setHistory((prev) => [...prev, { q: query, a: res.data.answer }]);
    } finally {
      setLoading(false);
      setQuery("");
    }
  };

  return (
    <div className="bg-white border rounded-xl shadow-sm p-4 sm:p-5 w-full">
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something..."
          className="flex-1 p-2 rounded border focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50"
          onKeyDown={(e) => {
            if (e.key === "Enter") handleAsk();
          }}
          disabled={loading}
        />
        <button
          onClick={handleAsk}
          className="inline-flex items-center justify-center whitespace-nowrap rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-green-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-green-500/50 disabled:opacity-60"
          disabled={loading}
        >
          {loading ? "Loading..." : "Ask"}
        </button>
      </div>

      <div className="mt-4 bg-gray-50 p-4 rounded max-h-96 overflow-y-auto space-y-4">
        {history.map((item, idx) => (
          <div key={idx} className="space-y-2">
            <div className="text-xs uppercase tracking-wide text-gray-500">You</div>
            <div className="bg-white border p-3 rounded">{item.q}</div>
            <div className="text-xs uppercase tracking-wide text-gray-500">Assistant</div>
            <div className="bg-white border p-3 rounded prose max-w-none">
              <ReactMarkdown>{item.a}</ReactMarkdown>
            </div>
          </div>
        ))}

        {!history.length && !loading && (
          <div className="text-sm text-gray-500">Ask a question to get started.</div>
        )}

        {loading && (
          <div className="text-sm text-gray-500">Thinking...</div>
        )}
      </div>
    </div>
  );
}
