# Nuzinger Check-in Bot

This script automatically checks the availability of lessons and checks you in for the selected lesson.

Create a profiles.json with the following structure:
```json
[
    {
        "location": "Tanzhaus Heidelberg",
        "selectedCustomer": 123456,
        "email": "example@example.com",
        "password": "password123",
        "lessons": [
            {"day": "SO", "time": "18:10", "name": "Singles Stufe 2"},
            {"day": "SO", "time": "19:20", "name": "Singles Stufe 3"},
            {"day": "DI", "time": "18:10", "name": "Paare Stufe 2"},
            {"day": "DI", "time": "19:20", "name": "Paare Stufe 3"}
        ]
    }
]
```