"""
API Integration Model
Stores connected banking/payment API credentials.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class IntegrationType(str, enum.Enum):
    """Supported API integration types."""
    BANKING = "banking"
    PAYMENT = "payment"


class SyncStatus(str, enum.Enum):
    """API sync status."""
    ACTIVE = "active"
    SYNCING = "syncing"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class APIIntegration(Base):
    """Stores connected banking/payment API credentials."""
    
    __tablename__ = "api_integrations"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Integration details
    api_type: Mapped[IntegrationType] = mapped_column(Enum(IntegrationType), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Credentials (should be encrypted in production)
    access_token: Mapped[str] = mapped_column(String(500), nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    token_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Status
    sync_status: Mapped[SyncStatus] = mapped_column(
        Enum(SyncStatus),
        default=SyncStatus.ACTIVE,
        nullable=False
    )
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    connected_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_integrations")
    
    def __repr__(self) -> str:
        return f"<APIIntegration(id={self.id}, provider={self.provider_name}, status={self.sync_status})>"
