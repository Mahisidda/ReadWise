"use client";

import { useState } from "react";

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

  const getRecommendations = async (userId) => {
    setLoading(true);
    setSelectedGenre(userId);
    try {
      const res = await fetch(`http://localhost:8000/recommend?user_id=${userId}`);
      const data = await res.json();
      setRecommendations(data);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>📚 Find Your Next Favorite Book</h1>
      <p>Select your mood or genre to get personalized picks:</p>

      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        {GENRE_OPTIONS.map((opt) => (
          <button
            key={opt.userId}
            onClick={() => getRecommendations(opt.userId)}
            style={{
              padding: "0.75rem 1.5rem",
              fontSize: "1rem",
              borderRadius: "12px",
              border: "1px solid #ccc",
              background: selectedGenre === opt.userId ? "#0070f3" : "#fff",
              color: selectedGenre === opt.userId ? "#fff" : "#000",
              cursor: "pointer",
            }}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {loading && <p>Loading recommendations...</p>}

      <ul style={{ marginTop: "2rem" }}>
        {recommendations.map((book, index) => (
          <li key={index}>
            <strong>{book.Book_Title}</strong> (Score: {book.Recommendation_Score.toFixed(2)})
          </li>
        ))}
      </ul>
    </div>
  );
}
