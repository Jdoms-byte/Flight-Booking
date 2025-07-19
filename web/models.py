from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from flask_login import UserMixin


# ---------------------------
# User Authentication Model
# ---------------------------
# models.py
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(225), unique=True, nullable=False)
    password = db.Column(db.String(225), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True, default='default.png')  # default image



from . import db

# ---------------------------
# Airport Model
# ---------------------------
class Airport(db.Model):
    __tablename__ = 'airport'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)

    # Relationships
    routes_departure = db.relationship('FlightRoute', back_populates='departure_airport', foreign_keys='FlightRoute.departure_airport_id')
    routes_arrival = db.relationship('FlightRoute', back_populates='arrival_airport', foreign_keys='FlightRoute.arrival_airport_id')

# ---------------------------
# Airline Model
# ---------------------------
class Airline(db.Model):
    __tablename__ = 'airline'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    aircraft = db.relationship('Aircraft', back_populates='airline')
    flights = db.relationship('Flight', back_populates='airline')
    flight_routes = db.relationship('FlightRoute', back_populates='airline')

# ---------------------------
# Aircraft Model
# ---------------------------
class Aircraft(db.Model):
    __tablename__ = 'aircraft'
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # NEW: "Domestic" or "International"
    capacity = db.Column(db.Integer, nullable=False)
    airline_id = db.Column(db.Integer, db.ForeignKey('airline.id'), nullable=False)

    airline = db.relationship('Airline', back_populates='aircraft')
    flights = db.relationship('Flight', back_populates='aircraft')


# ---------------------------
# FlightRoute Model
# ---------------------------
class FlightRoute(db.Model):
    __tablename__ = 'flight_route'
    id = db.Column(db.Integer, primary_key=True)
    departure_airport_id = db.Column(db.Integer, db.ForeignKey('airport.id'), nullable=False)
    arrival_airport_id = db.Column(db.Integer, db.ForeignKey('airport.id'), nullable=False)
    airline_id = db.Column(db.Integer, db.ForeignKey('airline.id'), nullable=False)
    aircraft_id = db.Column(db.Integer, db.ForeignKey('aircraft.id'), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Float, nullable=False)

    departure_airport = db.relationship('Airport', foreign_keys=[departure_airport_id], back_populates='routes_departure')
    arrival_airport = db.relationship('Airport', foreign_keys=[arrival_airport_id], back_populates='routes_arrival')
    airline = db.relationship('Airline', back_populates='flight_routes')
    aircraft = db.relationship('Aircraft', backref='flight_routes')

    flights = db.relationship('Flight', back_populates='route')


# ---------------------------
# Flight Model
# ---------------------------
class Flight(db.Model):
    __tablename__ = 'flight'
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), nullable=False, unique=True)
    airline_id = db.Column(db.Integer, db.ForeignKey('airline.id'), nullable=False)
    aircraft_id = db.Column(db.Integer, db.ForeignKey('aircraft.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('flight_route.id'), nullable=False)

    airline = db.relationship('Airline', back_populates='flights')
    aircraft = db.relationship('Aircraft', back_populates='flights')
    route = db.relationship('FlightRoute', back_populates='flights')
    schedules = db.relationship('FlightSchedule', back_populates='flight')


    

# ---------------------------
# FlightSchedule Model
# ---------------------------
class FlightSchedule(db.Model):
    __tablename__ = 'flight_schedule'
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)

    flight = db.relationship('Flight', back_populates='schedules')
    seats = db.relationship('FlightSeat', back_populates='flight_schedule')





# ---------------------------
# SeatClass Model
# ---------------------------
class SeatClass(db.Model):
    __tablename__ = 'seat_class'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    price_multiplier = db.Column(db.Float, nullable=False, default=1.0)

    seats = db.relationship('FlightSeat', back_populates='seat_class')

# ---------------------------
# FlightSeat Model
# ---------------------------
class FlightSeat(db.Model):
    __tablename__ = 'flight_seat'
    id = db.Column(db.Integer, primary_key=True)
    flight_schedule_id = db.Column(db.Integer, db.ForeignKey('flight_schedule.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_class_id = db.Column(db.Integer, db.ForeignKey('seat_class.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    price = db.Column(db.Float, nullable=False)

    flight_schedule = db.relationship('FlightSchedule', back_populates='seats')
    seat_class = db.relationship('SeatClass', back_populates='seats')
    booking_details = db.relationship('BookingDetail', back_populates='seat')

# ---------------------------
# Booking Model
# ---------------------------
class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    reference = db.Column(db.String(10), unique=True, nullable=False)
    booking_date = db.Column(db.DateTime, default=func.now())
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Confirmed')
    payment_status = db.Column(db.String(20), default='Pending')

    student = db.relationship('Student', back_populates='bookings')
    details = db.relationship('BookingDetail', back_populates='booking')
    payments = db.relationship('Payment', back_populates='booking')

# ---------------------------
# BookingDetail Model
# ---------------------------
class BookingDetail(db.Model):
    __tablename__ = 'booking_detail'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('flight_seat.id'), nullable=True)
    seat_class_id = db.Column(db.Integer, db.ForeignKey('seat_class.id'))  # ✅ Included
    quantity = db.Column(db.Integer)  # ✅ Included
    passenger_first_name = db.Column(db.String(50), nullable=False)
    passenger_last_name = db.Column(db.String(50), nullable=False)
    passenger_email = db.Column(db.String(100))
    passenger_phone = db.Column(db.String(20))
    passenger_dob = db.Column(db.Date)
    passport_number = db.Column(db.String(20))
    special_requests = db.Column(db.Text)

    booking = db.relationship('Booking', back_populates='details')
    seat = db.relationship('FlightSeat', back_populates='booking_details')
    seat_class = db.relationship('SeatClass')  # Optional


# ---------------------------
# Payment Model
# ---------------------------
class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime, default=func.now())
    status = db.Column(db.String(20), default='Completed')

    booking = db.relationship('Booking', back_populates='payments')
   

# ---------------------------
# CheckIn Model
# ---------------------------
class CheckIn(db.Model):
    __tablename__ = 'check_in'
    id = db.Column(db.Integer, primary_key=True)
    booking_detail_id = db.Column(db.Integer, db.ForeignKey('booking_detail.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=func.now())
    boarding_pass_issued = db.Column(db.Boolean, default=False)
    checked_baggage_count = db.Column(db.Integer, default=0)
    checked_baggage_weight = db.Column(db.Float, default=0.00)

    booking_detail = db.relationship('BookingDetail')

# ---------------------------
# Student Model
# ---------------------------
class Student(db.Model, UserMixin):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    bookings = db.relationship('Booking', back_populates='student')