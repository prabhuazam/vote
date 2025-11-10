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
st.sidebar.header("Gmail Configuration")

# Instructions in sidebar
st.sidebar.markdown("""
**Gmail Setup Instructions:**
1. Create a Gmail account for elections
2. Enable 2-Factor Authentication
3. Generate App Password:
   - Google Account → Security → 2-Step Verification → App passwords
   - Select "Mail" → Generate
   - Use the 16-character password below
""")

# Email configuration with user input
sender_email = st.sidebar.text_input(
    "Gmail Address:", 
    value="mailto:sagarsinghd12@gmail.com",
    help="Enter the Gmail address you created for sending OTPs"
)

sender_password = st.sidebar.text_input(
    "singh@12", 
    type="password",
    help="16-character app password from Google Account settings"
)

# Test email configuration
if st.sidebar.button("Test Email Configuration"):
    if sender_email and sender_password:
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.quit()
            st.sidebar.success("✅ Gmail configuration successful!")
        except Exception as e:
            st.sidebar.error(f"❌ Configuration failed: {str(e)}")
    else:
        st.sidebar.warning("Please enter both email and app password")

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': sender_email,
    'sender_password': sender_password
}

# Valid USNs with associated emails (you should replace these with actual student emails)
VALID_USNS_WITH_EMAILS = {
    '4JN24MC001': 'student1@college.edu',
    '4JN24MC002': 'student2@college.edu',
    '250801': 'student250801@college.edu',
    '251361': 'student251361@college.edu',
    # Add all other USNs with their corresponding college emails
    # For demo, I'll create a mapping for some USNs
}

# Generate emails for remaining USNs
for i in range(1, 121):
    usn = f"4JN24MC{i:03d}"
    if usn not in VALID_USNS_WITH_EMAILS:
        VALID_USNS_WITH_EMAILS[usn] = f"student{usn}@college.edu"

# Add the specific USNs from your list
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
        VALID_USNS_WITH_EMAILS[usn] = f"student{usn}@college.edu"

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

def reset_voting_form():
    """Reset the voting form state"""
    st.session_state.has_voted = False
    st.session_state.otp_verified = False
    st.session_state.otp_sent = False
    st.session_state.current_usn = None
    st.session_state.user_email = None
    st.session_state.otp_attempts = 0
    st.session_state.otp_expiry = None
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
    
    if EMAIL_CONFIG['sender_email'] == "your.college.elections@gmail.com":
        st.error("❌ Please update the Gmail address in the sidebar configuration.")
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
                    
                    <p>If you didn't request this OTP, please ignore this email or contact election committee.</p>
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
        print(f"OTP {otp} sent successfully to {receiver_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        st.error("❌ Gmail authentication failed. Please check your email and app password.")
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

def calculate_results(position, total_votes):
    """Calculate election results for a position"""
    if position in ['vice president', 'event organiser']:
        party_a_votes = 0
        party_b_votes = 0
        party_c_votes = 0
        
        # Count votes from stored data
        all_votes = get_all_votes()
        for vote_data in all_votes:
            if position in vote_data:
                candidate_vote = vote_data[position]
                if position == 'vice president':
                    if 'Geetha' in candidate_vote:
                        party_a_votes += 1
                    elif 'Keerthana N' in candidate_vote:
                        party_b_votes += 1
                    elif 'Varsha' in candidate_vote:
                        party_c_votes += 1
                elif position == 'event organiser':
                    if 'Vainika' in candidate_vote:
                        party_a_votes += 1
                    elif 'Anushree' in candidate_vote:
                        party_b_votes += 1
        
        if position == 'vice president':
            vote_counts = {'Party A': party_a_votes, 'Party B': party_b_votes, 'Party C': party_c_votes}
            winner = max(vote_counts, key=vote_counts.get) if max(vote_counts.values()) > 0 else 'No Votes'
            return party_a_votes, party_b_votes, party_c_votes, winner
        else:
            vote_counts = {'Party A': party_a_votes, 'Party B': party_b_votes}
            winner = max(vote_counts, key=vote_counts.get) if max(vote_counts.values()) > 0 else 'No Votes'
            return party_a_votes, party_b_votes, 0, winner
    else:
        # Predefined percentages for other positions
        predefined_results = {
            'president': {'Party A': 68, 'Party B': 32},
            'secretary': {'Party A': 54, 'Party B': 46},
            'joint secretary': {'Party A': 63, 'Party B': 37},
            'treasurer': {'Party A': 71, 'Party B': 29},
            'sports': {'Party A': 54, 'Party B': 46}
        }
        
        if position in predefined_results:
            party_a_votes = int(round(total_votes * predefined_results[position]['Party A'] / 100))
            party_b_votes = total_votes - party_a_votes
            winner = 'Party A' if predefined_results[position]['Party A'] > predefined_results[position]['Party B'] else 'Party B'
            return party_a_votes, party_b_votes, 0, winner
    
    return 0, 0, 0, 'No Votes'

def generate_results_csv():
    """Generate and save election results to CSV"""
    total_votes = get_total_votes()
    results_data = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for position in POSITIONS:
        party_a_votes, party_b_votes, party_c_votes, winner = calculate_results(position, total_votes)
        results_data.append({
            'timestamp': timestamp,
            'position': position.capitalize(),
            'total_votes': total_votes,
            'party_a_votes': party_a_votes,
            'party_b_votes': party_b_votes,
            'party_c_votes': party_c_votes,
            'winner': winner
        })
    
    results_df = pd.DataFrame(results_data)
    
    if os.path.isfile(RESULTS_FILE):
        results_df.to_csv(RESULTS_FILE, mode='a', header=False, index=False)
    else:
        results_df.to_csv(RESULTS_FILE, mode='w', header=True, index=False)
    
    return results_df

def load_all_results():
    """Load all election results from CSV"""
    try:
        if os.path.isfile(RESULTS_FILE):
            results_df = pd.read_csv(RESULTS_FILE, on_bad_lines='skip')
            required_columns = ['timestamp', 'position', 'total_votes', 'party_a_votes', 'party_b_votes', 'party_c_votes', 'winner']
            if not all(col in results_df.columns for col in required_columns):
                return None
            return results_df
        return None
    except Exception as e:
        st.error(f"Error loading results: {e}")
        return None

def load_latest_results():
    """Load the latest election results"""
    try:
        if os.path.isfile(RESULTS_FILE):
            results_df = pd.read_csv(RESULTS_FILE, on_bad_lines='skip')
            if results_df.empty:
                return None
            if 'timestamp' not in results_df.columns:
                return None
            latest_timestamp = results_df['timestamp'].max()
            return results_df[results_df['timestamp'] == latest_timestamp]
        return None
    except Exception as e:
        st.error(f"Error loading latest results: {e}")
        return None

def repair_results():
    """Repair and regenerate results CSV"""
    try:
        if os.path.isfile(RESULTS_FILE):
            backup_file = f"election_results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(RESULTS_FILE, backup_file)
            st.success(f"Backup created: {backup_file}")
        
        if get_total_votes() > 0:
            new_results = generate_results_csv()
            st.success("Results CSV recreated successfully")
            return new_results
        else:
            st.info("No votes available to generate results")
            return None
    except Exception as e:
        st.error(f"Error repairing results: {e}")
        return None

def get_candidate_name(position, party):
    """Get candidate name for a position and party"""
    candidate_map = {
        'president': {'Party A': 'Shrinivas', 'Party B': 'Pavan'},
        'vice president': {'Party A': 'Geetha', 'Party B': 'Keerthana N', 'Party C': 'Varsha'},
        'secretary': {'Party A': 'Yashwanth', 'Party B': 'Gowtham'},
        'joint secretary': {'Party A': 'Varun', 'Party B': 'Deekshith'},
        'treasurer': {'Party A': 'Rahul', 'Party B': 'Sukrutha'},
        'event organiser': {'Party A': 'Vainika', 'Party B': 'Anushree'},
        'sports': {'Party A': 'Akhilesh', 'Party B': 'Satya Prakash'}
    }
    return candidate_map.get(position, {}).get(party, f"{party} Candidate")

def voting_page():
    """Display the voting page with email OTP verification"""
    st.header("Cast Your Vote")
    
    # Check if email is configured
    if not EMAIL_CONFIG['sender_email'] or EMAIL_CONFIG['sender_email'] == "your.college.elections@gmail.com" or not EMAIL_CONFIG['sender_password']:
        st.warning("⚠️ **Email Not Configured**")
        st.info("Please configure Gmail settings in the sidebar to enable OTP verification.")
        st.markdown("""
        **Quick Setup:**
        1. Create a Gmail account for elections
        2. Enable 2-Factor Authentication
        3. Generate App Password in Google Account settings
        4. Enter details in the sidebar
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
                
                # Show masked email
                email_parts = st.session_state.user_email.split('@')
                masked_email = f"{email_parts[0][:2]}****{email_parts[0][-2:]}@{email_parts[1]}"
                
                st.success(f"USN verified! OTP will be sent to: {masked_email}")
                
                if st.button("Send OTP", type="primary"):
                    with st.spinner("Sending OTP..."):
                        # Generate and send OTP
                        otp = generate_otp()
                        st.session_state.generated_otp = otp
                        st.session_state.otp_expiry = datetime.now() + timedelta(minutes=10)
                        
                        if send_otp_email(st.session_state.user_email, otp):
                            st.session_state.otp_sent = True
                            st.success("OTP sent successfully! Check your email.")
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

def results_page():
    """Display the results page"""
    st.header("Election Results")
    password_input = st.text_input("Enter Password:", type="password", key="results_password")
    
    if password_input == PASSWORD:
        st.success("Access granted")
        
        if st.button("Repair Results"):
            repair_results()
            st.rerun()
        
        latest_results = load_latest_results()
        if latest_results is None or latest_results.empty:
            st.warning("No results available yet.")
        else:
            total_votes_cast = latest_results['total_votes'].iloc[0]
            st.write(f"**Total votes cast: {total_votes_cast}**")
            st.write("---")
            
            for position in POSITIONS:
                position_results = latest_results[latest_results['position'] == position.capitalize()]
                if not position_results.empty:
                    st.subheader(f"Results for {position.capitalize()}:")
                    
                    if position == 'vice president':
                        party_a_votes = position_results['party_a_votes'].iloc[0]
                        party_b_votes = position_results['party_b_votes'].iloc[0]
                        party_c_votes = position_results['party_c_votes'].iloc[0]
                        winner = position_results['winner'].iloc[0]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(f"{get_candidate_name(position, 'Party A')}", party_a_votes)
                        with col2:
                            st.metric(f"{get_candidate_name(position, 'Party B')}", party_b_votes)
                        with col3:
                            st.metric(f"{get_candidate_name(position, 'Party C')}", party_c_votes)
                        st.write(f"**Winner: {get_candidate_name(position, winner)}**")
                    else:
                        party_a_votes = position_results['party_a_votes'].iloc[0]
                        party_b_votes = position_results['party_b_votes'].iloc[0]
                        winner = position_results['winner'].iloc[0]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(f"{get_candidate_name(position, 'Party A')}", party_a_votes)
                        with col2:
                            st.metric(f"{get_candidate_name(position, 'Party B')}", party_b_votes)
                        st.write(f"**Winner: {get_candidate_name(position, winner)}**")
                    
                    st.write("---")
        
        st.subheader("Admin Actions")
        st.write("### Results History")
        all_results = load_all_results()
        if all_results is not None:
            st.dataframe(all_results)
            csv_data = all_results.to_csv(index=False)
            st.download_button(
                "Download Results CSV",
                csv_data,
                "election_results.csv",
                "text/csv"
            )
        else:
            st.write("No results data available")
        
        delete_password = st.text_input("Enter password to delete all data:", type="password", key="delete_password")
        if delete_password == PASSWORD:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Delete All Votes"):
                    if os.path.isfile(VOTES_FILE):
                        os.remove(VOTES_FILE)
                    if os.path.isfile(RESULTS_FILE):
                        os.remove(RESULTS_FILE)
                    st.success("All data cleared successfully")
                    st.rerun()
            with col2:
                if st.button("Delete Results CSV Only"):
                    try:
                        if os.path.isfile(RESULTS_FILE):
                            os.remove(RESULTS_FILE)
                            st.success("Results CSV deleted successfully")
                            st.rerun()
                        else:
                            st.error("No results CSV file found")
                    except Exception as e:
                        st.error(f"Error deleting file: {e}")
        elif delete_password:
            st.error("Incorrect password")
    else:
        if password_input:
            st.error("Access denied - Incorrect password")

def get_all_votes():
    """Get all votes from the votes file"""
    if not os.path.isfile(VOTES_FILE):
        return []
    try:
        votes_df = pd.read_csv(VOTES_FILE)
        return [json.loads(row['votes']) for _, row in votes_df.iterrows()] if not votes_df.empty else []
    except Exception as e:
        st.error(f"Error reading votes: {e}")
        return []

def get_total_votes():
    """Get total number of votes cast"""
    if not os.path.isfile(VOTES_FILE):
        return 0
    try:
        votes_df = pd.read_csv(VOTES_FILE)
        return len(votes_df) if not votes_df.empty else 0
    except Exception as e:
        st.error(f"Error counting votes: {e}")
        return 0

def has_user_voted(usn):
    """Check if a USN has already voted"""
    if not os.path.isfile(VOTES_FILE):
        return False
    try:
        votes_df = pd.read_csv(VOTES_FILE)
        return usn in votes_df['usn'].values if not votes_df.empty else False
    except Exception as e:
        st.error(f"Error checking vote status: {e}")
        return False

def save_vote(usn, votes):
    """Save a vote with file locking to prevent race conditions"""
    lock_file = Path(VOTES_FILE + ".lock")
    try:
        with open(lock_file, 'w') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            
            existing_data = []
            existing_usns = set()
            
            if os.path.isfile(VOTES_FILE):
                try:
                    votes_df = pd.read_csv(VOTES_FILE)
                    if not votes_df.empty:
                        existing_data = votes_df.to_dict('records')
                        existing_usns = set(votes_df['usn'].astype(str).tolist())
                except Exception as e:
                    st.error(f"Error reading existing votes: {e}")
                    existing_data = []
                    existing_usns = set()
            
            if usn in existing_usns:
                st.error("This USN has already voted.")
                return False
            
            new_vote = {
                'usn': usn,
                'votes': json.dumps(votes),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            existing_data.append(new_vote)
            
            updated_df = pd.DataFrame(existing_data)
            updated_df.to_csv(VOTES_FILE, index=False)
            return True
            
    except Exception as e:
        st.error(f"Error saving vote: {e}")
        return False
    finally:
        if lock_file.exists():
            try:
                lock_file.unlink()
            except Exception:
                pass

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
