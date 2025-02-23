import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import datetime, timedelta

# Configuration
GEMINI_API_KEY = "AIzaSyBPkVjk9aYoAvjDnHYPbHxD66A-DCIeC94"
EVENT_API_KEY = "25UDUKITT5JIIZJDC3"
IRCTC_API_KEY = "b32592978dmshdd659900c70a926p10e680jsne8a7f2500406"
AVIATIONSTACK_API_KEY = "1f285cc528a60fd27f947b918aa048b9"

# Configure AI model
genai.configure(api_key=GEMINI_API_KEY)

def get_iata_code(city_name):
    prompt = f"What is the IATA code for {city_name}?"
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip() if response else "Unknown"

def get_station_code(city_name):
    prompt = f"What is the main railway station code for {city_name} in India? Return only the station code in caps."
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

def is_indian_city(city_name):
    """Check if a city is in India"""
    prompt = f"Is {city_name} a city in India? Answer only 'yes' or 'no'."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip().lower() == "yes"

def get_train_options(source, destination):
    """Get AI-generated train options between cities"""
    try:
        source_in_india = is_indian_city(source)
        dest_in_india = is_indian_city(destination)
        currency = "INR" if source_in_india or dest_in_india else "USD"
        
        prompt = f"""List 5 trains that run between {source} and {destination}. 
        For each train include:
        - Train name and number
        - Departure and arrival times
        - Duration
        - Available classes (like AC 1st Class, AC 2 Tier, etc.)
        - Approximate fare range in {currency}
        Format each train on new lines with emoji 🚂. Do not use asterisks (*) in the response."""
        
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        trains = response.text.strip().split('\n')
        return [train for train in trains if train.strip()]
    except Exception as e:
        return ["Unable to find train information at the moment."]

def get_hotel_suggestions(destination, itinerary):
    """Get AI-generated hotel suggestions based on itinerary locations"""
    try:
        is_india = is_indian_city(destination)
        currency = "INR" if is_india else "USD"
        
        prompt = f"""Based on this itinerary for {destination}:
        {itinerary}
        
        Suggest 5 hotels that would be convenient for this schedule. For each hotel include:
        - Hotel name
        - Location/Area
        - Price range per night in {currency}
        - Star rating (use actual ⭐ emoji instead of asterisk)
        - Key amenities
        Format each hotel on new lines with emoji 🏨. Do not use asterisks (*) in the response."""
        
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        hotels = response.text.strip().split('\n')
        return [hotel for hotel in hotels if hotel.strip()]
    except Exception as e:
        return ["Unable to find hotel suggestions at the moment."]

def get_itinerary(destination, experience, days):
    prompt = f"""Generate a detailed {days}-day travel itinerary for {destination} focused on {experience}. 
    The schedule should include specific timestamps for activities, travel, and meals. 
    Ensure realism and do not use asterisks (*) in the response. Use actual formatting like 'Important:' or 'Note:' instead."""
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text if response else "Couldn't generate an itinerary."

def main():
    st.markdown(
        """
        <style>
        .main {
            background-color: #0e1117;
            color: #ffffff;
        }
        .css-1d391kg {
            background-color: #1e2126;
        }
        .content {
            padding: 20px;
        }
        .header {
            color: #00ff9f;
            font-size: 1.5em;
            margin: 10px 0;
            font-weight: bold;
        }
        .subheader {
            color: #00c4ff;
            font-size: 1.2em;
            margin: 10px 0;
        }
        .card {
            background-color: #1e2126;
            border: 1px solid #2d3035;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            color: #ffffff;
        }
        .error-card {
            background-color: #2d1215;
            border: 1px solid #ff4444;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            color: #ff4444;
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
    
    # Create a content area
    with st.container():
        st.markdown("<div class='content'>", unsafe_allow_html=True)

        if st.sidebar.button("Plan My Trip"):
            st.markdown(f"<div class='header'>Nice to meet you, {user_name}! 🎉</div>", unsafe_allow_html=True)
            
            if travel_preference.lower() == "flight":
                user_location_iata = get_iata_code(user_location)
                destination_iata = get_iata_code(destination)
                flights = get_flight_options(user_location_iata, destination_iata)
                st.markdown("<div class='subheader'>Available Flights: ✈️</div>", unsafe_allow_html=True)
                for flight in flights:
                    st.markdown(f"<div class='card'>{flight}</div>", unsafe_allow_html=True)
            elif travel_preference.lower() == "train":
                st.markdown("<div class='subheader'>Available Trains: 🚂</div>", unsafe_allow_html=True)
                st.markdown("<div class='card'>Searching for trains...</div>", unsafe_allow_html=True)
                trains = get_train_options(user_location, destination)
                for train in trains:
                    if "unable" in train.lower():
                        st.markdown(f"<div class='error-card'>{train}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='card'>{train}</div>", unsafe_allow_html=True)

            st.markdown("<div class='subheader'>Generating your detailed itinerary...</div>", unsafe_allow_html=True)
            itinerary = get_itinerary(destination, experience, days)
            st.markdown(f"<div class='header'>Here's your plan for {destination}:</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'>{itinerary}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='subheader'>Finding the best hotel options... 🏨</div>", unsafe_allow_html=True)
            hotels = get_hotel_suggestions(destination, itinerary)
            st.markdown(f"<div class='header'>Recommended Hotels in {destination}:</div>", unsafe_allow_html=True)
            for hotel in hotels:
                st.markdown(f"<div class='card'>{hotel}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='subheader'>Let me know if you need modifications or further details! 💬</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # Close the content area

if __name__ == "__main__":
    main()
