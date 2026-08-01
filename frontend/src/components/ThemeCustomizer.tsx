"use client";
import { useState } from "react";
import { useThemeGenerator } from "@/hooks/useThemeGenerator";

export default function ThemeCustomizer({ onApply }: { onApply: (theme: any) => void }) {
  const [prompt, setPrompt] = useState("");
  const { loading, generate } = useThemeGenerator();

  const handleGenerate = async () => {
    const theme = await generate(prompt);
    if (theme) {
      onApply(theme);
    }
  };

  return (
    <div className="flex space-x-2">
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="e.g., Cyberpunk Mumbai street style"
        className="border px-2 py-1 rounded"
      />
      <button
        onClick={handleGenerate}
        disabled={loading}
        className="bg-purple-600 text-white px-3 py-1 rounded disabled:opacity-50"
      >
        {loading ? "Generating..." : "Generate Theme"}
      </button>
    </div>
  );
}