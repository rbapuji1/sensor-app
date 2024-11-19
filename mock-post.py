import requests
import random
import time

# URL of the Flask endpoint
POST_URL = "http://127.0.0.1:5000/post"

# Function to generate random sensor data
def generate_sensor_data():
    return {
        "sensor1": round(random.uniform(20.0, 30.0), 2),  # Random float between 20.0 and 30.0
        "sensor2": round(random.uniform(40.0, 50.0), 2)   # Random float between 40.0 and 50.0
    }

def main():
    print(f"Starting to post data to {POST_URL}...")
    try:
        while True:
            # Generate random data
            data = generate_sensor_data()
            
            # Post data to the server
            response = requests.post(POST_URL, json=data)
            
            # Check response
            if response.status_code == 200:
                print(f"Successfully posted data: {data}")
            else:
                print(f"Failed to post data: {response.status_code} - {response.text}")
            
            # Wait 1 second before sending the next request
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped posting data.")

if __name__ == "__main__":
    main()
