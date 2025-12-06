import { NextResponse } from "next/server";

export async function GET(req, { params }) {
  try {

    const {admin} = await params;

    const backendUrl = `http://localhost:8000/Admins/${encodeURIComponent(admin)}`;

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