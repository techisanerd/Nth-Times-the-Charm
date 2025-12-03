"use client";

import { useState } from "react";
import Pagination from "../../components/Pagination";

export default function Reviews({ reviews }) {
  const REVIEWS_PER_PAGE = 5;
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(reviews.length / REVIEWS_PER_PAGE);

  const start = (currentPage - 1) * REVIEWS_PER_PAGE;
  const currentReviews = reviews.slice(start, start + REVIEWS_PER_PAGE);

  return (
    <div >

      <ul>
        {currentReviews.map((review) => (
          <li key={review.title}>
            <div style={{ maxWidth: '600px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', fontFamily: 'Arial, sans-serif' }}>
                <b>
                    {review.title} {review.rating} / 10 ⭐ <a href={"/users" + review.reviewer}>{review.reviewer}</a>
                </b>
                <br/>
                {review.description}
            </div>
          </li>
        ))}
      </ul>

      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
      />
    </div>
  );
}