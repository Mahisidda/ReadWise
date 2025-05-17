import { useState } from 'react';

export default function Home() {
  const [userId, setUserId] = useState('');
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const getRecommendations = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`http://localhost:8000/recommend?user_id=${userId}`);
      if (!res.ok) {
        throw new Error('User not found or server error');
      }
      const data = await res.json();
      setRecs(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>📚 Book Recommendation System</h1>
      <input
        type="number"
        placeholder="Enter User ID"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        style={{ marginRight: '1rem', padding: '0.5rem' }}
      />
      <button onClick={getRecommendations}>Get Recommendations</button>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <ul>
        {recs.map((book, index) => (
          <li key={index}>
            <strong>{book.Book_Title}</strong> (Score: {book.Recommendation_Score.toFixed(2)})
          </li>
        ))}
      </ul>
    </div>
  );
}
