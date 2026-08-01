import { useState } from "react";
import { generateTheme } from "@/utils/api";

export function useThemeGenerator() {
  const [theme, setTheme] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const generate = async (prompt: string): Promise<any> => {
    setLoading(true);
    try {
      const data = await generateTheme(prompt);
      const nextTheme = data?.theme ?? null;
      setTheme(nextTheme);
      return nextTheme;
    } catch (e) {
      console.error(e);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { theme, loading, generate };
}