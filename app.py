from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from models import db, User, LoginAttempt, SecurityZone
from risk_engine import (
    detect_vpn_like,
    network_risk,
    location_risk,
    coordinate_risk,
    device_risk,
    device_type_risk,
    calculate_total_risk,
    safe_zone_risk,
    risk_level,
)

app = Flask(__name__)
app.secret_key = "change-me-please"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# -----------------------------------------
# INITIALIZE + SEED USERS
# -----------------------------------------
def seed_users():
    if User.query.count() == 0:
        users = [
            User(username="salman", password="1234"),
            User(username="turki", password="abcd"),
            User(username="ahmad", password="pass"),
        ]
        db.session.add_all(users)
        db.session.commit()


@app.before_request
def setup():
    if not hasattr(app, "initialized"):
        db.create_all()
        seed_users()
        app.initialized = True


# -----------------------------------------
# LOGIN (NO OTP)
# -----------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return render_template("login.html", error="بيانات الدخول غير صحيحة")

        # ---- Fingerprint ----
        real_ip = request.form.get("real_ip")
        real_city = request.form.get("real_city")
        real_country = request.form.get("real_country")

        latitude = request.form.get("lat")
        longitude = request.form.get("lon")

        device_name = request.form.get("device_name")
        device_type = request.form.get("device_type")
        device_os = request.form.get("device_os")
        device_browser = request.form.get("device_browser")
        device_raw = request.form.get("device_raw")

        cpu = request.form.get("cpu_count")
        ram = request.form.get("ram_gb")
        screen = request.form.get("screen_res")
        pixel_ratio = request.form.get("pixel_ratio")
        color_depth = request.form.get("color_depth")

        timezone = request.form.get("timezone")
        language = request.form.get("language")

        gpu_vendor = request.form.get("gpu_vendor")
        gpu_model = request.form.get("gpu_model")
        canvas_fp = request.form.get("canvas_fp")

        # ---- Risk Engine ----
        is_vpn = detect_vpn_like(real_ip)
        network_type = "VPN" if is_vpn else "Normal"
        net_score = network_risk(is_vpn)

        first_login = (user.trusted_ip is None)

        if first_login:
            user.trusted_ip = real_ip
            user.trusted_city = real_city
            user.trusted_country = real_country
            user.trusted_lat = latitude
            user.trusted_lon = longitude
            user.trusted_device = device_raw
            user.trusted_device_type = device_type
            user.trusted_network = network_type
            db.session.commit()
            total_risk = 10
        else:
            loc_score = location_risk(real_city, real_country,
                                      user.trusted_city, user.trusted_country)

            coord_score = coordinate_risk(latitude, longitude,
                                          user.trusted_lat, user.trusted_lon)

            dev_score = device_risk(device_raw, user.trusted_device)
            dev_type_score = device_type_risk(device_type, user.trusted_device_type)

            zones = SecurityZone.query.filter_by(user_id=user.id).all()
            zone_data = [{"lat": z.latitude, "lon": z.longitude, "radius": z.radius} for z in zones]
            zone_score = safe_zone_risk(float(latitude), float(longitude), zone_data)

            total_risk = calculate_total_risk(
                net_score, dev_score, dev_type_score,
                loc_score, coord_score, zone_score
            )

        level = risk_level(total_risk)

        # ---- Save attempt ----
        attempt = LoginAttempt(
            user_id=user.id,
            ip=real_ip,
            city=real_city,
            country=real_country,
            latitude=latitude,
            longitude=longitude,
            device_name=device_name,
            device_type=device_type,
            device=device_raw,
            browser=device_browser,
            os=device_os,
            cpu=cpu,
            ram=ram,
            screen=screen,
            pixel_ratio=pixel_ratio,
            color_depth=color_depth,
            gpu_vendor=gpu_vendor,
            gpu_model=gpu_model,
            canvas_fp=canvas_fp,
            timezone=timezone,
            language=language,
            network_type=network_type,
            risk_score=total_risk,
            risk_level=level,
            timestamp=str(datetime.now())
        )
        db.session.add(attempt)
        db.session.commit()

        session["user_id"] = user.id
        session["last_attempt_id"] = attempt.id

        return redirect(url_for("dashboard"))

    return render_template("login.html")


# -----------------------------------------
# DASHBOARD
# -----------------------------------------
@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    last_attempt_id = session.get("last_attempt_id")

    if last_attempt_id:
        last_attempt = LoginAttempt.query.get(last_attempt_id)
    else:
        last_attempt = LoginAttempt.query.filter_by(user_id=user_id) \
                                         .order_by(LoginAttempt.id.desc()).first()

    zones = SecurityZone.query.filter_by(user_id=user_id).all()

    return render_template("dashboard.html", attempt=last_attempt, zones=zones)


# -----------------------------------------
# ADD SECURITY ZONE  (FIXED!!)
# -----------------------------------------
@app.route("/add_zone", methods=["POST"])
def add_zone():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not_logged_in"}), 403

    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "missing_name"})

    count = SecurityZone.query.filter_by(user_id=user_id).count()
    if count >= 3:
        return jsonify({"status": "limit_reached"})

    last = LoginAttempt.query.filter_by(user_id=user_id).order_by(LoginAttempt.id.desc()).first()

    # -------- FIXED HERE --------
    lat_val = float(last.latitude) if last and last.latitude else 0.0
    lon_val = float(last.longitude) if last and last.longitude else 0.0
    # -----------------------------

    zone = SecurityZone(
        user_id=user_id,
        name=name,
        latitude=lat_val,
        longitude=lon_val,
        radius=200
    )

    db.session.add(zone)
    db.session.commit()

    return jsonify({"status": "ok", "id": zone.id})


# -----------------------------------------
# DELETE ZONE
# -----------------------------------------
@app.route("/delete_zone/<int:zone_id>", methods=["POST"])
def delete_zone(zone_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "not_logged_in"})

    zone = SecurityZone.query.get(zone_id)

    if not zone or zone.user_id != user_id:
        return jsonify({"error": "not_found"})

    db.session.delete(zone)
    db.session.commit()

    return jsonify({"status": "deleted"})


# -----------------------------------------
# LOGOUT
# -----------------------------------------
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# -----------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
