import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import fcntl
from pathlib import Path

# Configuration
PARTIES = ['Party A', 'Party B']
POSITIONS = ['president', 'vice president', 'secretary', 'joint secretary', 'treasurer', 'event organiser', 'sports']
PARTIES_VICE_PRESIDENT = ['Party A', 'Party B', 'Party C']
ADMIN_PASSWORD = "AllInOne"
RESULTS_CSV = "election_results.csv"
VOTES_CSV = "election_votes.csv"

# PREDEFINED PROPORTIONS (as in original code)
PREDEFINED_PERCENTAGES = {
    'president': {'Party A': 68, 'Party B': 32},
    'secretary': {'Party A': 54, 'Party B': 46},
    'joint secretary': {'Party A': 63, 'Party B': 37},
    'treasurer': {'Party A': 71, 'Party B': 29},
    'sports': {'Party A': 51, 'Party B': 49}
}

# Candidate mapping
CANDIDATE_MAPPING = {
    'president': {'Party A': 'Shrinivas', 'Party B': 'Pavan'},
    'vice president': {'Party A': 'Geetha', 'Party B': 'Keerthana N', 'Party C': 'Varsha'},
    'secretary': {'Party A': 'Yashwanth', 'Party B': 'Gowtham'},
    'joint secretary': {'Party A': 'Varun', 'Party B': 'Deekshith'},
    'treasurer': {'Party A': 'Rahul', 'Party B': 'Sukrutha'},
    'event organiser': {'Party A': 'Vainika', 'Party B': 'Anushree'},
    'sports': {'Party A': 'Akhilesh', 'Party B': 'Satya Prakash'}
}

# Valid USNs
_valid_usns = {f"4JN24MC{i:03d}" for i in range(1, 121)} | {
    '250801','251361','251183','251348','251240','251270','251281','251250',
    '251353','251233','251301','251292','250940','251277','251298','251226',
    '251367','250950','251304','251224','251282','251208','251368','250771',
    '251227','251346','251330','251255','251307','251284','251285','250809',
    '251386','251287','250760','250452','251023','251359','251363','250934',
    '251184','251383','251340','251334','251388','251369','251372','250395',
    '251236','251351','251268','250821','251381','250544','251365','250456',
    '251209','250794','251274','251332','251291','251220','251211','251254',
    '251271','251175','251198','250747','250350','251305','251313','250341',
    '250740','251178','251333','250306','251235','251245','251201','251021',
    '251063','251259','251294','251223','250328','250339','251262','251384',
    '250921','251273','251344','251207','251257','251022','251350','251265',
    '251230','251357','251355','251385','251371','250751','251366','251300',
    '251296','250716','251035','251229'
}

# Initialize session state
if 'voting_complete' not in st.session_state:
    st.session_state.voting_complete = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Voting"
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0

def reset_voting_form():
    """Reset the voting form state"""
    st.session_state.voting_complete = False
    st.session_state.refresh_counter += 1

def get_candidate_name(position, party):
    """Get candidate name for position and party"""
    return CANDIDATE_MAPPING.get(position, {}).get(party, f"{party} Candidate")

def save_vote_safe(usn, vote_data):
    """Thread-safe vote saving with file locking"""
    lock_file = Path(VOTES_CSV + ".lock")
    
    try:
        # Create lock file
        with open(lock_file, 'w') as lock:
            # Acquire exclusive lock
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            
            # Read existing votes
            all_votes = []
            voted_usns = set()
            
            if os.path.isfile(VOTES_CSV):
                try:
                    df = pd.read_csv(VOTES_CSV)
                    if not df.empty:
                        all_votes = df.to_dict('records')
                        voted_usns = set(df['usn'].astype(str).tolist())
                except Exception as e:
                    st.error(f"Error reading votes file: {e}")
                    all_votes = []
                    voted_usns = set()
            
            # Check if USN already voted
            if usn in voted_usns:
                return False, "This USN has already voted"
            
            # Add new vote
            vote_record = {
                'usn': usn,
                'votes': json.dumps(vote_data),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            all_votes.append(vote_record)
            
            # Save all votes back to CSV
            df = pd.DataFrame(all_votes)
            df.to_csv(VOTES_CSV, index=False)
            
            return True, "Vote successfully recorded"
            
    except Exception as e:
        return False, f"System error: {str(e)}"
    finally:
        # Clean up lock file
        if lock_file.exists():
            try:
                lock_file.unlink()
            except:
                pass

def get_total_votes_count():
    """Get actual total votes from votes CSV"""
    if not os.path.isfile(VOTES_CSV):
        return 0
    
    try:
        df = pd.read_csv(VOTES_CSV)
        return len(df) if not df.empty else 0
    except:
        return 0

def is_usn_already_voted(usn):
    """Check if USN has already voted"""
    if not os.path.isfile(VOTES_CSV):
        return False
    
    try:
        df = pd.read_csv(VOTES_CSV)
        if df.empty:
            return False
        return usn in df['usn'].astype(str).values
    except:
        return False

def calculate_results_with_predefined_proportions():
    """Calculate results using predefined proportions for most positions"""
    total_votes = get_total_votes_count()
    
    if total_votes == 0:
        # Return empty results if no votes
        results = {}
        for position in POSITIONS:
            if position == 'vice president':
                results[position] = {'Party A': 0, 'Party B': 0, 'Party C': 0, 'winner': 'No Votes'}
            else:
                results[position] = {'Party A': 0, 'Party B': 0, 'winner': 'No Votes'}
        return results, total_votes
    
    results = {}
    
    for position in POSITIONS:
        if position in ['vice president', 'event organiser']:
            # Calculate ACTUAL votes for these positions
            party_a_votes = 0
            party_b_votes = 0
            party_c_votes = 0
            
            try:
                df = pd.read_csv(VOTES_CSV)
                for _, row in df.iterrows():
                    try:
                        votes = json.loads(row['votes'])
                        if position in votes:
                            selected_candidate = votes[position]
                            if position == 'vice president':
                                if 'Geetha' in selected_candidate:
                                    party_a_votes += 1
                                elif 'Keerthana N' in selected_candidate:
                                    party_b_votes += 1
                                elif 'Varsha' in selected_candidate:
                                    party_c_votes += 1
                            elif position == 'event organiser':
                                if 'Vainika' in selected_candidate:
                                    party_a_votes += 1
                                elif 'Anushree' in selected_candidate:
                                    party_b_votes += 1
                    except:
                        continue
            except:
                party_a_votes = 0
                party_b_votes = 0
                party_c_votes = 0
            
            if position == 'vice president':
                # Determine winner for vice president
                vote_counts = {'Party A': party_a_votes, 'Party B': party_b_votes, 'Party C': party_c_votes}
                max_votes = max(vote_counts.values())
                if max_votes > 0:
                    winner = max(vote_counts, key=vote_counts.get)
                else:
                    winner = 'No Votes'
                
                results[position] = {
                    'Party A': party_a_votes,
                    'Party B': party_b_votes,
                    'Party C': party_c_votes,
                    'winner': winner
                }
            else:  # event organiser
                # Determine winner for event organiser
                if party_a_votes > party_b_votes:
                    winner = 'Party A'
                elif party_b_votes > party_a_votes:
                    winner = 'Party B'
                else:
                    winner = 'No Votes' if party_a_votes == 0 else 'Tie'
                
                results[position] = {
                    'Party A': party_a_votes,
                    'Party B': party_b_votes,
                    'winner': winner
                }
        
        else:
            # Use PREDEFINED PROPORTIONS for other positions
            if position in PREDEFINED_PERCENTAGES:
                percentages = PREDEFINED_PERCENTAGES[position]
                party_a_votes = int(round(total_votes * percentages['Party A'] / 100))
                party_b_votes = total_votes - party_a_votes
                
                # Determine winner based on predefined percentages
                if percentages['Party A'] > percentages['Party B']:
                    winner = 'Party A'
                else:
                    winner = 'Party B'
                
                results[position] = {
                    'Party A': party_a_votes,
                    'Party B': party_b_votes,
                    'winner': winner
                }
            else:
                # Fallback for any position not in predefined list
                results[position] = {
                    'Party A': 0,
                    'Party B': 0,
                    'winner': 'No Votes'
                }
    
    return results, total_votes

def save_results_to_csv():
    """Save current results to CSV using predefined proportions"""
    results, total_votes = calculate_results_with_predefined_proportions()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    records = []
    for position, result in results.items():
        record = {
            'timestamp': timestamp,
            'position': position.capitalize(),
            'total_votes': total_votes,
            'party_a_votes': result['Party A'],
            'party_b_votes': result['Party B'],
            'party_c_votes': result.get('Party C', 0),
            'winner': result['winner']
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    
    # Save to CSV (append if file exists)
    if os.path.isfile(RESULTS_CSV):
        df.to_csv(RESULTS_CSV, mode='a', header=False, index=False)
    else:
        df.to_csv(RESULTS_CSV, mode='w', header=True, index=False)
    
    return df

def get_latest_results():
    """Get the latest results from CSV"""
    if not os.path.isfile(RESULTS_CSV):
        return None
    
    try:
        df = pd.read_csv(RESULTS_CSV)
        if df.empty:
            return None
        
        latest_timestamp = df['timestamp'].max()
        return df[df['timestamp'] == latest_timestamp]
    except:
        return None

def get_all_results_history():
    """Get all results history"""
    if not os.path.isfile(RESULTS_CSV):
        return None
    
    try:
        df = pd.read_csv(RESULTS_CSV)
        return df if not df.empty else None
    except:
        return None

def repair_election_data():
    """Repair election data by recreating results from votes"""
    try:
        # Create backup of existing files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if os.path.isfile(RESULTS_CSV):
            backup_name = f"election_results_backup_{timestamp}.csv"
            os.rename(RESULTS_CSV, backup_name)
            st.success(f"Backup created: {backup_name}")
        
        # Recreate results from votes if votes exist
        if os.path.isfile(VOTES_CSV):
            results_df = save_results_to_csv()
            st.success("Results recreated from vote data using predefined proportions")
            return results_df
        else:
            st.info("No vote data available to recreate results")
            return None
    except Exception as e:
        st.error(f"Repair failed: {e}")
        return None

def render_voting_interface():
    """Render the voting interface"""
    st.header("Cast Your Vote")
    
    usn_input = st.text_input("Enter USN:", key=f"usn_input_{st.session_state.refresh_counter}")
    
    if st.session_state.voting_complete:
        st.success("✅ Your vote has been submitted!")
        st.info("You cannot vote again with the same USN.")
        if st.button("Submit Another Vote"):
            reset_voting_form()
            st.rerun()
    else:
        if usn_input:
            usn_clean = usn_input.strip().upper()
            
            # Validate USN
            if usn_clean not in _valid_usns:
                st.error("❌ Invalid USN. Only registered MCA students are allowed to vote.")
            elif is_usn_already_voted(usn_clean):
                st.error("❌ This USN has already voted. Each student can only vote once.")
                st.session_state.voting_complete = True
            else:
                st.success("✅ USN validated. Please cast your vote below.")
                
                # Voting form
                with st.form("voting_form"):
                    st.subheader("Vote for Candidates:")
                    user_votes = {}
                    
                    for position in POSITIONS:
                        st.write(f"**{position.title()}:**")
                        
                        # Create candidate options
                        if position == 'vice president':
                            parties = PARTIES_VICE_PRESIDENT
                        else:
                            parties = PARTIES
                        
                        candidate_options = ["NOTA - None of the Above"]
                        for party in parties:
                            candidate_name = get_candidate_name(position, party)
                            candidate_options.append(f"{candidate_name} ({party})")
                        
                        # Radio button for selection
                        selected = st.radio(
                            f"Select candidate for {position}:",
                            candidate_options,
                            key=f"vote_{position}_{st.session_state.refresh_counter}"
                        )
                        user_votes[position] = selected
                    
                    # Submit button
                    submitted = st.form_submit_button("Submit Vote")
                    
                    if submitted:
                        # Save vote
                        success, message = save_vote_safe(usn_clean, user_votes)
                        
                        if success:
                            # Update results using predefined proportions
                            save_results_to_csv()
                            st.session_state.voting_complete = True
                            st.success("✅ Your vote has been successfully recorded!")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

def render_results_interface():
    """Render the results interface"""
    st.header("Election Results")
    
    # Password protection for admin features
    password = st.text_input("Enter Admin Password:", type="password", key="results_password")
    
    if password == ADMIN_PASSWORD:
        st.success("🔓 Admin access granted")
        
        # Display note about predefined proportions
        st.info("📊 **Note:** Most positions use predefined vote proportions. Only Vice President and Event Organiser use actual vote counts.")
        
        # Repair tool
        if st.button("🛠️ Repair Election Data"):
            with st.spinner("Repairing election data..."):
                repair_election_data()
            st.rerun()
        
        # Display current results
        st.subheader("Current Results")
        latest_results = get_latest_results()
        
        if latest_results is None or latest_results.empty:
            st.warning("No election results available yet.")
        else:
            total_votes = latest_results['total_votes'].iloc[0]
            st.write(f"**Total Votes Cast: {total_votes}**")
            st.write("---")
            
            for position in POSITIONS:
                position_result = latest_results[latest_results['position'] == position.capitalize()]
                
                if not position_result.empty:
                    st.subheader(f"Results for {position.title()}:")
                    
                    # Add indicator for predefined vs actual results
                    if position in ['vice president', 'event organiser']:
                        st.caption("🏆 **Actual Vote Count**")
                    else:
                        st.caption("📈 **Predefined Proportions**")
                    
                    if position == 'vice president':
                        party_a_votes = position_result['party_a_votes'].iloc[0]
                        party_b_votes = position_result['party_b_votes'].iloc[0]
                        party_c_votes = position_result['party_c_votes'].iloc[0]
                        winner = position_result['winner'].iloc[0]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(f"{get_candidate_name(position, 'Party A')}", party_a_votes)
                        with col2:
                            st.metric(f"{get_candidate_name(position, 'Party B')}", party_b_votes)
                        with col3:
                            st.metric(f"{get_candidate_name(position, 'Party C')}", party_c_votes)
                        
                        st.write(f"**Winner: {get_candidate_name(position, winner)}**")
                    else:
                        party_a_votes = position_result['party_a_votes'].iloc[0]
                        party_b_votes = position_result['party_b_votes'].iloc[0]
                        winner = position_result['winner'].iloc[0]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(f"{get_candidate_name(position, 'Party A')}", party_a_votes)
                        with col2:
                            st.metric(f"{get_candidate_name(position, 'Party B')}", party_b_votes)
                        
                        st.write(f"**Winner: {get_candidate_name(position, winner)}**")
                    
                    st.write("---")
        
        # Admin actions section
        st.subheader("Admin Actions")
        
        # Results history
        st.write("### Results History")
        all_results = get_all_results_history()
        if all_results is not None:
            st.dataframe(all_results)
            
            # Download button
            csv_data = all_results.to_csv(index=False)
            st.download_button(
                "Download Complete Results CSV",
                csv_data,
                "election_results_complete.csv",
                "text/csv"
            )
        else:
            st.write("No historical results data available.")
        
        # Data management
        st.write("### Data Management")
        delete_password = st.text_input("Enter password to delete data:", type="password", key="delete_password")
        
        if delete_password == ADMIN_PASSWORD:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Clear All Votes", type="secondary"):
                    try:
                        if os.path.isfile(VOTES_CSV):
                            os.remove(VOTES_CSV)
                        if os.path.isfile(RESULTS_CSV):
                            os.remove(RESULTS_CSV)
                        st.success("All election data cleared successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing data: {e}")
            
            with col2:
                if st.button("🗑️ Delete Results Only", type="secondary"):
                    try:
                        if os.path.isfile(RESULTS_CSV):
                            os.remove(RESULTS_CSV)
                            st.success("Results data deleted successfully")
                            st.rerun()
                        else:
                            st.error("No results file found")
                    except Exception as e:
                        st.error(f"Error deleting results: {e}")
        elif delete_password:
            st.error("❌ Incorrect password for data deletion")
    
    else:
        if password:
            st.error("❌ Access denied. Incorrect password.")

# Main application
st.title("🎓 MCA Forum College Voting System")
st.markdown("---")

# Navigation
page = st.radio(
    "Navigate to:",
    ["Voting", "Results"],
    index=0 if st.session_state.current_page == "Voting" else 1,
    horizontal=True,
    key="navigation"
)

# Update current page
if page != st.session_state.current_page:
    st.session_state.current_page = page
    st.rerun()

# Render the selected page
if st.session_state.current_page == "Voting":
    render_voting_interface()
else:
    render_results_interface()

# Sidebar
with st.sidebar:
    st.header("ℹ️ Election Information")
    
    total_votes = get_total_votes_count()
    st.write(f"**Total Votes Cast:** {total_votes}")
    st.write(f"**Current Page:** {st.session_state.current_page}")
    
    st.markdown("---")
    st.markdown("### 📋 Positions & Candidates")
    
    for position in POSITIONS:
        st.write(f"**{position.title()}:**")
        if position == 'vice president':
            for party in PARTIES_VICE_PRESIDENT:
                candidate = get_candidate_name(position, party)
                st.write(f"  - {candidate} ({party})")
        else:
            for party in PARTIES:
                candidate = get_candidate_name(position, party)
                st.write(f"  - {candidate} ({party})")
        st.write("")
    
    st.markdown("---")
    st.markdown("### 📊 Voting System")
    st.info("""
    **System Notes:**
    - Vice President & Event Organiser: Actual vote counts
    - Other positions: Predefined proportions
    - Each USN can vote only once
    """)

# Initialize vote tracking file if it doesn't exist
if not os.path.isfile(VOTES_CSV):
    try:
        pd.DataFrame(columns=['usn', 'votes', 'timestamp']).to_csv(VOTES_CSV, index=False)
    except:
        pass
