import { NextResponse } from 'next/server';
import { prisma } from '@/lib/db';

export async function GET() {
  try {
    const missions = await prisma.mission.findMany({
      orderBy: { created_at: 'desc' }
    });
    return NextResponse.json(missions);
  } catch (error) {
    console.error("Failed to fetch missions:", error);
    return NextResponse.json({ error: "Failed to fetch missions" }, { status: 500 });
  }
}

