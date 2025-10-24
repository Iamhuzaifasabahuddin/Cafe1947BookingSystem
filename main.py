import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytz
import streamlit as st
from notion_client import Client

st.set_page_config(page_title="Cafe Reservations", page_icon="☕", layout="centered")

st.markdown("""
    <style>
    
    /* Existing styling you already have */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&display=swap');


    html, body, [class*="stApp"] {
        font-family: 'Cinzel Decorative', serif !important;
        background: linear-gradient(135deg, #FBF8F3 0%, #F5EFE7 100%) !important;
        color: #1A1A1A !important;
    }

    [data-testid="stSidebar"] {
        background: #F5EFE7 !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* --- Button Styling --- */
    button[kind="primary"], div[data-testid="stFormSubmitButton"] button {
        background-color: #C17D5A !important;
        color: white !important;
        border: 1.5px solid #1A1A1A !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    /* Hover effect: text turns white */
    button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #F8EFE2 !important;
        color: #FFFFFF !important;
    }
    
        /* Remove autofill blue background */
    input:-webkit-autofill,
    input:-webkit-autofill:hover,
    input:-webkit-autofill:focus,
    input:-webkit-autofill:active {
        transition: background-color 9999s ease-in-out 0s !important;
        -webkit-text-fill-color: #1A1A1A !important;
        box-shadow: 0 0 0px 1000px #FBF8F3 inset !important;
        caret-color: #1A1A1A !important;
    }

    /* Apply to all text inputs for uniform look */
    input, textarea, select {
        background-color: #FBF8F3 !important;
        color: #1A1A1A !important;
        border: 1px solid vlack !important;
        font-family: 'Cinzel Decorative', serif !important;
        transition: all 0.3s ease !important;
    }

    /* Focus effect: subtle gold outline */
    input:focus, textarea:focus, select:focus {
        outline: none !important;
        border-color: #C17D5A !important;
        box-shadow: 0 0 5px #C8A951 !important;
    }
    
     div[data-testid="stForm"] {
        background: #F8EFE4 !important; /* soft warm ivory tone */
        border: 1px solid #DCCFC1 !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important;
    }
    
     /* --- Selectbox specific styling (dropdown) --- */
        div[data-baseweb="select"] > div {
            background-color: #FBF8F3 !important;
            color: #1A1A1A !important;
            font-family: 'Cinzel Decorative', serif !important;
            transition: all 0.3s ease !important;
        }

        div[data-baseweb="select"]:focus-within > div {
            outline: 3px solid #C17D5A !important;
            border-color: #C17D5A !important;
            box-shadow: 0 0 5px #C8A951 !important;
        }

        div[data-baseweb="select"] svg {
            color: #1A1A1A !important;
        }


    /* --- LABELS --- */
    label, p, legend {
        font-weight: 700 !important;
        color: #2C2A27 !important;
        font-family: 'Cinzel Decorative', serif !important;
        letter-spacing: 0.5px !important;
    }

    </style>
""", unsafe_allow_html=True)

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

SMTP_SERVER = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = st.secrets.get("SMTP_PORT", 587)
RESTAURANT_EMAIL = st.secrets.get("SENDER_EMAIL", "")
RESTAURANT_PWD = st.secrets.get("SENDER_PASSWORD", "")

if NOTION_API_KEY and DATABASE_ID:
    notion = Client(auth=NOTION_API_KEY)
else:
    st.error("⚠️ Please configure Notion API credentials in secrets")
    st.stop()


def send_email(to_email, subject, body):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = RESTAURANT_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(RESTAURANT_EMAIL, RESTAURANT_PWD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.warning(f"Email notification failed: {str(e)}")
        return False


def send_reservation_emails(name: str, email: str, phone: str, date: str, time: str, guests: int):
    """Send confirmation emails to customer and restaurant"""
    customer_subject = "☕ Reservation Confirmed - Our Cafe"
    customer_body = f"""
        <html>
        <head>
            <link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
        </head>
        <body style="font-family: 'Lato', sans-serif; line-height: 1.6; color: #2C2420; background: #FBF8F3; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; background: #FFFFFF; border: 1px solid #ADB9A0;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #F5EFE7 0%, #FBF8F3 100%); padding: 40px 30px; text-align: center; border-bottom: 2px solid #C17D5A;">
                    <h1 style="font-family: 'Cinzel Decorative', serif; font-size: 32px; font-weight: 400; color: #2C2420; margin: 0 0 10px 0; letter-spacing: 0.05em;">Cafe 1947</h1>
                    <p style="font-style: italic; color: #C17D5A; margin: 0; font-size: 16px;">Your table awaits</p>
                </div>

                <!-- Content -->
                <div style="padding: 40px 30px;">
                    <h2 style="font-family: 'Cinzel Decorative', serif; color: #C17D5A; font-size: 24px; font-weight: 400; margin: 0 0 20px 0;">Reservation Confirmed!</h2>

                    <p style="color: #2C2420; font-size: 16px; margin-bottom: 25px;">Dear {name.title()},</p>

                    <p style="color: #8B9A7B; font-size: 15px; margin-bottom: 30px;">Thank you for choosing Cafe 1947. We're delighted to confirm your reservation.</p>

                    <!-- Reservation Details Box -->
                    <div style="background: linear-gradient(135deg, #F5EFE7 0%, #FBF8F3 100%); border-left: 4px solid #C17D5A; padding: 25px; margin: 30px 0; border-radius: 2px;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; color: #8B9A7B; font-size: 14px; letter-spacing: 0.05em; text-transform: uppercase;">📅 Date</td>
                                <td style="padding: 8px 0; color: #2C2420; font-weight: 600; text-align: right;">{date}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #8B9A7B; font-size: 14px; letter-spacing: 0.05em; text-transform: uppercase;">🕐 Time</td>
                                <td style="padding: 8px 0; color: #2C2420; font-weight: 600; text-align: right;">{time}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #8B9A7B; font-size: 14px; letter-spacing: 0.05em; text-transform: uppercase;">👥 Guests</td>
                                <td style="padding: 8px 0; color: #2C2420; font-weight: 600; text-align: right;">{guests}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #8B9A7B; font-size: 14px; letter-spacing: 0.05em; text-transform: uppercase;">📞 Phone</td>
                                <td style="padding: 8px 0; color: #2C2420; font-weight: 600; text-align: right;">{phone}</td>
                            </tr>
                        </table>
                    </div>

                    <p style="color: #2C2420; font-size: 15px; margin: 25px 0;">We look forward to serving you an exceptional dining experience.</p>

                    <p style="color: #8B9A7B; font-size: 13px; font-style: italic; margin: 25px 0;">If you need to cancel or modify your reservation, please contact us on @ 0319 652 6326 / 0333 317 3698 at your earliest convenience.</p>
                </div>

                <!-- Footer -->
                <div style="background: #2C2420; color: #FBF8F3; padding: 30px; text-align: center;">
                    <p style="font-family: 'Cinzel Decorative', serif; font-size: 18px; margin: 0 0 10px 0;">Cafe 1947</p>
                    <p style="font-size: 13px; color: #ADB9A0; margin: 0; letter-spacing: 0.1em;">WHERE HERITAGE MEETS FLAVOR</p>
                </div>
            </div>
        </body>
        </html>
        """

    restaurant_subject = f"🔔 New Reservation - {name.title()} - {now_pkt.strftime('%d/%B/%Y @ %I:%M %p')}"
    restaurant_body = f"""
        <html>
        <head>
            <link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
        </head>
        <body style="font-family: 'Lato', sans-serif; line-height: 1.6; color: #2C2420; background: #FBF8F3; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; background: #FFFFFF; border: 1px solid #ADB9A0;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #C17D5A 0%, #8B9A7B 100%); padding: 30px; text-align: center;">
                    <h1 style="font-family: 'Cinzel Decorative', serif; font-size: 28px; color: #FBF8F3; margin: 0;">New Reservation Alert</h1>
                    <p style="color: #FBF8F3; font-size: 14px; margin: 10px 0 0 0;">Received: {now_pkt.strftime('%d %B %Y at %I:%M %p PKT')}</p>
                </div>

                <!-- Content -->
                <div style="padding: 40px 30px;">
                    <!-- Alert Box -->
                    <div style="background: #FFF3E0; border-left: 5px solid #C17D5A; padding: 25px; margin: 0 0 30px 0; border-radius: 2px;">
                        <h2 style="font-family: 'Cinzel Decorative', serif; color: #C17D5A; font-size: 20px; margin: 0 0 20px 0;">Reservation Details</h2>

                        <table style="width: 100%; border-collapse: collapse;">
                            <tr style="border-bottom: 1px solid rgba(139, 154, 123, 0.2);">
                                <td style="padding: 12px 0; color: #8B9A7B; font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600;">Customer</td>
                                <td style="padding: 12px 0; color: #2C2420; font-weight: 700; text-align: right; font-size: 16px;">{name.title()}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid rgba(139, 154, 123, 0.2);">
                                <td style="padding: 12px 0; color: #8B9A7B; font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600;">Email</td>
                                <td style="padding: 12px 0; color: #2C2420; text-align: right;">{email}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid rgba(139, 154, 123, 0.2);">
                                <td style="padding: 12px 0; color: #8B9A7B; font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600;">Phone</td>
                                <td style="padding: 12px 0; color: #2C2420; text-align: right; font-weight: 600;">{phone}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid rgba(139, 154, 123, 0.2);">
                                <td style="padding: 12px 0; color: #8B9A7B; font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600;">Date</td>
                                <td style="padding: 12px 0; color: #C17D5A; text-align: right; font-weight: 700; font-size: 16px;">{date}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid rgba(139, 154, 123, 0.2);">
                                <td style="padding: 12px 0; color: #8B9A7B; font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600;">Time</td>
                                <td style="padding: 12px 0; color: #C17D5A; text-align: right; font-weight: 700; font-size: 16px;">{time}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 0; color: #8B9A7B; font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600;">Guests</td>
                                <td style="padding: 12px 0; color: #2C2420; text-align: right; font-weight: 700; font-size: 18px;">{guests}</td>
                            </tr>
                        </table>
                    </div>

                    <div style="background: linear-gradient(135deg, #F5EFE7 0%, #FBF8F3 100%); padding: 20px; text-align: center; border-radius: 2px;">
                        <p style="color: #8B9A7B; font-size: 14px; margin: 0; font-style: italic;">Please prepare the table and ensure a warm welcome for our guest.</p>
                    </div>
                </div>

                <!-- Footer -->
                <div style="background: #2C2420; color: #FBF8F3; padding: 20px; text-align: center;">
                    <p style="font-size: 12px; color: #ADB9A0; margin: 0;">Cafe 1947 Reservation System</p>
                </div>
            </div>
        </body>
        </html>
        """

    customer_sent = send_email(email, customer_subject, customer_body)
    restaurant_sent = send_email(RESTAURANT_EMAIL, restaurant_subject, restaurant_body)

    return customer_sent, restaurant_sent


st.title("☕ Cafe Reservation System")
st.markdown("---")

st.subheader("Book a Table")
st.caption("Fields marked with * are required")

with st.form("reservation_form"):
    name = st.text_input("Name *", placeholder="Your name")
    email = st.text_input("Email *", placeholder="your@email.com")
    phone = st.text_input("Phone Number *", placeholder="03XX-XXXXXXX")

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date *", min_value=now_pkt.date())
    with col2:
        all_times = [
            "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM",
            "4:30 PM", "5:00 PM", "5:30 PM", "6:00 PM", "6:30 PM", "7:00 PM",
            "7:30 PM", "8:00 PM", "8:30 PM", "9:00 PM", "9:30 PM", "10:00 PM",
            "10:30 PM", "11:00 PM"
        ]


        def parse_time_label(label):
            return datetime.strptime(label, "%I:%M %p").time()


        available_times = []

        if date == now_pkt.date():
            for t in all_times:
                slot_time = parse_time_label(t)
                slot_datetime = pkt.localize(datetime.combine(now_pkt.date(), slot_time))
                if slot_datetime > now_pkt:
                    available_times.append(t)
        else:
            available_times = all_times

        time_selected = st.selectbox("Time *", available_times)
        if not available_times:
            st.warning("All time slots for today have passed. Please select a later date.")
            available_times = all_times

    guests = st.number_input("Number of Guests *", min_value=1, max_value=12, value=2)

    notes = st.text_area("Notes (Optional)", placeholder="Enter your notes")
    submitted = st.form_submit_button("Book Now", use_container_width=True)

    if submitted:
        if not name or not email or not phone or not guests:
            st.error("Please fill in all fields")
        else:
            try:
                notes = notes.strip() if notes else ""
                notion.pages.create(
                    parent={"database_id": DATABASE_ID},
                    properties={
                        "Name": {"title": [{"text": {"content": name.title()}}]},
                        "Email": {"email": email},
                        "Phone": {"phone_number": phone},
                        "Date": {"date": {"start": date.isoformat()}},
                        "Time": {"rich_text": [{"text": {"content": time_selected}}]},
                        "Guests": {"number": guests},
                        "Notes": {"rich_text": [{"text": {"content": notes}}]}
                    }
                )
                with st.spinner("Sending confirmation emails..."):
                    customer_sent, restaurant_sent = send_reservation_emails(
                        name, email, phone, date, time_selected, guests
                    )

                st.success(f"✅ Reservation confirmed for {name} on {date} at {time_selected}")

                if customer_sent:
                    st.info(f"📧 Confirmation email sent to {email}")
                if restaurant_sent:
                    st.info(f"📧 Notification sent to restaurant")

                st.balloons()
            except Exception as e:
                st.error(f"Error: {str(e)}")
