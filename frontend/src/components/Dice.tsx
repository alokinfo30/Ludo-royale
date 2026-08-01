export default function Dice({ value, onRoll }: { value: number | null; onRoll: () => void }) {
  return (
    <div className="flex flex-col items-center space-y-2">
      <div className="w-16 h-16 bg-white border-2 border-gray-800 rounded-lg flex items-center justify-center text-3xl font-bold">
        {value ?? "?"}
      </div>
      <button
        onClick={onRoll}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Roll Dice
      </button>
    </div>
  );
}