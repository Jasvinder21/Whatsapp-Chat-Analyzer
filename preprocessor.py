import re
import pandas as pd

def preprocess(data):
    # Corrected pattern to match DD/MM/YY, HH:MM AM/PM - with narrow no-break space
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\u202f[ap]m\s-\s'
    
    # Split and find dates
    messages = re.split(pattern, data)[1:]  # Messages after timestamps
    dates = re.findall(pattern, data)       # Extract timestamps
    
    # Create initial DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    
    # Convert message_date to datetime with correct 12-hour format
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M\u202f%p - ')
    
    # Rename column
    df.rename(columns={'message_date': 'date'}, inplace=True)
    
    # Extract users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)  # Use raw string and maxsplit=1
        if len(entry) > 2:  # User present
            users.append(entry[1])
            messages.append(" ".join(entry[2:]).strip())  # Join remaining parts and strip whitespace
        else:  # No user (group notification)
            users.append('group_notification')
            messages.append(entry[0].strip())  # Strip whitespace
    
    # Update DataFrame with users and messages
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    
    # Extract date components
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    
    # Calculate period (time slots)
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append('23-00')
        elif hour == 0:
            period.append('00-01')
        else:
            period.append(f'{hour:02d}-{hour + 1:02d}')  # Format with leading zeros
    
    df['period'] = period
    
    return df

