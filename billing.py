"""DocGen AI - Stripe Billing API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import stripe

from app.database import get_db
from app.models import User, UserTier
from app.dependencies import get_current_user
from app.config import get_settings

router = APIRouter(prefix="/api/billing", tags=["billing"])
settings = get_settings()

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


@router.post("/create-checkout-session")
async def create_checkout_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not settings.stripe_secret_key or not settings.stripe_pro_price_id:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
        
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            client_reference_id=current_user.id,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': settings.stripe_pro_price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url="https://docgenai-uheu.onrender.com/#success",
            cancel_url="https://docgenai-uheu.onrender.com/#cancelled",
        )
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header or not settings.stripe_webhook_secret:
        return {"status": "ignored"}

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        user_id = session.get("client_reference_id")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.tier = UserTier.PRO
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                db.commit()

    return {"status": "success"}
