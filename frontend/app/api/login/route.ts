import { NextResponse } from 'next/server';
import { prisma } from '@/lib/db';
import { signToken } from '@/lib/auth';
import * as bcrypt from 'bcrypt';

export async function POST(request: Request) {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return NextResponse.json({ detail: "Email and password are required" }, { status: 400 });
    }

    const user = await prisma.user.findUnique({
      where: { email },
      include: { organization: true }
    });

    if (!user) {
      return NextResponse.json({ detail: "Invalid credentials" }, { status: 401 });
    }

    const passwordMatch = await bcrypt.compare(password, user.hashed_password);
    
    if (!passwordMatch) {
      return NextResponse.json({ detail: "Invalid credentials" }, { status: 401 });
    }

    const token = await signToken({
      id: user.id,
      email: user.email,
      role: user.role
    });

    // Remove hashed_password from response
    const { hashed_password, ...safeUser } = user;

    return NextResponse.json({
      access_token: token,
      token_type: "bearer",
      user: safeUser,
    });
  } catch (error: unknown) {
    console.error("Login error:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

