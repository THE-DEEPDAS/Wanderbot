import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import datetime, timedelta
import random
from PIL import Image
from io import BytesIO

# Configuration
GEMINI_API_KEY = "AIzaSyBMtWuT-lSCW1bMYfF8swUJXCyY9gc1lIs"
EVENT_API_KEY = "AIDZRLNW2HGLNDOLIHPG"
AVIATIONSTACK_API_KEY = "94ac4623810c8348b283768fac83dafc"

# Configure AI model
genai.configure(api_key=GEMINI_API_KEY)

@st.cache_data
def load_and_resize_image(url, target_size=(400, 300)):
    """Load and resize image from URL with caching"""
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None

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

def get_hero_images():
    """Get list of beautiful travel images for hero section"""
    return [
        "https://images.unsplash.com/photo-1488085061387-422e29b40080?auto=format&w=400&h=300&q=80",  # World Travel
        "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&w=400&h=300&q=80",  # Adventure
        "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&w=400&h=300&q=80",  # Scenic
        "https://images.unsplash.com/photo-1504150558240-0b4fd8946624",  # Luxury
        "https://images.unsplash.com/photo-1454391304352-2bf4678b1a7a",  # Nature
        "https://images.unsplash.com/photo-1501785888041-af3ef285b470",  # Mountain
        "https://images.unsplash.com/photo-1530789253388-582c481c54b0",  # Beach
        "https://images.unsplash.com/photo-1516483638261-f4dbaf036963"   # City
    ]

def show_developer_info():
    """Display developer information in a beautiful card"""
    st.markdown(
        """
        <div class='developer-card'>
            <h2>Meet the Developer 👨‍💻</h2>
            <div class='developer-content'>
                <p>Created with ❤️ by Deep</p>
                <div class='social-links'>
                    <a href="https://github.com/THE-DEEPDAS" target="_blank">GitHub 🐱</a>
                    <a href="https://www.linkedin.com/in/deep-das-4b5aa527b/" target="_blank">LinkedIn 💼</a>
                    <a href="mailto:deepdblm@gmail.com">Email ✉️</a>
                </div>
                <p class='developer-quote'>"Making travel planning magical, one journey at a time."</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def set_page_configuration():
    """Configure the page settings"""
    return st.set_page_config(
        page_title="WanderBot - AI Travel Guide",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def main():
    # Must be the first Streamlit command
    set_page_configuration()
    
    # Initialize session state
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'show_hero' not in st.session_state:
        st.session_state.show_hero = True
    
    # Apply styling
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
        /* Hero Section */
        .hero-section {
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6));
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            text-align: center;
            animation: fadeIn 1.5s ease-in;
        }
        .hero-title {
            font-size: 3.5em;
            color: #FFD700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 20px;
        }
        .hero-subtitle {
            font-size: 1.8em;
            color: #E0FFFF;
            margin-bottom: 30px;
        }
        .hero-images {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
        }
        .hero-image {
            width: 100%;
            height: 300px;
            object-fit: cover;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
        }
        .hero-image:hover {
            transform: scale(1.05);
        }
        
        /* Developer Card */
        .developer-card {
            background: linear-gradient(45deg, #1a1a2e 0%, #16213e 100%);
            border: 2px solid #FFD700;
            border-radius: 15px;
            padding: 25px;
            margin: 30px 0;
            color: #ffffff;
            text-align: center;
            animation: slideUp 1s ease;
        }
        .developer-content {
            margin: 15px 0;
        }
        .social-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 15px 0;
        }
        .social-links a {
            color: #FFD700;
            text-decoration: none;
            padding: 8px 15px;
            border: 1px solid #FFD700;
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        .social-links a:hover {
            background: #FFD700;
            color: #16213e;
        }
        .developer-quote {
            font-style: italic;
            color: #C1EFFF;
            margin-top: 15px;
        }
        
        /* Enhanced Sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px;
            border-right: 2px solid #FFD700;
        }
        .css-1d391kg .stTextInput input {
            background: rgba(255,255,255,0.1);
            border: 1px solid #FFD700;
            color: #ffffff;
            border-radius: 10px;
            padding: 10px;
        }
        .css-1d391kg .stSelectbox select {
            background: rgba(255,255,255,0.1);
            border: 1px solid #FFD700;
            color: #ffffff;
            border-radius: 10px;
        }
        .css-1d391kg .stButton button {
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #1a1a2e;
            border: none;
            border-radius: 20px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .css-1d391kg .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255,215,0,0.3);
        }
        .timeline-image-right {
            animation: slideInRight 1.5s ease-out;
            margin: 20px 0;
        }
        .timeline-image-left {
            animation: slideInLeft 1.5s ease-out;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # App title
    st.title("🌍 WanderBot: Your AI Travel Guide 🧳")
    
    # Create two columns: sidebar and main content
    col1, col2 = st.columns([1, 3])
    
    # Sidebar inputs
    with col1:
        with st.form("travel_form"):
            st.markdown("## ✈️ Plan Your Journey")
            user_name = st.text_input("What's your name?", "Traveler")
            user_location = st.text_input("From where are you planning your trip?", "New York")
            destination = st.text_input("Where are you thinking of traveling to?", "Paris")
            experience = st.text_input("What kind of experience do you prefer?", "Cultural")
            travel_preference = st.selectbox("How would you like to travel?", ["Flight", "Train"])
            days = st.number_input("How many days do you plan to stay?", min_value=1, max_value=30, value=5)
            
            submitted = st.form_submit_button("Plan My Trip")
            if submitted:
                st.session_state.show_results = True
                st.session_state.show_hero = False
    
    # Main content
    with col2:
        if st.session_state.show_hero:
            # Display hero section
            with st.container():
                st.markdown("<div class='hero-section'>", unsafe_allow_html=True)
                st.markdown("<div class='hero-title'>Welcome to WanderBot</div>", unsafe_allow_html=True)
                st.markdown("<div class='hero-subtitle'>Your AI Travel Guide</div>", unsafe_allow_html=True)
                
                # Display hero images
                image_cols = st.columns(3)
                for idx, img_url in enumerate(get_hero_images()[:3]):
                    with image_cols[idx]:
                        img = load_and_resize_image(img_url)
                        if img:
                            st.image(img, use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.show_results:
            # Process and display results
            with st.container():
                st.markdown(f"<div class='header'>Welcome aboard, {user_name}! ✨</div>", unsafe_allow_html=True)
                
                with st.spinner("Planning your perfect trip..."):
                    # Display travel options based on preference
                    if travel_preference.lower() == "flight":
                        st.markdown(f"<div class='fun-fact-card'>{get_fun_fact()}</div>", unsafe_allow_html=True)
                        st.markdown("<div class='loading-card'>🔍 Searching for the perfect flights...</div>", unsafe_allow_html=True)
                        user_location_iata = get_iata_code(user_location)
                        destination_iata = get_iata_code(destination)
                        flights = get_flight_options(user_location_iata, destination_iata)
                        st.markdown("<div class='subheader'>Available Flights: ✈️</div>", unsafe_allow_html=True)
                        for flight in flights:
                            st.markdown(f"<div class='card'>{flight}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='fun-fact-card'>{get_fun_fact()}</div>", unsafe_allow_html=True)
                        st.markdown("<div class='loading-card'>🚂 Finding magical train journeys...</div>", unsafe_allow_html=True)
                        trains = get_train_options(user_location, destination)
                        for train in trains:
                            formatted_train = format_response(train)
                            if "unable" in train.lower():
                                st.markdown(f"<div class='error-card'>{formatted_train}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='card'>{formatted_train}</div>", unsafe_allow_html=True)
                    
                    # Display itinerary and hotels
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

        # Developer Info
        show_developer_info()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")