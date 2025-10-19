import requests
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt

api_key = "0dca1c1d395f4e0da49150643251909" #This is the API key I've obtained from World Weather Online 

#The following function allows to retrieve weather data
# The information obatined by this program can be verified in: https://map.worldweatheronline.com
def get_weather_data(location, forecast_days=5):
    url = f"https://api.worldweatheronline.com/premium/v1/weather.ashx?key={api_key}&q={location}&format=json&num_of_days={forecast_days}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    
    if response.status_code == 200: #This work if the HTTP request was successful
        weather_data = response.json()
        
        #This part allows to print an error meassage if ther was a error in the API
        #other words of ther if the name of the place exists and the API is not expired
        if "error" in weather_data["data"]:
            print("Error:", weather_data["data"]["error"][0]["msg"])
            return None
        
        # The following helps to find the useful information for our case
        # as the weather data obatined by the url is raw and hard to distinguish
        current_weather = weather_data["data"]["current_condition"][0]
        current_temperature = current_weather["temp_C"]
        weather_description = current_weather["weatherDesc"][0]["value"]

        #This part helps with the forecast, as this infromation is stored in the
        #url in the matrix weather
        forecast = weather_data["data"]["weather"]
        df_forecast = pd.DataFrame(forecast) #This helps us to visualise the data by converting in Datafram
        return current_temperature, weather_description, df_forecast
    else:
        print("Error number:", response.status_code) #Provides the erros code if the HTTP request is not right
        return None

#The following fucntion is to generate a question at the begining of the program 
def parse_weather_question(question): 
    location = input(f"{question}\nYou: ")
    return location.strip()

def create_temperature_visualisation(weather_data, output_type='display'):
    df = weather_data.copy() #this part allow us to retrieve again the weather data
    # In the following part firts we select the information from our wetaher data
    # getting the min and max temperature and the we covert them in to numeric values
    # to be able to graph them
    df["maxtempC"] = pd.to_numeric(df["maxtempC"])
    df["mintempC"] = pd.to_numeric(df["mintempC"])

    # Here we create the Figure by using the library matplotlib
    fig, ax = plt.subplots(figsize=(5, 4)) # We define the size
    ax.plot(df["date"], df["maxtempC"], marker="x", label="Max Temp (°C)") # Here the axis
    ax.plot(df["date"], df["mintempC"], marker="x", label="Min Temp (°C)") # Here the axis
    ax.set_title("Temperature Forecast") # We set a title for the graph
    ax.set_xlabel("Date") # Set a name for our date axis
    ax.set_ylabel("Temperature (°C)") # Set a name for our Temperature axis
    ax.legend() # We desplay a basic legend
    ax.grid(True, linestyle='--', alpha=0.7) # Add lines into the figure to have a better localisation
    plt.xticks(rotation=90) # We rotate the date data to have more space
    plt.tight_layout() # AI recomended us this tools for space adjusting
    
    # This small part allow us to hold the figure before we run the complete program
    # otherwise we would have a figure before we enter location information
    if output_type == "figure":
        return fig
    else:
        plt.show()

def create_precipitation_visualisation(weather_data, output_type='display'):
    df = weather_data.copy() #this part allow us to retrieve again the weather data again
    # In the following part firts we select the information from our wetaher data
    # getting infromation about the precipitation, but accordinly to AI, our precipitation
    # is displayed hourly, so we have to make the following arrangement to group this
    # information per day
    df["precipMM"] = df["hourly"].apply(
        lambda x: pd.DataFrame(x)["precipMM"].astype(float).sum()
        if isinstance(x, list) else 0
    )
    # And now, we do the same we did for our create_temperature_visualisation function
    # for the visualisation arrangements
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(df["date"], df["precipMM"], color="skyblue", label="Total Daily Precipitation (mm)")
    ax.set_title("Daily Precipitation Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Precipitation (mm)")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.xticks(rotation=90)
    plt.tight_layout()

    if output_type == "figure":
        return fig
    else:
        plt.show()

#Here is where we start calling the functions to get the weather data
model_question = ("Hello! I'm a weather chatbot assistant, how can I help you?\n"
                  "(For accurate information please iclude city and country :))")
location = parse_weather_question(model_question)

# The following line was done with AI support as I was not able to not include
# especial signs as "?" in the print section
location = location.encode("ascii", "ignore").decode().strip() 
print("\nThe weather for",location,"is the following:")

results = get_weather_data(location) #We called the weather function
if results:
    current_temperature, weather_description, df_forecast = results
    print(f"\nCurrent Temperature: {current_temperature}°C")
    print(f"Current Condition: {weather_description}\n")
    print("Forecast for: ",len(df_forecast), "days")
    print(tabulate(df_forecast[['date', 'maxtempC', 'mintempC']], headers='keys'))

    #For visualisation
    create_temperature_visualisation(df_forecast)

    create_precipitation_visualisation(df_forecast)

else:
    print("No data found, please try again!!!")