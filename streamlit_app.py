import streamlit as st
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

def main():
    st.markdown(
        """
        <style>
        .main {
            background-color: #f0f8ff;  /* Light blue background */
        }
        .header {
            color: #2e8b57;  /* Sea green */
        }
        .subheader {
            color: #4682b4;  /* Steel blue */
        }
        .highlight {
            background-color: #ffe4e1;  /* Misty rose */
            padding: 10px;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🌍 WanderBot: Your AI Travel Guide 🧳")
    
    st.sidebar.title("✈️ User Information")
    user_name = st.sidebar.text_input("What's your name?", "Traveler")
    user_location = st.sidebar.text_input("From where are you planning your trip?", "New York")
    destination = st.sidebar.text_input("Where are you thinking of traveling to?", "Paris")
    experience = st.sidebar.text_input("What kind of experience do you prefer?", "Cultural")
    travel_preference = st.sidebar.selectbox("How would you like to travel?", ["Flight", "Train"])
    days = st.sidebar.number_input("How many days do you plan to stay?", min_value=1, max_value=30, value=5)
    
    if st.sidebar.button("Plan My Trip"):
        st.markdown(f"<h3 class='header'>Nice to meet you, **{user_name}**! 🎉</h3>", unsafe_allow_html=True)
        
        if travel_preference.lower() == "flight":
            user_location_iata = get_iata_code(user_location)
            destination_iata = get_iata_code(destination)
            flights = get_flight_options(user_location_iata, destination_iata)
            st.markdown("<h3 class='subheader'>Available Flights: ✈️</h3>", unsafe_allow_html=True)
            for flight in flights:
                st.markdown(f"- {flight}")
        
        st.markdown("<h3 class='subheader'>Generating your detailed itinerary with timestamps... ⏳</h3>", unsafe_allow_html=True)
        itinerary = get_itinerary(destination, experience, days)
        st.markdown(f"<h3 class='header'>Here's your plan for **{destination}**:</h3>\n{itinerary}", unsafe_allow_html=True)
        
        st.markdown("<h3 class='subheader'>Finding the best hotel options... 🏨</h3>", unsafe_allow_html=True)
        hotels = get_hotel_suggestions(destination)
        st.markdown(f"<h3 class='header'>Recommended Hotels in **{destination}**:</h3>\n" + "\n".join(hotels), unsafe_allow_html=True)
        
        st.markdown("<h3 class='subheader'>Let me know if you need modifications or further details! 💬</h3>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
