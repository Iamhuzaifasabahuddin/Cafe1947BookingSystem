import time
from datetime import datetime

import pandas as pd
import pytz
import streamlit as st
from notion_client import Client

st.set_page_config(page_title="Cafe Reservations", page_icon="☕", layout="centered")

# st.markdown("""
#     <style>
#
#     /* Existing styling you already have */
#     @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&display=swap');
#
#     .st-emotion-cache-1w4gzkv h1, .st-emotion-cache-1w4gzkv h2, .st-emotion-cache-1w4gzkv h3, .st-emotion-cache-1w4gzkv h4, .st-emotion-cache-1w4gzkv h5, .st-emotion-cache-1w4gzkv h6, .st-emotion-cache-1w4gzkv span {
#                 font-family: 'Cinzel Decorative', serif !important;
#     }
#     html, body, [class*="stApp"] {
#         font-family: 'Cinzel Decorative', serif !important;
#         background: linear-gradient(135deg, #FBF8F3 0%, #F5EFE7 100%) !important;
#         color: #1A1A1A !important;
#     }
#
#     [data-testid="stSidebar"] {
#         background: #F5EFE7 !important;
#     }
#
#     [data-testid="stHeader"] {
#         background: transparent !important;
#     }
#
#     /* --- Button Styling --- */
#     button[kind="primary"], div[data-testid="stFormSubmitButton"] button {
#         background-color: #C17D5A !important;
#         color: white !important;
#         border: 1.5px solid #1A1A1A !important;
#         font-weight: 600 !important;
#         transition: all 0.3s ease !important;
#     }
#
#     /* Hover effect: text turns white */
#     button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] button:hover {
#         background-color: #F8EFE2 !important;
#         color: #FFFFFF !important;
#     }
#
#         /* Remove autofill blue background */
#     input:-webkit-autofill,
#     input:-webkit-autofill:hover,
#     input:-webkit-autofill:focus,
#     input:-webkit-autofill:active {
#         transition: background-color 9999s ease-in-out 0s !important;
#         -webkit-text-fill-color: #1A1A1A !important;
#         box-shadow: 0 0 0px 1000px #FBF8F3 inset !important;
#         caret-color: #1A1A1A !important;
#     }
#
#     /* Apply to all text inputs for uniform look */
#     input, textarea, select {
#         background-color: #FBF8F3 !important;
#         color: #1A1A1A !important;
#         border: 1px solid vlack !important;
#         font-family: 'Cinzel Decorative', serif !important;
#         transition: all 0.3s ease !important;
#     }
#
#     /* Focus effect: subtle gold outline */
#     input:focus, textarea:focus, select:focus {
#         outline: none !important;
#         border-color: #C17D5A !important;
#         box-shadow: 0 0 5px #C8A951 !important;
#     }
#
#      div[data-testid="stForm"] {
#         background: #F8EFE4 !important; /* soft warm ivory tone */
#         border: 1px solid #DCCFC1 !important;
#         border-radius: 15px !important;
#         padding: 2rem !important;
#         box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important;
#     }
#
#      /* --- Selectbox specific styling (dropdown) --- */
#         div[data-baseweb="select"] > div {
#             background-color: #FBF8F3 !important;
#             color: #1A1A1A !important;
#             font-family: 'Cinzel Decorative', serif !important;
#             transition: all 0.3s ease !important;
#         }
#
#         div[data-baseweb="select"]:focus-within > div {
#             outline: 3px solid #C17D5A !important;
#             border-color: #C17D5A !important;
#             box-shadow: 0 0 5px #C8A951 !important;
#         }
#
#         div[data-baseweb="select"] svg {
#             color: #1A1A1A !important;
#         }
#
#
#     /* --- LABELS --- */
#     label, p, legend {
#         font-weight: 700 !important;
#         color: #2C2A27 !important;
#         font-family: 'Cinzel Decorative', serif !important;
#         letter-spacing: 0.5px !important;
#     }
#
#     </style>
# """, unsafe_allow_html=True)

st.markdown(
    """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .st-emotion-cache-14vh5up{
            visibility: hidden;
            }
            ._profilePreview_gzau3_63{
            visibility: hidden;}
            ._link_gzau3_10{
            visibility: hidden;}
        </style>
            """
    , unsafe_allow_html=True)
pkt = pytz.timezone('Asia/Karachi')
now_pkt = datetime.now(pkt)
NOTION_API_KEY = st.secrets.get("NOTION_TOKEN", "")
DATABASE_ID = st.secrets.get("DATABASE_ID", "")
DATASOURCE_ID = st.secrets.get("DATASOURCE_ID", "")
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")
if NOTION_API_KEY and DATABASE_ID:
    notion = Client(auth=NOTION_API_KEY)
else:
    st.error("⚠️ Please configure Notion API credentials in secrets")
    st.stop()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔑 Cafe 1947 Booking System Login")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.success("Login successful! 🎉")
            time.sleep(2)
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


@st.cache_data(ttl=120)
def get_bookings():
    rides = []
    has_more = True
    start_cursor = None

    while has_more:
        # Fetch data from Notion (using pagination if needed)
        if start_cursor:
            data = notion.data_sources.query(
                data_source_id=DATASOURCE_ID,
                start_cursor=start_cursor
            )
        else:
            data = notion.data_sources.query(data_source_id=DATASOURCE_ID)

        for row in data["results"]:
            props = row.get("properties", {})

            name = (
                props.get("Name", {}).get("title", [{}])[0].get("plain_text", "")
                if props.get("Name", {}).get("title")
                else ""
            )
            email = props.get("Email", {}).get("email", "")
            phone = props.get("Phone", {}).get("phone_number", "")
            date = props.get("Date", {}).get("date", {}).get("start", "")
            time = (
                props.get("Time", {}).get("rich_text", [{}])[0].get("plain_text", "")
                if props.get("Time", {}).get("rich_text")
                else ""
            )
            guests = props.get("Guests", {}).get("number", "")
            notes = (
                props.get("Notes", {}).get("rich_text", [{}])[0].get("plain_text", "")
                if props.get("Notes", {}).get("rich_text")
                else ""
            )

            rides.append({
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Date": date,
                "Time": time,
                "Guests": guests,
                "Notes": notes
            })

        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

    return rides


bookings = get_bookings()

if bookings:
    booking_df = pd.DataFrame(bookings)
    booking_df["Date"] = pd.to_datetime(booking_df["Date"], errors="coerce")
    booking_df["month"] = booking_df["Date"].dt.strftime("%B")
    booking_df["year"] = booking_df["Date"].dt.year
    booking_df = booking_df.sort_values(by="Date", ascending=True)
    booking_df["Date"] = booking_df["Date"].dt.strftime("%d-%B-%Y")
    booking_df.index = range(1, len(booking_df) + 1)

    unique_years = sorted(booking_df["year"].dropna().unique(), reverse=True)
    unique_months = sorted(booking_df["month"].dropna().unique())

    current_month = datetime.now(pkt).strftime("%B")
    current_year = datetime.now(pkt).year

    view = st.radio(
        "Select View",
        ["📅 By Month", "📋 All Data", "📊 Summary", "❌ Delete"],
        horizontal=True
    )

    if view == "📋 All Data":
        st.subheader("All Booking Data")
        st.dataframe(booking_df)

    elif view == "📅 By Month":
        st.subheader("Filter by Month and Year")

        months = ["All"] + unique_months
        default_month_idx = unique_months.index(current_month) + 1 if current_month in unique_months else 0
        selected_month = st.selectbox("Select Month", months, index=default_month_idx)

        selected_year = st.number_input("Select Year", value=current_year, min_value=2025, max_value=current_year)

        if selected_month == "All":
            filtered_df = booking_df[booking_df["year"] == selected_year]
        else:
            filtered_df = booking_df[(booking_df["year"] == selected_year) & (booking_df["month"] == selected_month)]

        st.write(filtered_df)

        total_guests = filtered_df["Guests"].sum() if not filtered_df.empty else 0
        avg_guests = filtered_df["Guests"].mean() if not filtered_df.empty else 0

        st.metric("👥 Total Guests", f"{total_guests}")
        st.metric("👤 Average Guests per Booking", f"{avg_guests:.2f}")

    elif view == "📊 Summary":
        st.subheader("Overall Summary")
        total_guests = booking_df["Guests"].sum()
        avg_guests = booking_df["Guests"].mean()

        st.metric("👥 Total Guests (All Time)", f"{total_guests}")
        st.metric("👤 Average Guests per Booking", f"{avg_guests:.2f}")

        month_totals = booking_df.groupby(["year", "month"])["Guests"].sum().reset_index()
        st.bar_chart(month_totals.set_index("month"))

    elif view == "❌ Delete":
        st.subheader("Delete Bookings by Month/Year")

        months = ["All"] + unique_months
        default_month_idx = unique_months.index(current_month) + 1 if current_month in unique_months else 0
        selected_month = st.selectbox("Select Month", months, index=default_month_idx, key="delete_box")
        selected_year = st.number_input("Select Year", value=current_year, min_value=2025, max_value=current_year)

        booking_df["Date_dt"] = pd.to_datetime(booking_df["Date"], errors="coerce")
        if selected_month == "All":
            filtered_df = booking_df[booking_df["year"] == selected_year]
        else:
            filtered_df = booking_df[(booking_df["year"] == selected_year) & (booking_df["month"] == selected_month)]

        if filtered_df.empty:
            st.info("No bookings found for the selected filters.")
        else:
            for idx, (_, booking) in enumerate(filtered_df.iterrows(), start=1):
                with st.expander(
                        f"{booking['Date']} @ {booking['Time']} | {booking['Guests']} Guests | {booking['Name']} | {booking["Email"]}"):
                    if st.button("🗑 Delete Booking", key=f"delete_{idx}"):
                        try:

                            st.success(f"Deleted booking from {booking['Date']} @ {booking['Time']}")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting booking: {e}")

    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.success("Logged out successfully! 👋")
        time.sleep(2)
        st.rerun()

else:
    st.info("❌ No bookings recorded yet.")
