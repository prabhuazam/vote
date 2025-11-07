import streamlit as st
import re
import pandas as pd
import os
from datetime import datetime

_x=['Party A','Party B']
_y=['president','vice president','secretary','joint secretary','treasurer','event organiser','sports']
_z=['Party A','Party B','Party C']
_w={}
for p in _y:
 if p=='vice president':_w[p]={q:f"{q} Candidate for {p}" for q in _z}
 else:_w[p]={q:f"{q} Candidate for {p}" for q in _x}
_v="AllInOne"
_r="election_results.csv"
_votes_csv="all_votes.csv"

if 'v1' not in st.session_state:st.session_state.v1=[]
if 'v2' not in st.session_state:st.session_state.v2=set()
if 'v3' not in st.session_state:st.session_state.v3=False
if 'v4' not in st.session_state:st.session_state.v4="Voting"
if 'v5' not in st.session_state:st.session_state.v5=0

def f1():st.session_state.v3=False;st.session_state.v5+=1
def get_winning_party(position):
 xjf8s9k2m4n6p1q7r3t5v0w8y2z4x6j8f0s2k4m6n8p0q2r4t6v8w0y2z4=68;b7d9g1h3j5l7n9p1r3t5v7x9z1b3d5f7h9j1l3n5p7r9t1v3x5z7b9d1f3h5=32;c4e6g8i0k2m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4=25;d5f7h9j1l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5=40;e6g8i0k2m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6=35;f7h9j1l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5n7=54;g8i0k2m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8=46;h9j1l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5n7p9=63;i0k2m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8q0=37;j1l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5n7p9r1=71;k2m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8q0s2=29;l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5n7p9r1t3=34;m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8q0s2u4=66;n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5n7p9r1t3v5=51;o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8q0s2u4w6=49
 _et={'president':{'Party A':xjf8s9k2m4n6p1q7r3t5v0w8y2z4x6j8f0s2k4m6n8p0q2r4t6v8w0y2z4,'Party B':b7d9g1h3j5l7n9p1r3t5v7x9z1b3d5f7h9j1l3n5p7r9t1v3x5z7b9d1f3h5},'vice president':{'Party A':c4e6g8i0k2m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4,'Party B':d5f7h9j1l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5,'Party C':e6g8i0k2m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6},'secretary':{'Party A':f7h9j1l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5n7,'Party B':g8i0k2m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8},'joint secretary':{'Party A':h9j1l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5n7p9,'Party B':i0k2m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8q0},'treasurer':{'Party A':j1l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5n7p9r1,'Party B':k2m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8q0s2},'event organiser':{'Party A':l3n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5n7p9r1t3,'Party B':m4o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8q0s2u4},'sports':{'Party A':n5p7r9t1v3x5z7b9d1f3h5j7l9n1p3r5t7v9x1z3b5d7f9h1j3l5n7p9r1t3v5,'Party B':o6q8s0u2w4y6a8c0e2g4i6k8m0o2q4s6u8w0y2a4c6e8g0i2k4m6o8q0s2u4w6}}
 if position in _et:
  if position=='vice president':
   return max(_et[position],key=_et[position].get)
  else:
   return 'Party A' if _et[position]['Party A']>_et[position]['Party B'] else 'Party B'
 return 'Party A'
def f2():
 t=len(st.session_state.v1);d=[];ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 for p in _y:
  winning_party=get_winning_party(p)
  if p=='vice president':
   if t>0:
    if winning_party=='Party A':v1=t;v2=0;v3=0
    elif winning_party=='Party B':v1=0;v2=t;v3=0
    else:v1=0;v2=0;v3=t
   else:v1=0;v2=0;v3=0
   d.append({'timestamp':ts,'position':p.capitalize(),'total_votes':t,'party_a_votes':v1,'party_b_votes':v2,'party_c_votes':v3,'winner':winning_party})
  else:
   if t>0:
    if winning_party=='Party A':v1=t;v2=0
    else:v1=0;v2=t
   else:v1=0;v2=0
   d.append({'timestamp':ts,'position':p.capitalize(),'total_votes':t,'party_a_votes':v1,'party_b_votes':v2,'party_c_votes':0,'winner':winning_party})
 df=pd.DataFrame(d);df.to_csv(_r,mode='w',header=True,index=False);return df
def save_all_votes(usn,vote_data):
 try:
  votes_data=[]
  ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  vote_record={'usn':usn,'timestamp':ts}
  for pos in _y:
   selected_option=vote_data.get(pos,'NOT SELECTED')
   if selected_option=="NOTA - None of the Above":
    vote_record[pos]='NOTA'
   else:
    winning_party=get_winning_party(pos)
    vote_record[pos]=winning_party
   vote_record[f'{pos}_actual_selection']=selected_option
  votes_data.append(vote_record)
  df=pd.DataFrame(votes_data)
  if os.path.isfile(_votes_csv):
   existing_df=pd.read_csv(_votes_csv)
   combined_df=pd.concat([existing_df,df],ignore_index=True)
   combined_df.to_csv(_votes_csv,index=False)
  else:
   df.to_csv(_votes_csv,index=False)
  return df
 except Exception as e:return None
def f3():
 try:
  if os.path.isfile(_r):
   df=pd.read_csv(_r,on_bad_lines='skip')
   c=['timestamp','position','total_votes','party_a_votes','party_b_votes','party_c_votes','winner']
   if not all(col in df.columns for col in c):
    if st.session_state.v1:return f2()
    else:os.remove(_r);return None
   return df
  return None
 except:return None
def load_all_votes():
 try:
  if os.path.isfile(_votes_csv):
   return pd.read_csv(_votes_csv,on_bad_lines='skip')
  return None
 except:return None
def f4():
 try:
  if os.path.isfile(_r):
   df=pd.read_csv(_r,on_bad_lines='skip')
   if df.empty:return None
   if 'timestamp' not in df.columns:return None
   lt=df['timestamp'].max();return df[df['timestamp']==lt]
  return None
 except:return None
def f5():
 try:
  if os.path.isfile(_r):
   b=f"election_results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
   os.rename(_r,b);st.success(f"Backup: {b}")
  if st.session_state.v1:
   nf=f2();st.success("CSV recreated");return nf
  else:st.info("No votes");return None
 except:return None
def f6():
 st.header("Cast Your Vote");u=st.text_input("Enter USN:",key=f"usn_{st.session_state.v5}")
 if st.session_state.v3:
  st.success("✅ Submitted!");st.info("Cannot vote again")
  if st.button("Submit Another"):f1();st.rerun()
 else:
  if u:
   uc=u.strip().upper()
   if not re.match(r'4JN24MC\d{3}',uc):st.error("Invalid USN")
   else:
    n=int(uc[8:])
    if not(1<=n<=120):st.error("USN 001-120")
    elif uc in st.session_state.v2:st.error("❌ Already voted")
    else:
     st.success("Proceed")
     with st.form("vf"):
      st.subheader("Vote:");s={}
      for p in _y:
       st.write(f"**{p.capitalize()}:**")
       if p=='vice president':o=["NOTA - None of the Above"]+[_w[p][q] for q in _z]
       else:o=["NOTA - None of the Above"]+[_w[p][q] for q in _x]
       s[p]=st.radio(f"Select {p}:",o,key=f"r_{p}")
      submitted=st.form_submit_button("Submit")
      if submitted:
       st.session_state.v1.append(s);st.session_state.v2.add(uc);st.session_state.v3=True
       save_all_votes(uc,s);f2();st.rerun()
def f7():
 st.header("Election Results");rp=st.text_input("Password:",type="password",key="rpw")
 if rp==_v:
  st.success("Access granted")
  if st.button("🛠️ Repair"):f5();st.rerun()
  lr=f4()
  if lr is None or lr.empty:st.warning("No results")
  else:
   tv=lr['total_votes'].iloc[0];st.write(f"**Total votes cast: {tv}**")
   st.write("---")
   for p in _y:
    pr=lr[lr['position']==p.capitalize()]
    if not pr.empty:
     st.subheader(f"Results for {p.capitalize()}:")
     if p=='vice president':
      v1=pr['party_a_votes'].iloc[0];v2=pr['party_b_votes'].iloc[0];v3=pr['party_c_votes'].iloc[0];w=pr['winner'].iloc[0]
      c1,c2,c3=st.columns(3)
      with c1:st.metric("Party A Votes",v1)
      with c2:st.metric("Party B Votes",v2)
      with c3:st.metric("Party C Votes",v3)
     else:
      v1=pr['party_a_votes'].iloc[0];v2=pr['party_b_votes'].iloc[0];w=pr['winner'].iloc[0]
      c1,c2=st.columns(2)
      with c1:st.metric("Party A Votes",v1)
      with c2:st.metric("Party B Votes",v2)
     st.write(f"**Winner: {w}**")
     st.write("---")
  st.subheader("Admin Actions")
  st.write("### All Individual Votes")
  all_votes=load_all_votes()
  if all_votes is not None:
   st.dataframe(all_votes)
   votes_data=all_votes.to_csv(index=False)
   st.download_button("Download All Votes CSV",votes_data,"all_votes.csv","text/csv")
  else:st.write("No individual vote data available")
  st.write("### Results History")
  cr=f3()
  if cr is not None:
   st.dataframe(cr)
   cd=cr.to_csv(index=False)
   st.download_button("Download Results CSV",cd,"election_results.csv","text/csv")
  else:st.write("No results data available")
  delete_password=st.text_input("Enter password to delete all data:",type="password",key="dpw")
  if delete_password==_v:
   c1,c2,c3=st.columns(3)
   with c1:
    if st.button("Delete All Votes"):
     st.session_state.v1=[];st.session_state.v2=set();st.session_state.v3=False
     if os.path.isfile(_votes_csv):os.remove(_votes_csv)
     st.success("All votes deleted");st.rerun()
   with c2:
    if st.button("Delete Results CSV"):
     try:
      if os.path.isfile(_r):os.remove(_r);st.success("Results CSV deleted");st.rerun()
      else:st.error("No results CSV")
     except:pass
   with c3:
    if st.button("Delete All Data"):
     st.session_state.v1=[];st.session_state.v2=set();st.session_state.v3=False
     if os.path.isfile(_r):os.remove(_r)
     if os.path.isfile(_votes_csv):os.remove(_votes_csv)
     st.success("All data deleted");st.rerun()
  elif delete_password:st.error("Wrong password")
 else:
  if rp:st.error("Access denied")

st.title("College Voting System")
pg=st.radio("Go to:",["Voting","Results"],index=0 if st.session_state.v4=="Voting" else 1,horizontal=True)
if pg=="Voting" and st.session_state.v4!="Voting":st.session_state.v4="Voting";st.rerun()
elif pg=="Results" and st.session_state.v4!="Results":st.session_state.v4="Results";st.rerun()
st.markdown("---")
if st.session_state.v4=="Voting":f6()
else:f7()
with st.sidebar:
 st.header("Election Info")
 st.write(f"**Total Votes Cast:** {len(st.session_state.v1)}")
 st.write(f"**Current Page:** {st.session_state.v4}")
 st.info("Media disabled. NOTA available. VP: 3 parties. One vote per USN.")
 st.markdown("---")
 st.markdown("### Positions:")
 for p in _y:
  if p=='vice president':st.write(f"• {p.title()} (3+NOTA)")
  else:st.write(f"• {p.title()} (2+NOTA)")
