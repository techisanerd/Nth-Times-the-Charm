import { NextResponse } from "next/server";

export async function GET(req, { params }) {
  try {

    const backendUrl = `http://localhost:8000/Users/`;

    const res = await fetch(backendUrl);
    const text = await res.text();

    return new NextResponse(text);
  } catch (err) {
    return NextResponse.json(
      { error: err.message },
      { status: 500 }
    );
  }
}