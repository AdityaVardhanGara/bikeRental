from fastapi import FastAPI,Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime
import firebase_admin
from firebase_admin import credentials, db
import random
import string

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize Firebase Admin SDK (replace 'path/to/serviceAccountKey.json' with the path to your Firebase service account key file)
cred = credentials.Certificate('vizigo-a97d2-8361e3913135.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://vizigo-a97d2-default-rtdb.firebaseio.com/'
})


class BikeUpdate(BaseModel):
    brand_name: str
    name: str
    model_name: str
    registration_number: str
    kilometers_driven: str
    color: str
    model_year: str
    description: str
    city: str
    location: str
    created_at: date = None
    purchase_date: date
    availability: str
    price_per_day: str
    price_per_month: str
    category: str

def generate_bike_id():
    # Generate a random alphanumeric string of length 8 for bikeId
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@app.post("/update_bike/")
async def update_bike(request: BikeUpdate):
    """
    Update bike details and store in Firebase Realtime Database.
    """
    # Get the current date if created_at is not provided
    if not request.created_at:
        request.created_at = datetime.now().date()

    # Generate a unique bikeId
    bike_id = generate_bike_id()

    # Push bike details to Firebase Realtime Database
    ref = db.reference('vehicles')
    new_bike_ref = ref.push({
        "bikeId": bike_id,
        "brand_name": request.brand_name,
        "name": request.name,
        "model_name": request.model_name,
        "registration_number": request.registration_number,
        "kilometers_driven": request.kilometers_driven,
        "color": request.color,
        "model_year": request.model_year,
        "description": request.description,
        "city": request.city,
        "location": request.location,
        "created_at": request.created_at.isoformat(),
        "purchase_date": request.purchase_date.isoformat(),
        "availability": request.availability,
        "price_per_day": request.price_per_day,
        "price_per_month": request.price_per_month,
        "category": request.category
    })
    return {"message": "Bike details updated successfully", "bike_id": new_bike_ref.key}


class RentalRequest(BaseModel):
    name: str
    number: str
    bike_name: str
    from_date: date
    to_date: date

@app.post("/rental/")
async def create_rental(request: RentalRequest):
    """
    Create a new rental request.
    """
    # Push rental request to Firebase Realtime Database
    ref = db.reference('rental_requests')
    new_rental_ref = ref.push({
        "name": request.name,
        "number": request.number,
        "bike_name": request.bike_name,
        "from_date": request.from_date.isoformat(),
        "to_date": request.to_date.isoformat()
    })
    return {"message": "Rental request created successfully", "rental_id": new_rental_ref.key}


@app.get("/bikes")
async def get_bike_details():
    """
    Get details of all bikes from Firebase Realtime Database.
    """
    try:
        # Reference to the 'vehicles' node in Firebase Realtime Database
        ref = db.reference('vehicles')

        # Retrieve bike details from Firebase Realtime Database
        bike_data = []
        bikes_snapshot = ref.get()
        if bikes_snapshot:
            for bike_id, bike_details in bikes_snapshot.items():
                bike_data.append({
                    "bikeId": bike_id,
                    "brand_name": bike_details.get('brand_name'),
                    "name": bike_details.get('name'),
                    "model_name": bike_details.get('model_name'),
                    "registration_number": bike_details.get('registration_number'),
                    "kilometers_driven": bike_details.get('kilometers_driven'),
                    "color": bike_details.get('color'),
                    "model_year": bike_details.get('model_year'),
                    "description": bike_details.get('description'),
                    "city": bike_details.get('city'),
                    "location": bike_details.get('location'),
                    "created_at": date.fromisoformat(bike_details.get('created_at')) if bike_details.get('created_at') else None,
                    "purchase_date": date.fromisoformat(bike_details.get('purchase_date')),
                    "availability": bike_details.get('availability'),
                    "price_per_day": bike_details.get('price_per_day'),
                    "price_per_month": bike_details.get('price_per_month'),
                    "category": bike_details.get('category')
                })

        return bike_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    from fastapi.openapi.utils import get_openapi

    @app.get("/openapi.json")
    async def get_open_api_endpoint():
        return get_openapi(title="FastAPI", version=1.0, routes=app.routes)

    uvicorn.run(app, host="0.0.0.0", port=8000)
