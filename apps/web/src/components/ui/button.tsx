import { ButtonHTMLAttributes } from "react";

const base =
  "inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium transition";

const variants: Record<string, string> = {
  primary: "bg-[color:var(--accent)] text-white shadow-glow hover:opacity-90",
  ghost: "border border-[color:var(--border)] text-[color:var(--ink)] hover:bg-white/40",
};

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
};

export default function Button({
  className = "",
  variant = "primary",
  ...props
}: ButtonProps) {
  const variantClass = variants[variant] ?? variants.primary;
  return <button className={`${base} ${variantClass} ${className}`} {...props} />;
}
