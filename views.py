from flask import render_template, request, url_for, redirect
from controls import get_dates, receive_data, Carbon, get_reviews
from constants import CURRENCY_NAMES
from models import Review, db, Users

# emission calculate
fly_green = Carbon()


def init(application):
    @application.before_request
    def before_request():
        proto = request.headers.get('X-Forwarded-Proto')
        if proto == 'http' or request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            code = 301
            return redirect(url, code=code)

    @application.route('/')
    @application.route('/home')
    def home():
        """index page"""
        # generate dates for search
        departure_date, return_date = get_dates()
        template_data = {
            'data_departure': departure_date,
            'data_return': return_date,
        }
        reviews = get_reviews()

        return render_template('index.html',reviews=reviews,  **template_data)


    @application.route('/currency', methods=['GET', 'POST'])
    def currency():
        """currency convector page"""
        if request.method == 'POST':

            amount = float(request.form['amount'])
            from_currency = request.form['from_currency'][:3]
            to_currency = request.form['to_currency'][:3]

            # get data request
            currency_data = receive_data()
            if currency_data != False:
                # get current data rates
                data = currency_data.get("date")
                conversion_rate = currency_data.get("rates")[to_currency] / \
                                  currency_data.get("rates")[from_currency]

                converted_amount = round(amount * conversion_rate, 2)  # round
                # return template rates
                return render_template('currency.html', data=f'Rates from Data: {data}', amount=amount,
                                       from_currency=from_currency + " =",
                                       converted_amount=converted_amount, to_currency=to_currency,
                                       currencies=CURRENCY_NAMES)

            else:
                return render_template('currency.html', data="Oops:( Something Wrong", currencies=CURRENCY_NAMES)
        else:
            return render_template('currency.html', currencies=CURRENCY_NAMES)


    @application.route('/carbon', methods=['GET', 'POST'])
    def carbon():
        """emission calculate"""
        if request.method == 'POST':
            # get from page
            from_city = request.form['input1']
            to_city = request.form['input2']
            passengers_n = request.form['input3']
            round_trip = request.form.get('checkbox')

            # output roundtrip
            trip = ""
            if round_trip: trip = "(Round Trip)"
            try:
                # get result from carbon api
                result = fly_green.carbon_request(from_city, to_city, round_trip, int(passengers_n))
                distance = result['data']['attributes']['distance_value']
                carbon_kg = result['data']['attributes']['carbon_kg']
            except:
                return render_template('carbon.html', error="Oops:( Something Wrong")

            else:
                return render_template('carbon.html', from_city=f' From : {from_city}', to_city=f'To: {to_city}{trip}',

                                       distance=f'Distance:{distance} km',
                                       carbon_kg=f'Calculated emissions: {carbon_kg} kg')
        else:
            return render_template('carbon.html')


    @application.route('/contact')
    def contact():
        """Contact Us page"""
        return render_template('contact.html')


    @application.route('/about')
    def about():
        """About page"""
        return render_template('about.html')

    @application.route('/add_review', methods=['POST'])
    def add_review():
        # Extract data from form
        name = request.form.get('name')
        title = request.form.get('title')
        stars = request.form.get('stars')
        text = request.form.get('text')

        # Create new Review object
        new_review = Review(title=title, stars=int(stars), name=name, text=text)

        # Add new Review to the session
        db.session.add(new_review)

        # Commit the session to save the changes
        db.session.commit()

        # Redirect to the reviews page
        return redirect('/')


    @application.route('/airlines')
    def airlines():
        """Airlines page"""
        return render_template('airlines.html')

    @application.route('/admin_login')
    def login():
        """login page"""
        return render_template('login.html')



    @application.route('/submit-login', methods= (['POST']))
    def login_check():
        if request.method == "POST":
            email = request.form['email']
            password = request.form['password']

            # check user in database
            user = Users.query.filter_by(email=email).first()
            if  user and user.password == password:
                return redirect('/myadminlink')

            else:
                return render_template('login.html', result_login = "Incorrect Email or Password")

