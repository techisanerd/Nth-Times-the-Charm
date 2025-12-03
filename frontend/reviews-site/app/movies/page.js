"use client";

import { use, useEffect, useState } from "react";

export default function MovieList() {

  const [movies, setMovies] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/getMovies`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch movies");
        return res.json();
      })
      .then(setMovies)
      .catch((err) => setError(err.message));
  }, []);

  

  if (error) return <p>Error: {error}</p>;
  if (!movies) return <p>Loading…</p>;

  
  return (
    <ul>
        {movies.map((movie) => (
          <li key={movie.title}>
            <div style={{ maxWidth: '600px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', fontFamily: 'Arial, sans-serif' }}>
                <a href={"/movies/" + movie.title}>
                    <h1>{movie.title} - {movie.rating} ⭐</h1>
                    {movie.description}
                </a>
            </div>

          </li>
        ))}
    </ul>
  );
}
