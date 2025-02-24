# WanderBot: Your AI Travel Guide 🧳

Welcome to WanderBot, your ultimate AI-powered travel guide designed to make your travel planning seamless and magical. WanderBot leverages cutting-edge Generative AI to provide personalized travel itineraries, flight and train options, hotel suggestions, and fun travel facts.

## Features

- **Personalized Itineraries**: Generate detailed travel itineraries based on your destination, preferred experience, and duration of stay.
- **Flight Options**: Get the best flight options from your origin to your destination.
- **Train Options**: Find train journeys between cities, especially useful for travel within India.
- **Hotel Suggestions**: Receive recommendations for hotels near your destination based on your itinerary.
- **Fun Travel Facts**: Enjoy random travel-related fun facts to keep your wanderlust alive.
- **Beautiful UI**: A visually appealing and user-friendly interface to enhance your travel planning experience.

## Methodology

### Generative AI Approach

WanderBot utilizes Google's Generative AI (GenAI) to generate content and provide accurate travel information. The AI model is configured using the `gemini-pro` model, which is known for its high-quality content generation capabilities.

#### Key Components

1. **IATA and Station Codes**: The AI model is used to fetch IATA codes for airports and station codes for railway stations.
2. **Travel Options**: The AI generates prompts to list flight and train options based on user inputs.
3. **Hotel Suggestions**: The AI suggests hotels near the destination, considering the user's itinerary.
4. **Itinerary Generation**: The AI creates a detailed travel itinerary, including timestamps for activities, travel, and meals.

### Implementation

- **Streamlit**: The web application is built using Streamlit, which provides an interactive and responsive UI.
- **APIs**: Various APIs are integrated to fetch real-time data:
  - **Eventbrite API**: To get suggested travel destinations.
  - **AviationStack API**: To fetch flight options.
- **Caching**: Images are loaded and resized with caching to improve performance.

### Pros of the Project

- **Personalization**: Tailored travel plans based on user preferences.
- **Efficiency**: Quick and accurate travel information, saving users time and effort.
- **User Experience**: Aesthetic and intuitive interface enhances user engagement.
- **Scalability**: The modular design allows easy addition of new features and integrations.
- **Innovation**: Utilizes advanced AI technology to provide a unique travel planning experience.

## How to Use WanderBot

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/THE-DEEPDAS/Travel-Bot.git
   cd Travel-Bot
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:

   ```bash
   streamlit run streamlit_app.py
   ```

4. **Interact with the App**:
   - Enter your name, origin, destination, preferred experience, travel mode, and duration of stay.
   - Click on "Plan My Trip" to get personalized travel plans.

## Screenshots

### Welcome Screen

![Welcome Screen](<screenshots/website%20(1).png>)

### Travel Planning Interface

![Travel Planning](<screenshots/website%20(2).png>)

### Flight Search Results

![Flight Search](<screenshots/website%20(3).png>)

### Train Journey Options

![Train Options](<screenshots/website%20(4).png>)

### Personalized Itinerary

![Itinerary](<screenshots/website%20(5).png>)

### Hotel Recommendations

![Hotels](<screenshots/website%20(6).png>)

### Travel Facts and Tips

![Travel Facts](<screenshots/website%20(7).png>)

### Interactive Elements

![Interactive UI](<screenshots/website%20(8).png>)

### Developer Information

![Developer Info](<screenshots/website%20(9).png>)

## Developer Information

Created with ❤️ by Deep Das. Connect with me on:

- [GitHub](https://github.com/THE-DEEPDAS)
- [LinkedIn](https://www.linkedin.com/in/deep-das-4b5aa527b/)
- [Email](mailto:deepdblm@gmail.com)

"Making travel planning magical, one journey at a time."

## License

This project is made by me so please give credits even if you extend my work.
