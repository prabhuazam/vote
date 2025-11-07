import streamlit as st
import re

# Constants
PARTIES = ['Party A', 'Party B']
POSITIONS = ['president', 'vice president', 'secretary', 'joint secretary', 'treasurer', 'event organiser', 'sports']  # Removed 'media'
CANDIDATES = {pos: {party: f"{party} Candidate for {pos}" for party in PARTIES} for pos in POSITIONS}
PASSWORD = "AllInOne"  # Set a password for accessing results and deleting votes

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

def reset_voting_form():
    """Reset the voting form and clear USN input"""
    st.session_state.vote_submitted = False
    # Clear the USN input by using a unique key that we can manipulate
    if 'usn_input_key' not in st.session_state:
        st.session_state.usn_input_key = 0
    st.session_state.usn_input_key += 1

st.title("College Voting System")

# Sidebar for Admin Results
with st.sidebar:
    st.header("Admin Panel")
    
    # Collapsible section for election results
    with st.expander("Election Results (Admin Access)", expanded=False):
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
                
                st.write(f"**Party A:** {party_a_votes} votes")
                st.write(f"**Party B:** {party_b_votes} votes")
                st.write(f"**Winner: {winner}**")
                
                # Display vote progression bars (showing only vote counts in text)
                col1, col2 = st.columns(2)
                with col1:
                    st.progress(party_a_percent / 100, 
                              text=f"Party A: {party_a_votes} votes")
                with col2:
                    st.progress(party_b_percent / 100, 
                              text=f"Party B: {party_b_votes} votes")
                
                st.write("---")
            
            # Admin Actions Section
            st.subheader("Admin Actions")
            delete_password = st.text_input("Enter password to delete all votes:", type="password", key="delete_pw")
            if delete_password == PASSWORD:
                if st.button("Delete All Votes"):
                    st.session_state.votes = []
                    st.session_state.voted_usns = set()
                    st.session_state.vote_submitted = False
                    st.success("All votes have been deleted.")
                    st.rerun()
            elif delete_password:  # Only show error if something was entered
                st.error("Incorrect password for deletion.")
        else:
            if result_password:  # Only show error if password was entered
                st.error("Incorrect password. Access denied.")
    
    # Display note about disabled media position
    st.info("Note: Media position voting has been disabled for this election.")
    
    # Display current vote count in sidebar
    st.write(f"**Current Votes Cast:** {len(st.session_state.votes)}")

# Main voting interface
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