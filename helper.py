# helper.py
import re
from wordcloud import WordCloud
import pandas as pd
import emoji
from textblob import TextBlob

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    num_messages = df.shape[0]
    words = df['message'].apply(lambda x: len(str(x).split())).sum()
    num_media_messages = df[df['message'] == '<Media omitted>'].shape[0]
    num_links = df['message'].apply(lambda x: len(re.findall(r'http\S+|www\S+', str(x)))).sum()
    
    return num_messages, words, num_media_messages, num_links

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + '-' + timeline['year'].astype(str)
    return timeline[['time', 'message']]

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline[['only_date', 'message']]

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    pivot_table = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return pivot_table.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

def most_busy_users(df):
    x = df['user'].value_counts().head(10)
    new_df = pd.DataFrame(x).reset_index()
    new_df.columns = ['user', 'message_count']
    return x, new_df

def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    wc.generate(' '.join(df['message'].astype(str)))
    return wc

def most_common_words(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    temp = df[df['message'] != '<Media omitted>']
    words = ' '.join(temp['message']).lower().split()
    words = [word for word in words if word not in set(['a', 'the', 'is', 'and', 'to'])]  # Basic stop words
    word_counts = pd.Series(words).value_counts().head(10)
    return word_counts.index, word_counts.values

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
    
    emoji_df = pd.DataFrame({'emoji': emojis}).value_counts().head(10).reset_index(name='count')
    return emoji_df['emoji'], emoji_df['count']

def hourly_activity_map(selected_user, df):
    # If analyzing a specific user, filter the DataFrame
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    # Ensure there is a datetime column; adjust if your column is named differently
    if 'date' in df.columns:
        df['hour'] = pd.to_datetime(df['date']).dt.hour
    elif 'message_date' in df.columns:
        df['hour'] = pd.to_datetime(df['message_date']).dt.hour
    # If you already have an 'hour' column, skip the above
    return df['hour'].value_counts().sort_index()

def sentiment_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    sentiments = df['message'].astype(str).apply(lambda x: TextBlob(x).sentiment.polarity)
    df = df.copy()
    df['sentiment'] = sentiments
    # Aggregate by date or user as needed
    sentiment_by_date = df.groupby('only_date')['sentiment'].mean().reset_index()
    return sentiment_by_date

def active_hours_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    # Ensure hour and day_name columns exist
    if 'hour' not in df.columns:
        if 'date' in df.columns:
            df['hour'] = pd.to_datetime(df['date']).dt.hour
        elif 'message_date' in df.columns:
            df['hour'] = pd.to_datetime(df['message_date']).dt.hour
    if 'day_name' not in df.columns:
        if 'date' in df.columns:
            df['day_name'] = pd.to_datetime(df['date']).dt.day_name()
        elif 'message_date' in df.columns:
            df['day_name'] = pd.to_datetime(df['message_date']).dt.day_name()
    heatmap = df.pivot_table(index='day_name', columns='hour', values='message', aggfunc='count').fillna(0)
    # Reorder days for better visualization
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap = heatmap.reindex(days_order)
    return heatmap