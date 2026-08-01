export default function Token({ color, id, style, themeColor }: any) {
  const bg = themeColor || getDefaultColor(color);
  return (
    <div
      className="w-8 h-8 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-xs font-bold"
      style={{ background: bg, ...style }}
    >
      {id}
    </div>
  );
}

function getDefaultColor(c: string) {
  const map: any = { RED: "#e53e3e", GREEN: "#38a169", YELLOW: "#d69e2e", BLUE: "#3182ce" };
  return map[c] || "#aaa";
}