from flask import Flask, render_template, request
import pymysql as sql

app = Flask(__name__)
my_connection = sql.connect(
    host="localhost",
    user="pavan",
    password="Pavan@123",
    database="project3"
)
my_cursor = my_connection.cursor()
table_query = """ 
        create table if not exists events (event_id int primary key auto_increment,
        event_name varchar(45), event_type varchar(45),
        event_desc varchar(200), org_email varchar(45),
        org_num varchar(15), max_seats int);
    """
my_cursor.execute(table_query)

book_table_query = """ 
        create table if not exists bookings (booking_id int primary key auto_increment,
        event_id int, booking_date date, seats_req int, contact_email varchar(50)
        );
    """
my_cursor.execute(book_table_query)


@app.route("/", methods=["GET"])
def homepage():
    return render_template("index.html")

@app.route("/register_event", methods=["GET", "POST"])
def register_event():
    if request.method == "POST":
        event_name = request.form["event_name"]
        event_type = request.form["event_type"]
        event_desc = request.form["event_desc"]
        org_email = request.form["org_email"]
        org_num = request.form["org_num"]
        max_seats = request.form["max_seats"]

        insert_query = """ 
        insert into events (event_name, event_type, event_desc, org_email, org_num, max_seats) 
        values (%s, %s, %s, %s, %s, %s);
            """ 
        values = [event_name, event_type, event_desc, org_email, org_num, max_seats]
        my_cursor.execute(insert_query, values)
        my_connection.commit()
        return "sample"
    else:
        return render_template("register_event.html")

@app.route("/view_events", methods=["GET"])
def view_events():
    read_query = """ 
        select * from events;
    """
    my_cursor.execute(read_query)
    raw = my_cursor.fetchall()
    print(raw)
    return render_template("view_events.html", output=raw)


@app.route("/book_event", methods=["GET", "POST"])
def book_event():
    if request.method == "POST":
        event_id = int(request.form["event_id"])
        seats_req = int(request.form["seats"])
        booking_date = request.form["booking_date"]
        contact_email = request.form["contact_email"]
        
        get_event_query = """ 
            select max_seats from events where event_id = %s;
        """
        values = [event_id]
        my_cursor.execute(get_event_query, values)
        fetched = my_cursor.fetchall()

        if not fetched:
            return f"Invalid EventID {event_id}"
        else:
            check_query = """ 
                select booking_date from bookings
                 where event_id=%s and booking_date=%s;
            """
            values = [event_id, booking_date]

            my_cursor.execute(check_query, values)
            booked = my_cursor.fetchall()
            if booked:
                return f"Slot Unavailable on {booking_date}"

            max_seats = fetched[0][0]
            if seats_req > max_seats:
                return f"Cannot book more than {max_seats}"
            else:
                insert_query = """ 
                    insert into bookings (event_id, booking_date, seats_req, contact_email)
                    values (%s, %s, %s, %s);
                """
                values = [event_id,  booking_date, seats_req, contact_email]
                my_cursor.execute(insert_query, values)
                my_connection.commit()
                return "Booking Succesfull"
    else:
        return render_template("book_event.html")

@app.route("/view_bookings", methods=["GET"])
def view_bookings():
    read_query = """ 
        select booking_id, event_id, booking_date, seats_req, contact_email
           from bookings;
    """
    my_cursor.execute(read_query)
    raw = my_cursor.fetchall()
    # print(raw)
    return render_template("view_bookings.html", output=raw)

@app.route("/cancel_booking", methods=["GET", "POST"])
def cancel_booking():
    if request.method == "POST":
        booking_id = request.form["booking_id"]
        cancel_query = """ 
            delete from bookings where booking_id=%s;
        """
        values = [booking_id]
        my_cursor.execute(cancel_query, values)
        return "Booking Deleted"
    else:
        return render_template("cancel_booking.html")


# my_connection.close()

app.run(debug=True)