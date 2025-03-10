import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import datetime, timedelta
import random

# Configuration
GEMINI_API_KEY = "AIzaSyB_G0L0lkcGn_Pu_4mSj4vNJsYbaj3wizI"
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
    try:
        source_in_india = is_indian_city(source)
        dest_in_india = is_indian_city(destination)
        currency = "INR" if source_in_india or dest_in_india else "USD"
        
        prompt = f"""List 5 trains that run between {source} and {destination}. Format as shown:
        🚂 Train Name - Number
        ├─ Departure: HH:MM AM/PM ({source})
        ├─ Arrival: HH:MM AM/PM ({destination})
        ├─ Duration: X hours Y minutes
        ├─ Classes: [list available classes]
        └─ Fare Range: {currency} [range]
        
        Ensure each train detail is on a new line with proper indentation using ├─ and └─."""
        
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip().split('\n\n')
    except Exception as e:
        return ["Unable to find train information at the moment."]

def get_hotel_suggestions(destination, itinerary):
    try:
        is_india = is_indian_city(destination)
        currency = "INR" if is_india else "USD"
        
        prompt = f"""Suggest 5 hotels near {destination} based on the itinerary. Format as shown:
        🏨 Hotel Name
        ├─ Location: [area/neighborhood]
        ├─ Price: {currency} [range] per night
        ├─ Rating: [1-5] ⭐
        └─ Amenities: [key features]
        
        Ensure each hotel detail is on a new line with proper indentation using ├─ and └─."""
        
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip().split('\n\n')
    except Exception as e:
        return ["Unable to find hotel suggestions at the moment."]

def get_itinerary(destination, experience, days):
    prompt = f"""Generate a detailed {days}-day travel itinerary for {destination} focused on {experience}. 
    The schedule should include specific timestamps for activities, travel, and meals. 
    Ensure realism and do not use asterisks (*) in the response. Use actual formatting like 'Important:' or 'Note:' instead."""
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text if response else "Couldn't generate an itinerary."

def get_fun_fact():
    """Get a random travel-related fun fact"""
    facts = [
        "✈️ The world's shortest commercial flight is in Scotland, lasting only 1.5 minutes!",
        "🌍 There are 195 countries in the world to explore.",
        "🏨 The oldest hotel in the world has been operating since 705 AD in Japan.",
        "🚂 The longest train journey in the world takes 18 days from Portugal to Vietnam.",
        "🌟 The Northern Lights can be seen from 60 different countries.",
        "🏖️ Singapore has a man-made waterfall that's 130 feet tall!",
        "🗺️ Vatican City is the smallest country in the world.",
        "🌅 There's a pink lake in Australia called Lake Hillier.",
        "🏔️ Mount Everest grows about 4mm taller every year!",
        "🌊 The Great Barrier Reef is the largest living structure on Earth."
    ]
    return random.choice(facts)

def format_response(text):
    """Format response with proper line breaks and remove markdown"""
    text = text.replace('**', '')  # Remove bold markdown
    text = text.replace('├─', '\n├─')  # Add line breaks before tree symbols
    text = text.replace('└─', '\n└─')  # Add line breaks before tree symbols
    return text

def get_progress_message():
    messages = [
        "🔮 Consulting the travel oracle...",
        "🌟 Sprinkling some wanderlust magic...",
        "🎨 Crafting your perfect journey...",
        "🌈 Weaving travel dreams together...",
        "✨ Adding a touch of magic to your plans..."
    ]
    return random.choice(messages)

def main():
    st.markdown(
        """
        <style>
        .main {
            background: linear-gradient(135deg, #000428 0%, #004e92 100%);
            color: #ffffff;
            font-family: 'Quicksand', sans-serif;
        }
        .css-1d391kg {
            background: linear-gradient(45deg, #000428 0%, #004e92 100%);
        }
        .content {
            padding: 20px;
        }
        .header {
            color: #FFE5B4;
            font-size: 1.8em;
            margin: 15px 0;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            background: linear-gradient(90deg, rgba(0,4,40,0.8) 0%, rgba(0,78,146,0.8) 100%);
            padding: 15px 25px;
            border-radius: 15px;
            border-left: 5px solid #FFD700;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .subheader {
            color: #E0FFFF;
            font-size: 1.4em;
            margin: 12px 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        .card {
            background: linear-gradient(45deg, rgba(0,4,40,0.9) 0%, rgba(0,78,146,0.9) 100%);
            border: 1px solid #FFD700;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            color: #ffffff;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            white-space: pre-line;
        }
        .card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            border-color: #FFF8DC;
        }
        .fun-fact-card {
            background: linear-gradient(45deg, #2C3E50 0%, #3498DB 100%);
            border: 2px solid #FFD700;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            color: #FFF8DC;
            animation: glow 2s infinite alternate;
        }
        .loading-card {
            background: linear-gradient(45deg, #000428 0%, #004e92 100%);
            border: 2px solid #FFD700;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            color: #FFF8DC;
            animation: pulse 2s infinite;
        }
        @keyframes glow {
            from {
                box-shadow: 0 0 10px #FFD700, 0 0 20px #FFD700, 0 0 30px #FFD700;
            }
            to {
                box-shadow: 0 0 20px #FFD700, 0 0 30px #FFD700, 0 0 40px #FFD700;
            }
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #251B37;
        }
        ::-webkit-scrollbar-thumb {
            background: #FFDBA4;
            border-radius: 5px;
        }
        /* Sidebar styling */
        .css-1d391kg .stSelectbox, 
        .css-1d391kg .stTextInput {
            background-color: #372948;
            color: #ffffff;
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
    
    # Create a content area
    with st.container():
        st.markdown("<div class='content'>", unsafe_allow_html=True)

        if st.sidebar.button("Plan My Trip"):
            st.markdown(f"<div class='header'>Welcome to your magical journey, {user_name}! ✨</div>", unsafe_allow_html=True)
            
            if travel_preference.lower() == "flight":
                st.markdown(f"<div class='fun-fact-card'>{get_fun_fact()}</div>", unsafe_allow_html=True)
                st.markdown("<div class='loading-card'>🔍 Searching for the perfect flights...</div>", unsafe_allow_html=True)
                user_location_iata = get_iata_code(user_location)
                destination_iata = get_iata_code(destination)
                flights = get_flight_options(user_location_iata, destination_iata)
                st.markdown("<div class='subheader'>Available Flights: ✈️</div>", unsafe_allow_html=True)
                for flight in flights:
                    st.markdown(f"<div class='card'>{flight}</div>", unsafe_allow_html=True)
            elif travel_preference.lower() == "train":
                st.markdown(f"<div class='fun-fact-card'>{get_fun_fact()}</div>", unsafe_allow_html=True)
                st.markdown("<div class='loading-card'>🚂 Finding magical train journeys...</div>", unsafe_allow_html=True)
                trains = get_train_options(user_location, destination)
                for train in trains:
                    formatted_train = format_response(train)
                    if "unable" in train.lower():
                        st.markdown(f"<div class='error-card'>{formatted_train}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='card'>{formatted_train}</div>", unsafe_allow_html=True)

            st.markdown(f"<div class='fun-fact-card'>{get_fun_fact()}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='loading-card'>{get_progress_message()}</div>", unsafe_allow_html=True)
            itinerary = format_response(get_itinerary(destination, experience, days))
            st.markdown(f"<div class='header'>Here's your plan for {destination}:</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'>{itinerary}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='subheader'>Finding the best hotel options... 🏨</div>", unsafe_allow_html=True)
            hotels = get_hotel_suggestions(destination, itinerary)
            st.markdown(f"<div class='header'>Recommended Hotels in {destination}:</div>", unsafe_allow_html=True)
            for hotel in hotels:
                formatted_hotel = format_response(hotel)
                st.markdown(f"<div class='card'>{formatted_hotel}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='subheader'>See you again 👋</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # Close the content area

if __name__ == "__main__":
    main()