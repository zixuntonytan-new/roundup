import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

_BRANCH = "debug-gh-actions"
_RAW = f"https://raw.githubusercontent.com/Hutchins-RAs/roundup/{_BRANCH}"


def load_df():
    df = pd.read_csv(f"{_RAW}/data/wp_data.csv", parse_dates=["est_PubDate"])
    source_options = df.Source.unique()
    current_date = datetime.now()
    return df, source_options, current_date


def load_status():
    status_df = pd.read_csv(
        f"{_RAW}/streamlit/scraper_status.txt", names=["Source", "Status"]
    )
    return status_df


def load_last_run():
    try:
        r = requests.get(f"{_RAW}/streamlit/last_run.txt", timeout=10)
        parts = r.text.strip().split(",")
        run_date = parts[0]
        new_papers = int(parts[1]) if len(parts) > 1 else 0
        return run_date, new_papers
    except Exception:
        return None, None


def check_rows(column, options):
    return res.loc[res[column].isin(options)]


st.set_page_config(page_title="Roundup Data Viewer", page_icon="📖", layout="wide")
st.title("Roundup: Aggregating the Latest Economics Research")

st.write(
    "What are economists researching? We aggregate recent economics working papers from "
    "20 sources, with results updated daily by 7:00 a.m. EST. "
    "Working papers, also known as pre-print papers, are recently written research "
    "articles that have not yet been vetted by the peer review process at an academic "
    "journal."
)
st.write("")
st.write(
    "This version of the roundup scraper is maintained by the research assistants of the Hutchins Center on Monetary and Fiscal Policy at Brookings. Our code can be found at: "
    "https://github.com/Hutchins-RAs/roundup"
)
st.write("")
st.write(
    "See the original source code from Lorae Stojanovic at: "
    "https://github.com/lorae/roundup"
)
st.divider()

# Load data
df, source_options, current_date = load_df()
res = df
status_df = load_status()
last_run_date, last_run_count = load_last_run()

# Calculate the number of active web scrapers
total_scrapers = status_df.shape[0]
active_scrapers = (status_df["Status"] == "on").sum()

########## Sidebar ##########
st.sidebar.header("Options")

all_sources_option = "All"
source_options_with_all = [all_sources_option] + list(source_options)
source_selection = st.sidebar.multiselect(
    "Select source(s)", source_options_with_all, default=[all_sources_option]
)
slider_selection = st.sidebar.slider(
    "How many days of data would you like to view?",
    min_value=1,
    max_value=30,
    value=7,
    step=1,
)

# Last run info
st.sidebar.header("Last Run")
if last_run_date and last_run_date != "pending":
    st.sidebar.write(f"**Date:** {last_run_date}")
    st.sidebar.write(f"**New papers added:** {last_run_count}")
else:
    st.sidebar.write("Not yet available")

# Web scraper status
st.sidebar.header("Web Scraper Status")
scraper_expander_message = f"{active_scrapers} of {total_scrapers} web scrapers active"
with st.sidebar.expander(scraper_expander_message, expanded=False):
    for _, row in status_df.iterrows():
        col1, col2 = st.columns([3, 1])
        # Write the values to the columns
        col1.write(row["Source"])
        col2.write(row["Status"])


########## Main ##########

min_date = current_date - timedelta(days=(slider_selection))

if all_sources_option in source_selection:
    df_filtered = df[df["est_PubDate"] >= min_date]
else:
    df_filtered = df[
        (df["est_PubDate"] >= min_date) & (df["Source"].isin(source_selection))
    ]

posted = pd.to_datetime(df_filtered["Date"], errors="coerce")
df_filtered = df_filtered[posted.isna() | (posted >= current_date - timedelta(days=30))]

source_order = [
    "NBER", "FED-BOARD", "FED-BOARD-NOTES", "FED-ATLANTA", "FED-BOSTON",
    "FED-CHICAGO", "FED-CLEVELAND", "FED-DALLAS", "FED-KANSASCITY",
    "FED-MINNEAPOLIS", "FED-NEWYORK", "FED-PHILADELPHIA", "FED-RICHMOND",
    "FED-SANFRANCISCO", "FED-STLOUIS", "BEA", "BFI", "BIS", "BOE", "ECB", "IMF",
]
sort_key = df_filtered["Source"].map(
    lambda x: source_order.index(x) if x in source_order else len(source_order)
)
df_filtered = df_filtered.iloc[sort_key.argsort()]

num_results = len(df_filtered)
st.write(f"{num_results} entries found")

entry_number = 1
for _, row in df_filtered.iterrows():
    index_col, text_col = st.columns([1, 15])

    with index_col:
        st.markdown(f"### {entry_number}")

    with text_col:
        st.markdown(f"###  `{row['Source']}` [{row['Title']}]({row['Link']})")
        st.markdown(f"##### {row['Author']}")
        colA, colB = st.columns([1, 1])
        with colA:
            st.markdown(
                f"###### **Estimated Pub Date:** {row['est_PubDate'].strftime('%Y-%m-%d')}"
            )
        with colB:
            st.markdown(f"###### **Posted Pub Date:** {row['Date']}")
        st.markdown("**Abstract:** " + str(row["Abstract"]).replace("$", "\\$"))

    entry_number += 1
