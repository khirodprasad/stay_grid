from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.database import get_db

router = APIRouter()


@router.get("/availability", summary="Find available rooms")
def availability(check_in: date, check_out: date, guests: int = Query(default=1, ge=1, le=20),
                 hotel_id: int | None = Query(default=None, gt=0), db=Depends(get_db)):
    if check_in < date.today() or check_out <= check_in:
        raise HTTPException(422, "Dates must be valid and check_in cannot be in the past")
    sql = "SELECT r.id AS room_id,r.hotel_id,h.name AS hotel_name,r.room_number,r.floor,rt.name AS room_type,rt.capacity,COALESCE(r.price,rt.base_price) AS price FROM rooms r JOIN hotels h ON h.id=r.hotel_id JOIN room_types rt ON rt.id=r.room_type_id WHERE h.is_active=1 AND r.status='available' AND rt.capacity>=? AND NOT EXISTS (SELECT 1 FROM bookings b WHERE b.room_id=r.id AND b.status='confirmed' AND b.check_in<? AND b.check_out>?)"
    params = [guests, check_out.isoformat(), check_in.isoformat()]
    if hotel_id:
        sql += " AND r.hotel_id=?"; params.append(hotel_id)
    return {"check_in": check_in, "check_out": check_out, "rooms": [dict(row) for row in db.execute(sql + " ORDER BY price", params).fetchall()]}


@router.get("/{room_id}", summary="Get room details")
def room_details(room_id: int, db=Depends(get_db)):
    row = db.execute("SELECT r.*,h.name AS hotel_name,h.city,h.address,rt.name AS room_type,rt.description AS room_description,rt.capacity,COALESCE(r.price,rt.base_price) AS nightly_price FROM rooms r JOIN hotels h ON h.id=r.hotel_id JOIN room_types rt ON rt.id=r.room_type_id WHERE r.id=? AND h.is_active=1", (room_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Room not found")
    return dict(row)
