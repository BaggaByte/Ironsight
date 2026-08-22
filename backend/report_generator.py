import json
from datetime import datetime
import models
from database import SessionLocal

def generate_grc_report(scan_id: int):
    """
    Generates a generic GRC (Governance, Risk, and Compliance) style report
    from a specific scan. Ported conceptually from Mini-Mythos.
    """
    db = SessionLocal()
    try:
        scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
        if not scan:
            return {"error": "Scan not found"}

        target = db.query(models.Target).filter(models.Target.id == scan.target_id).first()
        findings = db.query(models.Finding).filter(models.Finding.scan_id == scan_id).all()

        report = {
            "title": "Sentinel GRC Compliance Report",
            "date": datetime.utcnow().isoformat(),
            "target": target.hostname if target else "Unknown",
            "executive_summary": "Automated security posture assessment.",
            "metrics": {
                "total_findings": len(findings),
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0
            },
            "findings": []
        }

        for finding in findings:
            vuln = db.query(models.Vulnerability).filter(models.Vulnerability.id == finding.vulnerability_id).first()
            sev_key = vuln.severity.lower() if vuln else "info"
            if sev_key in report["metrics"]:
                report["metrics"][sev_key] += 1
            
            report["findings"].append({
                "cve": vuln.cve_id if vuln else "Unknown",
                "severity": vuln.severity if vuln else "INFO",
                "details": finding.details
            })

        # Provide compliance mappings (placeholder mapping logic)
        report["compliance"] = {
            "NIST_CSF": "Needs Improvement" if report["metrics"]["high"] > 0 else "Compliant",
            "ISO_27001": "Non-Compliant" if report["metrics"]["critical"] > 0 else "Compliant"
        }
        
        return report

    finally:
        db.close()
