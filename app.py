# How to run this web app:
# open the shell in the Deliverable repo
# `streamlit run team_projects/example_member/web_app/app.py`
#
# Source: https://github.com/data-mastery-courses/web-app-streamlit-vf

# %%
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

# %%

st.title("Deliverable - Customer Insights App")
st.markdown("This app explores Deliverable review data and CBS demographical data.")


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
        datetime >= '2022-01-01'
        and datetime < '2023-02-01'
        and location_city in ('Groningen', 'Amsterdam', 'Rotterdam')
    group by
        DATE(datetime),
        location_city
    """,
        con=engine,
    )
    return df_reviews_avr


def min_max_dates(df_reviews):
    min_date_df = df_reviews.review_date.min()
    max_date_df = df_reviews.review_date.max()
    return min_date_df, max_date_df


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


def plot_reviews_over_time(df):
    chart = px.line(df_reviews_filter, x="review_date", y="avg_del_score", color="location_city")
    return chart


# Load data
df_reviews = load_data()

# %%
min_date_df, max_date_df = min_max_dates(df_reviews)

min_date, max_date = st.slider(
    min_value=min_date_df,
    max_value=max_date_df,
    label="Select dates",
    value=(date(2022, 1, 1), date(2022, 12, 31)),
)

# fiter df_reviews on min_date and max_date
df_reviews_filter = df_reviews.loc[
    ((df_reviews.review_date >= min_date) & (df_reviews.review_date <= max_date))
]
df_reviews_filter = df_reviews_filter.sort_values(by="review_date")

# %%
st.write("### Average reviews in main cities")

chart = plot_avr_reviews(df_reviews_filter)
st.plotly_chart(chart)

st.write("### Reviews over time")

chart_time = plot_reviews_over_time(df_reviews_filter)
st.plotly_chart(chart_time)
