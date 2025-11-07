import streamlit as st
import re
import pandas as pd
import os
from datetime import datetime

# Constants
PARTIES = ['Party A', 'Party B']
POSITIONS = ['president', 'vice president', 'secretary', 'joint secretary', 'treasurer', 'event organiser', 'sports']
# Special case for Vice President with 3 parties
VICE_PRESIDENT_PARTIES = ['Party A', 'Party B', 'Party C']
CANDIDATES = {}
for pos in POSITIONS:
    if pos == 'vice president':
        CANDIDATES[pos] = {party: f"{party} Candidate for {pos}" for party in VICE_PRESIDENT_PARTIES}
    else:
        CANDIDATES[pos] = {party: f"{party} Candidate for {pos}" for party in PARTIES}

PASSWORD = "AllInOne"
RESULTS_FILE = "election_results.csv"

# Predefined results as requested (updated for Vice President with 3 parties)
PREDEFINED_RESULTS = {
    'president': {'Party A': 68, 'Party B': 32},
    'vice president': {'Party A': 25, 'Party B': 40, 'Party C': 35},
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
            if pos == 'vice president':
                # For vice president with 3 parties
                party_a_percent = PREDEFINED_RESULTS[pos]['Party A']
                party_b_percent = PREDEFINED_RESULTS[pos]['Party B']
                party_c_percent = PREDEFINED_RESULTS[pos]['Party C']
                
                # Determine winner
                party_votes = {
                    'Party A': party_a_percent,
                    'Party B': party_b_percent,
                    'Party C': party_c_percent
                }
                winner = max(party_votes, key=party_votes.get)
                
                # Calculate theoretical vote counts based on total votes
                if total_votes > 0:
                    party_a_votes = int(round(total_votes * party_a_percent / 100))
                    party_b_votes = int(round(total_votes * party_b_percent / 100))
                    party_c_votes = total_votes - party_a_votes - party_b_votes
                else:
                    party_a_votes = 0
                    party_b_votes = 0
                    party_c_votes = 0
                
                results_data.append({
                    'timestamp': timestamp,
                    'position': pos.capitalize(),
                    'total_votes': total_votes,
                    'party_a_votes': party_a_votes,
                    'party_b_votes': party_b_votes,
                    'party_c_votes': party_c_votes,
                    'winner': winner
                })
            else:
                # For other positions with 2 parties
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
                    'party_c_votes': 0,  # Zero for other positions
                    'winner': winner
                })
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(results_data)
        
        # Always write with header to ensure consistent structure
        df.to_csv(RESULTS_FILE, mode='w', header=True, index=False)
        
        return df
    except Exception as e:
        st.error(f"Error saving results to CSV: {e}")
        return None

def load_results_from_csv():
    """Load and display results from CSV file with error handling"""
    try:
        if os.path.isfile(RESULTS_FILE):
            # Try to read with error handling for inconsistent column numbers
            df = pd.read_csv(RESULTS_FILE, on_bad_lines='skip')
            
            # Check if we have the expected columns
            expected_columns = ['timestamp', 'position', 'total_votes', 'party_a_votes', 
                              'party_b_votes', 'party_c_votes', 'winner']
            
            # If columns don't match, recreate the file with current structure
            if not all(col in df.columns for col in expected_columns):
                st.warning("CSV structure outdated. Recreating with current format...")
                # Delete the old file and create new one
                if st.session_state.votes:
                    total_votes = len(st.session_state.votes)
                    new_df = save_results_to_csv(total_votes)
                    return new_df
                else:
                    os.remove(RESULTS_FILE)
                    return None
            
            return df
        else:
            return None
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        # Try to recover by recreating the file
        try:
            if os.path.isfile(RESULTS_FILE):
                os.remove(RESULTS_FILE)
                st.info("Corrupted CSV file removed. New file will be created when results are saved.")
        except:
            pass
        return None

def get_latest_results():
    """Get the latest results from CSV file with error handling"""
    try:
        if os.path.isfile(RESULTS_FILE):
            # Use error handling for reading CSV
            df = pd.read_csv(RESULTS_FILE, on_bad_lines='skip')
            
            if df.empty:
                return None
            
            # Check if we have the expected structure
            if 'timestamp' not in df.columns:
                st.error("CSV file has incorrect structure. Please delete and recreate.")
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

def fix_csv_file():
    """Fix the CSV file by recreating it with current data"""
    try:
        if os.path.isfile(RESULTS_FILE):
            backup_file = f"election_results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(RESULTS_FILE, backup_file)
            st.success(f"Corrupted file backed up as {backup_file}")
        
        if st.session_state.votes:
            total_votes = len(st.session_state.votes)
            new_df = save_results_to_csv(total_votes)
            if new_df is not None:
                st.success("CSV file recreated with current data structure")
                return new_df
        else:
            st.info("No votes to save. New file will be created when votes are cast.")
            return None
    except Exception as e:
        st.error(f"Error fixing CSV file: {e}")
        return None

def display_voting_page():
    """Display the main voting page"""
    st.header("Cast Your Vote")
    
    # USN Input and Validation with dynamic key to allow reset
    usn = st.text_input("Enter your USN (e.g., 4JN24MC001):", key=f"usn_{st.session_state.usn_input_key}")

    if st.session_state.vote_submitted:
        st.success("✅ Your vote has been submitted successfully!")
        st.info("You cannot vote again with the same USN.")
        if st.button("Submit Another Vote"):
            reset_voting_form()
            st.rerun()
    else:
        if usn:
            # Convert to uppercase and remove spaces for consistency
            usn_clean = usn.strip().upper()
            
            if not re.match(r'4JN24MC\d{3}', usn_clean):
                st.error("Invalid USN format. Must be 4JN24MC followed by 3 digits.")
            else:
                num = int(usn_clean[8:])
                if not (1 <= num <= 120):
                    st.error("USN number must be between 001 and 120.")
                elif usn_clean in st.session_state.voted_usns:
                    st.error("❌ This USN has already voted. You cannot vote again.")
                else:
                    st.success("USN validated. Proceed to vote.")

                    # Voting Form
                    with st.form("voting_form"):
                        st.subheader("Vote for each position:")
                        selections = {}
                        for pos in POSITIONS:
                            st.write(f"**{pos.capitalize()}:**")
                            
                            # Create options with NOTA as first option
                            if pos == 'vice president':
                                options = ["NOTA - None of the Above"] + [CANDIDATES[pos][party] for party in VICE_PRESIDENT_PARTIES]
                            else:
                                options = ["NOTA - None of the Above"] + [CANDIDATES[pos][party] for party in PARTIES]
                            
                            selections[pos] = st.radio(
                                f"Select candidate for {pos}:", 
                                options, 
                                key=f"vote_{pos}"
                            )
                        
                        submitted = st.form_submit_button("Submit Vote")
                        if submitted:
                            # Record vote
                            vote = {pos: selections[pos] for pos in POSITIONS}
                            st.session_state.votes.append(vote)
                            st.session_state.voted_usns.add(usn_clean)  # Store cleaned USN
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
    3. **NOTA (None of the Above)** option is available for all positions
    4. **Vice President** has 3 party candidates (Party A, Party B, Party C)
    5. Click 'Submit Vote' to cast your vote
    6. **Each USN can vote only once** - duplicate voting is strictly restricted
    """)

def display_results_page():
    """Display the results page - now fetches from CSV"""
    st.header("Election Results")
    
    result_password = st.text_input("Enter password to view results:", type="password", key="results_pw")
    
    if result_password == PASSWORD:
        st.success("Access granted.")
        
        # Add CSV repair option
        if st.button("🛠️ Repair CSV File"):
            fixed_df = fix_csv_file()
            if fixed_df is not None:
                st.rerun()
        
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
                    
                    if pos == 'vice president':
                        # Display for Vice President with 3 parties
                        party_a_votes = pos_results['party_a_votes'].iloc[0]
                        party_b_votes = pos_results['party_b_votes'].iloc[0]
                        party_c_votes = pos_results['party_c_votes'].iloc[0]
                        winner = pos_results['winner'].iloc[0]
                        
                        # Display results in a clean format
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Party A Votes", value=party_a_votes)
                        with col2:
                            st.metric(label="Party B Votes", value=party_b_votes)
                        with col3:
                            st.metric(label="Party C Votes", value=party_c_votes)
                        
                    else:
                        # Display for other positions with 2 parties
                        party_a_votes = pos_results['party_a_votes'].iloc[0]
                        party_b_votes = pos_results['party_b_votes'].iloc[0]
                        winner = pos_results['winner'].iloc[0]
                        
                        # Display results in a clean format
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(label="Party A Votes", value=party_a_votes)
                        with col2:
                            st.metric(label="Party B Votes", value=party_b_votes)
                    
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
    
    # Display note about disabled media position and new features
    st.info("""
    **Notes:**
    - Media position voting has been disabled
    - NOTA option available for all positions
    - Vice President has 3 candidates (Party A, B, C)
    - **Strict one-vote-per-USN policy**
    """)
    
    st.markdown("---")
    st.markdown("### Positions Available:")
    for pos in POSITIONS:
        if pos == 'vice president':
            st.write(f"• {pos.title()} (3 candidates + NOTA)")
        else:
            st.write(f"• {pos.title()} (2 candidates + NOTA)")
