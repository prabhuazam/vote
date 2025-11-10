import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import json
import fcntl
from pathlib import Path
import smtplib
import random
import string
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Constants
PARTIES = ['Party A', 'Party B']
POSITIONS = ['president', 'vice president', 'secretary', 'joint secretary', 'treasurer', 'event organiser', 'sports']
VICE_PRESIDENT_PARTIES = ['Party A', 'Party B', 'Party C']

# Candidate configuration
CANDIDATE_CONFIG = {}
for position in POSITIONS:
    if position == 'vice president':
        CANDIDATE_CONFIG[position] = {party: f"{party} Candidate for {position}" for party in VICE_PRESIDENT_PARTIES}
    else:
        CANDIDATE_CONFIG[position] = {party: f"{party} Candidate for {position}" for party in PARTIES}

# App configuration
PASSWORD = "AllInOne"
RESULTS_FILE = "election_results.csv"
VOTES_FILE = "election_votes.csv"

# Gmail Configuration Section
st.sidebar.header("📧 Gmail Configuration")

# Instructions in sidebar
st.sidebar.markdown("""
**Gmail Setup Instructions:**
1. Use your Gmail account (sagarsinghd12@gmail.com)
2. **Enable 2-Factor Authentication** in Google Account
3. **Generate App Password**:
   - Go to Google Account → Security → 2-Step Verification
   - Scroll down to "App passwords"
   - Select "Mail" and "Other" (name: "Election System")
   - Copy the 16-character password
4. Enter the app password below (NOT your Gmail password)
""")

# Email configuration with user input
sender_email = st.sidebar.text_input(
    "Gmail Address:", 
    value="sagarsinghd12@gmail.com",  # Fixed: removed "mailto:"
    help="Enter your Gmail address for sending OTPs"
)

sender_password = st.sidebar.text_input(
    "Gmail App Password:",  # Fixed: proper label
    type="password",
    help="16-character app password from Google Account settings",
    placeholder="Enter your 16-character app password"
)

# Store email config in session state to persist across reruns
if 'email_config' not in st.session_state:
    st.session_state.email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': sender_email,
        'sender_password': sender_password
    }
else:
    # Update with current values
    st.session_state.email_config.update({
        'sender_email': sender_email,
        'sender_password': sender_password
    })

EMAIL_CONFIG = st.session_state.email_config

# Test email configuration
if st.sidebar.button("Test Email Configuration"):
    if sender_email and sender_password:
        try:
            with st.spinner("Testing email configuration..."):
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.quit()
                st.sidebar.success("✅ Gmail configuration successful!")
                st.session_state.email_configured = True
        except smtplib.SMTPAuthenticationError:
            st.sidebar.error("""
            ❌ Authentication failed! 
            
            **Common solutions:**
            1. Make sure 2-Factor Authentication is enabled
            2. Use App Password (16 characters), not your regular password
            3. Check if the app password is generated for "Mail"
            """)
        except Exception as e:
            st.sidebar.error(f"❌ Configuration failed: {str(e)}")
    else:
        st.sidebar.warning("Please enter both email and app password")

# Valid USNs with associated emails - UPDATED WITH REAL TESTING EMAILS
VALID_USNS_WITH_EMAILS = {
    '4JN24MC001': 'sagarsinghd12@gmail.com',  # Using your email for testing
    '4JN24MC002': 'sagarsinghd12@gmail.com',  # Using your email for testing
    '250801': 'sagarsinghd12@gmail.com',
    '251361': 'sagarsinghd12@gmail.com',
}

# Generate emails for remaining USNs - ALL POINTING TO YOUR TEST EMAIL
for i in range(1, 121):
    usn = f"4JN24MC{i:03d}"
    if usn not in VALID_USNS_WITH_EMAILS:
        VALID_USNS_WITH_EMAILS[usn] = 'sagarsinghd12@gmail.com'  # Your email for testing

# Add the specific USNs from your list - ALL POINTING TO YOUR TEST EMAIL
additional_usns = {
    '250801', '251361', '251183', '251348', '251240', '251270', '251281', '251250',
    '251353', '251233', '251301', '251292', '250940', '251277', '251298', '251226',
    '251367', '250950', '251304', '251224', '251282', '251208', '251368', '250771',
    '251227', '251346', '251330', '251255', '251307', '251284', '251285', '250809',
    '251386', '251287', '250760', '250452', '251023', '251359', '251363', '250934',
    '251184', '251383', '251340', '251334', '251388', '251369', '251372', '250395',
    '251236', '251351', '251268', '250821', '251381', '250544', '251365', '250456',
    '251209', '250794', '251274', '251332', '251291', '251220', '251211', '251254',
    '251271', '251175', '251198', '250747', '250350', '251305', '251313', '250341',
    '250740', '251178', '251333', '250306', '251235', '251245', '251201', '251021',
    '251063', '251259', '251294', '251223', '250328', '250339', '251262', '251384',
    '250921', '251273', '251344', '251207', '251257', '251022', '251350', '251265',
    '251230', '251357', '251355', '251385', '251371', '250751', '251366', '251300',
    '251296', '250716', '251035', '251229'
}

for usn in additional_usns:
    if usn not in VALID_USNS_WITH_EMAILS:
        VALID_USNS_WITH_EMAILS[usn] = 'sagarsinghd12@gmail.com'  # Your email for testing

VALID_USNS = set(VALID_USNS_WITH_EMAILS.keys())

# Session state initialization
if 'has_voted' not in st.session_state:
    st.session_state.has_voted = False
if 'page_title' not in st.session_state:
    st.session_state.page_title = "Voting"
if 'form_counter' not in st.session_state:
    st.session_state.form_counter = 0
if 'otp_verified' not in st.session_state:
    st.session_state.otp_verified = False
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False
if 'current_usn' not in st.session_state:
    st.session_state.current_usn = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'otp_attempts' not in st.session_state:
    st.session_state.otp_attempts = 0
if 'otp_expiry' not in st.session_state:
    st.session_state.otp_expiry = None
if 'email_configured' not in st.session_state:
    st.session_state.email_configured = False
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None

def reset_voting_form():
    """Reset the voting form state"""
    st.session_state.has_voted = False
    st.session_state.otp_verified = False
    st.session_state.otp_sent = False
    st.session_state.current_usn = None
    st.session_state.user_email = None
    st.session_state.otp_attempts = 0
    st.session_state.otp_expiry = None
    st.session_state.generated_otp = None
    st.session_state.form_counter += 1

def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(receiver_email, otp):
    """Send OTP to user's email using Gmail"""
    # Check if email is configured
    if not EMAIL_CONFIG['sender_email'] or not EMAIL_CONFIG['sender_password']:
        st.error("❌ Email not configured. Please set up Gmail in the sidebar.")
        return False
    
    try:
        # Create message
        message = MimeMultipart()
        message['From'] = EMAIL_CONFIG['sender_email']
        message['To'] = receiver_email
        message['Subject'] = 'College Election System - OTP Verification'
        
        # Email body with better formatting
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #2563eb; text-align: center; letter-spacing: 8px; margin: 20px 0; padding: 15px; background: white; border: 2px dashed #2563eb; border-radius: 8px; }}
                .warning {{ background: #fef3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 College Election System</h1>
                    <p>Secure Voting Authentication</p>
                </div>
                <div class="content">
                    <h2>OTP Verification Required</h2>
                    <p>Dear Student,</p>
                    <p>Your One-Time Password (OTP) for voting authentication is:</p>
                    <div class="otp-code">{otp}</div>
                    <p>This OTP is valid for <strong>10 minutes</strong>.</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong><br>
                        • Do not share this OTP with anyone<br>
                        • College officials will never ask for your OTP<br>
                        • This OTP is for one-time use only
                    </div>
                    
                    <p>If you didn't request this OTP, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from College Election System.<br>
                    Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        message.attach(MimeText(body, 'html'))
        
        # Create SMTP session with timeout
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'], timeout=30)
        server.starttls()  # Enable security
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        
        # Send email
        text = message.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], receiver_email, text)
        server.quit()
        
        # Log successful send (for debugging)
        st.success(f"✅ OTP sent to {receiver_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        st.error("""
        ❌ Gmail authentication failed! 
        
        **Please check:**
        1. 2-Factor Authentication is enabled
        2. You're using App Password (16 characters), not regular password
        3. App password is generated for "Mail"
        """)
        return False
    except smtplib.SMTPException as e:
        st.error(f"❌ Email sending failed: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return False

def verify_otp(user_otp, stored_otp, expiry_time):
    """Verify the OTP entered by user"""
    if datetime.now() > expiry_time:
        return False, "OTP has expired. Please request a new one."
    
    if user_otp == stored_otp:
        return True, "OTP verified successfully!"
    else:
        return False, "Invalid OTP. Please try again."

# ... (rest of your existing functions remain the same - calculate_results, generate_results_csv, etc.)

def voting_page():
    """Display the voting page with email OTP verification"""
    st.header("Cast Your Vote")
    
    # Check if email is configured
    if not EMAIL_CONFIG['sender_email'] or not EMAIL_CONFIG['sender_password']:
        st.warning("⚠️ **Email Not Configured**")
        st.info("Please configure Gmail settings in the sidebar to enable OTP verification.")
        st.markdown("""
        **Quick Setup for sagarsinghd12@gmail.com:**
        1. Go to Google Account → Security → 2-Step Verification
        2. Enable 2-Factor Authentication
        3. Generate App Password for "Mail"
        4. Enter the 16-character app password in the sidebar
        5. Click 'Test Email Configuration'
        """)
        return
    
    if st.session_state.has_voted:
        st.success("Vote submitted successfully!")
        st.info("You cannot vote again.")
        if st.button("Submit Another Vote"):
            reset_voting_form()
            st.rerun()
        return

    # Step 1: USN Verification
    if not st.session_state.otp_sent:
        st.subheader("Step 1: Verify Your Identity")
        usn_input = st.text_input("Enter USN:", key=f"usn_{st.session_state.form_counter}")
        
        if usn_input:
            usn = usn_input.strip().upper()
            if usn not in VALID_USNS:
                st.error("Invalid USN. Please check your USN and try again.")
            elif has_user_voted(usn):
                st.error("This USN has already voted.")
                st.session_state.has_voted = True
                st.rerun()
            else:
                st.session_state.current_usn = usn
                st.session_state.user_email = VALID_USNS_WITH_EMAILS[usn]
                
                st.success(f"USN verified! OTP will be sent to your email.")
                
                if st.button("Send OTP", type="primary"):
                    with st.spinner("Sending OTP..."):
                        # Generate and send OTP
                        otp = generate_otp()
                        st.session_state.generated_otp = otp
                        st.session_state.otp_expiry = datetime.now() + timedelta(minutes=10)
                        
                        if send_otp_email(st.session_state.user_email, otp):
                            st.session_state.otp_sent = True
                            st.rerun()
                        else:
                            st.error("Failed to send OTP. Please check the configuration and try again.")

    # Step 2: OTP Verification
    elif st.session_state.otp_sent and not st.session_state.otp_verified:
        st.subheader("Step 2: Enter OTP")
        
        # Show OTP expiry timer
        time_remaining = st.session_state.otp_expiry - datetime.now()
        if time_remaining.total_seconds() > 0:
            minutes = int(time_remaining.total_seconds() // 60)
            seconds = int(time_remaining.total_seconds() % 60)
            st.info(f"⏰ OTP expires in: {minutes:02d}:{seconds:02d}")
            
            # Visual progress bar
            progress = time_remaining.total_seconds() / 600  # 10 minutes total
            st.progress(progress)
        else:
            st.error("OTP has expired. Please request a new one.")
            if st.button("Request New OTP"):
                st.session_state.otp_sent = False
                st.rerun()
            return

        otp_input = st.text_input("Enter 6-digit OTP:", max_chars=6, key="otp_input", placeholder="123456")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Verify OTP", type="primary"):
                if otp_input and len(otp_input) == 6:
                    is_valid, message = verify_otp(otp_input, st.session_state.generated_otp, st.session_state.otp_expiry)
                    if is_valid:
                        st.session_state.otp_verified = True
                        st.session_state.otp_attempts = 0
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.session_state.otp_attempts += 1
                        st.error(message)
                        
                        # Limit OTP attempts
                        if st.session_state.otp_attempts >= 3:
                            st.error("🚫 Too many failed attempts. Please request a new OTP.")
                            if st.button("Request New OTP"):
                                st.session_state.otp_sent = False
                                st.session_state.otp_attempts = 0
                                st.rerun()
                else:
                    st.error("Please enter a 6-digit OTP")
        
        with col2:
            if st.button("Request New OTP"):
                st.session_state.otp_sent = False
                st.rerun()

    # Step 3: Voting Form
    elif st.session_state.otp_verified:
        st.subheader("Step 3: Cast Your Vote")
        st.success(f"✅ Identity verified! Welcome, USN: {st.session_state.current_usn}")
        
        with st.form("vote_form"):
            st.subheader("Cast Your Votes:")
            votes = {}
            
            for position in POSITIONS:
                st.write(f"**{position.capitalize()}:**")
                if position == 'vice president':
                    candidates = ["NOTA - None of the Above"] + [f"{get_candidate_name(position, party)}" for party in VICE_PRESIDENT_PARTIES]
                else:
                    candidates = ["NOTA - None of the Above"] + [f"{get_candidate_name(position, party)}" for party in PARTIES]
                
                votes[position] = st.radio(
                    f"Select candidate for {position}:",
                    candidates,
                    key=f"radio_{position}_{st.session_state.form_counter}"
                )
            
            submitted = st.form_submit_button("Submit Vote", type="primary")
            
            if submitted:
                if save_vote(st.session_state.current_usn, votes):
                    st.session_state.has_voted = True
                    generate_results_csv()
                    st.success("🎉 Your vote has been recorded successfully!")
                    st.rerun()

# ... (rest of your existing functions remain exactly the same)

# Main app
def main():
    st.title("🎓 College Election System")
    
    # Navigation
    page = st.sidebar.selectbox("Navigate to:", ["Voting", "Results"])
    
    if page == "Voting":
        voting_page()
    elif page == "Results":
        results_page()

if __name__ == "__main__":
    main()
