from fastapi import APIRouter, Depends

from app.db.database import get_db

router = APIRouter()


COUNT_QUERIES = {
    "hotels": "SELECT COUNT(*) AS count FROM hotels WHERE is_active=1",
    "room_types": "SELECT COUNT(*) AS count FROM room_types",
    "rooms": "SELECT COUNT(*) AS count FROM rooms WHERE status!='inactive'",
    "availability": "SELECT COUNT(*) AS count FROM rooms WHERE status='available'",
    "bookings": "SELECT COUNT(*) AS count FROM bookings",
    "guests": "SELECT COUNT(*) AS count FROM users WHERE role='customer'",
    "administration": "SELECT COUNT(*) AS count FROM users WHERE role='admin'",
}


@router.get("", summary="List database-backed StayGrid categories")
def list_categories(db=Depends(get_db)):
    rows = db.execute("SELECT slug,name,description,count_source FROM categories WHERE is_active=1 ORDER BY sort_order, name").fetchall()
    return {"items": [{**dict(row), "count": db.execute(COUNT_QUERIES[row["count_source"]]).fetchone()["count"]} for row in rows]}
