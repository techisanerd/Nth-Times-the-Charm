import { NextRequest, NextResponse } from 'next/server';

export async function POST(request) {
    try {
        const { name, email, password, } = await request.json();

        const response = await fetch('http://localhost:8000/Users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({name, email, password, profilePicURL}),
        });

        const data = await response.json();

        if (!response.ok) {
            return NextResponse.json(
                { error: data.detail || 'Login failed' },
                { status: response.status }
            );
        }

        const result = NextResponse.json(data, { status: 200 });
        result.cookies.set('token', data.access_token, {
            httpOnly: true,
            secure: true,
            sameSite: 'strict',
        });

        return result;
    } catch (error) {
        return NextResponse.json(
            { error: 'Server error' },
            { status: 500 }
        );
    }
}