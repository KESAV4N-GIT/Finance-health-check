"""
Integrations API Endpoints
Handles banking and payment API integrations.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.api_integration import APIIntegration, IntegrationType, SyncStatus
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class IntegrationConnect(BaseModel):
    """Schema for connecting an integration."""
    api_type: IntegrationType
    provider_name: str
    access_token: str
    refresh_token: Optional[str] = None


class IntegrationResponse(BaseModel):
    """Schema for integration response."""
    id: int
    api_type: IntegrationType
    provider_name: str
    sync_status: SyncStatus
    last_sync: Optional[datetime] = None
    connected_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/connect", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def connect_integration(
    integration: IntegrationConnect,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Connect a banking or payment API.
    
    Maximum 2 integrations allowed per user.
    """
    # Check integration limit
    count_result = await db.execute(
        select(func.count(APIIntegration.id))
        .where(APIIntegration.user_id == current_user.id)
    )
    count = count_result.scalar()
    
    if count >= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 2 integrations allowed. Please disconnect an existing integration first."
        )
    
    # Check for duplicate provider
    existing = await db.execute(
        select(APIIntegration)
        .where(APIIntegration.user_id == current_user.id)
        .where(APIIntegration.provider_name == integration.provider_name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Already connected to {integration.provider_name}"
        )
    
    # Create integration
    api_integration = APIIntegration(
        user_id=current_user.id,
        api_type=integration.api_type,
        provider_name=integration.provider_name,
        access_token=integration.access_token,  # Should be encrypted in production
        refresh_token=integration.refresh_token,
        sync_status=SyncStatus.ACTIVE
    )
    
    db.add(api_integration)
    await db.flush()
    await db.refresh(api_integration)
    
    return IntegrationResponse.model_validate(api_integration)


@router.get("/", response_model=List[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all connected integrations.
    """
    result = await db.execute(
        select(APIIntegration)
        .where(APIIntegration.user_id == current_user.id)
    )
    integrations = result.scalars().all()
    
    return [IntegrationResponse.model_validate(i) for i in integrations]


@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger manual sync for an integration.
    """
    result = await db.execute(
        select(APIIntegration)
        .where(APIIntegration.id == integration_id)
        .where(APIIntegration.user_id == current_user.id)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    if integration.sync_status == SyncStatus.SYNCING:
        return {"message": "Sync already in progress"}
    
    # Update status
    integration.sync_status = SyncStatus.SYNCING
    await db.flush()
    
    # Queue background sync (placeholder)
    # background_tasks.add_task(sync_integration_data, integration.id)
    
    return {"message": "Sync started", "integration_id": integration_id}


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disconnect an integration.
    """
    result = await db.execute(
        select(APIIntegration)
        .where(APIIntegration.id == integration_id)
        .where(APIIntegration.user_id == current_user.id)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    await db.delete(integration)
    await db.flush()
    
    return {"message": f"Disconnected from {integration.provider_name}"}


@router.get("/providers")
async def list_available_providers():
    """
    List available integration providers.
    """
    return {
        "banking": [
            {
                "name": "ICICI Bank",
                "type": "banking",
                "description": "Connect your ICICI business account",
                "features": ["Transaction history", "Balance", "Statements"]
            },
            {
                "name": "HDFC Bank",
                "type": "banking", 
                "description": "Connect your HDFC business account",
                "features": ["Transaction history", "Balance", "Statements"]
            },
            {
                "name": "Axis Bank",
                "type": "banking",
                "description": "Connect your Axis business account",
                "features": ["Transaction history", "Balance"]
            }
        ],
        "payment": [
            {
                "name": "Razorpay",
                "type": "payment",
                "description": "Connect your Razorpay account",
                "features": ["Payment history", "Settlements", "Refunds"]
            },
            {
                "name": "PayU",
                "type": "payment",
                "description": "Connect your PayU merchant account",
                "features": ["Transaction history", "Settlements"]
            }
        ]
    }
