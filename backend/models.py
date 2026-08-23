from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import datetime
import enum
from database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("User", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organization = relationship("Organization", back_populates="users")

class ScanStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scans = relationship("Scan", back_populates="target")
    findings = relationship("Finding", back_populates="target")

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"))
    status = Column(Enum(ScanStatus), default=ScanStatus.PENDING)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    target = relationship("Target", back_populates="scans")
    findings = relationship("Finding", back_populates="scan")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String, unique=True, index=True, nullable=True)
    severity = Column(String)
    description = Column(String)

    findings = relationship("Finding", back_populates="vulnerability")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"))
    scan_id = Column(Integer, ForeignKey("scans.id"))
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"))
    details = Column(String, nullable=True)

    target = relationship("Target", back_populates="findings")
    scan = relationship("Scan", back_populates="findings")
    vulnerability = relationship("Vulnerability", back_populates="findings")
