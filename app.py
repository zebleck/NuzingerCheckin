import requests
from datetime import datetime
import locale
import json
import logging

# Define the URLs
login_url = "https://community.nimbuscloud.at/api/v1/authenticate"
pre_checkin_courses_url = (
    "https://community.nimbuscloud.at/api/v1/checkin/pre-checkin-courses"
)
pre_checkin_url = "https://community.nimbuscloud.at/api/v1/checkin/toggle-pre-checkin"


with open("profiles.json", "r") as file:
    profiles = json.load(file)


def parse_date(timestamp):
    try:
        locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "de_DE")
        except locale.Error:
            locale.setlocale(locale.LC_TIME, "de_DE.utf8")
    return datetime.fromtimestamp(int(timestamp)).strftime("%a %d.%m.").upper()


def parse_time(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime("%H:%M")


def parse_time(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime("%H:%M")


def get_attendances(session, profile):
    print("Getting attendances...")
    attendances_url = "https://community.nimbuscloud.at/api/v1/checkin/attendances"
    attendances_payload = {"selectedCustomer": profile["selectedCustomer"]}

    # Get attendances
    attendances_response = session.post(attendances_url, data=attendances_payload)

    if attendances_response.status_code == 200:
        return attendances_response.json()
    else:
        print("Failed to get attendances:", attendances_response.text)


def check_attendance(attendances, event):
    for month in attendances["attendances"]:
        for attendance in month["attendances"]:
            if (
                attendance["displayName"] == event["name"]
                and parse_date(attendance["date"]) == event["start_date"].strip()
            ):
                return True
    return False


if __name__ == "__main__":
    for lesson_profile in profiles:
        # Start a session
        session = requests.Session()

        login_payload = {
            "account-email": lesson_profile["email"],
            "account-password": lesson_profile["password"],
            "init-system": "nuzinger",
            "source": "browser",
        }

        # Perform login
        login_response = session.post(login_url, data=login_payload)

        if login_response.status_code == 200:
            print(f"Login successful for {lesson_profile['email']}")
        else:
            print("Login failed:", login_response.text)
            continue

        attendances = get_attendances(session, lesson_profile)

        preferred_location = lesson_profile["location"]

        # Pre-checkin courses payload
        pre_checkin_courses_payload = {
            "selectedCustomer": lesson_profile["selectedCustomer"]
        }

        # Get pre-checkin courses
        pre_checkin_courses_response = session.post(
            pre_checkin_courses_url, data=pre_checkin_courses_payload
        )

        if pre_checkin_courses_response.status_code == 200:
            courses_data = pre_checkin_courses_response.json()

            # Find the specific event
            events = []
            print(f"Looking for courses at {preferred_location}...")
            for location in courses_data["content"]["locations"]:
                if location is not None and location["name"] != preferred_location:
                    continue
                for day in location["days"]:
                    for course in day["courses"]:
                        for lesson in lesson_profile["lessons"]:
                            if (
                                lesson["day"] in course["start_date"]
                                and course["start_time"] == lesson["time"]
                                and course["name"] == lesson["name"]
                            ):
                                events.append(course)
                                print(
                                    f"Found event: {course['name']} at {course['start_date']} {course['start_time']} (ID: {course['event']})"
                                )
                                break

            for event in events:
                print(
                    f"Trying to check in to {event['name']} on {event['start_date']}."
                )
                event_id = event["event"]
                if check_attendance(attendances, event):
                    print(
                        f"Already checked in to {event['name']} on {event['start_date']}"
                    )
                    continue

                # Pre-checkin payload
                pre_checkin_payload = {
                    "event": event_id,
                    "selectedCustomer": "129471",
                }

                # Perform pre-checkin
                pre_checkin_response = session.post(
                    pre_checkin_url, data=pre_checkin_payload
                )

                # Check if pre-checkin was successful
                if pre_checkin_response.status_code == 200:
                    pre_checkin_result = pre_checkin_response.json()
                    if pre_checkin_result.get("status") == "fail":
                        print("Pre-checkin failed: Course is full or other issue.")
                    else:
                        print("Pre-checkin successful!")
                else:
                    print("Pre-checkin failed:", pre_checkin_response.text)
        else:
            print(
                "Failed to get pre-checkin courses:", pre_checkin_courses_response.text
            )

        # Logout from the session
        logout_url = "https://community.nimbuscloud.at/api/v1/logout"
        logout_response = session.post(logout_url)

        if logout_response.status_code == 200:
            print("Logout successful.")
        else:
            print("Logout failed:", logout_response.text)

        # Close the session
        session.close()
