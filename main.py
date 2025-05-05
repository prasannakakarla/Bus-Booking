import datetime
import os
from bson import ObjectId
from flask import Flask, render_template, request, redirect, session
import pymongo
my_client = pymongo.MongoClient("mongodb://localhost:27017/")
my_database = my_client["Bus_Booking_system"]
app = Flask(__name__)
app.secret_key= 'online_shopping'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
BUS_IMAGE_PATH = APP_ROOT + "/static/bus_image"

app = Flask(__name__)

admin_collection = my_database["admin"]
Bus_Owners_collection = my_database["bus_owners"]
Locations_collection = my_database["locations"]
Bus_collection = my_database["Bus"]
customers_collection = my_database["customers"]
Schedule_collection = my_database["schedule"]
Bookings_collection = my_database["bookings"]
Payments_collection = my_database["payments"]


admin_username = "admin"
admin_password = "admin"
app.secret_key = "sample_web"

@app.route("/") #http://127.0.0.1:5000/
def index():
    return render_template("index.html")

@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")

@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == admin_username and password ==  admin_password:
        session["role"] = "admin"
        return redirect("/admin_home")
    else:
        return render_template("message.html", message="Invalid login details" )


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")

@app.route("/bus_owner_registration")
def bus_owner_registration():
    return render_template("bus_owner_registration.html")

@app.route("/bus_owner_registration_action", methods=['post'])
def bus_owner_registration_action():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    password = request.form.get("password")

    query = {"email" : email }
    count = Bus_Owners_collection.count_documents(query)

    if count > 0:
        return render_template("message.html", message="Duplicate Email Address")

    query = {"phone": phone}
    count = Bus_Owners_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate phone Number")

    query = {"name" : name, "email" : email, "phone": phone, "address" : address, "password" : password,"status":'unauthorized'}
    Bus_Owners_collection.insert_one(query)
    return render_template("message.html", message="Bus Owner Registration Successful")

@app.route("/bus_owner_login")
def bus_owner_login():
    return render_template("bus_owner_login.html")

@app.route("/bus_owner_login_action", methods=['post'])
def bus_owner_login_action():
    email = request.form.get("email")
    password = request.form.get("password")

    query = {"email":email, "password" : password}
    count=Bus_Owners_collection.count_documents(query)
    if count>0:
        bus_owner = Bus_Owners_collection.find_one(query)
        if bus_owner['status'] == 'authorized' :
            session['bus_owner_id'] = str(bus_owner['_id'])
            session['role'] = 'Bus Owner'
            return redirect("/bus_owner_home")
        else :
            return render_template("message.html", message = 'you are not authorised' )
    else:
        return render_template("message.html", message="Invalid login details")

@app.route("/bus_owner_home")
def bus_owner_home():
    return render_template("bus_owner_home.html")

@app.route("/customer_login")
def customer_login():
    return render_template("customer_login.html")

@app.route("/customer_login_action", methods=['post'])
def customer_login_action():
    email = request.form.get("email")
    password = request.form.get("password")

    query = {"email":email, "password" : password}
    count=customers_collection.count_documents(query)
    if count>0:
        customer = customers_collection.find_one(query)
        session['customer_id'] = str(customer['_id'])
        session['role'] = 'customer'
        return redirect("/customer_home")
    else:
        return render_template("message.html", message="Invalid login details")

@app.route("/customer_registration")
def customer_registration():
    return render_template("customer_registration.html")

@app.route("/customer_registration_action", methods=['post'])
def customer_registration_action():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    password = request.form.get("password")

    query = {"email" : email }
    count = customers_collection.count_documents(query)

    if count > 0:
        return render_template("message.html", message="Duplicate Email Address")

    query = {"phone": phone}
    count = customers_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate phone Number")

    query = {"name" : name, "email" : email, "phone": phone, "address" : address, "password" : password}
    customers_collection.insert_one(query)
    return render_template("message.html", message="Customer Registration Successful")


@app.route("/customer_home")
def customer_home():
    return render_template("customer_home.html")

@app.route("/view_bus_owner")
def view_bus_owner():
    query = {}
    bus_owners = Bus_Owners_collection.find(query)
    bus_owners = list(bus_owners)
    return render_template("view_bus_owner.html", bus_owners = bus_owners)

@app.route("/authorize_bus_owner")
def authorize_bus_owner():
    bus_owner_id = request.args.get('bus_owner_id')
    query = {"_id": ObjectId(bus_owner_id)}
    query2 = {"$set": {"status": "authorized"}}
    Bus_Owners_collection.update_one(query, query2)
    return redirect("/view_bus_owner")

@app.route("/unauthorize_bus_owner")
def unauthorize_bus_owner():
    bus_owner_id = request.args.get('bus_owner_id')
    query = {"_id": ObjectId(bus_owner_id)}
    query2 = {"$set": {"status": "unauthorized"}}
    Bus_Owners_collection.update_one(query, query2)
    return redirect("/view_bus_owner")

@app.route("/locations")
def locations():
    query = {}
    locations = Locations_collection.find(query)
    locations = list(locations)
    message = request.args.get('message')
    return render_template("locations.html", message=message, locations = locations)


@app.route("/add_location_action",methods=['POST'])
def add_location_action():
    location_name = request.form.get('location_name')
    query = {"location_name": location_name}
    count = Locations_collection.count_documents(query)
    if count > 0:
        return redirect("/locations?message=location name already registered")
    query = {"location_name":location_name}
    Locations_collection.insert_one(query)
    return redirect("/locations?message=location added successfully")

@app.route("/add_bus")
def add_bus():
    query = {}
    add_buses = Bus_collection.find(query)
    add_buses = list(add_buses)
    message = request.args.get('message')
    return render_template("add_bus.html", message=message, add_buses = add_buses)

@app.route("/add_bus_action",methods=['POST'])
def add_bus_action():
    bus_number = request.form.get('bus_number')
    bus_name = request.form.get('bus_name')
    bus_type = request.form.get('bus_type')
    available_seats = request.form.get('available_seats')
    bus_image = request.files.get('bus_image')
    print(session)
    bus_owner_id = session["bus_owner_id"]

    bus_image = request.files.get("bus_image")
    path = BUS_IMAGE_PATH + "/" + bus_image.filename
    bus_image.save(path)

    query = {"bus_number": bus_number}
    count = Bus_collection.count_documents(query)

    if count > 0:
        return render_template("message2.html", message="Duplicate Bus number")

    query = {"bus_number": bus_number,
             "bus_name": bus_name,
             "bus_type": bus_type,
             "available_seats": available_seats,
             "status": 'verified',
             "bus_image": bus_image.filename,
             "bus_owner_id": ObjectId(bus_owner_id)
             }
    Bus_collection.insert_one(query)
    return render_template("message2.html", message="Bus added Successfully")

@app.route("/view_buses")
def view_buses():
    bus_owners_id = request.args.get('bus_owners_id')
    if bus_owners_id == None or bus_owners_id =="":
        query = {}
        bus_owners = Bus_Owners_collection.find(query)
    else:
        query = {"_id": ObjectId(bus_owners_id)}
        bus_owners = Bus_Owners_collection.find(query)
    bus_owners = list(bus_owners)
    query = {}
    add_buses = Bus_collection.find(query)
    add_buses = list(add_buses)
    return render_template("view_buses.html", 
                         add_buses=add_buses, 
                         bus_owners=bus_owners,
                         get_bus_owner_name_by_bus_owner_id=get_bus_owner_name_by_bus_owner_id)

@app.route("/verify_bus")
def verify_bus():
    bus_id = request.args.get('bus_id')
    query = {"_id": ObjectId(bus_id)}
    query2 = {"$set": {"status": "verified"}}
    Bus_collection.update_one(query, query2)
    return redirect("/view_buses")

@app.route("/unverify_bus")
def unverify_bus():
    bus_id = request.args.get('bus_id')
    query = {"_id": ObjectId(bus_id)}
    query2 = {"$set": {"status": "unverified"}}
    Bus_collection.update_one(query, query2)
    return redirect("/view_buses")

@app.route("/buses")
def buses():
    bus_owners_id = request.args.get('bus_owners_id')
    if bus_owners_id == None or bus_owners_id == "":
        query = {}
        bus_owners = Bus_Owners_collection.find(query)
    else:
        query = {"_id": ObjectId(bus_owners_id)}
        bus_owners = Bus_Owners_collection.find(query)
    bus_owners = list(bus_owners)
    query = {}
    add_buses = Bus_collection.find(query)
    add_buses = list(add_buses)
    return render_template("buses.html",
                           add_buses=add_buses,
                           bus_owners=bus_owners,
                           get_bus_owner_name_by_bus_owner_id = get_bus_owner_name_by_bus_owner_id)


def get_bus_owner_name_by_bus_owner_id(bus_owner_id):
     query = {"_id": ObjectId(bus_owner_id)}
     bus_owner = Bus_Owners_collection.find_one(query)
     return bus_owner


def get_source_location_name_by_source_location_id(Source_location_id):
    query = {"_id": ObjectId(Source_location_id)}
    # location = Locations_collection.find.one(query)
    schedules = Locations_collection.find_one(query)
    return schedules

def get_destination_location_name_by_destination_location_id(Destination_location_id):
    query = {"_id": ObjectId(Destination_location_id)}
    # location = Locations_collection.find.one(query)
    schedules = Locations_collection.find_one(query)
    return schedules


@app.route("/schedules")   
def schedules():
    bus_id = request.args.get("bus_id")
    schedules = Schedule_collection.find({'bus_id':ObjectId(bus_id)})
    schedules = list(schedules)
    query = {}
    add_buses = Bus_collection.find(query)
    add_buses = list(add_buses)
    locations = Locations_collection.find()
    locations2 = Locations_collection.find()
    return render_template("schedules.html",get_remain_seats2=get_remain_seats2,get_destination_location_name_by_destination_location_id = get_destination_location_name_by_destination_location_id, get_bus_by_bus_id=get_bus_by_bus_id,locations2=locations2, get_bus_owner_name_by_bus_owner_id = get_bus_owner_name_by_bus_owner_id, add_buses = add_buses, get_source_location_name_by_source_location_id=get_source_location_name_by_source_location_id, locations = locations, bus_id = bus_id, str = str, buses = buses, schedules=schedules)

def get_remain_seats2(schedule_id,departureDate,available_seats):
    departureDate= datetime.datetime.strptime(departureDate,"%Y-%m-%d")
    bookings = Bookings_collection.find({"departureDate":departureDate,"schedule_id":ObjectId(schedule_id),"status":'Booked'})
    booked_seats = 0
    for booking in bookings:
        booked_seats = booked_seats+len(booking['seat_numbers'])

    remain_seats = int(available_seats)-int(booked_seats)
    return remain_seats

def get_bus_by_bus_id(bus_id):
    bus = Bus_collection.find_one({"_id":ObjectId(bus_id)})
    return bus

@app.route("/add_schedule_action", methods=['post'])
def add_schedule_action():
    bus_id = request.form.get("bus_id")
    Source_location_id = request.form.get("Source_location_id")
    Departure_date_time = request.form.get("Departure_date_time")
    Destination_location_id = request.form.get("Destination_location_id")
    Arrival_date_time = request.form.get("Arrival_date_time")
    Departure_platform_number = request.form.get("Departure_platform_number")
    Arrival_platform_number = request.form.get("Arrival_platform_number")
    Price_per_seat = request.form.get("Price_per_seat")
    departure = datetime.datetime.strptime(Departure_date_time,"%Y-%m-%dT%H:%M")
    departure = departure.strftime('%Y-%m-%d')
    query = {"Source_location_id": ObjectId(Source_location_id), "Departure_date_time": Departure_date_time, "Destination_location_id": ObjectId(Destination_location_id),"Arrival_date_time": Arrival_date_time, "Departure_platform_number": Departure_platform_number, "Arrival_platform_number": Arrival_platform_number, "Price_per_seat": Price_per_seat,"bus_id":ObjectId(bus_id),"departure":departure}
    Schedule_collection.insert_one(query)
    return render_template("message.html", message="Schedule added Successfully")


@app.route("/search_view_buses")
def search_view_buses():
    source_location = request.args.get("source_location")
    destination_location = request.args.get("destination_location")
    departureDate= request.args.get("departureDate")
    print(departureDate)
    query = {}
    if source_location == None:
        source_location = ""
    if destination_location == None:
        destination_location = ""
    if departureDate == None:
        departureDate = ""
    if source_location == "" and destination_location == "" and departureDate == "" :
        query = {"departure" : datetime.datetime.today()}
    else:
        query = {"departure" : departureDate, "Source_location_id" : ObjectId(source_location), "Destination_location_id" : ObjectId(destination_location)}
    schedules = Schedule_collection.find(query)
    locations = Locations_collection.find()
    locations2 = Locations_collection.find()
    return render_template("search_view_buses.html",get_date_format=get_date_format,get_remain_seats=get_remain_seats,departureDate=departureDate,source_location=source_location,destination_location=destination_location,locations=locations, locations2=locations2, str=str, schedules = schedules, get_bus_by_bus_id = get_bus_by_bus_id,get_bus_owner_name_by_bus_owner_id=get_bus_owner_name_by_bus_owner_id,get_source_location_name_by_source_location_id=get_source_location_name_by_source_location_id,get_destination_location_name_by_destination_location_id=get_destination_location_name_by_destination_location_id)

def get_date_format(from_date):
    from_date = datetime.datetime.strptime(from_date,"%Y-%m-%dT%H:%M")
    return from_date

@app.route('/search')
def search():
    query = request.args.get('query')
    return render_template('search_results.html', query=query)

@app.route("/book_bus")
def book_bus():
    source_location = request.args.get("source_location")
    destination_location = request.args.get("destination_location")
    price = request.args.get("price")
    available_seats = request.args.get("available_seats")
    schedule_id = request.args.get("schedule_id")
    schedule = Schedule_collection.find_one({"_id":ObjectId(schedule_id)})
    departureDate = request.args.get("departureDate")
    departureDate2 = datetime.datetime.strptime(departureDate,"%Y-%m-%d")
    return render_template("book_bus.html",get_remain_seats=get_remain_seats,get_is_seat_booked=get_is_seat_booked,departureDate=departureDate,int=int, get_bus_by_bus_id=get_bus_by_bus_id, get_destination_location_name_by_destination_location_id=get_destination_location_name_by_destination_location_id, get_source_location_name_by_source_location_id = get_source_location_name_by_source_location_id, available_seats = available_seats, schedule_id = schedule_id,  schedule = schedule , source_location=source_location,destination_location=destination_location, price = price,departureDate2=departureDate2)

def get_is_seat_booked(departureDate,seat,schedule_id):
    departureDate= datetime.datetime.strptime(departureDate,"%Y-%m-%d")
    count = Bookings_collection.count_documents({"departureDate":departureDate,"schedule_id":ObjectId(schedule_id),"status":'Booked'})
    if count>0:
        bookings = Bookings_collection.find({"departureDate":departureDate,"schedule_id":ObjectId(schedule_id),"status":'Booked'})
        for booking in bookings:
            seat_numbers = booking['seat_numbers']
            for seat_number in seat_numbers:
                print(seat_number['seat_number'])
                if int(seat_number['seat_number'])== int(seat):
                    return True
    return False

def get_remain_seats(schedule_id,departureDate,available_seats):
    departureDate= datetime.datetime.strptime(departureDate,"%Y-%m-%d")
    bookings = Bookings_collection.find({"departureDate":departureDate,"schedule_id":ObjectId(schedule_id),"status":'Booked'})
    booked_seats = 0
    for booking in bookings:
        booked_seats = booked_seats+len(booking['seat_numbers'])

    remain_seats = int(available_seats)-int(booked_seats)
    return remain_seats

@app.route("/book_bus_action", methods=['post'])
def book_bus_action():
    schedule_id = request.form.get("schedule_id")
    total_price = request.form.get("total_price")
    departure_date = request.form.get("departureDate")
    customer_id = request.form.get("customers_id")
    schedule = Schedule_collection.find_one({'_id': ObjectId(schedule_id)})
    bus  = Bus_collection.find_one({"_id":ObjectId(schedule['bus_id'])})
    number_of_seats = request.form.get("number_of_seats")
    total_price = float(number_of_seats)*float(schedule['Price_per_seat'])
    seat_numbers = []
    departureDate = datetime.datetime.strptime(departure_date, "%Y-%m-%d")
    query = {"date": datetime.datetime.now(), "status": "Payment Pending", "schedule_id": ObjectId(schedule_id),
             "customer_id": ObjectId(session['customer_id']), "departureDate": departureDate,"total_price":total_price}
    booking = Bookings_collection.insert_one(query)
    booking_id = booking.inserted_id
    for i in range(1, int(bus['available_seats']) + 1):
        seat_number = request.form.get("seat" + str(i))
        if seat_number!=None:
            seat_numbers.append(str(i))
            name = request.form.get("name" + str(i))
            phone = request.form.get("phone" + str(i))
            age = request.form.get("age" + str(i))
            seat_number2 = {
                "name" : name,
                "phone" : phone,
                "age" : age,
                "seat_number" : str(i)
            }
            query2 = {"$push":{"seat_numbers":seat_number2}}
            Bookings_collection.update_one({"_id":ObjectId(booking_id)},query2)
    number_of_seats = list(number_of_seats)
    query = {"_id":ObjectId(schedule_id)}
    schedule1 = Schedule_collection.find_one(query)
    booking = Bookings_collection.find_one({"_id":ObjectId(booking_id)})
    return render_template("payment.html", str = str,booking=booking, schedule_id=schedule_id, seat_numbers=seat_numbers,number_of_seats=number_of_seats, departure_date=departure_date, total_price=total_price, schedule1= schedule1 )

@app.route("/payment")
def payment():
    return render_template("payment.html")

@app.route("/payment_action",  methods=['post'])
def payment_action():
    booking_id = request.form.get("booking_id")
    total_price = request.form.get("total_price")
    cvv = request.form.get("cvv")
    card_name = request.form.get("card_name")
    card_type = request.form.get("card_type")
    card_number = request.form.get("card_number")
    expiry_date = request.form.get("expiry_date")
    schedule_id = request.form.get("schedule_id")
    query = {"date": datetime.datetime.now(), "status": "Payment Completed", "total_price" : total_price, "cvv" : cvv, "card_name" : card_name, "card_type" : card_type, "card_number" : card_number, "expiry_date" : expiry_date, "booking_id" : ObjectId(booking_id) }
    payments = Payments_collection.insert_one(query)
    query = {"$set" : {"status" : 'Booked'}}
    Bookings_collection.update_one({"_id":ObjectId(booking_id)}, query)
    return render_template("message3.html", message = "Tickets Booked Successfully")

@app.route("/view_bookings")
def view_bookings():
    query = {}
    if session['role'] == 'customer':
        query = {"customer_id": ObjectId(session['customer_id'])}
    elif session['role'] == 'Bus Owner':
        schedule_id = request.args.get("schedule_id")
        if schedule_id is None:
            query = {"bus_owner_id": ObjectId(session['bus_owner_id'])}
            buses = Bus_collection.find(query)
            bus_ids = [{"bus_id": ObjectId(bus['_id'])} for bus in buses]
            schedules = Schedule_collection.find({"$or": bus_ids})
            schedule_ids = [{"schedule_id": ObjectId(schedule['_id'])} for schedule in schedules]
            query = {"$or": schedule_ids}
        else:
            query = {"schedule_id": ObjectId(schedule_id)}
    elif session['role'] == 'admin':
        query = {}

    bookings = list(Bookings_collection.find(query))


    for booking in bookings:
        departure_date = booking['departureDate']
        if isinstance(departure_date, str):
            departure_date = datetime.datetime.strptime(departure_date, "%Y-%m-%d %H:%M:%S")
        booking['is_past'] = datetime.datetime.now() >= departure_date

    return render_template(
        "view_bookings.html",
        get_discount_applied=get_discount_applied,
        get_source_location_name_by_source_location_id=get_source_location_name_by_source_location_id,
        get_destination_location_name_by_destination_location_id=get_destination_location_name_by_destination_location_id,
        bookings=bookings,
        get_customer_by_customer_id=get_customer_by_customer_id,
        get_bus_by_bus_id=get_bus_by_bus_id,
        get_schedule_by_schedule_id=get_schedule_by_schedule_id
    )

def get_discount_applied(booking_id):
    booking = Bookings_collection.find_one({"_id":ObjectId(booking_id)})
    departureDate = booking['departureDate']
    cur_date = datetime.date.today()
    cur_date = datetime.datetime.strptime(str(cur_date),"%Y-%m-%d")
    departureDate = datetime.datetime.strptime(str(departureDate), "%Y-%m-%d %H:%M:%S")
    diif_days = departureDate-cur_date
    print(cur_date)
    days  = diif_days.days
    print(days)
    if cur_date >= departureDate:
        return 0.0
    original_price = booking['total_price']
    hours_until_departure = diif_days.total_seconds() / 3600

    # Apply discount logic
    if hours_until_departure > 24:
        discounted_price = original_price * 0.85  # 15% off
    elif hours_until_departure < 4:
        discounted_price = original_price * 0.50  # 50% off
    else:
        discounted_price = original_price  # No discount

    return discounted_price

def get_schedule_by_schedule_id(schedule_id):
    schedule = Schedule_collection.find_one({"_id":ObjectId(schedule_id)})
    return schedule

def get_customer_by_customer_id(customer_id):
    customer = customers_collection.find_one({"_id":ObjectId(customer_id)})
    return customer

def get_booking_by_booking_id(booking_id):
    booking = Bookings_collection.find_one({"_id":ObjectId(booking_id)})
    print(booking)
    return booking

def get_payment_by_payment_id(booking_id):
    payment = Payments_collection.find_one({"_id":ObjectId(booking_id)})
    return payment


@app.route("/cancel_booking")
def cancel_booking():
    booking_id = request.args.get("booking_id")
    discount = request.args.get("discount")
    query = {"$set":{"status": "Cancelled","refund_amount":discount}}
    bookings = Bookings_collection.update_one({"_id":ObjectId(booking_id)},query)
    return render_template ("message3.html", message = "Booking cancelled")

@app.route("/view_payments")
def view_payments():
    booking_id = request.args.get("booking_id")
    query = {"booking_id":ObjectId(booking_id)}
    payment = Payments_collection.find(query)
    payments = list(payment)
    return render_template("view_payments.html", str = str, payments = payments, get_booking_by_booking_id = get_booking_by_booking_id,  get_customer_by_customer_id=get_customer_by_customer_id )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



app.run(debug=True)

