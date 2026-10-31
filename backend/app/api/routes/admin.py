from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import admin_user
from app.db.database import get_db
from app.schemas import HotelInput, RoomInput, RoomTypeInput

router = APIRouter(dependencies=[Depends(admin_user)])


@router.post("/hotels", status_code=201, summary="Create a hotel")
def create_hotel(payload: HotelInput, db=Depends(get_db)):
    values = payload.model_dump()
    cursor = db.execute("INSERT INTO hotels(name,description,address,city,country,contact,rating,amenities) VALUES(:name,:description,:address,:city,:country,:contact,:rating,:amenities)", values)
    return dict(db.execute("SELECT * FROM hotels WHERE id=?", (cursor.lastrowid,)).fetchone())


@router.put("/hotels/{hotel_id}", summary="Update a hotel")
def update_hotel(hotel_id: int, payload: HotelInput, db=Depends(get_db)):
    if not db.execute("SELECT 1 FROM hotels WHERE id=?", (hotel_id,)).fetchone():
        raise HTTPException(404, "Hotel not found")
    values = payload.model_dump(); values["id"] = hotel_id
    db.execute("UPDATE hotels SET name=:name,description=:description,address=:address,city=:city,country=:country,contact=:contact,rating=:rating,amenities=:amenities WHERE id=:id", values)
    return dict(db.execute("SELECT * FROM hotels WHERE id=?", (hotel_id,)).fetchone())


@router.delete("/hotels/{hotel_id}", summary="Deactivate a hotel")
def deactivate_hotel(hotel_id: int, db=Depends(get_db)):
    cursor = db.execute("UPDATE hotels SET is_active=0 WHERE id=? AND is_active=1", (hotel_id,))
    if not cursor.rowcount:
        raise HTTPException(404, "Active hotel not found")
    return {"id": hotel_id, "is_active": False}


@router.post("/room-types", status_code=201, summary="Create a room type")
def create_room_type(payload: RoomTypeInput, db=Depends(get_db)):
    values = payload.model_dump()
    cursor = db.execute("INSERT INTO room_types(name,description,capacity,base_price) VALUES(:name,:description,:capacity,:base_price)", values)
    return dict(db.execute("SELECT * FROM room_types WHERE id=?", (cursor.lastrowid,)).fetchone())


@router.get("/room-types", summary="List room types")
def list_room_types(db=Depends(get_db)):
    return {"items": [dict(row) for row in db.execute("SELECT * FROM room_types ORDER BY name").fetchall()]}


@router.post("/rooms", status_code=201, summary="Create a room")
def create_room(payload: RoomInput, db=Depends(get_db)):
    values = payload.model_dump()
    cursor = db.execute("INSERT INTO rooms(hotel_id,room_type_id,room_number,floor,status,price) VALUES(:hotel_id,:room_type_id,:room_number,:floor,:status,:price)", values)
    return dict(db.execute("SELECT * FROM rooms WHERE id=?", (cursor.lastrowid,)).fetchone())


@router.put("/rooms/{room_id}", summary="Update a room")
def update_room(room_id: int, payload: RoomInput, db=Depends(get_db)):
    if not db.execute("SELECT 1 FROM rooms WHERE id=?", (room_id,)).fetchone():
        raise HTTPException(404, "Room not found")
    values = payload.model_dump(); values["id"] = room_id
    db.execute("UPDATE rooms SET hotel_id=:hotel_id,room_type_id=:room_type_id,room_number=:room_number,floor=:floor,status=:status,price=:price WHERE id=:id", values)
    return dict(db.execute("SELECT * FROM rooms WHERE id=?", (room_id,)).fetchone())


@router.delete("/rooms/{room_id}", summary="Deactivate a room")
def deactivate_room(room_id: int, db=Depends(get_db)):
    cursor = db.execute("UPDATE rooms SET status='inactive' WHERE id=? AND status!='inactive'", (room_id,))
    if not cursor.rowcount:
        raise HTTPException(404, "Active room not found")
    return {"id": room_id, "status": "inactive"}


@router.get("/bookings", summary="List all bookings")
def list_bookings(status: str | None = None, db=Depends(get_db)):
    if status and status not in {"confirmed", "cancelled", "completed"}:
        raise HTTPException(422, "Invalid booking status")
    sql = "SELECT b.*,u.name AS customer_name,u.email AS customer_email,r.room_number,h.name AS hotel_name FROM bookings b JOIN users u ON u.id=b.user_id JOIN rooms r ON r.id=b.room_id JOIN hotels h ON h.id=r.hotel_id"
    rows = db.execute(sql + (" WHERE b.status=?" if status else "") + " ORDER BY b.created_at DESC", (status,) if status else ()).fetchall()
    return {"items": [dict(row) for row in rows]}


@router.patch("/bookings/{booking_id}/status", summary="Set booking status")
def set_booking_status(booking_id: int, status: str, db=Depends(get_db)):
    if status not in {"confirmed", "cancelled", "completed"}:
        raise HTTPException(422, "Invalid booking status")
    cursor = db.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    if not cursor.rowcount:
        raise HTTPException(404, "Booking not found")
    return {"id": booking_id, "status": status}
