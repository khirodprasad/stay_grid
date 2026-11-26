import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'

type AdminDashboardProps = {
  hotels: any[]
  bookings: any[]
  hotelForm: any
  setHotelForm: (value: any) => void
  createHotel: (event: FormEvent) => void
  setMessage: (message: string) => void
  request: (path: string, options?: RequestInit) => Promise<any>
}

const emptyRoomType = { name: '', description: '', capacity: '2', base_price: '100' }
const emptyRoom = { hotel_id: '', room_type_id: '', room_number: '', floor: '1', price: '', status: 'available' }

export default function AdminDashboardPanel({ hotels, bookings, hotelForm, setHotelForm, createHotel, setMessage, request }: AdminDashboardProps) {
  const [section, setSection] = useState('overview')
  const [roomType, setRoomType] = useState(emptyRoomType)
  const [room, setRoom] = useState(emptyRoom)
  const [roomTypes, setRoomTypes] = useState<any[]>([])
  const [allBookings, setAllBookings] = useState<any[]>(bookings)
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  const refresh = async () => {
    setLoading(true)
    try {
      const [types, reservationData] = await Promise.all([request('/admin/room-types'), request('/admin/bookings')])
      setRoomTypes(types.items || [])
      setAllBookings(reservationData.items || [])
    } catch (error: any) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { refresh() }, [])
  useEffect(() => { setAllBookings(bookings) }, [bookings])

  const addType = async (event: FormEvent) => {
    event.preventDefault()
    try {
      await request('/admin/room-types', { method: 'POST', body: JSON.stringify({ ...roomType, capacity: Number(roomType.capacity), base_price: Number(roomType.base_price) }) })
      setRoomType(emptyRoomType); await refresh(); setMessage('Room type created.')
    } catch (error: any) { setMessage(error.message) }
  }

  const addRoom = async (event: FormEvent) => {
    event.preventDefault()
    try {
      await request('/admin/rooms', { method: 'POST', body: JSON.stringify({ ...room, hotel_id: Number(room.hotel_id), room_type_id: Number(room.room_type_id), floor: Number(room.floor), price: room.price ? Number(room.price) : null }) })
      setRoom(emptyRoom); setMessage('Room created.'); await refresh()
    } catch (error: any) { setMessage(error.message) }
  }

  const setStatus = async (id: number, status: string) => {
    try { await request(`/admin/bookings/${id}/status?status=${status}`, { method: 'PATCH' }); await refresh(); setMessage('Booking status updated.') }
    catch (error: any) { setMessage(error.message) }
  }

  const filteredBookings = useMemo(() => filter === 'all' ? allBookings : allBookings.filter((booking) => booking.status === filter), [allBookings, filter])
  const revenue = allBookings.filter((booking) => booking.status !== 'cancelled').reduce((total, booking) => total + Number(booking.total_amount || 0), 0)
  const confirmed = allBookings.filter((booking) => booking.status === 'confirmed').length
  const cancelled = allBookings.filter((booking) => booking.status === 'cancelled').length
  const nav = [['overview', 'Overview'], ['hotels', 'Hotels'], ['rooms', 'Rooms & types'], ['bookings', 'Bookings'], ['reports', 'Reports']]

  return <main className="admin-layout">
    <aside className="admin-sidebar">
      <div><p className="eyebrow">STAYGRID CONTROL</p><h1>Admin panel</h1><p className="admin-muted">Manage properties, inventory, and reservations.</p></div>
      <nav aria-label="Admin sections">{nav.map(([id, label]) => <button key={id} className={section === id ? 'active' : ''} onClick={() => setSection(id)}>{label}</button>)}</nav>
      <a className="admin-console" href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">Open API console ↗</a>
    </aside>
    <section className="admin-main">
      <header className="admin-panel-header"><div><p className="eyebrow">{section.toUpperCase()}</p><h2>{section === 'overview' ? 'Good morning, Admin' : nav.find(([id]) => id === section)?.[1]}</h2></div><button className="outline" onClick={refresh}>↻ Refresh</button></header>
      {section === 'overview' && <>
        <div className="admin-stat-grid">
          <div className="admin-stat-card"><span>Active hotels</span><strong>{hotels.length}</strong><small>Public listings</small></div>
          <div className="admin-stat-card"><span>Room types</span><strong>{roomTypes.length}</strong><small>Configured types</small></div>
          <div className="admin-stat-card"><span>Total bookings</span><strong>{allBookings.length}</strong><small>{confirmed} confirmed</small></div>
          <div className="admin-stat-card"><span>Registered guests</span><strong>{new Set(allBookings.map((booking) => booking.customer_email || booking.user_id)).size}</strong><small>From reservations</small></div>
          <div className="admin-stat-card"><span>Cancelled</span><strong>{cancelled}</strong><small>Needs attention</small></div>
          <div className="admin-stat-card accent"><span>Revenue</span><strong>₹{revenue.toLocaleString('en-IN')}</strong><small>Confirmed and completed</small></div>
        </div>
        <div className="admin-overview-grid"><section className="admin-panel-card"><div className="admin-card-heading"><div><p className="eyebrow">RECENT ACTIVITY</p><h3>Latest bookings</h3></div><button className="link" onClick={() => setSection('bookings')}>View all →</button></div>{loading ? <p className="form-help">Loading bookings…</p> : filteredBookings.slice(0, 5).map((booking) => <div className="admin-list-row" key={booking.id}><div><b>#{booking.id} · {booking.hotel_name}</b><small>{booking.customer_name || 'Guest'} · {booking.check_in} → {booking.check_out}</small></div><span className={`status ${booking.status}`}>{booking.status}</span></div>)}{!loading && !filteredBookings.length && <p className="form-help">No bookings yet.</p>}</section><section className="admin-panel-card"><p className="eyebrow">QUICK ACTIONS</p><h3>Keep your inventory fresh</h3><button className="admin-action" onClick={() => setSection('hotels')}>＋ Add a hotel</button><button className="admin-action" onClick={() => setSection('rooms')}>＋ Add room type or room</button><button className="admin-action" onClick={() => setSection('bookings')}>⌁ Review bookings</button></section></div>
      </>}
      {section === 'hotels' && <section className="admin-panel-card admin-form"><p className="eyebrow">PROPERTY MANAGEMENT</p><h3>Add a hotel</h3><form onSubmit={createHotel}><div className="form-grid"><input required placeholder="Hotel name" value={hotelForm.name} onChange={(event) => setHotelForm({ ...hotelForm, name: event.target.value })} /><input required placeholder="City" value={hotelForm.city} onChange={(event) => setHotelForm({ ...hotelForm, city: event.target.value })} /><input required placeholder="Address" value={hotelForm.address} onChange={(event) => setHotelForm({ ...hotelForm, address: event.target.value })} /><input placeholder="Country" value={hotelForm.country} onChange={(event) => setHotelForm({ ...hotelForm, country: event.target.value })} /><input placeholder="Contact" value={hotelForm.contact} onChange={(event) => setHotelForm({ ...hotelForm, contact: event.target.value })} /><input type="number" min="0" max="5" step="0.1" placeholder="Rating" value={hotelForm.rating} onChange={(event) => setHotelForm({ ...hotelForm, rating: event.target.value })} /></div><textarea required placeholder="Short description" value={hotelForm.description} onChange={(event) => setHotelForm({ ...hotelForm, description: event.target.value })} /><input placeholder="Amenities (comma separated)" value={hotelForm.amenities} onChange={(event) => setHotelForm({ ...hotelForm, amenities: event.target.value })} /><button className="gold" type="submit">Create hotel →</button></form></section>}
      {section === 'rooms' && <div className="admin-overview-grid"><section className="admin-panel-card admin-form"><p className="eyebrow">ROOM TYPES</p><h3>Add room type</h3><form onSubmit={addType}><input required placeholder="Type name" value={roomType.name} onChange={(event) => setRoomType({ ...roomType, name: event.target.value })} /><input placeholder="Description" value={roomType.description} onChange={(event) => setRoomType({ ...roomType, description: event.target.value })} /><div className="form-grid"><input type="number" min="1" required placeholder="Capacity" value={roomType.capacity} onChange={(event) => setRoomType({ ...roomType, capacity: event.target.value })} /><input type="number" min="0" required placeholder="Base price" value={roomType.base_price} onChange={(event) => setRoomType({ ...roomType, base_price: event.target.value })} /></div><button className="gold">Create room type</button></form><div className="admin-mini-list">{roomTypes.map((type) => <span key={type.id}>{type.name} · {type.capacity} guests</span>)}</div></section><section className="admin-panel-card admin-form"><p className="eyebrow">ROOM INVENTORY</p><h3>Add room</h3><form onSubmit={addRoom}><select required value={room.hotel_id} onChange={(event) => setRoom({ ...room, hotel_id: event.target.value })}><option value="">Select hotel</option>{hotels.map((hotel) => <option key={hotel.id} value={hotel.id}>{hotel.name}</option>)}</select><select required value={room.room_type_id} onChange={(event) => setRoom({ ...room, room_type_id: event.target.value })}><option value="">Select room type</option>{roomTypes.map((type) => <option key={type.id} value={type.id}>{type.name}</option>)}</select><div className="form-grid"><input required placeholder="Room number" value={room.room_number} onChange={(event) => setRoom({ ...room, room_number: event.target.value })} /><input type="number" min="0" placeholder="Floor" value={room.floor} onChange={(event) => setRoom({ ...room, floor: event.target.value })} /></div><input type="number" min="0" placeholder="Price override" value={room.price} onChange={(event) => setRoom({ ...room, price: event.target.value })} /><select value={room.status} onChange={(event) => setRoom({ ...room, status: event.target.value })}><option value="available">Available</option><option value="maintenance">Maintenance</option><option value="inactive">Inactive</option></select><button className="gold">Create room</button></form></section></div>}
      {section === 'bookings' && <section className="admin-panel-card"><div className="admin-card-heading"><div><p className="eyebrow">RESERVATIONS</p><h3>Booking management</h3></div><select value={filter} onChange={(event) => setFilter(event.target.value)}><option value="all">All bookings</option><option value="confirmed">Confirmed</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option></select></div>{loading ? <p className="form-help">Loading bookings…</p> : filteredBookings.map((booking) => <div className="admin-booking" key={booking.id}><div><b>#{booking.id} · {booking.hotel_name}</b><small>{booking.customer_name || 'Guest'} · {booking.customer_email || ''} · Room {booking.room_number} · {booking.check_in} → {booking.check_out}</small></div><select value={booking.status} onChange={(event) => setStatus(booking.id, event.target.value)}><option>confirmed</option><option>completed</option><option>cancelled</option></select></div>)}{!loading && !filteredBookings.length && <p className="form-help">No bookings match this filter.</p>}</section>}
      {section === 'reports' && <div className="admin-overview-grid"><section className="admin-panel-card"><p className="eyebrow">PERFORMANCE</p><h3>Reporting centre</h3><div className="report-line"><span>Confirmed bookings</span><b>{confirmed}</b></div><div className="report-line"><span>Cancelled bookings</span><b>{cancelled}</b></div><div className="report-line"><span>Revenue</span><b>₹{revenue.toLocaleString('en-IN')}</b></div><button className="gold" onClick={() => setMessage('Report export will be available after report storage is connected.')}>Export report</button></section><section className="admin-panel-card"><p className="eyebrow">NEXT PHASE</p><h3>Operations centre</h3><p className="form-help">Payments, invoices, housekeeping, maintenance, notifications, and audit logs can be connected here as their database tables and endpoints are added.</p></section></div>}
    </section>
  </main>
}
