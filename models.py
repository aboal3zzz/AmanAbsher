from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

    trusted_ip = db.Column(db.String(50))
    trusted_city = db.Column(db.String(50))
    trusted_country = db.Column(db.String(50))
    trusted_lat = db.Column(db.String(50))
    trusted_lon = db.Column(db.String(50))

    trusted_device = db.Column(db.String(500))
    trusted_device_type = db.Column(db.String(50))
    trusted_network = db.Column(db.String(50))


class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)

    ip = db.Column(db.String(50))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))

    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))

    device_name = db.Column(db.String(200))
    device_type = db.Column(db.String(50))
    device = db.Column(db.String(500))
    browser = db.Column(db.String(300))
    os = db.Column(db.String(200))

    cpu = db.Column(db.String(50))
    ram = db.Column(db.String(50))

    screen = db.Column(db.String(50))
    pixel_ratio = db.Column(db.String(50))
    color_depth = db.Column(db.String(50))

    gpu_vendor = db.Column(db.String(200))
    gpu_model = db.Column(db.String(200))
    canvas_fp = db.Column(db.String(500))

    timezone = db.Column(db.String(100))
    language = db.Column(db.String(50))

    network_type = db.Column(db.String(50))
    risk_score = db.Column(db.Float)
    risk_level = db.Column(db.String(20))
    timestamp = db.Column(db.String(50))


class SecurityZone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    radius = db.Column(db.Float, default=200)
