from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
import os
import json
import logging
from app.database import SessionLocal
from app.models import TransactionModel
from app.config import settings

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Stripe webhook endpoint for handling payment events.
    In production, verify the signature using stripe.Signature.verify_header().
    """
    webhook_secret = settings.stripe_webhook_secret

    if not webhook_secret:
        logger.warning("Stripe webhook secret not configured")
        raise HTTPException(status_code=400, detail="Webhook secret not configured")

    payload = await request.body()

    try:
        # Parse the JSON payload
        event = json.loads(payload)
        event_type = event.get("type")
        logger.info(f"Received Stripe event: {event_type}")

        # Handle payment_intent.succeeded event
        if event_type == "payment_intent.succeeded":
            intent = event.get("data", {}).get("object", {})
            amount_received = intent.get("amount_received", 0)
            amount_usd = amount_received / 100.0  # Convert cents to USD
            client_secret = intent.get("client_secret", "unknown")

            # Record transaction in database
            transaction = TransactionModel(
                amount=amount_usd,
                type="credit",
                recipient_or_source=f"stripe_payment:{client_secret}",
                memo=f"Stripe payment intent succeeded: {intent.get('id')}",
            )
            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            logger.info(f"Credited {amount_usd} USD to wallet via Stripe")
            return {
                "status": "success",
                "event_type": event_type,
                "credited_amount": amount_usd,
                "transaction_id": transaction.id,
            }

        # Handle payment_intent.payment_failed event
        elif event_type == "payment_intent.payment_failed":
            intent = event.get("data", {}).get("object", {})
            logger.error(f"Payment failed for intent: {intent.get('id')}")
            return {"status": "payment_failed", "event_type": event_type}

        # Handle charge.refunded event
        elif event_type == "charge.refunded":
            charge = event.get("data", {}).get("object", {})
            amount_refunded = charge.get("amount_refunded", 0) / 100.0
            logger.info(f"Refund processed: {amount_refunded} USD")
            return {
                "status": "refund_recorded",
                "event_type": event_type,
                "refunded_amount": amount_refunded,
            }

        # Log unhandled event types
        logger.info(f"Ignoring unhandled event type: {event_type}")
        return {"status": "ignored", "event_type": event_type}

    except json.JSONDecodeError:
        logger.error("Failed to parse webhook payload as JSON")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")


@router.post("/health")
async def webhook_health():
    """
    Health check endpoint for webhook infrastructure.
    """
    return {
        "status": "webhook_service_operational",
        "stripe_configured": bool(settings.stripe_webhook_secret),
    }
