"""DocGen AI - PayPal Billing API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx
import base64

from app.database import get_db
from app.models import User, UserTier
from app.dependencies import get_current_user
from app.config import get_settings

router = APIRouter(prefix="/api/billing", tags=["billing"])
settings = get_settings()

def get_paypal_base_url():
    if settings.paypal_mode.lower() == "live":
        return "https://api-m.paypal.com"
    return "https://api-m.sandbox.paypal.com"

async def get_paypal_access_token():
    auth_str = f"{settings.paypal_client_id}:{settings.paypal_client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{get_paypal_base_url()}/v1/oauth2/token",
            headers={
                "Authorization": f"Basic {b64_auth_str}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to authenticate with PayPal")
            
        return response.json()["access_token"]


@router.get("/paypal-config")
async def get_paypal_config():
    """Provides the frontend with the necessary IDs to render the PayPal button"""
    if not settings.paypal_client_id or not settings.paypal_plan_id:
        raise HTTPException(status_code=500, detail="PayPal is not configured")
        
    return {
        "client_id": settings.paypal_client_id,
        "plan_id": settings.paypal_plan_id,
        "mode": settings.paypal_mode
    }


class VerifySubscriptionRequest(BaseModel):
    subscription_id: str

@router.post("/verify-paypal-subscription")
async def verify_paypal_subscription(
    request: VerifySubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        access_token = await get_paypal_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{get_paypal_base_url()}/v1/billing/subscriptions/{request.subscription_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid subscription ID")
                
            sub_data = response.json()
            
            if sub_data.get("status") == "ACTIVE":
                current_user.tier = UserTier.PRO
                current_user.stripe_subscription_id = request.subscription_id
                db.commit()
                return {"status": "success", "message": "Account upgraded to Pro!"}
            else:
                return {"status": "pending", "message": f"Subscription status is {sub_data.get('status')}"}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
