import google.generativeai as genai
import requests
import json
from datetime import datetime, timedelta

# Configuration
GEMINI_API_KEY = "AIzaSyBPkVjk9aYoAvjDnHYPbHxD66A-DCIeC94"
EVENT_API_KEY = "25UDUKITT5JIIZJDC3"
IRCTC_API_KEY = "585fbd08a542ca3c10ad7c001c07de41"
AVIATIONSTACK_API_KEY = "1f285cc528a60fd27f947b918aa048b9"

# Configure AI model
genai.configure(api_key=GEMINI_API_KEY)

def get_iata_code(city_name):
    prompt = f"What is the IATA code for {city_name}?"
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip() if response else "Unknown"

def get_suggested_destinations():
    url = f"https://www.eventbriteapi.com/v3/events/search/?q=travel&token={EVENT_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        events = response.json()
        top_destinations = [event['venue']['city'] for event in events.get("events", [])[:5] if 'venue' in event and 'city' in event['venue']]
        return top_destinations if top_destinations else ["Delhi", "Mumbai", "Goa"]
    return ["Delhi", "Mumbai", "Goa"]

def get_hotel_suggestions(destination):
    url = f"https://data.xotelo.com/api/list?location={destination}"
    response = requests.get(url)
    if response.status_code == 200:
        hotels = response.json()
        return [hotel["name"] for hotel in hotels.get("hotels", [])[:5]] if "hotels" in hotels else ["No available hotels found."]
    return ["No available hotels found."]

def get_flight_options(origin, destination):
    url = f"http://api.aviationstack.com/v1/flights?access_key={AVIATIONSTACK_API_KEY}&dep_iata={origin}&arr_iata={destination}&limit=5"
    response = requests.get(url)
    if response.status_code == 200:
        flights = response.json()
        if "data" in flights and flights["data"]:
            flight_info = []
            for flight in flights["data"][:5]:
                flight_info.append(f"Airline: {flight['airline']['name']}, Flight: {flight['flight']['iata']}, Departure: {flight['departure']['airport']}, Arrival: {flight['arrival']['airport']}")
            return flight_info
    return ["No flights found"]

def get_itinerary(destination, experience, days):
    prompt = f"Generate a detailed {days}-day travel itinerary for {destination} focused on {experience}. The schedule should include specific timestamps for activities, travel, and meals. Ensure realism."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text if response else "Couldn't generate an itinerary."

def travel_assistant():
    print("\U0001F30D Welcome to WanderBot! Your AI Travel Guide \U0001F9F3")
    user_name = input("WanderBot: Hi! What's your name? ")
    print(f"WanderBot: Nice to meet you, {user_name}!")
    
    user_location = input("WanderBot: From where are you planning your trip? ")
    destination = input("WanderBot: Where are you thinking of traveling to? ")
    experience = input("WanderBot: What kind of experience do you prefer? ")
    travel_preference = input("WanderBot: How would you like to travel? (Train, Flight)? ")
    days = input("WanderBot: How many days do you plan to stay? ")
    
    if travel_preference.lower() == "flight":
        user_location_iata = get_iata_code(user_location)
        destination_iata = get_iata_code(destination)
        flights = get_flight_options(user_location_iata, destination_iata)
        print("WanderBot: Here are the available flights:")
        for flight in flights:
            print(flight)
    
    print("\nGenerating your detailed itinerary with timestamps...\n")
    itinerary = get_itinerary(destination, experience, days)
    print(f"WanderBot: Here's your plan for {destination}:\n{itinerary}")
    
    print("\nFinding the best hotel options...\n")
    hotels = get_hotel_suggestions(destination)
    print(f"WanderBot: Recommended Hotels in {destination}:\n" + "\n".join(hotels))
    
    print("\nWanderBot: Let me know if you need modifications or further details!")
    
if name == "main":
    travel_assistant()