from contextlib import asynccontextmanager
from datetime import datetime
import json
import os
from fastapi import FastAPI, status, HTTPException
import httpx
import requests
from models import models
from functions.identity import validate_mobile_number
import logging
import config
from dotenv import load_dotenv
import asyncio
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


APP_URL = os.environ.get("APP_URL", "https://lucopay.onrender.com")

PING_INTERVAL = 100

async def keep_alive():
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                logger.info(f"Sending keep-alive ping to {APP_URL}/health")
                response = await client.get(f"{APP_URL}/health")
                logger.info(f"Keep-alive response: {response.status_code}")
            except Exception as e:
                logger.error(f"Keep-alive ping failed: {str(e)}")
            
            
            await asyncio.sleep(PING_INTERVAL)
            
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    task = asyncio.create_task(keep_alive())
    yield
    
    task.cancel()

app = FastAPI(
    lifespan=lifespan,
    title="LucoPay",
    description="A Payment Gateway API and Mobile Number Validator",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root(status=status.HTTP_200_OK):
    return {
        "Welcome To Luco Pay": "True"
        }


@app.post("/identity/msisdn", status_code=status.HTTP_200_OK)
async def  msisdn_identity(identity: models.Identity):
    if not identity.msisdn:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="msisdn is required")
    
    result = validate_mobile_number(identity.msisdn)
    
    if result:
        return models.IdResponse(
            identityname=result.get("customer_name"),
            message=result.get("message"),
            success=result.get("success")
        )
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to validate mobile number")
    
@app.post("/api/v1/request_payment", status_code=status.HTTP_200_OK)
async def request_payment(payment: models.PaymentModel):

    payload = {
        **payment.dict(),
        "username": config.DEVCRAFT_USERNAME,
        "password": config.DEVCRAFT_PASSWORD,
        "success-re-url": 'https://your_url/payment/success',
        "failed-re-url": f'https://your_url/payment/failed'
    }
    try:
        # response = requests.post(f"{config.API_BASE_URL}/process_payment", headers=config.HEADER, data=json.dumps(payload))
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{config.API_BASE_URL}/process_payment", 
                headers=config.HEADER, 
                json=payload
            )
        if response.status_code == 200:
            return {
                "message": "Payment requested successfully",
                "data": response.json()
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Payment processing failed: {response.text}"
            )
            
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
#WEBHOOK TO CHECK TRANSACTION STATUS

@app.post("/api/v1/payment_webhook", response_model=models.WebhookResponse, status_code=status.HTTP_200_OK)
async def payment_webhook(reference: models.TransReference):
    
    logger.info(f"Received webhook for reference: {reference.reference}")
    transc_history = {
        "apikey": config.DEVCRAFT_USERNAME,
        "apipassword": config.DEVCRAFT_PASSWORD,
        "reference": reference.reference
    }
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{config.API_BASE_URL}/check_transaction_status", 
                headers=config.HEADER, 
                json=transc_history
            )
            
        logger.info(f"Checking transaction at: {config.API_BASE_URL}/check_transaction_status")
        
        if response.status_code == 200:
            data = response.json()
            return models.WebhookResponse(
                message="Transaction found",
                status=data.get("status", "unknown"),
                amount=data.get("amount"),
                number=data.get("number"),
                created=data.get("created", datetime.utcnow().isoformat()),
                transid=data.get("transid", reference.reference),
                reference=reference.reference
            )
        else:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Failed to fetch transaction: {response.text}"
            )
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transaction: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {str(e)}")

