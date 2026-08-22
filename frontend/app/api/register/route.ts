import { NextResponse } from 'next/server';
import { prisma } from '@/lib/db';
import { signToken } from '@/lib/auth';
import * as bcrypt from 'bcrypt';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, password, org_name } = body;

    if (!email || !password || !org_name) {
      return NextResponse.json({ detail: "Email, password, and org_name are required" }, { status: 400 });
    }

    // Check if user exists
    const existingUser = await prisma.user.findUnique({ where: { email } });
    if (existingUser) {
      return NextResponse.json({ detail: "Email already registered" }, { status: 400 });
    }

    // Find or create organization
    let org = await prisma.organization.findUnique({ where: { name: org_name } });
    if (!org) {
      org = await prisma.organization.create({ data: { name: org_name } });
    }

    // Hash password
    const hashed_password = await bcrypt.hash(password, 10);

    // Create user
    const user = await prisma.user.create({
      data: {
        email,
        hashed_password,
        organization_id: org.id,
        role: "user" // Default role
      },
      include: { organization: true }
    });

    const token = await signToken({
      id: user.id,
      email: user.email,
      role: user.role
    });

    const { hashed_password: _, ...safeUser } = user;

    return NextResponse.json({
      access_token: token,
      token_type: "bearer",
      user: safeUser,
    });
  } catch (error: unknown) {
    console.error("Registration error:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

