# StayGrid Ticket Development Phases

This plan breaks a StayGrid feature ticket into reviewable phases. Copy the checklist into a ticket and mark each item when complete. The production database target is MySQL.

## Functional requirements

### Accounts and access

- [ ] A visitor can create a customer account with name, email, and password.
- [ ] The system rejects invalid email addresses, weak passwords, duplicate emails, and unknown credentials.
- [ ] A customer can sign in, sign out, and view the current account.
- [ ] Protected actions require an access token.
- [ ] Admin actions require the administrator role.
- [ ] Unauthorized and forbidden requests return clear errors.

### Hotels and search

- [ ] A visitor can list active hotels.
- [ ] A visitor can search by text and city.
- [ ] A visitor can view hotel details, address, rating, amenities, and rooms.
- [ ] A visitor can filter results by dates and guest capacity.
- [ ] Inactive hotels are hidden from public results.
- [ ] Empty searches return a useful empty state.

### Room inventory and availability

- [ ] An admin can create, edit, and deactivate hotels.
- [ ] An admin can create room types with capacity and base price.
- [ ] An admin can create, edit, and deactivate rooms.
- [ ] The system prevents duplicate room numbers within one hotel.
- [ ] A visitor can view room details and nightly price.
- [ ] Availability checks include check-in, check-out, capacity, active hotel, room status, and existing bookings.
- [ ] Maintenance and inactive rooms cannot be booked.

### Bookings

- [ ] An authenticated customer can book an available room.
- [ ] The system validates dates, guest count, room capacity, and price calculation.
- [ ] The system prevents overlapping confirmed bookings for the same room.
- [ ] A customer can view their bookings.
- [ ] A booking owner or admin can cancel a confirmed booking.
- [ ] A cancelled or completed booking cannot be cancelled again.
- [ ] An admin can list bookings and change their status.

### Responses and operations

- [ ] Successful creates return `201` where appropriate.
- [ ] Validation errors identify the invalid field.
- [ ] Missing resources return `404`.
- [ ] Duplicate or availability conflicts return `409`.
- [ ] API behavior is represented in Swagger/OpenAPI.
- [ ] The frontend shows loading, success, empty, validation, authorization, conflict, and server-error states.

## Non-functional requirements

### Security

- [ ] Passwords are stored as salted, slow hashes and never in plain text.
- [ ] Access tokens are signed, expire, and are validated on every protected request.
- [ ] Role checks are enforced on the backend, not only in the frontend.
- [ ] CORS allows only approved frontend origins.
- [ ] Secrets and customer data are excluded from source control and logs.
- [ ] Production deployments use strong secrets and HTTPS.

### Performance and scalability

- [ ] Common hotel and availability queries use appropriate indexes.
- [ ] List endpoints support bounded pagination or result limits.
- [ ] Booking writes use a transaction to avoid race-condition double bookings.
- [ ] The frontend avoids duplicate requests and gives feedback during slow requests.
- [ ] Database and API timeouts are configured for production.

### Reliability and data integrity

- [ ] Foreign keys and database constraints protect relationships and valid states.
- [ ] Failed writes roll back without partial bookings or inventory changes.
- [ ] The API returns a health response for monitoring.
- [ ] Database backups and restore procedures are defined before production use.
- [ ] Configuration errors fail clearly during startup.

### Usability and accessibility

- [ ] Primary flows work on desktop and mobile widths.
- [ ] Forms have labels, required-field feedback, and readable errors.
- [ ] Keyboard users can navigate menus, forms, dialogs, and buttons.
- [ ] Focus remains understandable when a modal opens or closes.
- [ ] Color contrast and status indicators remain readable.
- [ ] Dates, currency, and booking status are displayed consistently.

### Maintainability and quality

- [ ] Backend routes, schemas, security, and database code remain separated by responsibility.
- [ ] Frontend API calls use one shared request helper.
- [ ] New behavior includes focused endpoint and UI verification.
- [ ] API examples and environment variables are documented.
- [ ] Generated files, local databases, credentials, and virtual environments are ignored.
- [ ] Changes pass formatting, build, import, and diff checks.

### Deployment and operations

- [ ] Separate development and production configuration is documented.
- [ ] The frontend API URL is configurable without source changes.
- [ ] The backend can run behind a production ASGI server.
- [ ] Logs exclude passwords, tokens, and sensitive personal data.
- [ ] Monitoring covers health, errors, latency, database failures, and booking conflicts.
- [ ] A rollback plan exists for database and application releases.

## Phase 0 - Ticket definition

- [ ] Write the user story and expected outcome.
- [ ] Define the user role: guest, customer, admin, or staff.
- [ ] List affected screens, API endpoints, database entities, and permissions.
- [ ] Define acceptance criteria and error cases.
- [ ] Confirm whether the change affects existing bookings or customer data.
- [ ] Identify out-of-scope work.

## Phase 1 - Investigation and design

- [ ] Inspect the existing frontend route and component flow.
- [ ] Inspect related FastAPI routes, schemas, dependencies, and database tables.
- [ ] Confirm the API contract: method, path, request body, query parameters, response, and status codes.
- [ ] Decide loading, empty, validation, unauthorized, conflict, and server-error states.
- [ ] Create or update a small data-flow or screen sketch when the ticket crosses layers.
- [ ] Record migrations or backwards-compatibility needs.

## Phase 2 - Database and domain model

- [ ] Add or update tables, columns, indexes, constraints, or seed data.
- [ ] Preserve foreign keys and booking date-overlap protection.
- [ ] Add model validation for required fields, ranges, dates, and allowed statuses.
- [ ] Plan rollback or migration handling.
- [ ] Verify existing records still load correctly.

## Phase 3 - Backend implementation

- [ ] Add Pydantic request and response schemas.
- [ ] Add the route under `backend/app/api/routes/`.
- [ ] Register the route in `backend/app/api/router.py`.
- [ ] Add authentication and role checks where required.
- [ ] Use the shared database dependency and commit changes transactionally.
- [ ] Return consistent success and error responses.
- [ ] Handle duplicate, missing, unavailable, and invalid resources.
- [ ] Update Swagger summaries and response documentation.

## Phase 4 - Frontend implementation

- [ ] Add or update the page, component, form, or navigation entry.
- [ ] Connect requests through the shared API helper.
- [ ] Include bearer authentication for protected requests.
- [ ] Add loading, success, empty, validation, unauthorized, conflict, and failure states.
- [ ] Validate user input before submission and show backend errors clearly.
- [ ] Keep the StayGrid visual system and responsive behavior.
- [ ] Confirm keyboard and mobile usability.

## Phase 5 - Integration

- [ ] Run the backend and frontend together.
- [ ] Verify frontend origin is allowed by backend CORS.
- [ ] Test the complete user flow from the UI.
- [ ] Test the same endpoint in Swagger UI.
- [ ] Confirm database changes appear in subsequent reads.
- [ ] Confirm refresh, sign-out, expired-token, and retry behavior.

## Phase 6 - Verification

- [ ] Test the happy path.
- [ ] Test invalid input and missing fields.
- [ ] Test unauthenticated and wrong-role access.
- [ ] Test duplicate and conflicting requests.
- [ ] Test missing resources and empty results.
- [ ] Test booking overlap and cancellation rules when relevant.
- [ ] Run `npm run build` from `frontend/`.
- [ ] Verify backend imports and `/openapi.json`.
- [ ] Run `git diff --check`.

## Phase 7 - Documentation and handoff

- [ ] Update `backend/README.md` when an endpoint or setup step changes.
- [ ] Update `docs/PROJECT_DOCUMENTATION.md` when architecture or configuration changes.
- [ ] Add request and response examples for new API behavior.
- [ ] Record environment variables and admin permissions needed.
- [ ] Summarize changed files, verification performed, and known limitations.
- [ ] Confirm generated files, credentials, local databases, and `.venv` are not included.

## Ticket completion gate

- [ ] Acceptance criteria are demonstrably satisfied.
- [ ] Existing flows still work.
- [ ] Frontend build passes.
- [ ] Backend and Swagger checks pass.
- [ ] Documentation is current.
- [ ] The branch is ready for review.
