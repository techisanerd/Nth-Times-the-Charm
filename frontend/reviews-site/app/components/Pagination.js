"use client";

export default function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  windowSize = 3,
}) {
  const startPage = Math.max(1, currentPage - windowSize);
  const endPage = Math.min(totalPages, currentPage + windowSize);

  const pages = [];
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }

  return (
    <div style={{ marginTop: "1rem" }}>
      <button
        onClick={() => onPageChange(1)}
        disabled={currentPage === 1}
      >
        Start
      </button>

      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        Prev
      </button>

      {pages.map((page) => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          disabled={page === currentPage}
          style={{
            fontWeight: page === currentPage ? "bold" : "normal",
            margin: "0 4px",
          }}
        >
          {page}
        </button>
      ))}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        Next
      </button>

      <button
        onClick={() => onPageChange(totalPages)}
        disabled={currentPage === totalPages}
      >
        End
      </button>
    </div>
  );
}