from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Flight, FlightRoute, Airport, FlightSchedule, FlightSeat, SeatClass, Airline, Aircraft, Booking, BookingDetail, Payment, Student, CheckIn
from . import db
from flask_login import login_required
from werkzeug.security import generate_password_hash
from datetime import datetime
import random
import string
import os
from flask import request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user


upload_folder = os.path.join('web', 'static', 'uploads')
views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('index.html')

# ---------------------------
# Dashboard View
# ---------------------------
@views.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ---------------------------
# User View
# ---------------------------
@views.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@views.route('/profile/update-image', methods=['POST'])
@login_required
def update_profile_image():
    if 'profile_image' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('views.profile'))

    file = request.files['profile_image']
    if file.filename == '':
        flash('Please choose a file.', 'error')
        return redirect(url_for('views.profile'))

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    current_user.profile_image = filename
    db.session.commit()
    flash('Profile image updated successfully!', 'success')
    return redirect(url_for('views.profile'))

# ---------------------------
# Flight View
# ---------------------------
@views.route('/flights')
@login_required
def flights():
    flights = Flight.query.all()
    return render_template('flight/flights.html', flights=flights)

@views.route('/flights/add', methods=['GET', 'POST'])
@login_required
def add_flight():
    airlines = Airline.query.all()
    aircrafts = Aircraft.query.all()
    routes = FlightRoute.query.all()

    if request.method == 'POST':
        flight_number = request.form['flight_number']
        airline_id = request.form['airline_id']
        aircraft_id = request.form['aircraft_id']
        route_id = request.form['route_id']

        # ✅ Check if flight number already exists
        existing_flight = Flight.query.filter_by(flight_number=flight_number).first()
        if existing_flight:
            flash('Flight number already exists. Please use a different one.', 'error')
            return render_template('flight/add_flight.html',
                                   airlines=airlines,
                                   aircrafts=aircrafts,
                                   routes=routes)

        new_flight = Flight(
            flight_number=flight_number,
            airline_id=airline_id,
            aircraft_id=aircraft_id,
            route_id=route_id
        )
        db.session.add(new_flight)
        db.session.commit()
        flash('Flight added successfully!', 'success')
        return redirect(url_for('views.flights'))

    return render_template('flight/add_flight.html',
                           airlines=airlines,
                           aircrafts=aircrafts,
                           routes=routes)


@views.route('/flights/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_flight(id):
    flight = Flight.query.get_or_404(id)
    if request.method == 'POST':
        flight.flight_number = request.form['flight_number']
        flight.airline_id = request.form['airline_id']
        flight.aircraft_id = request.form['aircraft_id']
        flight.route_id = request.form['route_id']
        db.session.commit()
        flash('Flight updated successfully!', 'success')
        return redirect(url_for('views.flights'))
    return render_template('flight/edit_flight.html', flight=flight)

@views.route('/flights/delete/<int:id>')
@login_required
def delete_flight(id):
    flight = Flight.query.get_or_404(id)
    db.session.delete(flight)
    db.session.commit()
    flash('Flight deleted.', 'danger')
    return redirect(url_for('views.flights'))

# ---------------------------
# FlightRoute View
# ---------------------------
@views.route('/flight_routes')
@login_required
def flight_routes():
    routes = FlightRoute.query.all()
    return render_template('flight_routes/flight_routes.html', routes=routes)

@views.route('/flight_routes/add', methods=['GET', 'POST'])
@login_required
def add_flight_route():
    airports = Airport.query.all()
    airlines = Airline.query.all()
    aircraft = Aircraft.query.all()

    if request.method == 'POST':
        departure_airport_id = request.form['departure_airport_id']
        arrival_airport_id = request.form['arrival_airport_id']
        airline_id = request.form['airline_id']
        aircraft_id = request.form['aircraft_id']
        distance = request.form['distance']
        duration = request.form['duration']

        new_route = FlightRoute(
            departure_airport_id=departure_airport_id,
            arrival_airport_id=arrival_airport_id,
            airline_id=airline_id,
            aircraft_id=aircraft_id,
            distance=distance,
            duration=duration
        )

        db.session.add(new_route)
        db.session.commit()
        flash('Flight route added successfully!', 'success')
        return redirect(url_for('views.flight_routes'))

    return render_template('flight_routes/add_route.html', airports=airports, airlines=airlines, aircraft=aircraft)


@views.route('/flight_routes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_flight_route(id):
    route = FlightRoute.query.get_or_404(id)
    airports = Airport.query.all()
    if request.method == 'POST':
        route.departure_airport_id = request.form['departure_airport_id']
        route.arrival_airport_id = request.form['arrival_airport_id']
        route.distance = request.form['distance']
        route.duration = request.form['duration']
        db.session.commit()
        flash('Flight route updated successfully!', 'success')
        return redirect(url_for('views.flight_routes'))
    return render_template('flight_routes/edit_route.html', route=route, airports=airports)

@views.route('/flight_routes/delete/<int:id>')
@login_required
def delete_flight_route(id):
    route = FlightRoute.query.get_or_404(id)
    db.session.delete(route)
    db.session.commit()
    flash('Flight route deleted.', 'danger')
    return redirect(url_for('views.flight_routes'))

# ---------------------------
# FlightSchedule View
# ---------------------------
@views.route('/flight_schedules')
@login_required
def flight_schedules():
    schedules = FlightSchedule.query.all()
    current_time = datetime.now()  # Use local time instead of UTC

    schedule_data = []
    for s in schedules:
        if current_time < s.departure_time:
            status = 'Standby'
        elif s.departure_time <= current_time < s.arrival_time:
            status = 'On Flight'
        else:
            status = 'Arrived'
        schedule_data.append({
            'schedule': s,
            'status': status
        })

    return render_template(
        'flight_schedules/flight_schedules.html',
        schedule_data=schedule_data,
        current_time=current_time
    )


@views.route('/flight_schedules/add', methods=['GET', 'POST'])
@login_required
def add_flight_schedule():
    flights = Flight.query.all()
    if request.method == 'POST':
        flight_id = request.form['flight_id']
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']

        # Parse datetime strings to datetime objects
        departure_dt = datetime.strptime(departure_time, '%Y-%m-%dT%H:%M')
        arrival_dt = datetime.strptime(arrival_time, '%Y-%m-%dT%H:%M')

        new_schedule = FlightSchedule(
            flight_id=flight_id,
            departure_time=departure_dt,
            arrival_time=arrival_dt
        )
        db.session.add(new_schedule)
        db.session.commit()
        flash('Flight schedule added successfully!', 'success')
        return redirect(url_for('views.flight_schedules'))

    return render_template('flight_schedules/add_schedule.html', flights=flights)


@views.route('/flight_schedules/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_flight_schedule(id):
    schedule = FlightSchedule.query.get_or_404(id)
    flights = Flight.query.all()
    if request.method == 'POST':
        schedule.flight_id = request.form['flight_id']
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']
        schedule.departure_time = datetime.strptime(departure_time, '%Y-%m-%dT%H:%M')
        schedule.arrival_time = datetime.strptime(arrival_time, '%Y-%m-%dT%H:%M')
        db.session.commit()
        flash('Flight schedule updated successfully!', 'success')
        return redirect(url_for('views.flight_schedules'))
    return render_template('flight_schedules/edit_schedule.html', schedule=schedule, flights=flights)

@views.route('/flight_schedules/delete/<int:id>')
@login_required
def delete_flight_schedule(id):
    schedule = FlightSchedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Flight schedule deleted.', 'danger')
    return redirect(url_for('views.flight_schedules'))

# ---------------------------
# FlightSeat View
# ---------------------------
@views.route('/flight_seats')
@login_required
def flight_seats():
    seats = FlightSeat.query.all()
    return render_template('flight_seats/flight_seats.html', seats=seats)

@views.route('/flight_seats/add', methods=['GET', 'POST'])
@login_required
def add_flight_seat():
    schedules = FlightSchedule.query.all()
    seat_classes = SeatClass.query.all()
    if request.method == 'POST':
        flight_schedule_id = request.form['flight_schedule_id']
        seat_number = request.form['seat_number']
        seat_class_id = request.form['seat_class_id']
        is_available = request.form.get('is_available') == 'on'
        price = request.form['price']

        new_seat = FlightSeat(
            flight_schedule_id=flight_schedule_id,
            seat_number=seat_number,
            seat_class_id=seat_class_id,
            is_available=is_available,
            price=price
        )
        db.session.add(new_seat)
        db.session.commit()
        flash('Flight seat added successfully!', 'success')
        return redirect(url_for('views.flight_seats'))

    return render_template('flight_seats/add_seat.html', schedules=schedules, seat_classes=seat_classes)


@views.route('/flight_seats/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_flight_seat(id):
    seat = FlightSeat.query.get_or_404(id)
    schedules = FlightSchedule.query.all()
    seat_classes = SeatClass.query.all()
    if request.method == 'POST':
        seat.flight_schedule_id = request.form['flight_schedule_id']
        seat.seat_number = request.form['seat_number']
        seat.seat_class_id = request.form['seat_class_id']
        seat.is_available = request.form.get('is_available') == 'on'
        seat.price = request.form['price']

        db.session.commit()
        flash('Flight seat updated successfully!', 'success')
        return redirect(url_for('views.flight_seats'))

    return render_template('flight_seats/edit_seat.html', seat=seat, schedules=schedules, seat_classes=seat_classes)

@views.route('/flight_seats/delete/<int:id>')
@login_required
def delete_flight_seat(id):
    seat = FlightSeat.query.get_or_404(id)
    db.session.delete(seat)
    db.session.commit()
    flash('Flight seat deleted.', 'danger')
    return redirect(url_for('views.flight_seats'))

# ---------------------------
# SeatClass View
# ---------------------------
@views.route('/seat_classes')
@login_required
def seat_classes():
    classes = SeatClass.query.all()
    return render_template('assets/seat_classes.html', classes=classes)

@views.route('/seat_classes/add', methods=['GET', 'POST'])
@login_required
def add_seat_class():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price_multiplier = float(request.form.get('price_multiplier', 1.0))

        new_class = SeatClass(name=name, description=description, price_multiplier=price_multiplier)
        db.session.add(new_class)
        db.session.commit()
        flash('Seat class added successfully!', 'success')
        return redirect(url_for('views.seat_classes'))

    return render_template('assets/add_class.html')

@views.route('/seat_classes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_seat_class(id):
    seat_class = SeatClass.query.get_or_404(id)
    if request.method == 'POST':
        seat_class.name = request.form['name']
        seat_class.description = request.form['description']
        seat_class.price_multiplier = float(request.form.get('price_multiplier', 1.0))
        db.session.commit()
        flash('Seat class updated successfully!', 'success')
        return redirect(url_for('views.seat_classes'))

    return render_template('seat_classes/edit_class.html', seat_class=seat_class)

@views.route('/seat_classes/delete/<int:id>')
@login_required
def delete_seat_class(id):
    seat_class = SeatClass.query.get_or_404(id)
    db.session.delete(seat_class)
    db.session.commit()
    flash('Seat class deleted.', 'danger')
    return redirect(url_for('views.seat_classes'))

# ---------------------------
# Airport View
# ---------------------------
@views.route('/airports')
@login_required
def airports():
    all_airports = Airport.query.all()
    return render_template('assets/airports.html', airports=all_airports)

@views.route('/airports/add', methods=['GET', 'POST'])
@login_required
def add_airport():
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        city = request.form['city']
        country = request.form['country']

        # Check for duplicate code
        existing_airport = Airport.query.filter_by(code=code).first()
        if existing_airport:
            flash('Airport code already exists. Please use a different code.', category='error')
            return redirect(url_for('views.add_airport'))

        new_airport = Airport(code=code, name=name, city=city, country=country)
        db.session.add(new_airport)
        db.session.commit()
        flash('Airport added successfully!', category='success')
        return redirect(url_for('views.airports'))

    return render_template('assets/add_airport.html')


@views.route('/airports/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_airport(id):
    airport = Airport.query.get_or_404(id)
    if request.method == 'POST':
        airport.code = request.form['code']
        airport.name = request.form['name']
        airport.city = request.form['city']
        airport.country = request.form['country']
        db.session.commit()
        return redirect(url_for('views.airports'))
    return render_template('assets/edit_airport.html', airport=airport)


@views.route('/airports/delete/<int:id>')
@login_required
def delete_airport(id):
    airport = Airport.query.get_or_404(id)
    db.session.delete(airport)
    db.session.commit()
    return redirect(url_for('views.airports'))

# ---------------------------
# Airline View
# ---------------------------
@views.route('/airlines')
@login_required
def airlines():
    all_airlines = Airline.query.all()
    return render_template('assets/airlines.html', airlines=all_airlines)

@views.route('/airlines/add', methods=['GET', 'POST'])
@login_required
def add_airline():
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        new_airline = Airline(code=code, name=name)
        db.session.add(new_airline)
        db.session.commit()
        return redirect(url_for('views.airlines'))
    return render_template('assets/add_airline.html')

@views.route('/airlines/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_airline(id):
    airline = Airline.query.get_or_404(id)
    if request.method == 'POST':
        airline.code = request.form['code']
        airline.name = request.form['name']
        db.session.commit()
        return redirect(url_for('views.airlines'))
    return render_template('assets/edit_airline.html', airline=airline)

@views.route('/airlines/delete/<int:id>')
@login_required
def delete_airline(id):
    airline = Airline.query.get_or_404(id)
    db.session.delete(airline)
    db.session.commit()
    return redirect(url_for('views.airlines'))

# ---------------------------
# Aircraft View
# ---------------------------
@views.route('/aircraft')
@login_required
def aircraft():
    all_aircraft = Aircraft.query.all()
    return render_template('assets/aircraft.html', aircraft=all_aircraft)

@views.route('/aircraft/add', methods=['GET', 'POST'])
@login_required
def add_aircraft():
    airlines = Airline.query.all()
    if request.method == 'POST':
        model = request.form['model']
        aircraft_type = request.form['type']
        capacity = request.form['capacity']
        airline_id = request.form['airline_id']

        new_aircraft = Aircraft(
            model=model,
            type=aircraft_type,
            capacity=capacity,
            airline_id=airline_id
        )

        db.session.add(new_aircraft)
        db.session.commit()
        return redirect(url_for('views.aircraft'))

    return render_template('assets/add_aircraft.html', airlines=airlines)


@views.route('/aircraft/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_aircraft(id):
    aircraft = Aircraft.query.get_or_404(id)
    airlines = Airline.query.all()

    if request.method == 'POST':
        aircraft.model = request.form['model']
        aircraft.capacity = request.form['capacity']
        aircraft.airline_id = request.form['airline_id']
        db.session.commit()
        return redirect(url_for('views.aircraft'))

    return render_template('assets/edit_aircraft.html', aircraft=aircraft, airlines=airlines)


@views.route('/aircraft/delete/<int:id>')
@login_required
def delete_aircraft(id):
    aircraft = Aircraft.query.get_or_404(id)
    db.session.delete(aircraft)
    db.session.commit()
    return redirect(url_for('views.aircraft'))

# ---------------------------
# Booking View
# ---------------------------
@views.route('/bookings')
@login_required
def bookings():
    all_bookings = Booking.query.all()
    return render_template('booking_payment/bookings.html', bookings=all_bookings)

def generate_reference():
    return 'BKG' + ''.join(random.choices(string.digits, k=7))

@views.route('/bookings/add', methods=['GET', 'POST'])
@login_required
def add_booking():
    students = Student.query.all()
    if request.method == 'POST':
        student_id = request.form['student_id']
        status = request.form['status']

        reference = generate_reference()
        # Optional: Ensure reference is unique
        while Booking.query.filter_by(reference=reference).first():
            reference = generate_reference()

        new_booking = Booking(
            student_id=student_id,
            reference=reference,
            total_amount=0.0,  # default, or update later from booking details
            status=status
        )
        db.session.add(new_booking)
        db.session.commit()
        flash('Booking created successfully!', 'success')
        return redirect(url_for('views.bookings'))

    return render_template('booking_payment/add_booking.html', students=students)

@views.route('/bookings/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_booking(id):
    booking = Booking.query.get_or_404(id)
    students = Student.query.all()

    if request.method == 'POST':
        booking.student_id = request.form['student_id']
        booking.status = request.form['status']
        db.session.commit()
        flash('Booking updated!', 'success')
        return redirect(url_for('views.bookings'))

    return render_template('booking_payment/edit_booking.html', booking=booking, students=students)

@views.route('/bookings/delete/<int:id>')
@login_required
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted.', 'danger')
    return redirect(url_for('views.bookings'))

# ---------------------------
# Booking_Details View
# ---------------------------
@views.route('/booking-details')
def booking_details():
    all_details = BookingDetail.query.all()
    return render_template('booking_payment/booking_details.html', booking_details=all_details)

@views.route('/booking-details/add', methods=['GET', 'POST'])
def add_booking_detail():
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        flight_id = request.form.get('flight_id')
        seat_class_id = request.form.get('seat_class_id')
        quantity = request.form.get('quantity')

        new_detail = BookingDetail(
            booking_id=booking_id,
            flight_id=flight_id,
            seat_class_id=seat_class_id,
            quantity=quantity,
            passenger_first_name='N/A',  # Temporary dummy data
            passenger_last_name='N/A'    # Required fields
        )

        try:
            db.session.add(new_detail)
            db.session.commit()
            flash('Booking detail added successfully!', 'success')
            return redirect(url_for('views.booking_details'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding booking detail: {e}', 'danger')

    return render_template('booking_payment/add_booking_detail.html')

@views.route('/booking-details/edit/<int:id>', methods=['GET', 'POST'])
def edit_booking_detail(id):
    detail = BookingDetail.query.get_or_404(id)
    if request.method == 'POST':
        detail.booking_id = request.form.get('booking_id')
        detail.flight_id = request.form.get('flight_id')
        detail.seat_class_id = request.form.get('seat_class_id')
        detail.quantity = request.form.get('quantity')

        try:
            db.session.commit()
            flash('Booking detail updated successfully!', 'success')
            return redirect(url_for('views.booking_details'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating booking detail: {e}', 'danger')

    return render_template('booking_payment/edit_booking_detail.html', detail=detail)

@views.route('/booking-details/delete/<int:id>', methods=['POST'])
def delete_booking_detail(id):
    detail = BookingDetail.query.get_or_404(id)
    try:
        db.session.delete(detail)
        db.session.commit()
        flash('Booking detail deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting booking detail: {e}', 'danger')
    return redirect(url_for('views.booking_details'))

# ---------------------------
# Payment View
# ---------------------------
@views.route('/payments')
def payments():
    all_payments = Payment.query.all()
    return render_template('booking_payment/payments.html', payments=all_payments)

# Add payment
@views.route('/payments/add', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        amount = request.form['amount']
        method = request.form['method']
        transaction_id = request.form['transaction_id']
        status = request.form['status']

        new_payment = Payment(
            booking_id=booking_id,
            amount=amount,
            method=method,
            transaction_id=transaction_id,
            status=status
        )
        db.session.add(new_payment)
        db.session.commit()
        return redirect(url_for('views.payments'))

    bookings = Booking.query.all()  # For dropdown selection
    return render_template('booking_payment/add_payment.html', bookings=bookings)

# Edit payment
@views.route('/payments/edit/<int:id>', methods=['GET', 'POST'])
def edit_payment(id):
    payment = Payment.query.get_or_404(id)

    if request.method == 'POST':
        payment.booking_id = request.form['booking_id']
        payment.amount = request.form['amount']
        payment.method = request.form['method']
        payment.transaction_id = request.form['transaction_id']
        payment.status = request.form['status']

        db.session.commit()
        return redirect(url_for('views.payments'))

    bookings = Booking.query.all()
    return render_template('booking_payment/edit_payment.html', payment=payment, bookings=bookings)

# Delete payment
@views.route('/payments/delete/<int:id>', methods=['POST'])
def delete_payment(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    return redirect(url_for('views.payments'))

# ---------------------------
# Checkin View
# ---------------------------
@views.route('/check-ins')
def check_ins():
    all_check_ins = CheckIn.query.all()
    return render_template('admin/check_ins.html', check_ins=all_check_ins)

@views.route('/check-ins/add', methods=['GET', 'POST'])
def add_check_in():
    if request.method == 'POST':
        booking_detail_id = request.form.get('booking_detail_id')
        baggage_count = request.form.get('checked_baggage_count', 0)
        baggage_weight = request.form.get('checked_baggage_weight', 0.0)

        new_check_in = CheckIn(
            booking_detail_id=booking_detail_id,
            checked_baggage_count=baggage_count,
            checked_baggage_weight=baggage_weight
        )
        db.session.add(new_check_in)
        db.session.commit()
        flash('Check-in successfully added!', 'success')
        return redirect(url_for('views.check_ins'))

    booking_details = BookingDetail.query.all()
    return render_template('admin/add_check_in.html', booking_details=booking_details)

@views.route('/check-ins/toggle/<int:check_in_id>')
def toggle_boarding_pass(check_in_id):
    check_in = CheckIn.query.get_or_404(check_in_id)
    check_in.boarding_pass_issued = not check_in.boarding_pass_issued
    db.session.commit()
    flash('Boarding pass status updated.', 'info')
    return redirect(url_for('views.check_ins'))

@views.route('/check-ins/edit/<int:check_in_id>', methods=['GET', 'POST'])
def edit_check_in(check_in_id):
    check_in = CheckIn.query.get_or_404(check_in_id)

    if request.method == 'POST':
        check_in.checked_baggage_count = request.form.get('checked_baggage_count', 0)
        check_in.checked_baggage_weight = request.form.get('checked_baggage_weight', 0.0)
        check_in.boarding_pass_issued = bool(request.form.get('boarding_pass_issued'))

        db.session.commit()
        flash('Check-in updated successfully!', 'success')
        return redirect(url_for('views.check_ins'))

    return render_template('admin/edit_check_in.html', check_in=check_in)

@views.route('/check-ins/delete/<int:check_in_id>', methods=['POST'])
def delete_check_in(check_in_id):
    check_in = CheckIn.query.get_or_404(check_in_id)
    db.session.delete(check_in)
    db.session.commit()
    flash('Check-in deleted successfully!', 'danger')
    return redirect(url_for('views.check_ins'))

# ---------------------------
# Student Views
# ---------------------------
@views.route('/students')
def students():
    all_students = Student.query.all()
    return render_template('admin/students.html', students=all_students)

@views.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        date_of_birth_str = request.form.get('date_of_birth')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')

        # ✅ Convert string to date
        date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()

        new_student = Student(
            username=username,
            password=generate_password_hash(password),
            email=email,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            phone_number=phone_number,
            address=address
        )
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('views.students'))

    return render_template('admin/add_student.html')


@views.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.username = request.form.get('username')
        student.email = request.form.get('email')
        student.first_name = request.form.get('first_name')
        student.last_name = request.form.get('last_name')
        date_of_birth_str = request.form.get('date_of_birth')
        student.phone_number = request.form.get('phone_number')
        student.address = request.form.get('address')

        # ✅ Convert string to date
        student.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()

        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('views.students'))

    return render_template('admin/edit_student.html', student=student)

@views.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'danger')
    return redirect(url_for('views.students'))
