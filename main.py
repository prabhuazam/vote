import streamlit as st
import re
import pandas as pd
import os
from datetime import datetime

# Constants
PARTIES = ['Party A', 'Party B']
POSITIONS = ['president', 'vice president', 'secretary', 'joint secretary', 'treasurer', 'event organiser', 'sports']
CANDIDATES = {pos: {party: f"{party} Candidate for {pos}" for party in PARTIES} for pos in POSITIONS}
PASSWORD = "AllInOne"
RESULTS_FILE = "election_results.csv"

# Predefined results as requested
PREDEFINED_RESULTS = {
    'president': {'Party A': 68, 'Party B': 32},
    'vice president': {'Party A': 35, 'Party B': 65},
    'secretary': {'Party A': 54, 'Party B': 46},
    'joint secretary': {'Party A': 63, 'Party B': 37},
    'treasurer': {'Party A': 71, 'Party B': 29},
    'event organiser': {'Party A': 34, 'Party B': 66},
    'sports': {'Party A': 51, 'Party B': 49}
}

# Initialize session state with proper checks
if 'votes' not in st.session_state:
    st.session_state.votes = []
if 'voted_usns' not in st.session_state:
    st.session_state.voted_usns = set()
if 'vote_submitted' not in st.session_state:
    st.session_state.vote_submitted = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Voting"
if 'usn_input_key' not in st.session_state:
    st.session_state.usn_input_key = 0

def reset_voting_form():
    """Reset the voting form and clear USN input"""
    st.session_state.vote_submitted = False
    st.session_state.usn_input_key += 1

def save_results_to_csv(total_votes):
    """Save election results to CSV file"""
    try:
        results_data = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for pos in POSITIONS:
            party_a_percent = PREDEFINED_RESULTS[pos]['Party A']
            party_b_percent = PREDEFINED_RESULTS[pos]['Party B']
            winner = 'Party A' if party_a_percent > party_b_percent else 'Party B'
            
            # Calculate theoretical vote counts based on total votes
            if total_votes > 0:
                party_a_votes = int(round(total_votes * party_a_percent / 100))
                party_b_votes = total_votes - party_a_votes
            else:
                party_a_votes = 0
                party_b_votes = 0
            
            results_data.append({
                'timestamp': timestamp,
                'position': pos.capitalize(),
                'total_votes': total_votes,
                'party_a_votes': party_a_votes,
                'party_b_votes': party_b_votes,
                'winner': winner
            })
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(results_data)
        
        # Check if file exists to determine whether to write header
        file_exists = os.path.isfile(RESULTS_FILE)
        
        # Save to CSV (append if file exists, otherwise create new)
        if file_exists:
            df.to_csv(RESULTS_FILE, mode='a', header=False, index=False)
        else:
            df.to_csv(RESULTS_FILE, mode='w', header=True, index=False)
        
        return df
    except Exception as e:
        st.error(f"Error saving results to CSV: {e}")
        return None

def load_results_from_csv():
    """Load and display results from CSV file"""
    try:
        if os.path.isfile(RESULTS_FILE):
            df = pd.read_csv(RESULTS_FILE)
            return df
        else:
            return None
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

def get_latest_results():
    """Get the latest results from CSV file"""
    try:
        if os.path.isfile(RESULTS_FILE):
            df = pd.read_csv(RESULTS_FILE)
            if df.empty:
                return None
            
            # Get the latest timestamp
            latest_timestamp = df['timestamp'].max()
            
            # Filter for the latest results
            latest_results = df[df['timestamp'] == latest_timestamp]
            
            return latest_results
        else:
            return None
    except Exception as e:
        st.error(f"Error loading latest results: {e}")
        return None

def display_voting_page():
    """Display the main voting page"""
    st.header("Cast Your Vote")
    
    # USN Input and Validation with dynamic key to allow reset
    usn = st.text_input("Enter your USN (e.g., 4JN24MC001):", key=f"usn_{st.session_state.usn_input_key}")

    if st.session_state.vote_submitted:
        st.success("✅ Your vote has been submitted successfully!")
        if st.button("Submit Another Vote"):
            reset_voting_form()
            st.rerun()
    else:
        if usn:
            if not re.match(r'4JN24MC\d{3}', usn):
                st.error("Invalid USN format. Must be 4JN24MC followed by 3 digits.")
            else:
                num = int(usn[8:])
                if not (1 <= num <= 120):
                    st.error("USN number must be between 001 and 120.")
                elif usn in st.session_state.voted_usns:
                    st.error("You have already voted.")
                else:
                    st.success("USN validated. Proceed to vote.")

                    # Voting Form
                    with st.form("voting_form"):
                        st.subheader("Vote for each position:")
                        selections = {}
                        for pos in POSITIONS:
                            st.write(f"**{pos.capitalize()}:**")
                            options = [CANDIDATES[pos][party] for party in PARTIES]
                            selections[pos] = st.radio(f"Select candidate for {pos}:", options, key=f"vote_{pos}")
                        
                        submitted = st.form_submit_button("Submit Vote")
                        if submitted:
                            # Record vote
                            vote = {pos: selections[pos] for pos in POSITIONS}
                            st.session_state.votes.append(vote)
                            st.session_state.voted_usns.add(usn)
                            st.session_state.vote_submitted = True
                            
                            # Save results to CSV after voting
                            total_votes = len(st.session_state.votes)
                            save_results_to_csv(total_votes)
                            st.rerun()

    # Display voting instructions
    st.markdown("""
    ### Voting Instructions:
    1. Enter your USN in the format: 4JN24MC001 to 4JN24MC120
    2. Select your preferred candidate for each position
    3. Click 'Submit Vote' to cast your vote
    4. Each USN can vote only once
    """)

def display_results_page():
    """Display the results page - now fetches from CSV"""
    st.header("Election Results")
    
    result_password = st.text_input("Enter password to view results:", type="password", key="results_pw")
    
    if result_password == PASSWORD:
        st.success("Access granted.")
        
        # Load latest results from CSV
        latest_results = get_latest_results()
        
        if latest_results is None or latest_results.empty:
            st.warning("No results available in the system.")
            st.info("Results will appear here after votes have been cast and saved.")
        else:
            # Display total votes from the latest results
            total_votes = latest_results['total_votes'].iloc[0]
            st.write(f"**Total votes cast: {total_votes}**")
            st.write("---")
            
            # Display results for each position from CSV data
            for pos in POSITIONS:
                pos_results = latest_results[latest_results['position'] == pos.capitalize()]
                
                if not pos_results.empty:
                    st.subheader(f"Results for {pos.capitalize()}:")
                    
                    party_a_votes = pos_results['party_a_votes'].iloc[0]
                    party_b_votes = pos_results['party_b_votes'].iloc[0]
                    winner = pos_results['winner'].iloc[0]
                    
                    # Display results in a clean format
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            label="Party A Votes",
                            value=party_a_votes
                        )
                    with col2:
                        st.metric(
                            label="Party B Votes",
                            value=party_b_votes
                        )
                    
                    st.write(f"**Winner: {winner}**")
                    st.write("---")
        
        # Admin Actions Section
        st.subheader("Admin Actions")
        
        # Display full CSV Results history
        st.write("### All Results History")
        csv_results = load_results_from_csv()
        if csv_results is not None:
            st.dataframe(csv_results)
            
            # Download CSV button
            csv_data = csv_results.to_csv(index=False)
            st.download_button(
                label="Download Results CSV",
                data=csv_data,
                file_name="election_results.csv",
                mime="text/csv"
            )
        else:
            st.write("No results data available in CSV.")
        
        # Manual results update button
        st.write("### Update Results")
        if st.button("Update Results with Current Votes"):
            total_votes = len(st.session_state.votes)
            if total_votes > 0:
                results_df = save_results_to_csv(total_votes)
                if results_df is not None:
                    st.success(f"Results updated and saved to {RESULTS_FILE}")
                    st.rerun()
            else:
                st.warning("No votes to save. Cast some votes first.")
        
        delete_password = st.text_input("Enter password to delete all votes:", type="password", key="delete_pw")
        if delete_password == PASSWORD:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Delete All Votes"):
                    st.session_state.votes = []
                    st.session_state.voted_usns = set()
                    st.session_state.vote_submitted = False
                    st.success("All votes have been deleted.")
                    st.rerun()
            with col2:
                if st.button("Delete CSV File"):
                    try:
                        if os.path.isfile(RESULTS_FILE):
                            os.remove(RESULTS_FILE)
                            st.success("CSV file deleted.")
                            st.rerun()
                        else:
                            st.error("CSV file not found.")
                    except Exception as e:
                        st.error(f"Error deleting CSV: {e}")
        elif delete_password:
            st.error("Incorrect password for deletion.")
    else:
        if result_password:
            st.error("Incorrect password. Access denied.")

# Main App
st.title("College Voting System")

# Navigation - Fixed to work better with Streamlit Cloud
page = st.radio(
    "Navigate to:",
    ["Voting Page", "Results Page"],
    index=0 if st.session_state.current_page == "Voting" else 1,
    horizontal=True
)

# Update current page based on selection
if page == "Voting Page" and st.session_state.current_page != "Voting":
    st.session_state.current_page = "Voting"
    st.rerun()
elif page == "Results Page" and st.session_state.current_page != "Results":
    st.session_state.current_page = "Results"
    st.rerun()

st.markdown("---")

# Display current page
if st.session_state.current_page == "Voting":
    display_voting_page()
else:
    display_results_page()

# Sidebar for general info
with st.sidebar:
    st.header("Election Info")
    st.write(f"**Current Votes Cast:** {len(st.session_state.votes)}")
    st.write(f"**Current Page:** {st.session_state.current_page}")
    
    # Display note about disabled media position
    st.info("Note: Media position voting has been disabled for this election.")
    
    st.markdown("---")
    st.markdown("### Positions Available:")
    for pos in POSITIONS:
        st.write(f"• {pos.title()}")
