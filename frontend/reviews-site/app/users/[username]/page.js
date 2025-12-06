"use client"

import { use, useEffect, useState } from "react";

export default function UserPage({ params }) {
  const { username } = use(params);

  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/Users/${username}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch user");
        return res.json();
      })
      .then(setUser)
      .catch((err) => setError(err.message));
  }, [user]);

  if (error) return <p>Error: {error}</p>;
   if (!user) return <p>Loading…</p>;

  return (<h1> {username} </h1>);
} 