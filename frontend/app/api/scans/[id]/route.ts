import { NextResponse } from 'next/server';
import { prisma } from '@/lib/db';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const dbId = id.startsWith('SCN-') ? parseInt(id.replace('SCN-', '')) : parseInt(id);

    if (isNaN(dbId)) {
      return NextResponse.json({ detail: `Invalid scan ID format` }, { status: 400 });
    }

    const scan = await prisma.scan.findUnique({
      where: { id: dbId },
      include: { target: true, findings: true }
    });

    if (scan) {
      const mappedScan = {
        ...scan,
        scan_id: `SCN-${scan.id}`,
        target: scan.target.hostname,
        tool_used: 'nmap',
        completed_at: scan.end_time,
        risk_score: scan.findings.length > 0 ? 'HIGH' : 'INFO'
      };
      return NextResponse.json(mappedScan);
    }

    return NextResponse.json(
      { detail: `Scan ${id} not found` },
      { status: 404 }
    );
  } catch (error) {
    console.error("Failed to fetch scan:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

