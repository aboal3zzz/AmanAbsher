import math

# ---------------------------
# VPN detection (placeholder)
# ---------------------------
def detect_vpn_like(ip):
    # هنا ممكن تضيف منطق للكشف عن VPN مستقبلاً
    return False


def network_risk(is_vpn):
    # لو VPN نخلي المخاطر أعلى
    return 60 if is_vpn else 10


# ---------------------------
# Device fingerprint checks
# ---------------------------
def device_risk(current_device, trusted_device):
    """
    يقارن البصمة الكاملة للجهاز الحالي مع أول جهاز موثوق
    """
    if not trusted_device:
        return 0
    return 25 if current_device != trusted_device else 0


def device_type_risk(current, trusted):
    """
    يقارن نوع الجهاز (موبايل / ديسكتوب) مع النوع الموثوق
    """
    if not trusted:
        return 0
    return 10 if current != trusted else 0


# ---------------------------
# City / Country checks
# ---------------------------
def location_risk(city, country, t_city, t_country):
    """
    يقارن المدينة والدولة الحالية مع المدينة والدولة الموثوقة
    """
    if not t_city or not t_country:
        return 0

    risk = 0
    if country and country != t_country:
        risk += 25
    if city and city != t_city:
        risk += 15
    return risk


# ---------------------------
# Distance calculation
# ---------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    يحسب المسافة بالكيلومتر بين نقطتين باستخدام Haversine
    """
    try:
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    except Exception:
        return 0.0

    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # km


# ---------------------------
# Coordinate-based risk
# ---------------------------
def coordinate_risk(lat, lon, t_lat, t_lon):
    """
    يستخدم المسافة بين الإحداثيات الحالية والموثوقة
    لزيادة المخاطر لو ابتعدنا كثير
    """
    if not t_lat or not t_lon:
        return 0

    distance = calculate_distance(lat, lon, t_lat, t_lon)

    if distance < 10:
        return 0
    elif distance < 50:
        return 10
    elif distance < 200:
        return 20
    else:
        return 40


# ---------------------------
# SAFE ZONE system
# ---------------------------
def safe_zone_risk(lat, lon, zones):
    """
    zones: list of dicts
    [{"lat": ..., "lon": ..., "radius": ...}, ...]

    يرجع درجة مخاطرة منخفضة لو المستخدم داخل أي منطقة أمان
    أو قريب منها، وإلا يرجّع None عشان نستخدم القواعد العادية
    """
    if not zones:
        return None

    for z in zones:
        distance_km = calculate_distance(lat, lon, z["lat"], z["lon"])
        radius_km = (z.get("radius") or 200) / 1000.0  # radius بالمتر -> كم

        # جوّا المنطقة بالضبط
        if distance_km <= radius_km:
            return 0

        # قريب جداً من حدود المنطقة
        if distance_km <= radius_km + 0.3:
            return 5

        # قريب نوعاً ما
        if distance_km <= radius_km + 1.0:
            return 10

    # ما في أي زون قريبة
    return None


# ---------------------------
# TOTAL RISK
# ---------------------------
def calculate_total_risk(net, device, dtype, l_score, coord, zone_score):
    """
    لو zone_score مو None → نستخدمه ونتجاهل location + coordinate
    """
    if zone_score is not None:
        return net + device + dtype + zone_score

    return net + device + dtype + l_score + coord


# ---------------------------
# RISK LEVEL
# ---------------------------
def risk_level(score):
    if score <= 20:
        return "Low"
    if score <= 50:
        return "Medium"
    if score <= 75:
        return "High"
    return "Critical"
