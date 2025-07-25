from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import datetime
from dateutil import parser as date_parser
import pytz

# Scopes - what permissions we need
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def parse_event_time(event, local_tz=None):
    """Parse event start and end times, handling both datetime and all-day events, converting to local timezone"""
    if local_tz is None:
        local_tz = datetime.datetime.now().astimezone().tzinfo  # Use system's local timezone
        
    start_raw = event['start'].get('dateTime', event['start'].get('date'))
    end_raw = event['end'].get('dateTime', event['end'].get('date'))
    
    # Parse start time
    if 'T' in start_raw:  # datetime format
        start_time = date_parser.parse(start_raw)
        # Convert to local timezone
        start_time = start_time.astimezone(local_tz)
    else:  # date only (all-day event)
        start_time = date_parser.parse(start_raw)
        # For all-day events, assume they start at midnight in local timezone
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=local_tz)
    
    # Parse end time
    if 'T' in end_raw:  # datetime format
        end_time = date_parser.parse(end_raw)
        # Convert to local timezone
        end_time = end_time.astimezone(local_tz)
    else:  # date only (all-day event)
        end_time = date_parser.parse(end_raw)
        # For all-day events, assume they end at midnight in local timezone
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=local_tz)
    
    # Ensure both times have timezone info and are in local timezone
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=local_tz)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=local_tz)
    
    return start_time, end_time

def find_free_time(events, min_free_hours=2, start_hour=8, end_hour=16, local_tz=None):
    """Find free time periods between events during business hours (8 AM - 4 PM by default)"""
    if not events:
        return []
    
    if local_tz is None:
        local_tz = datetime.datetime.now().astimezone().tzinfo  # Use system's local timezone
    
    # Parse and sort events by start time
    parsed_events = []
    for event in events:
        try:
            start_time, end_time = parse_event_time(event, local_tz)
            parsed_events.append({
                'summary': event['summary'],
                'start': start_time,
                'end': end_time
            })
        except Exception as e:
            print(f"Warning: Could not parse event '{event.get('summary', 'Unknown')}': {e}")
            continue
    
    if not parsed_events:
        return []
    
    # Sort by start time
    parsed_events.sort(key=lambda x: x['start'])
    
    def is_business_hours(dt, start_h=start_hour, end_h=end_hour):
        """Check if datetime falls within business hours"""
        hour = dt.hour
        return start_h <= hour < end_h
    
    def trim_to_business_hours(start_dt, end_dt):
        """Trim a time period to only include business hours"""
        periods = []
        current_date = start_dt.date()
        end_date = end_dt.date()
        
        while current_date <= end_date:
            # Create business hours window for this date
            day_start = datetime.datetime.combine(current_date, datetime.time(start_hour, 0))
            day_end = datetime.datetime.combine(current_date, datetime.time(end_hour, 0))
            
            # Make timezone-aware using local timezone
            if start_dt.tzinfo:
                day_start = day_start.replace(tzinfo=start_dt.tzinfo)
                day_end = day_end.replace(tzinfo=start_dt.tzinfo)
            else:
                day_start = day_start.replace(tzinfo=local_tz)
                day_end = day_end.replace(tzinfo=local_tz)
            
            # Find overlap with our free period
            period_start = max(start_dt, day_start)
            period_end = min(end_dt, day_end)
            
            # If there's a valid overlap, add it
            if period_start < period_end:
                duration_hours = (period_end - period_start).total_seconds() / 3600
                if duration_hours >= min_free_hours:
                    periods.append({
                        'start': period_start,
                        'end': period_end,
                        'duration_hours': duration_hours
                    })
            
            current_date += datetime.timedelta(days=1)
        
        return periods
    
    free_periods = []
    
    # Get current time with local timezone awareness
    now = datetime.datetime.now().astimezone(local_tz)
    # Start checking free time from beginning of today to capture today's free periods
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Check if there's free time before the first event
    first_event_start = parsed_events[0]['start']
    gap_before_first = (first_event_start - today_start).total_seconds() / 3600
    if gap_before_first > 0:  # Any positive gap
        business_periods = trim_to_business_hours(today_start, first_event_start)
        free_periods.extend(business_periods)
    
    # Check gaps between consecutive events
    for i in range(len(parsed_events) - 1):
        current_event_end = parsed_events[i]['end']
        next_event_start = parsed_events[i + 1]['start']
        
        gap_duration_hours = (next_event_start - current_event_end).total_seconds() / 3600
        
        if gap_duration_hours > 0:  # Any positive gap
            business_periods = trim_to_business_hours(current_event_end, next_event_start)
            free_periods.extend(business_periods)
    
    return free_periods

def get_calendar_events():
    creds = None
    
    # Check if we have saved credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build the service
    service = build('calendar', 'v3', credentials=creds)
    
    # Get events from start of today until 10 days ahead (using local time)
    # This ensures we capture all events for today, not just future events
    # Use the system's local timezone
    local_now = datetime.datetime.now().astimezone()
    local_tz = local_now.tzinfo
    
    today_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    future_date = today_start + datetime.timedelta(days=10)
    
    

    
    
    now = today_start.isoformat()
    
    future_date = future_date.isoformat()
    
    print(f"Fetching events from: {today_start.strftime('%Y-%m-%d %H:%M:%S %Z')} to {future_date}")
    print(f"Current time: {local_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=future_date,
        maxResults=50,  # Get more events to better analyze free time
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        print('No upcoming events found.')
        return
    
    print('=== UPCOMING EVENTS ===')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{start}: {event['summary']}")
    
    print('\n=== FREE TIME PERIODS (8 AM - 4 PM) ===')
    free_periods = find_free_time(events, local_tz=local_tz)
    
    if not free_periods:
        print('No significant free time periods found during business hours (looking for 2+ hour gaps between 8 AM - 4 PM)')
    else:
        for period in free_periods:
            start_str = period['start'].strftime('%Y-%m-%d %H:%M')
            end_str = period['end'].strftime('%Y-%m-%d %H:%M')
            duration = period['duration_hours']
            
            if duration >= 6:  # 6+ hours is a full work day
                print(f"🗓️  {start_str} to {end_str} ({duration:.1f} hours)")
            else:
                print(f"⏰ {start_str} to {end_str} ({duration:.1f} hours)")
    
    # Calculate summary statistics
    print('\n=== SUMMARY ===')
    
    # Get current date in local timezone
    today = datetime.datetime.now().astimezone(local_tz).date()
    tomorrow = today + datetime.timedelta(days=1)
    three_days_from_now = today + datetime.timedelta(days=3)
    
    # Count events for today
    events_today = 0
    events_next_3_days = 0
    
    for event in events:
        try:
            start_time, _ = parse_event_time(event, local_tz)
            event_date = start_time.date()
            
            if event_date == today:
                events_today += 1
            elif tomorrow <= event_date <= three_days_from_now:
                events_next_3_days += 1
        except Exception:
            continue
    
    # Calculate free time for today
    today_free_time = 0
    for period in free_periods:
        if period['start'].date() == today:
            today_free_time += period['duration_hours']
    
    # Calculate free time for next 3 days (excluding today)
    next_3_days_free_time = 0
    for period in free_periods:
        if tomorrow <= period['start'].date() <= three_days_from_now:
            next_3_days_free_time += period['duration_hours']
    
    # Display results
    print("📅 TODAY:")
    print(f"   Events: {events_today}")
    print(f"   Free time: {today_free_time:.1f} hours")
    
    print("📊 NEXT 3 DAYS:")
    print(f"   Events: {events_next_3_days}")
    print(f"   Free time: {next_3_days_free_time:.1f} hours")

    # return the hole summary as a string
    return """Today: {events_today} events, {today_free_time:.1f} hours free
Next 3 days: {events_next_3_days} events, {next_3_days_free_time:.1f} hours free"""

if __name__ == '__main__':
    print(get_calendar_events()) 