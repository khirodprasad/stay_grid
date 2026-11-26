from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user
from app.db.database import get_db
from app.schemas import BookingInput

router = APIRouter()


@router.post("", status_code=201, summary="Book an available room")
def create_booking(payload: BookingInput, user=Depends(current_user), db=Depends(get_db)):
    db.execute("BEGIN IMMEDIATE")
    room = db.execute("SELECT r.*,h.is_active,rt.capacity,COALESCE(r.price,rt.base_price) AS nightly_price FROM rooms r JOIN hotels h ON h.id=r.hotel_id JOIN room_types rt ON rt.id=r.room_type_id WHERE r.id=?", (payload.room_id,)).fetchone()
    if not room or not room["is_active"] or room["status"] != "available":
        raise HTTPException(404, "Available room not found")
    if payload.guests > room["capacity"]:
        raise HTTPException(422, "Guest count exceeds room capacity")
    conflict = db.execute("SELECT 1 FROM bookings WHERE room_id=? AND status='confirmed' AND check_in<? AND check_out>? LIMIT 1",
                          (payload.room_id, payload.check_out.isoformat(), payload.check_in.isoformat())).fetchone()
    if conflict:
        raise HTTPException(409, "Room is not available for those dates")
    nights = (payload.check_out - payload.check_in).days
    total = round(room["nightly_price"] * nights, 2)
    cursor = db.execute("INSERT INTO bookings(user_id,room_id,check_in,check_out,guests,total_amount) VALUES(?,?,?,?,?,?)",
                        (user["id"], payload.room_id, payload.check_in.isoformat(), payload.check_out.isoformat(), payload.guests, total))
    return {"id": cursor.lastrowid, "room_id": payload.room_id, "check_in": payload.check_in,
            "check_out": payload.check_out, "guests": payload.guests, "total_amount": total, "status": "confirmed"}


@router.get("", summary="List the current user's bookings")
def my_bookings(user=Depends(current_user), db=Depends(get_db)):
    rows = db.execute("SELECT b.*,r.room_number,h.id AS hotel_id,h.name AS hotel_name,h.city FROM bookings b JOIN rooms r ON r.id=b.room_id JOIN hotels h ON h.id=r.hotel_id WHERE b.user_id=? ORDER BY b.created_at DESC", (user["id"],)).fetchall()
    return {"items": [dict(row) for row in rows]}


@router.delete("/{booking_id}", summary="Cancel a booking")
def cancel_booking(booking_id: int, user=Depends(current_user), db=Depends(get_db)):
    row = db.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()
    if not row or (row["user_id"] != user["id"] and user["role"] != "admin"):
        raise HTTPException(404, "Booking not found")
    if row["status"] != "confirmed":
        raise HTTPException(409, "Only confirmed bookings can be cancelled")
    db.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
    return {"id": booking_id, "status": "cancelled"}
