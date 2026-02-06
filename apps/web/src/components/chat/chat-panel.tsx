import Message from "./message";

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatPanel({ messages }: { messages: ChatMessage[] }) {
  return (
    <section className="space-y-4">
      {messages.map((msg, idx) => (
        <Message key={idx} role={msg.role} content={msg.content} />
      ))}
    </section>
  );
}
