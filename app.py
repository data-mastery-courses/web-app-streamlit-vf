import os
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOSTNAME = os.getenv("DB_HOSTNAME")
DB_NAME = os.getenv("DB_NAME")

st.title("Deliverable - Customer Insights App")
st.write("This app explores Deliverable review data.")


@st.cache_data
def load_data():
    """Fetch data from database into pandas df"""

    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}")

    df_reviews_avr = pd.read_sql_query(
        """
    select
        DATE(datetime) as review_date,
        location_city,
        count(*) as n_reviews,
        AVG(rating_delivery) as avg_del_score,
        AVG(rating_food) as avg_food_score
    from
        reviews revs
    left join
    restaurants rests
    on
        revs.restaurant_id = rests.restaurant_id
    where
        datetime >= '2023-01-01'
        and datetime < '2024-01-01'
        and location_city in ('Groningen', 'Amsterdam', 'Rotterdam')
    group by
        DATE(datetime),
        location_city
    """,
        con=engine,
    )
    return df_reviews_avr


# Load data
df_reviews = load_data()

min_date, max_date = st.slider(
    min_value=df_reviews.review_date.min(),
    max_value=df_reviews.review_date.max(),
    label="Select dates",
    value=(date(2023, 1, 1), date(2023, 12, 31)),
)

# fiter df_reviews on min_date and max_date
df_reviews_filter = df_reviews.loc[
    ((df_reviews.review_date >= min_date) & (df_reviews.review_date <= max_date))
]
df_reviews_filter = df_reviews_filter.sort_values(by="review_date")

st.write("### Average reviews in main cities")


def plot_avr_reviews(df_reviews):
    # The average number of reviews per day in each city (calculated as one number per city over the entire year)
    avg_reviews = df_reviews.groupby(["location_city"], as_index=False)["n_reviews"].mean()

    # Same but with nicer layout
    chart = px.bar(
        avg_reviews,
        x="location_city",
        y="n_reviews",
        labels={
            "n_reviews": "No. of reviews / Day",
            "location_city": "",
        },
        title="Average number of reviews per city per day",
        width=600,
    ).update_layout(title_x=0.5)

    return chart


chart = plot_avr_reviews(df_reviews_filter)
st.plotly_chart(chart)

st.write("### Reviews over time")

chart_time = px.line(df_reviews_filter, x="review_date", y="avg_del_score", color="location_city")
st.plotly_chart(chart_time)
