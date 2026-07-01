from fastapi import APIRouter

from services.disinfection_facilities import load_disinfection_facilities

router = APIRouter(tags=["facilities"])


@router.get("/facilities")
def list_facilities():
    return [
        {
            "id": f.id,
            "name": f.name,
            "address": f.address,
            "lat": f.lat,
            "lng": f.lng,
            "operatingHours": f.operating_hours,
            "phone": f.phone,
        }
        for f in load_disinfection_facilities()
    ]
