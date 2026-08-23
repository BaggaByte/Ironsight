from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import database
import models
import auth
from worker import run_recon_scan

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    org_name: str
    first_name: str
    last_name: str
    job_title: str

app = FastAPI(title="Ironsight API")

# CORS: allow Next.js frontend on port 3000 and Praxis frontend on port 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://sentinel_frontend:3000",
        "http://nexus_frontend:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic request/response schemas
class TargetCreate(BaseModel):
    hostname: str

class TargetResponse(BaseModel):
    id: int
    hostname: str

class ScanCreate(BaseModel):
    target_id: int

class ScanResponse(BaseModel):
    scan_id: int
    status: str

class OrchestrateRequest(BaseModel):
    goal: str
    target: str

@app.post("/register")
def register(body: RegisterRequest, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    org = db.query(models.Organization).filter(models.Organization.name == body.org_name).first()
    if org:
        raise HTTPException(status_code=400, detail="Organization already exists. Contact your administrator for an invite.")
        
    org = models.Organization(name=body.org_name)
    db.add(org)
    db.commit()
    db.refresh(org)
    
    new_user = models.User(
        email=body.email,
        hashed_password=auth.get_password_hash(body.password),
        organization_id=org.id,
        role="admin"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/login")
def login(body: LoginRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not auth.verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth.create_access_token({"id": user.id, "email": user.email, "role": user.role, "organization_id": user.organization_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "role": user.role, "organization_id": user.organization_id}
    }

@app.post("/orchestrate")
def orchestrate(body: OrchestrateRequest, db: Session = Depends(database.get_db), user: dict = Depends(auth.get_current_user)):
    import uuid
    target = db.query(models.Target).filter(models.Target.hostname == body.target).first()
    if not target:
        target = models.Target(hostname=body.target)
        db.add(target)
        db.commit()
        db.refresh(target)
    
    db_scan = models.Scan(target_id=target.id, status=models.ScanStatus.PENDING)
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    
    run_recon_scan.delay(db_scan.id, target.hostname)
    
    return {
        "mission_id": str(uuid.uuid4())[:8],
        "planner_reasoning": f"Analyzed goal: '{body.goal}'. Identified safe scan path for target {body.target}.",
        "tasks_dispatched": 1,
        "scans": [{
            "scan_id": str(db_scan.id),
            "tool": "nmap",
            "target": target.hostname,
            "status": "pending"
        }]
    }

@app.get("/me")
def get_me(user: dict = Depends(auth.get_current_user)):
    return user

@app.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(database.get_db), user: dict = Depends(auth.get_current_user)):
    import models
    total_targets = db.query(models.Target).count()
    total_scans = db.query(models.Scan).count()
    completed = db.query(models.Scan).filter(models.Scan.status == models.ScanStatus.COMPLETED).count()
    failed = db.query(models.Scan).filter(models.Scan.status == models.ScanStatus.FAILED).count()
    critical = db.query(models.Finding).join(models.Vulnerability).filter(models.Vulnerability.severity == "CRITICAL").count()
    return {
        "total_assets": total_targets,
        "total_scans": total_scans,
        "completed_scans": completed,
        "failed_scans": failed,
        "risk_breakdown": {"CRITICAL": critical, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    }

class ReconRequest(BaseModel):
    target: str
    tool: str

@app.post("/recon")
def trigger_recon(body: ReconRequest, db: Session = Depends(database.get_db), user: dict = Depends(auth.get_current_user)):
    import uuid
    target = db.query(models.Target).filter(models.Target.hostname == body.target, models.Target.organization_id == user["organization_id"]).first()
    if not target:
        target = models.Target(hostname=body.target, organization_id=user["organization_id"])
        db.add(target)
        db.commit()
        db.refresh(target)
    db_scan = models.Scan(target_id=target.id, organization_id=user["organization_id"], status=models.ScanStatus.PENDING)
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    run_recon_scan.delay(db_scan.id, target.hostname)
    return {"scan_id": str(db_scan.id)}

@app.get("/assets")
def get_assets(db: Session = Depends(database.get_db), user: dict = Depends(auth.get_current_user)):
    targets = db.query(models.Target).filter(models.Target.organization_id == user["organization_id"]).all()
    return [{"asset_id": str(t.id), "target": t.hostname, "asset_type": "hostname", "scan_count": len(t.scans)} for t in targets]

@app.get("/missions")
def get_missions(user: dict = Depends(auth.get_current_user)):
    return []

@app.get("/scans/schedule")
def get_schedule(user: dict = Depends(auth.get_current_user)):
    return []

@app.get("/reports/summary")
def get_reports_summary(user: dict = Depends(auth.get_current_user)):
    return {"daily_trend": []}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/targets/", response_model=TargetResponse, status_code=201)
def create_target(body: TargetCreate, db: Session = Depends(database.get_db), user: dict = Depends(auth.get_current_user)):
    existing = db.query(models.Target).filter(models.Target.hostname == body.hostname, models.Target.organization_id == user["organization_id"]).first()
    if existing:
        raise HTTPException(status_code=409, detail="Target already exists")
    db_target = models.Target(hostname=body.hostname, organization_id=user["organization_id"])
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return {"id": db_target.id, "hostname": db_target.hostname}

@app.get("/targets/", response_model=List[dict])
def read_targets(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), user: dict = Depends(auth.get_current_user)):
    targets = db.query(models.Target).filter(models.Target.organization_id == user["organization_id"]).offset(skip).limit(limit).all()
    return [{"id": t.id, "hostname": t.hostname} for t in targets]

@app.post("/scans/", response_model=ScanResponse, status_code=202)
def trigger_scan(body: ScanCreate, db: Session = Depends(database.get_db), user: dict = Depends(auth.get_current_user)):
    target = db.query(models.Target).filter(models.Target.id == body.target_id, models.Target.organization_id == user["organization_id"]).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    db_scan = models.Scan(target_id=target.id, organization_id=user["organization_id"], status=models.ScanStatus.PENDING)
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    
    # Trigger Celery task asynchronously
    run_recon_scan.delay(db_scan.id, target.hostname)
    
    return {"scan_id": db_scan.id, "status": db_scan.status.value}

@app.get("/scans/", response_model=List[dict])
def list_scans(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), user: dict = Depends(auth.get_current_user)):
    scans = db.query(models.Scan).filter(models.Scan.organization_id == user["organization_id"]).offset(skip).limit(limit).all()
    return [{
        "id": scan.id, 
        "target_id": scan.target_id, 
        "target_hostname": scan.target.hostname if scan.target else "Unknown",
        "start_time": scan.start_time.isoformat() if scan.start_time else None,
        "end_time": scan.end_time.isoformat() if scan.end_time else None,
        "status": scan.status.value,
        "findings_count": len(scan.findings)
    } for scan in scans]

@app.get("/scans/{scan_id}")
def get_scan(scan_id: int, db: Session = Depends(database.get_db), user: dict = Depends(auth.get_current_user)):
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id, models.Scan.organization_id == user["organization_id"]).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {
        "id": scan.id, 
        "target_id": scan.target_id, 
        "status": scan.status.value,
        "findings_count": len(scan.findings)
    }

from neo4j import GraphDatabase
import os

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "sentinel_neo4j")

try:
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")
    neo4j_driver = None

@app.get("/graph/")
def get_graph_data(user: dict = Depends(auth.get_current_user)):
    if not neo4j_driver:
        return {"nodes": [], "links": []}
        
    def get_node_group(labels):
        if "Target" in labels: return 1
        if "Vulnerability" in labels: return 2
        if "Network_Segment" in labels: return 3
        if "Threat_Actor" in labels: return 4
        if "User_Role" in labels: return 5
        return 6
        
    try:
        with neo4j_driver.session() as session:
            # Query all nodes and relationships
            result = session.run("""
                MATCH (n)
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN n, r, m
            """)
            
            nodes_dict = {}
            links = []
            
            for record in result:
                n = record["n"]
                if n:
                    node_id = str(n.element_id)
                    if node_id not in nodes_dict:
                        nodes_dict[node_id] = {
                            "id": node_id,
                            "name": n.get("name", n.get("hostname", n.get("cve_id", "Unknown"))),
                            "group": get_node_group(n.labels)
                        }
                
                r = record["r"]
                m = record["m"]
                
                if r and m:
                    target_id = str(m.element_id)
                    if target_id not in nodes_dict:
                        nodes_dict[target_id] = {
                            "id": target_id,
                            "name": m.get("name", m.get("hostname", m.get("cve_id", "Unknown"))),
                            "group": get_node_group(m.labels)
                        }
                        
                    links.append({
                        "source": str(n.element_id),
                        "target": target_id,
                        "value": 1,
                        "type": r.type  # correct neo4j relationship type accessor
                    })
                    
            return {
                "nodes": list(nodes_dict.values()),
                "links": links
            }
    except Exception as e:
        print(f"Error querying Neo4j: {e}")
        return {"nodes": [], "links": []}

@app.get("/analytics/")
def get_analytics(db: Session = Depends(database.get_db), user: dict = Depends(auth.get_current_user)):
    """Returns aggregate metrics for the SOC dashboard."""
    import models
    total_targets = db.query(models.Target).count()
    total_scans = db.query(models.Scan).count()
    completed = db.query(models.Scan).filter(models.Scan.status == models.ScanStatus.COMPLETED).count()
    failed = db.query(models.Scan).filter(models.Scan.status == models.ScanStatus.FAILED).count()
    running = db.query(models.Scan).filter(models.Scan.status == models.ScanStatus.RUNNING).count()
    critical_findings = db.query(models.Finding).join(models.Vulnerability).filter(
        models.Vulnerability.severity == "CRITICAL"
    ).count()
    return {
        "totalTargets": total_targets,
        "totalScans": total_scans,
        "completedScans": completed,
        "failedScans": failed,
        "activeScans": running,
        "criticalVulns": critical_findings,
        "playbooks": 0  # Populated by Aegis AI service
    }

@app.get("/reports/{scan_id}")
def get_grc_report(scan_id: int, user: dict = Depends(auth.get_current_user)):
    """
    Generate a GRC-style compliance report for a given scan.
    """
    from report_generator import generate_grc_report
    report = generate_grc_report(scan_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    return report
