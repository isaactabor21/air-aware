# This is probably where the api should be 
 
# Shared flight data and helper functions

flights_data = [
    {
        "id": 1,
        "airline": "United",
        "flight_num": "441",
        "origin": "MSP",
        "destination": "DCA",
        "departure": "9:15 AM",
        "arrival": "12:20 PM",
        "duration": "3h 05m",
        "stops": "Nonstop",
        "on_time_prob": 91,
        "price": 342,
        "risk_factors": ["Clear weather expected"]
    },
    {
        "id": 2,
        "airline": "American",
        "flight_num": "882",
        "origin": "MSP",
        "destination": "DCA",
        "departure": "2:30 PM",
        "arrival": "5:28 PM",
        "duration": "2h 58m",
        "stops": "Nonstop",
        "on_time_prob": 32,
        "price": 298,
        "risk_factors": ["Winter storm warning", "Historical delays on this route"]
    },
    {
        "id": 3,
        "airline": "Delta",
        "flight_num": "1205",
        "origin": "MSP",
        "destination": "DCA",
        "departure": "6:45 AM",
        "arrival": "9:50 AM",
        "duration": "3h 05m",
        "stops": "Nonstop",
        "on_time_prob": 78,
        "price": 315,
        "risk_factors": ["Minor wind advisory"]
    },
    {
        "id": 4,
        "airline": "Southwest",
        "flight_num": "2341",
        "origin": "MSP",
        "destination": "DCA",
        "departure": "11:20 AM",
        "arrival": "2:35 PM",
        "duration": "3h 15m",
        "stops": "Nonstop",
        "on_time_prob": 45,
        "price": 276,
        "risk_factors": ["Aircraft arriving from delayed route"]
    },
    {
        "id": 5,
        "airline": "United",
        "flight_num": "892",
        "origin": "MSP",
        "destination": "DCA",
        "departure": "4:10 PM",
        "arrival": "7:15 PM",
        "duration": "3h 05m",
        "stops": "Nonstop",
        "on_time_prob": 94,
        "price": 389,
        "risk_factors": ["Clear conditions"]
    }
]

def get_probability_color(prob):
    """Return color based on on-time probability"""
    if prob >= 67:
        return "#28a745", "🟢"
    elif prob >= 33:
        return "#ffc107", "🟡"
    else:
        return "#dc3545", "🔴"