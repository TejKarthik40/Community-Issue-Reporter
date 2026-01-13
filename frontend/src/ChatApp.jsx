import React, { useState, useRef, useEffect } from "react";


function ChatApp() {
  const chatEndRef = useRef(null);
  const [messages, setMessages] = useState([
    { from: "bot", text: "Hello! Please describe your issue." }
  ]);
  const [input, setInput] = useState("");
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (msg) => {
    setMessages((msgs) => [...msgs, { from: "user", text: msg }]);
    setLoading(true);
    const res = await fetch("https://community-issue-reporter-kk98.onrender.com/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    setMessages((msgs) => [...msgs, { from: "bot", text: data.reply }]);
    setOptions(data.options || []);
    setLoading(false);
  };

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      sendMessage(input.trim());
      setInput("");
    }
  };

  const handleOption = (opt) => {
    sendMessage(opt);
    setOptions([]);
  };

    return (
      <div style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg,#43cea2 0%,#185a9d 100%)",
        padding: "0",
        margin: "0",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "Segoe UI, Arial, sans-serif"
      }}>
        <div style={{
          maxWidth: 500,
          width: "100%",
          margin: "40px auto",
          background: "rgba(255,255,255,0.98)",
          boxShadow: "0 4px 24px rgba(25,118,210,0.12)",
          borderRadius: 18,
          padding: 0,
          overflow: "hidden"
        }}>
          <div style={{
            textAlign: "center",
            fontWeight: 700,
            fontSize: "2rem",
            padding: "24px 0 10px 0",
            color: "#185a9d",
            letterSpacing: 1,
            background: "linear-gradient(90deg,#43cea2,#185a9d)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent"
          }}>
            Community Issue Reporter
          </div>
          <div style={{
            background: "#fff",
            borderRadius: 0,
            padding: "24px 24px 0 24px",
            minHeight: 340,
            maxHeight: 400,
            overflowY: "auto"
          }}>
            {messages.map((m, i) => (
              <div key={i} style={{ textAlign: m.from === "bot" ? "left" : "right", margin: "12px 0" }}>
                <span style={{
                  background: m.from === "bot" ? "#e3f2fd" : "#c8e6c9",
                  color: "#185a9d",
                  padding: "12px 20px",
                  borderRadius: 20,
                  display: "inline-block",
                  fontSize: "1.08rem",
                  boxShadow: m.from === "bot" ? "0 1px 6px #90caf9" : "0 1px 6px #a5d6a7",
                  fontWeight: m.from === "bot" ? 500 : 600
                }}>{m.text}</span>
              </div>
            ))}
            {options.length > 0 && (
              <div style={{ margin: "18px 0", display: "flex", gap: "12px", flexWrap: "wrap", justifyContent: "center" }}>
                {options.map((opt, i) => (
                  <button
                    key={i}
                    onClick={() => handleOption(opt)}
                    style={{
                      background: "linear-gradient(90deg,#1976d2,#64b5f6)",
                      color: "#fff",
                      border: "none",
                      borderRadius: 24,
                      padding: "12px 28px",
                      fontWeight: 600,
                      fontSize: "1.08rem",
                      cursor: "pointer",
                      boxShadow: "0 2px 12px rgba(25,118,210,0.12)",
                      transition: "background 0.2s"
                    }}
                  >{opt}</button>
                ))}
              </div>
            )}
            {loading && <div style={{ textAlign: "center", color: "#1976d2", margin: "12px 0" }}>...</div>}
            <div ref={chatEndRef} />
          </div>
          <div style={{ display: "flex", padding: "18px 24px 24px 24px", background: "#fff" }}>
            <input
              style={{
                flex: 1,
                padding: 14,
                borderRadius: 24,
                border: "1px solid #bdbdbd",
                fontSize: "1.08rem",
                outline: "none",
                boxShadow: "0 1px 4px #eee"
              }}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSend()}
              placeholder="Type your message..."
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              style={{
                marginLeft: 16,
                background: "linear-gradient(90deg,#43cea2,#185a9d)",
                color: "#fff",
                border: "none",
                borderRadius: 24,
                padding: "12px 28px",
                fontWeight: 600,
                fontSize: "1.08rem",
                cursor: loading ? "not-allowed" : "pointer",
                boxShadow: "0 2px 12px rgba(25,118,210,0.12)",
                transition: "background 0.2s"
              }}
            >Send</button>
          </div>
        </div>
      </div>
    );
}

export default ChatApp;
