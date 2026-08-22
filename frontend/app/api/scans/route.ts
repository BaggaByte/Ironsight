import { NextResponse } from 'next/server';
import { prisma } from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '50');
    
    const scans = await prisma.scan.findMany({
      take: limit,
      orderBy: { start_time: 'desc' },
      include: { target: true, findings: true }
    });
    
    const mappedScans = scans.map(s => ({
      ...s,
      scan_id: `SCN-${s.id}`,
      target: s.target.hostname,
      tool_used: 'nmap',
      completed_at: s.end_time,
      risk_score: s.findings.length > 0 ? 'HIGH' : 'INFO'
    }));

    return NextResponse.json(mappedScans);
  } catch (error) {
    console.error("Failed to fetch scans:", error);
    return NextResponse.json({ error: "Failed to fetch scans" }, { status: 500 });
  }
}


