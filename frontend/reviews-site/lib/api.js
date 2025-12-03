const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getMovie(movieId) {
  const res = await fetch(`${API_URL}/movies/${movieId}`);

  if (!res.ok) {
    throw new Error("Failed to fetch movie");
  }

  return res.json();
}