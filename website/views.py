from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Favorite
from . import db
import json, requests
import datetime

views = Blueprint('views', __name__)

with open('config.json', 'r') as f:
    config = json.load(f)


api_key_geo = config['api_key_geo']
api_key_weather = config['api_key_weather']
api_key_tank = config['api_key_tank']


@views.route('/')
def home():
    return render_template("home/home.html", user=current_user)

@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes_view():
    if request.method == 'POST':
        note = request.form.get('note')
        
        if len(note) < 1:
            flash('Notiz ist zu kurz!', category = 'error')
        else: 
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.strptime(now_str, "%Y-%m-%d %H:%M:%S")
            
            new_note = Note(data=note, date=now, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Notiz erfolgreich hinzugefügt!', category='success')
            return redirect(url_for('views.notes_view'))
    
    return render_template("home/notes.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash('Notiz erfolgreich gelöscht!', category='success')
    
    return jsonify({})

@views.route('/delete-favorite', methods=['POST'])
@login_required
def delete_favorite():
    data = request.get_json()
    fav_city = data["fav_city"]

    favorite = Favorite.query.filter_by(fav_city=fav_city, user_id=current_user.id).first()

    db.session.delete(favorite)
    db.session.commit()
    flash('Stadt wurde erfolgreich aus den Favoriten entfernt!', category='success')
    
    return jsonify({})


@views.route("/weather_submit")
@login_required
def weather_submit():
    return render_template("home/weather_submit.html", user=current_user)

@views.route('/add-to-favorites', methods=['POST'])
def add_to_favorites():
    if request.method == 'POST':
        city = request.json['city']
        existing_fav = Favorite.query.filter_by(user_id=current_user.id, fav_city=city).first()

        if existing_fav:
            return '', 409

        else:
            new_fav = Favorite(fav_city=city, user_id=current_user.id)
            db.session.add(new_fav)
            db.session.commit()

            return '', 200

@views.route('/favorite')
def favorites():
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    city_names = [fav.fav_city for fav in favorites]

    temperatures = []
    weather_data = {}

    for fav in city_names:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={fav}&limit=1&appid={api_key_geo}"
        response_geo = requests.get(geo_url)
        geo_data = response_geo.json()

        latitude = geo_data[0]["lat"]
        longitude = geo_data[0]["lon"]

        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key_weather}&lang=de&units=metric"
        response = requests.get(weather_url)
        weather_data = response.json()

        weather_desc = weather_data["weather"][0]["description"]
        temperature = round(weather_data["main"]["temp"])
        temperature_min = round(weather_data["main"]["temp_min"])
        temperature_max = round(weather_data["main"]["temp_max"])
        temp_feels = round(weather_data["main"]["feels_like"])
        humidity = weather_data["main"]["humidity"]
        cloudiness = weather_data["clouds"]["all"]
        weather_icon = weather_data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{weather_icon}@2x.png"
        temperatures.append([fav, temperature, temperature_min, temperature_max, temp_feels, cloudiness, humidity, weather_desc, icon_url])

    temperatures_sorted = sorted(temperatures, key=lambda x: x[1], reverse=True)
    temperatures_dict = {fav: (temperature, temperature_min, temperature_max, temp_feels, cloudiness, humidity, weather_desc, icon_url) for fav, temperature, temperature_min, temperature_max, temp_feels, cloudiness, humidity, weather_desc, icon_url in temperatures_sorted}

    return render_template('home/favorites.html', favorites=favorites,temperatures=temperatures_dict, weather_data=weather_data, user=current_user)

@views.route("/weather", methods=["GET", "POST"])
@login_required
def weather(): 
    continent = request.form.get("continent")
    
    europe = [
        "Barcelona", 
        "Athen", 
        "Lissabon", 
        "Madrid", 
        "Rom", 
        "Neapel", 
        "Palma de Mallorca", 
        "Valencia", 
        "Málaga", 
        "Sevilla", 
        "Istanbul", 
        "Antalya", 
        "Rhodos", 
        "Kreta",
        "Duisburg",
        "Bochum"
    ]
    
    asia = [
        "Bangkok", 
        "Singapur", 
        "Kuala Lumpur", 
        "Manila", 
        "Bali", 
        "Hongkong", 
        "Ho-Chi-Minh-Stadt", 
        "Tokyo", 
        "Phuket", 
        "Taipeh", 
        "Hanoi", 
        "Chiang Mai", 
        "Phnom Penh", 
        "Siem Reap", 
        "Boracay"
    ]

    southamerica = [
        "Rio de Janeiro", 
        "Salvador", 
        "Natal", 
        "Fortaleza", 
        "Recife", 
        "São Paulo", 
        "Brasília", 
        "Florianópolis", 
        "Belo Horizonte", 
        "Porto Alegre", 
        "Cartagena", 
        "Bogotá", 
        "Lima", 
        "Cusco", 
        "Santiago de Chile"
    ]

    northamerica = [
        "Miami",
        "Los Angeles",
        "San Diego",
        "Phoenix",
        "Las Vegas",
        "New Orleans",
        "Dallas",
        "Houston",
        "Austin",
        "San Antonio",
        "Orlando",
        "Tampa",
        "Honolulu",
        "Cancun",
        "Puerto Vallarta"
    ]

    australia = [
        "Sydney",
        "Melbourne",
        "Brisbane",
        "Adelaide",
        "Perth",
        "Gold Coast",
        "Cairns",
        "Darwin",
        "Alice Springs",
        "Uluru",
        "Hobart",
        "Airlie Beach",
        "Fraser Island",
        "Whitsunday Island",
        "Noosa"
    ]
    
    africa = [
        "Kapstadt",
        "Durban",
        "Johannesburg",
        "Port Elizabeth",
        "Marrakesch",
        "Agadir",
        "Hurghada",
        "Sharm El-Sheikh",
        "Dahab",
        "Safaga",
        "Diani Beach",
        "Mombasa",
        "Stone Town",
        "Kilifi",
        "Watamu"
    ]

    if continent == "europa":
        cities = europe
    elif continent == "asien":
        cities = asia
    elif continent == "suedamerika":
        cities = southamerica
    elif continent == "nordamerika":
        cities = northamerica
    elif continent == "australien":
        cities = australia
    elif continent == "afrika":
        cities = africa

    temperatures = []

    for city in cities:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key_geo}"
        response_geo = requests.get(geo_url)
        geo_data = response_geo.json()

        latitude = geo_data[0]["lat"]
        longitude = geo_data[0]["lon"]

        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key_weather}&lang=de&units=metric"
        response = requests.get(weather_url)
        weather_data = response.json()

        weather_desc = weather_data["weather"][0]["description"]
        temperature = round(weather_data["main"]["temp"])
        temperature_min = round(weather_data["main"]["temp_min"])
        temperature_max = round(weather_data["main"]["temp_max"])
        temp_feels = round(weather_data["main"]["feels_like"])
        humidity = weather_data["main"]["humidity"]
        cloudiness = weather_data["clouds"]["all"]
        weather_icon = weather_data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{weather_icon}@2x.png"
        temperatures.append([city, temperature, temperature_min, temperature_max, temp_feels, cloudiness, humidity, weather_desc, icon_url])

    temperatures_sorted = sorted(temperatures, key=lambda x: x[1], reverse=True)
    temperatures_dict = {city: (temperature, temperature_min, temperature_max, temp_feels, cloudiness, humidity, weather_desc, icon_url) for city, temperature, temperature_min, temperature_max, temp_feels, cloudiness, humidity, weather_desc, icon_url in temperatures_sorted}

    return render_template("home/weather.html", temperatures=temperatures_dict, continent=continent.capitalize(), weather_data=weather_data, user=current_user)


@views.route("/404")
def error404():
    return render_template("error/404.html", user=current_user)