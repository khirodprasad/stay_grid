from fastapi import APIRouter, Depends

from app.api.dependencies import hotel_admin_user
from app.db.database import get_db

router = APIRouter(dependencies=[Depends(hotel_admin_user)])


@router.get("/overview", summary="Hotel administrator overview")
def overview(user=Depends(hotel_admin_user), db=Depends(get_db)):
    hotels = db.execute("SELECT id,name,city,address,contact,rating,amenities,is_active FROM hotels WHERE created_by=? ORDER BY name", (user["id"],)).fetchall()
    hotel_ids = [row["id"] for row in hotels]
    if not hotel_ids:
        return {"hotel_admin": user, "hotels": [], "rooms": 0, "bookings": 0, "revenue": 0}
    marks = ",".join("?" for _ in hotel_ids)
    rooms = db.execute(f"SELECT COUNT(*) AS count FROM rooms WHERE hotel_id IN ({marks})", hotel_ids).fetchone()["count"]
    bookings = db.execute(f"SELECT COUNT(*) AS count FROM bookings b JOIN rooms r ON r.id=b.room_id WHERE r.hotel_id IN ({marks})", hotel_ids).fetchone()["count"]
    revenue = db.execute(f"SELECT COALESCE(SUM(b.total_amount),0) AS total FROM bookings b JOIN rooms r ON r.id=b.room_id WHERE r.hotel_id IN ({marks}) AND b.status!='cancelled'", hotel_ids).fetchone()["total"]
    return {"hotel_admin": user, "hotels": [dict(row) for row in hotels], "rooms": rooms, "bookings": bookings, "revenue": revenue}
