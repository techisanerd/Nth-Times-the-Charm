"use client";

import { use, useEffect, useState } from "react";
import Reviews from "./Reviews";

export default function MoviePage({ params }) {
  const { movie } = use(params);

  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const [reviews, setReviews] = useState(null);
  const [reviewError, setReviewError] = useState(null);
  useEffect(() => {
    fetch(`/api/Movies/${movie}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch movie");
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, [movie]);

  

  useEffect(() => {
    fetch(`/api/Reviews/${movie}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch reviews");
        return res.json();
      })
      .then(setReviews)
      .catch((err) => setReviewError(err.message));
  }, [movie]);

  if (error) return <p>Error: {error}</p>;
  if (!data) return <p>Loading…</p>;

  if (reviewError) return <p>Error: {reviewError}</p>;
  if (!reviews) return <p>Loading…</p>;


  return (
  <div>
    <div style={{ maxWidth: '600px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', fontFamily: 'Arial, sans-serif' }}>
        
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px' }}>{data.title}</h1>
      <h1 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '10px' }}>{data.rating} / 10 ⭐</h1>
      <div>
        <strong>Description:</strong>
        <p>{data.description}</p>
      </div>
      <div style={{ marginBottom: '15px' }}>
        <div>Rating Count: {data.ratingCount}</div>
        <div>Reviews: {data.userReviews}</div>
      </div>
      <div style={{ marginBottom: '15px' }}>
        <div>Genres: {data.genres.join(', ')}</div>
        <div>Directors: {data.directors.join(', ')}</div>
        <div>Creators: {data.creators.join(', ')}</div>
        <div>Actors: {data.actors.join(', ')}</div>
        <div>Release Date: {data.releaseDate}</div>
        <div>Duration: {data.duration} Minutes</div>
      </div>
      
    </div>

    <Reviews reviews={reviews} />
  </div>
  );
}
