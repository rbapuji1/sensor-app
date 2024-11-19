from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
import json
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)

# Set up the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL_UNPOOLED", "postgresql://user:password@localhost/dbname")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Define the database table
class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor1 = db.Column(db.Float, nullable=False)
    sensor2 = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

# Create the database
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

# POST endpoint to save new sensor data
@app.route("/post", methods=["POST"])
def post_data():
    data = request.get_json()
    sensor1 = data.get("sensor1")
    sensor2 = data.get("sensor2")
    if sensor1 is None or sensor2 is None:
        return jsonify({"error": "Missing value in request body"}), 400

    new_data = DataPoint(sensor1=sensor1, sensor2=sensor2)
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Data saved successfully!"}), 200

# GET endpoint to fetch chart data (all historical data)
@app.route('/chart-data')
def chart_data():
    # Fetch the latest 50 data points from the database
    data = DataPoint.query.order_by(DataPoint.id.desc()).limit(50).all()
    # Reverse the data to get it in ascending order (oldest first)
    data = data[::-1]
    
    # Convert to a list of dictionaries
    data_dict = [{
        "timestamp": data_point.timestamp.isoformat(),
        "sensor1": data_point.sensor1,
        "sensor2": data_point.sensor2
    } for data_point in data]
    
    return jsonify(data_dict)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
    
