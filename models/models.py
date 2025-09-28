from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

import config
from functions.trefernce import generate_secure_refer_id

#secure order id 
secure_refernce = generate_secure_refer_id(size=6, secret_key=config.SECRET_KEY)

#IDENTITY CHEcK MODEL

class Identity(BaseModel):
    msisdn: str = "+256700000000"
    
class IdResponse(BaseModel):
    identityname : str
    message : str
    success: bool
    
#PATMENT REQUEST MODEL

class PaymentModel(BaseModel):
    amount: str = '500'
    number: str = '256708215305'
    refer: str = secure_refernce['order_id']
    
# TRANSCATION MODEL
class TransReference(BaseModel):
    reference: str

class WebhookResponse(BaseModel):
    message: str
    status: str
    amount: Optional[float] = None 
    number: str
    created: str
    transid: str
    reference: str



