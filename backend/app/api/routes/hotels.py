from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.database import get_db

router = APIRouter()


@router.get("", summary="List and search hotels")
def list_hotels(city: str | None = None, q: str | None = None,
                check_in: date | None = None, check_out: date | None = None,
                guests: int | None = Query(default=None, ge=1, le=20),
                page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100),
                db=Depends(get_db)):
    if (check_in is None) != (check_out is None):
        raise HTTPException(422, "Provide both check_in and check_out")
    if check_in and (check_out <= check_in or check_in < date.today()):
        raise HTTPException(422, "Dates must be valid and check_in cannot be in the past")
    clauses, params = ["h.is_active=1"], []
    if city:
        clauses.append("h.city LIKE ?"); params.append(f"%{city}%")
    if q:
        clauses.append("(h.name LIKE ? OR h.description LIKE ? OR h.city LIKE ?)")
        params.extend([f"%{q}%"] * 3)
    availability = ""
    if check_in and check_out:
        availability = " AND EXISTS (SELECT 1 FROM rooms r JOIN room_types rt ON rt.id=r.room_type_id WHERE r.hotel_id=h.id AND r.status='available' AND rt.capacity>=? AND NOT EXISTS (SELECT 1 FROM bookings b WHERE b.room_id=r.id AND b.status='confirmed' AND b.check_in<? AND b.check_out>?))"
        params.extend([guests or 1, check_out.isoformat(), check_in.isoformat()])
    where = " AND ".join(clauses)
    count = db.execute(f"SELECT COUNT(*) FROM hotels h WHERE {where}{availability}", params).fetchone()[0]
    items = db.execute(f"SELECT h.* FROM hotels h WHERE {where}{availability} ORDER BY h.rating DESC,h.name LIMIT ? OFFSET ?",
                       [*params, page_size, (page - 1) * page_size]).fetchall()
    return {"items": [dict(row) for row in items], "page": page, "page_size": page_size, "total": count}


@router.get("/{hotel_id}", summary="Get hotel details")
def hotel_details(hotel_id: int, db=Depends(get_db)):
    hotel = db.execute("SELECT * FROM hotels WHERE id=? AND is_active=1", (hotel_id,)).fetchone()
    if not hotel:
        raise HTTPException(404, "Hotel not found")
    return {**dict(hotel), "rooms": [dict(r) for r in db.execute(
        "SELECT r.id,r.room_number,r.floor,r.status,COALESCE(r.price,rt.base_price) AS price,rt.name AS room_type,rt.description AS room_type_description,rt.capacity FROM rooms r JOIN room_types rt ON rt.id=r.room_type_id WHERE r.hotel_id=? AND r.status!='inactive' ORDER BY r.room_number", (hotel_id,)).fetchall()]}
