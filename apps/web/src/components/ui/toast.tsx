export default function Toast({ message }: { message: string }) {
  return (
    <div className="rounded-full border border-[color:var(--border)] bg-white/80 px-4 py-2 text-xs text-[color:var(--muted)] shadow-lg">
      {message}
    </div>
  );
}
