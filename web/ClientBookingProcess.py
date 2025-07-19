from flask import Blueprint, render_template,request, flash, url_for, redirect,session
from .models import FlightSchedule, Airport
from datetime import datetime, timedelta



ClientBookingProcess = Blueprint('ClientBookingProcess', __name__)


# Home
@ClientBookingProcess.route('/home',methods=['POST', 'GET'])
def home():
    countryAndCity = Airport.query.all()
    
    if request.method == 'POST':
        tripType = request.form.get('tripType')

        departure = request.form.get('departure')
        destination = request.form.get('destination')
        departOn = request.form.get('departOn')
        returnOn = request.form.get('returnOn')

        valid_location = [f"{a.country}, {a.city}" for a in countryAndCity]

        if departure not in valid_location or destination not in valid_location:
            flash(f"Invalid departure or destination. You entered: {departure}, {destination}", "error")  
            return redirect(url_for('ClientBookingProcess.home')) 
        else:
            # ✅ Store form data in session
            session['search_data'] = {
                'tripType': tripType,
                'departure': departure,
                'destination': destination,
                'departOn': departOn,
                'returnOn': returnOn
            }

            return redirect(url_for('ClientBookingProcess.search'))

    return render_template('ClientBookingProcess/home.html',countryAndCity=countryAndCity)
# Home



# search
@ClientBookingProcess.route('/search', methods=['POST', 'GET'])
def search():
    countryAndCity = Airport.query.all()
    search_data = session.get('search_data', {})
    if request.method == 'POST':
        # Get new input
        new_data = {
            'tripType': request.form.get('tripType'),
            'departure': request.form.get('departure'),
            'destination': request.form.get('destination'),
            'departOn': request.form.get('departOn'),
            'returnOn': request.form.get('returnOn'),
            'adult': request.form.get('adult'),
            'children': request.form.get('children'),
            'infant': request.form.get('infant')
        }

        # Check validity
        valid_location = [f"{a.country}, {a.city}" for a in countryAndCity]
        if new_data['departure'] not in valid_location or new_data['destination'] not in valid_location:
            flash(f"Invalid departure or destination. You entered: {new_data['departure']}, {new_data['destination']}", "error")
            return redirect(url_for('ClientBookingProcess.home'))

        # Compare with current session and update if needed
        search_data = session.get('search_data', {})
        updated = False
        for key, new_value in new_data.items():
            if search_data.get(key) != new_value:
                search_data[key] = new_value
                updated = True

        if updated:
            session['search_data'] = search_data

        return redirect(url_for('ClientBookingProcess.select'))

    return render_template('ClientBookingProcess/search.html', countryAndCity=countryAndCity, data=search_data)

# search

# select a Flight
@ClientBookingProcess.route('/select')
def select():
    search_data = session.get('search_data', {})
    

    return render_template('ClientBookingProcess/select_flight.html',data= search_data)
# select a flight





@ClientBookingProcess.route('/test')
def test():
    return render_template('ClientBookingProcess/test.html')

 
@ClientBookingProcess.route('/view_selected_flight')
def ClientBookingProcesselectedFlight():
    return render_template('ClientBookingProcess/view_selected_flight.html')

@ClientBookingProcess.route('/information')
def passenger_information():
    return render_template('ClientBookingProcess/passenger_information.html')

@ClientBookingProcess.route('/seats')
def select_seats():
    seats = [
        {'status': 'unavailable'},
        {'status': 'number', 'value': 200},
        {'status': 'free'},
        {'status': 'reserved'},
        {'status': 'free'}
    ]
    return render_template('ClientBookingProcess/select_seat.html',seats=seats)

@ClientBookingProcess.route('/summary')
def summary():
    return render_template('ClientBookingProcess/booking_summary.html')


@ClientBookingProcess.route('/payment')
def payment():
    return render_template('ClientBookingProcess/payment.html')






def getDate():
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    total_dates = 7
    dates = []

    for i in range(-1, total_dates - 1):
        date = today + timedelta(days=i)
        is_past = date < today
        is_today = date == today
        formatted = date.strftime("%d %b %Y")  # Example: 17 Jul 2025

        dates.append({
            "label": formatted,
            "price": "1,123.00",
            "is_today": is_today,
            "is_past": is_past,
        })

    return dates