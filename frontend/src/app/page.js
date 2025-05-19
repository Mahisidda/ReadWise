"use client";

import { useState } from "react";
import BookCard from "./components/BookCard";

const GENRE_OPTIONS = [
  { label: "📖 Fiction", userId: 276725 },
  { label: "🧠 Self-Help", userId: 277427 },
  { label: "🚀 Sci-Fi", userId: 276797 },
  { label: "💔 Romance", userId: 276999 },
  { label: "🔍 Mystery", userId: 276747 },
];

export default function Home() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedGenre, setSelectedGenre] = useState(null);
  const [error, setError] = useState('');

  const getRecommendations = async (userId) => {
    setLoading(true);
    setError('');
    setSelectedGenre(userId);
    try {
      const res = await fetch(`http://localhost:8001/recommend?user_id=${userId}`);
      if (!res.ok) {
        throw new Error('Failed to fetch recommendations');
      }
      const data = await res.json();
      setRecommendations(data);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      setError('Failed to load recommendations. Please try again.');
    }
    setLoading(false);
  };

  return (
    <main className="min-h-screen p-8 max-w-7xl mx-auto">
      <h1 className="text-4xl font-bold text-center mb-4">
        📚 Find Your Next Favorite Book
      </h1>
      
      <p className="text-center text-gray-600 mb-8">
        Select your mood or genre to get personalized picks:
      </p>

      <div className="flex flex-wrap gap-4 justify-center mb-8">
        {GENRE_OPTIONS.map((opt) => (
          <button
            key={opt.userId}
            onClick={() => getRecommendations(opt.userId)}
            className={`px-6 py-3 rounded-xl text-base font-medium transition-all duration-200
              ${selectedGenre === opt.userId 
                ? 'bg-blue-600 text-white shadow-lg' 
                : 'bg-white text-gray-800 border border-gray-200 hover:shadow-md hover:-translate-y-0.5'
              }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="text-center my-8">
          <div className="inline-block w-10 h-10 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="mt-4 text-gray-600">Loading recommendations...</p>
        </div>
      )}

      {error && (
        <p className="text-red-500 text-center my-8">
          {error}
        </p>
      )}

      {!loading && !error && recommendations.length === 0 && (
        <p className="text-gray-600 text-center my-8">
          No recommendations yet. Pick a genre above to get started!
        </p>
      )}

      <div className="flex flex-wrap gap-6 justify-center mt-8">
        {recommendations.map((book, index) => (
          <BookCard key={index} book={book} />
        ))}
      </div>
    </main>
  );
} 