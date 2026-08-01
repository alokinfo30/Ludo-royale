export default function ChatBox({ messages }: { messages: string[] }) {
  return (
    <div className="w-64 h-40 overflow-y-auto border p-2 bg-white">
      {messages.map((msg, i) => (
        <p key={i} className="text-sm mb-1">{msg}</p>
      ))}
    </div>
  );
}