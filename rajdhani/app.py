import sqlite3

from flask import Flask, abort, jsonify, redirect, render_template, request
from urllib.parse import urlparse
from . import config
from . import db
from . import db_ops
from . import auth


app = Flask(__name__)

app.secret_key = config.secret_key


@app.route("/")
def index():
    from_station_code = request.args.get("from_station_code")
    to_station_code = request.args.get("to_station_code")
    ticket_class = request.args.get("class")

    if from_station_code and to_station_code:
        trains = db.search_trains(
            from_station_code=from_station_code,
            to_station_code=to_station_code,
            ticket_class=ticket_class)
    else:
        trains = None
    return render_template("index.html", config=config, trains=trains, args=request.args)

@app.route("/api/flags")
def api_flags():
    flags = {k: v for k, v in config.__dict__.items() if k.startswith("flag_")}
    return jsonify(flags)

@app.route("/api/stations")
def api_stations():
    q = request.args.get("q")
    stations = db.search_stations(q)
    return jsonify(stations)

@app.route("/api/search")
def api_search():
    from_station = request.args.get("from")
    to_station = request.args.get("to")
    ticket_class = request.args.get("class")
    date = request.args.get("date")

    trains = db.search_trains(from_station, to_station, ticket_class, date)
    return jsonify(trains)

@app.route("/search")
def search():
    from_station = request.args.get("from")
    to_station = request.args.get("to")
    ticket_class = request.args.get("class")
    date = request.args.get("date")

    trains = db.search_trains(from_station, to_station, ticket_class, date)
    return render_template("search.html",
        trains=trains,
        from_station=from_station,
        to_station=to_station,
        ticket_class=ticket_class,
        date=date)

@app.route("/db/reset")
def reset_db():
    db_ops.reset_db()
    return "ok"

@app.route("/db/exec")
def exec_db():
    q = request.args.get("q")
    columns, rows = db_ops.exec_query(q)
    return {
        "columns": columns,
        "rows": rows
    }

@app.route("/data-explorer")
def explore_data():
    q = request.args.get("q")

    error, columns, rows = None, None, None
    if q:
        try:
            columns, rows = db_ops.exec_query(q)
        except (sqlite3.Error, sqlite3.Warning) as e:
            error = str(e)

    return render_template(
        "data_explorer.html",
        error=error, columns=columns, rows=rows, query=q,
    )

@app.route("/progress")
def progress():
    url = urlparse(request.base_url)
    username = url.hostname.split(".", maxsplit=1)[0]
    redirect_url = f"{config.base_status_page_url}/{username}"

    return redirect(redirect_url, code=302)

@app.route("/hello")
def hello():
    """Simple endpoint to check the authenticated user is
    """
    if (email := auth.get_logged_in_user_email()):
        return f"Hello, {email}!"
    else:
        abort(403)

@app.route("/login")
def login():
    if email := request.args.get("email"):
        auth.login(email)
        return redirect("/hello")

    return render_template("login.html")

@app.route("/logout")
def logout():
    auth.logout()
    return redirect("/")
