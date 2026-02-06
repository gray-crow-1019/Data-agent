export default function Message({ role, content }: { role: "user" | "assistant"; content: string }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
          isUser
            ? "bg-[color:var(--accent)] text-white"
            : "bg-white/80 text-[color:var(--ink)]"
        }`}
      >
        <div className="text-xs uppercase tracking-[0.2em] opacity-70">
          {isUser ? "你" : "Agent"}
        </div>
        <p className="mt-2 leading-relaxed">{content}</p>
      </div>
    </div>
  );
}
