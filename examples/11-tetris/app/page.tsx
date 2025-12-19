import { TetrisGame } from "./components/TetrisGame";
import { HighScores } from "./components/HighScores";
import { UserButton } from "./components/UserButton";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-end mb-4">
          <UserButton />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 flex justify-center">
            <TetrisGame />
          </div>
          <div>
            <HighScores />
          </div>
        </div>
      </div>
    </main>
  );
}
