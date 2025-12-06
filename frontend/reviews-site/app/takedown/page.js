"use client"

import { use, useEffect, useState } from "react";
import { useSearchParams } from 'next/navigation'

export default function TakedownReviewPage({ params }) {
  const searchParams = useSearchParams();
  const reviewer= searchParams.get('reviewer');
  const movie = searchParams.get('movie');
  const reviewTitle = searchParams.get('title');
 

  return (<h1>Review to be taken down: {reviewer} {movie} {reviewTitle}</h1>)
}