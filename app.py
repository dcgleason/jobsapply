from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, constr
from typing import Optional


# Define your Pydantic model to represent the request body
class ApplyModel(BaseModel):
    email: EmailStr
    phone_country_code: constr(regex=r'^\+\d{1,3}$')
    mobile_phone_number: constr(regex=r'^\d{10,15}$')
    has_technical_experience: bool
    has_teaching_experience: bool
    is_us_citizen: bool

app = FastAPI()

# Define the home route
@app.get('/')
def home():
    return {"message": "HOME"}

# Update the apply route to accept the new parameters
@app.post('/apply')
def apply_jobs(apply_details: ApplyModel):
    # Extract the details from the request body
    email = apply_details.email
    phone_country_code = apply_details.phone_country_code
    mobile_phone_number = apply_details.mobile_phone_number
    has_technical_experience = apply_details.has_technical_experience
    has_teaching_experience = apply_details.has_teaching_experience
    is_us_citizen = apply_details.is_us_citizen
    
    # Here, you would initialize and run your bot or any other logic you need,
    # passing these parameters as needed. For demonstration purposes, we'll just echo them back.
    # Replace the below return statement with your actual logic.
    result = {
        "email": email,
        "phone": f"{phone_country_code} {mobile_phone_number}",
        "has_technical_experience": has_technical_experience,
        "has_teaching_experience": has_teaching_experience,
        "is_us_citizen": is_us_citizen,
        "message": "Application process initiated."
    }
    return result

# Ensure you have `uvicorn` installed to run FastAPI apps
# Run the app with: uvicorn main:app --reload
