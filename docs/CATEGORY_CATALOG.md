# StayGrid Category Catalogue

This catalogue defines the product categories required for a complete hotel management system. `Implemented` means the current project already has the category in the API or frontend. `TODO` identifies categories that should be added for a full production system.

## 1. Authentication and accounts - Implemented

Purpose: identify users and protect private actions.

Core data: name, email, password hash, role, token expiry, created date.

Required actions:

- [x] Customer registration and login.
- [x] Current-user profile.
- [x] Admin role protection.
- [ ] Password reset and email verification.
- [ ] Account lockout and refresh tokens.

## 2. Guests and customer profiles - Partial

Purpose: store the guest information needed for stays and communication.

Core data: guest name, email, phone, address, identification, emergency contact, preferences.

Required actions:

- [x] Customer account identity.
- [ ] Guest profile update.
- [ ] Multiple guests under one booking.
- [ ] Guest identification verification.
- [ ] Guest booking history and preferences.

## 3. Hotels and properties - Implemented

Purpose: manage properties published on StayGrid.

Core data: name, description, address, city, country, contact, rating, amenities, active status, images.

Required actions:

- [x] Public hotel listing and search.
- [x] Hotel details.
- [x] Admin create, update, and deactivate hotel.
- [ ] Hotel image gallery.
- [ ] Check-in policy, cancellation policy, tax profile, and operating hours.

## 4. Room types - Implemented

Purpose: define reusable room categories and pricing defaults.

Core data: name, description, capacity, base price, bed configuration, amenities.

Required actions:

- [x] Admin create and list room types.
- [ ] Admin update and deactivate room types.
- [ ] Seasonal and weekend pricing.
- [ ] Room-type image gallery.

## 5. Rooms and inventory - Implemented

Purpose: track physical rooms and their operating state.

Core data: hotel, room type, room number, floor, price override, status.

Required actions:

- [x] Admin create, update, and deactivate rooms.
- [x] Duplicate room prevention within a hotel.
- [x] Available, maintenance, and inactive states.
- [ ] Room cleaning state and housekeeping assignment.
- [ ] Room blocks and out-of-order periods.

## 6. Availability and search - Implemented

Purpose: return rooms that can accommodate a requested stay.

Core data: destination, check-in, check-out, guests, room status, booking overlaps.

Required actions:

- [x] Hotel text and city search.
- [x] Date and guest-capacity filtering.
- [x] Date-overlap protection.
- [ ] Sorting, filters, pagination, and map search.
- [ ] Rate and promotion filters.

## 7. Reservations and bookings - Implemented

Purpose: manage the complete stay lifecycle.

Core data: guest, room, dates, guests, total amount, status, created date.

Required actions:

- [x] Create a confirmed booking.
- [x] View customer bookings.
- [x] Cancel confirmed bookings.
- [x] Admin booking list and status changes.
- [ ] Modify dates or room.
- [ ] Check-in, checked-in, check-out, no-show, and refund statuses.

## 8. Payments and refunds - TODO

Purpose: collect and reconcile booking payments.

Core data: booking, amount, currency, payment method, provider reference, payment status, paid date.

Required actions:

- [ ] Payment intent and authorization.
- [ ] Cash, card, bank transfer, and online payment methods.
- [ ] Payment confirmation and webhook handling.
- [ ] Partial and full refunds.
- [ ] Failed payment retry and reconciliation.

## 9. Invoices and taxes - TODO

Purpose: produce legally useful charges and receipts.

Core data: invoice number, booking, subtotal, taxes, fees, discount, total, currency, status, issue date.

Required actions:

- [ ] Generate invoice after payment or checkout.
- [ ] Configure tax and service-charge rules.
- [ ] Download or email invoice.
- [ ] Credit notes and refund adjustments.

## 10. Hotel services and service orders - TODO

Purpose: manage extras requested during a stay.

Core data: service name, description, price, availability, booking, quantity, order date, status.

Required actions:

- [ ] Admin service catalogue.
- [ ] Customer service request.
- [ ] Quantity, pricing, and booking charge integration.
- [ ] Fulfilment status and staff assignment.

## 11. Staff and roles - TODO

Purpose: give hotel employees access appropriate to their duties.

Core data: hotel, name, role, contact, hire date, active status.

Required actions:

- [ ] Staff accounts and role permissions.
- [ ] Front desk, housekeeping, maintenance, finance, and manager roles.
- [ ] Staff assignment to rooms, tasks, and service orders.
- [ ] Disable former staff access.

## 12. Housekeeping and maintenance - TODO

Purpose: keep rooms safe, clean, and ready to sell.

Core data: room, reported by, description, priority, status, assigned staff, timestamps.

Required actions:

- [ ] Maintenance request creation and tracking.
- [ ] Cleaning schedule and room readiness.
- [ ] Priority, assignment, comments, and completion evidence.
- [ ] Automatically block rooms under maintenance.

## 13. Notifications and communication - TODO

Purpose: keep guests and staff informed.

Core data: recipient, channel, template, event, delivery status, sent date.

Required actions:

- [ ] Booking confirmation.
- [ ] Cancellation, payment, check-in, and checkout notifications.
- [ ] Email and optional SMS or push channels.
- [ ] Retry failed deliveries and record delivery status.

## 14. Reviews and ratings - TODO

Purpose: collect verified guest feedback.

Core data: booking, guest, hotel, rating, comment, response, moderation status.

Required actions:

- [ ] Review only after a completed stay.
- [ ] Rating summary per hotel.
- [ ] Admin moderation and hotel response.
- [ ] Report abusive content.

## 15. Reports and analytics - TODO

Purpose: help administrators understand hotel performance.

Core data: occupancy, revenue, bookings, cancellations, average rate, service sales, periods.

Required actions:

- [ ] Occupancy and availability reports.
- [ ] Revenue and payment reports.
- [ ] Cancellation and no-show reports.
- [ ] Export CSV or spreadsheet reports.
- [ ] Date-range filters and hotel filters.

## 16. Administration and settings - Partial

Purpose: configure and govern the platform.

Required actions:

- [x] Admin hotel, room, and booking management.
- [ ] User and staff management.
- [ ] Hotel policies, taxes, currencies, and cancellation rules.
- [ ] Audit log for sensitive changes.
- [ ] Feature flags and system settings.

## 17. Platform quality requirements

- [ ] Secure password storage, expiring tokens, role checks, and HTTPS in production.
- [ ] MySQL foreign keys, indexes, transactions, backups, and restore testing.
- [ ] Request validation and consistent error responses.
- [ ] Responsive and keyboard-accessible frontend.
- [ ] API, integration, security, and frontend flow tests.
- [ ] Health monitoring, structured logs, alerting, and deployment rollback.
