import streamlit as st
import re
import pandas as pd
import os
from datetime import datetime

# Constants
PARTIES = ['Party A', 'Party B']
POSITIONS = ['president', 'vice president', 'secretary', 'joint secretary', 'treasurer', 'event organiser', 'sports']  # Removed 'media'
CANDIDATES = {pos: {party: f"{party} Candidate for {pos}" for party in PARTIES} for pos in POSITIONS}
PASSWORD = "AllInOne"  # Set a password for accessing results and deleting votes
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

# Session state for votes and voted USNs
if 'votes' not in st.session_state:
    st.session_state.votes = []
if 'voted_usns' not in st.session_state:
    st.session_state.voted_usns = set()
if 'vote_submitted' not in st.session_state:
    st.session_state.vote_submitted = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Voting"

def reset_voting_form():
    """Reset the voting form and clear USN input"""
    st.session_state.vote_submitted = False
    # Clear the USN input by using a unique key that we can manipulate
    if 'usn_input_key' not in st.session_state:
        st.session_state.usn_input_key = 0
    st.session_state.usn_input_key += 1

def save_results_to_csv(total_votes):
    """Save election results to CSV file"""
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
            'party_a_percentage': party_a_percent,
            'party_b_percentage': party_b_percent,
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

def load_results_from_csv():
    """Load and display results from CSV file"""
    if os.path.isfile(RESULTS_FILE):
        df = pd.read_csv(RESULTS_FILE)
        return df
    else:
        return None

def display_voting_page():
    """Display the main voting page"""
    st.header("Cast Your Vote")
    
    # USN Input and Validation with dynamic key to allow reset
    usn_key = st.session_state.get('usn_input_key', 0)
    usn = st.text_input("Enter your USN (e.g., 4JN24MC001):", key=f"usn_{usn_key}")

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
                            selections[pos] = st.radio(f"Select candidate for {pos}:", options, key=pos)
                        
                        submitted = st.form_submit_button("Submit Vote")
                        if submitted:
                            # Record vote
                            vote = {pos: selections[pos] for pos in POSITIONS}
                            st.session_state.votes.append(vote)
                            st.session_state.voted_usns.add(usn)
                            st.session_state.vote_submitted = True
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
    """Display the results page"""
    st.header("Election Results")
    
    result_password = st.text_input("Enter password to view results:", type="password", key="results_pw")
    
    if result_password == PASSWORD:
        st.success("Access granted.")
        
        total_votes = len(st.session_state.votes)
        st.write(f"**Total votes cast: {total_votes}**")
        st.write("---")
        
        # Show predefined results regardless of actual votes
        for pos in POSITIONS:
            st.subheader(f"Results for {pos.capitalize()}:")
            
            # Use exact predefined percentages
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
            
            # Display results in a clean format without progress bars
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Party A Votes",
                    value=party_a_votes,
                    delta=None
                )
            with col2:
                st.metric(
                    label="Party B Votes",
                    value=party_b_votes,
                    delta=None
                )
            
            st.write(f"**Winner: {winner}**")
            st.write("---")
        
        # Save results to CSV when viewing
        if total_votes > 0:
            results_df = save_results_to_csv(total_votes)
            st.success(f"Results saved to {RESULTS_FILE}")
        
        # Admin Actions Section
        st.subheader("Admin Actions")
        
        # Display CSV Results
        st.write("### CSV Results Data")
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
                    if os.path.isfile(RESULTS_FILE):
                        os.remove(RESULTS_FILE)
                        st.success("CSV file deleted.")
                    else:
                        st.error("CSV file not found.")
        elif delete_password:  # Only show error if something was entered
            st.error("Incorrect password for deletion.")
    else:
        if result_password:  # Only show error if password was entered
            st.error("Incorrect password. Access denied.")

# Main App
st.title("College Voting System")

# Navigation
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Voting Page"):
        st.session_state.current_page = "Voting"
        st.rerun()
with col2:
    if st.button("📊 Results Page"):
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
