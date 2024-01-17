import datetime

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine


@st.cache_data
def load_data():
    DB_USER = "deliverable_taskforce"  # noqa: N806
    DB_PASSWORD = "learn_sql_2024"  # noqa: N806
    DB_HOSTNAME = "training.postgres.database.azure.com"  # noqa: N806
    DB_NAME = "deliverable"  # noqa: N806

    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}")
    df_daily_reviews = pd.read_sql_query(
        f"""
            select 
                res.colophon_data_city as city, 
                date_trunc('day', rev.datetime) as review_day,
                count(*) as n_reviews
            from 
                public.reviews rev
                join restaurants res
                using (restaurant_id)
            where res.colophon_data_city in ('Amsterdam', 'Rotterdam', 'Groningen') and rev.datetime >= '2022-01-01' and rev.datetime < '2023-01-01'
            group by res.colophon_data_city, review_day 
            """,  # noqa: F541
        con=engine,
    )
    return df_daily_reviews


# Create a nice title
st.title("Data in main cities")
# Create a text element and let the reader know the data is loading.
data_load_state = st.text("Loading data...")
# Load Data
data = load_data()

# Filter Data on Date
data["review_day"] = data["review_day"].dt.date
date_min, date_max = st.slider(
    label="Included date range",
    min_value=datetime.date(2022, 1, 1),
    max_value=datetime.date(2023, 1, 1),
    value=(datetime.date(2022, 1, 1), datetime.date(2023, 1, 1)),
    step=datetime.timedelta(days=1),
)
# date_min = st.date_input(label="earliest included date", value=datetime.date(2022, 1, 1))
# date_max = st.date_input(label="last included date", value=datetime.date(2022, 12, 31)) + datetime.timedelta(
# days=1
# )

filtered_data = data[(data["review_day"] >= date_min) & (data["review_day"] < date_max)]


# Notify the reader that the data was successfully loaded.
data_load_state.text("Loading data...done!")


# Create summed data and plot it
data_summed = filtered_data[["city", "n_reviews"]].groupby("city").sum().reset_index()
st.bar_chart(data_summed, x="city", y="n_reviews")

# Create a line chart of reviews over time
st.line_chart(filtered_data, x="review_day", y="n_reviews", color="city")
