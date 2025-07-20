import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #f5f7fa;
    }
    /* Card-like containers */
    .block-container {
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        padding: 2rem 2rem 1rem 2rem;
        margin-bottom: 2rem;
    }
    /* Section headers */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Segoe UI', sans-serif;
        margin-top: 1.5rem;
    }
    /* Dataframe styling */
    .stDataFrame {
        background: #f9fafb;
        border-radius: 8px;
    }
    /* Sidebar styling */
    .css-1d391kg, .css-1d391kg .css-1v0mbdj {
        background: #2c3e50 !important;
        color: #fff !important;
    }
    /* Buttons */
    .stButton>button {
        background: #2c3e50;
        color: #fff;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border: none;
        margin-top: 1rem;
    }
    .stButton>button:hover {
        background: #34495e;
        color: #fff;
    }
    /* Divider */
    hr {
        border: 1px solid #e1e4e8;
        margin: 2rem 0;
    }
    .stat-box {
        border: 3px solid #222;
        border-radius: 18px;
        padding: 18px 10px 10px 10px;
        margin: 10px 0;
        background: #fff;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
    .stat-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
    }
    .stat-number {
        font-size: 2.2rem;
        font-weight: 800;
        color: #222;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.image("https://img.icons8.com/color/96/000000/whatsapp--v1.png", width=60)
st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    
    
    # Fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        with st.container():
            st.title("📊 Top Statistics")
            col1, col2, col3, col4 = st.columns(4)

            stats = helper.fetch_stats(selected_user, df)
            stat_titles = ["Total Messages", "Total Words", "Media Shared", "Links Shared"]

            for i, col in enumerate([col1, col2, col3, col4]):
                with col:
                    st.markdown(
                        f"""
                        <div class="stat-box">
                            <div class="stat-title">{stat_titles[i]}</div>
                            <div class="stat-number">{stats[i]}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        st.markdown("<hr>", unsafe_allow_html=True)

        with st.container():
            st.title("📅 Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig = px.line(timeline, x='time', y='message', title='Monthly Timeline', markers=True)
            st.plotly_chart(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Activity map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Finding the busiest users in the group (Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)
        st.markdown("<hr>", unsafe_allow_html=True)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Most common words
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')
        st.title('Most common words')
        st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
            st.pyplot(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Sentiment Analysis
        st.title("😊 Sentiment Analysis")
        sentiment_df = helper.sentiment_analysis(selected_user, df)
        fig = px.line(sentiment_df, x='only_date', y='sentiment', title='Average Sentiment Over Time')
        st.plotly_chart(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Active Hours Heatmap (Interactive)
        st.title("Active Hours Heatmap")
        active_heatmap = helper.active_hours_heatmap(selected_user, df)
        fig = px.imshow(active_heatmap, labels=dict(x="Hour of Day", y="Day of Week", color="Message Count"),
                        x=active_heatmap.columns, y=active_heatmap.index, aspect="auto", title="Active Hours Heatmap")
        st.plotly_chart(fig)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Hourly activity
        st.title("🕒 Hourly Activity")
        hourly_activity = helper.hourly_activity_map(selected_user, df)
        fig, ax = plt.subplots()
        ax.bar(hourly_activity.index, hourly_activity.values, color='skyblue')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)