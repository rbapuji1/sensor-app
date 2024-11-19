from flask import Flask, request, jsonify, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()

app = Flask(__name__)

# Set up the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL_UNPOOLED", "postgresql://user:password@localhost/dbname")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

@app.route('/chart-data')
def chart_data():
    def event_stream():
        last_id = 0  # Starting point
        # Fetch all historical data immediately
        with app.app_context():  # Ensure the database query is within the app context
            all_data = DataPoint.query.order_by(DataPoint.id).all()  # Get all data from the database
            for data in all_data:
                data_dict = {
                    "id": data.id,
                    "timestamp": data.timestamp.isoformat(),
                    "sensor1": data.sensor1,
                    "sensor2": data.sensor2
                }
                yield f"data: {json.dumps(data_dict)}\n\n"  # Send all historical data
        
        # Now start listening for new data incrementally
        while True:
            with app.app_context():  # Ensure the database query is within the app context
                # Fetch the latest data that is greater than the last_id
                new_data = DataPoint.query.filter(DataPoint.id > last_id).order_by(DataPoint.id).limit(1).all()
                if new_data:
                    data = new_data[0]
                    last_id = data.id  # Update the last seen ID
                    data_dict = {
                        "id": data.id,
                        "timestamp": data.timestamp.isoformat(),
                        "sensor1": data.sensor1,
                        "sensor2": data.sensor2
                    }
                    yield f"data: {json.dumps(data_dict)}\n\n"
            time.sleep(1)  # Delay to simulate real-time updates (adjust as needed)
    
    return Response(event_stream(), content_type='text/event-stream')



if __name__ == "__main__":
    app.run(debug=True, threaded=True)
