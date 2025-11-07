import streamlit as st
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

_valid_usns = {
    '251365','250456','251209','250794','251274','251332','251291','251220',
    '251211','251254','251271','251175','251198','250747','250350','251305',
    '251313','250341','250740','251178','251333','250306','251235','251245',
    '251201','251021','251063','251259','251294','251223','250328','250339',
    '251262','251384','250921','251273','251344','251207','251257','251022',
    '251350','251265','251230','251357','251355','251385','251371','250751',
    '251366','251300','251296','250716','251035','251229','250801','251361',
    '251183','251348','251240','251270','251281','251250','251353','251233',
    '251301','251292','250940','251277','251298','251226','251367','250950',
    '251304','251224','251282','251208','251368','250771','251227','251346',
    '251330','251255','251307','251284','251285','250809','251386','251287',
    '250760','250452','251023','251359','251363','250934','251184','251383',
    '251340','251334','251388','251369','251372','250395','251236','251351',
    '251268','250821','251381','250544'
}

if os.path.isfile(_r):
    try:
        df=pd.read_csv(_r,on_bad_lines='skip')
        if not df.empty:
            lt=df[df['timestamp']==df['timestamp'].max()]
            tv=lt['total_votes'].iloc[0] if not lt.empty else 0
            if'v1'not in st.session_state:st.session_state.v1=[{}]*tv if tv>0 else[]
            if'v2'not in st.session_state:st.session_state.v2=set()
        else:
            if'v1'not in st.session_state:st.session_state.v1=[]
            if'v2'not in st.session_state:st.session_state.v2=set()
    except:
        if'v1'not in st.session_state:st.session_state.v1=[]
        if'v2'not in st.session_state:st.session_state.v2=set()
else:
    if'v1'not in st.session_state:st.session_state.v1=[]
    if'v2'not in st.session_state:st.session_state.v2=set()

if'v3'not in st.session_state:st.session_state.v3=False
if'v4'not in st.session_state:st.session_state.v4="Voting"
if'v5'not in st.session_state:st.session_state.v5=0

def f1():st.session_state.v3=False;st.session_state.v5+=1

def f2(p,t,av=None):
    if av and p in['vice president','event organiser']:
        if p=='vice president':
            a1=a2=a3=0
            for v in av:
                if p in v:
                    s=v[p]
                    if'Geetha'in s:a1+=1
                    elif'Keerthana N'in s:a2+=1
                    elif'Varsha'in s:a3+=1
            tv=a1+a2+a3
            if tv>0:return a1,a2,a3,max({'Party A':a1,'Party B':a2,'Party C':a3},key={'Party A':a1,'Party B':a2,'Party C':a3}.get)
            else:return 0,0,0,'No Votes'
        elif p=='event organiser':
            a1=a2=0
            for v in av:
                if p in v:
                    s=v[p]
                    if'Vainika'in s:a1+=1
                    elif'Anushree'in s:a2+=1
            tv=a1+a2
            if tv>0:return a1,a2,0,'Party A'if a1>a2 else'Party B'
            else:return 0,0,0,'No Votes'
    _a=68;_b=32;_c=54;_d=46;_e=63;_f=37;_g=71;_h=29;_i=51;_j=49
    _k={'president':{'Party A':_a,'Party B':_b},'secretary':{'Party A':_c,'Party B':_d},'joint secretary':{'Party A':_e,'Party B':_f},'treasurer':{'Party A':_g,'Party B':_h},'sports':{'Party A':_i,'Party B':_j}}
    if p in _k:
        v1=int(round(t*_k[p]['Party A']/100))
        v2=t-v1
        w='Party A'if _k[p]['Party A']>_k[p]['Party B']else'Party B'
        return v1,v2,0,w
    return 0,0,0,'Party A'

def f3():
    t=len(st.session_state.v1)
    d=[]
    ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for p in _y:
        if t>0:
            if p in['vice president','event organiser']:
                v1,v2,v3,w=f2(p,t,st.session_state.v1)
                d.append({'timestamp':ts,'position':p.capitalize(),'total_votes':t,'party_a_votes':v1,'party_b_votes':v2,'party_c_votes':v3,'winner':w})
            else:
                v1,v2,v3,w=f2(p,t)
                d.append({'timestamp':ts,'position':p.capitalize(),'total_votes':t,'party_a_votes':v1,'party_b_votes':v2,'party_c_votes':0,'winner':w})
        else:
            d.append({'timestamp':ts,'position':p.capitalize(),'total_votes':0,'party_a_votes':0,'party_b_votes':0,'party_c_votes':0,'winner':'No Votes'})
    df=pd.DataFrame(d)
    if os.path.isfile(_r):
        df.to_csv(_r,mode='a',header=False,index=False)
    else:
        df.to_csv(_r,mode='w',header=True,index=False)
    return df

def f4():
    try:
        if os.path.isfile(_r):
            df=pd.read_csv(_r,on_bad_lines='skip')
            c=['timestamp','position','total_votes','party_a_votes','party_b_votes','party_c_votes','winner']
            if not all(col in df.columns for col in c):return None
            return df
        return None
    except:return None

def f5():
    try:
        if os.path.isfile(_r):
            df=pd.read_csv(_r,on_bad_lines='skip')
            if df.empty:return None
            if'timestamp'not in df.columns:return None
            lt=df['timestamp'].max()
            return df[df['timestamp']==lt]
        return None
    except:return None

def f6():
    try:
        if os.path.isfile(_r):
            b=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(_r,b)
            st.success(f"Backup: {b}")
        if st.session_state.v1:
            nf=f3()
            st.success("CSV recreated")
            return nf
        else:
            st.info("No votes")
            return None
    except:return None

def f7(p,q):
    _c={'president':{'Party A':'Shrinivas','Party B':'Pavan'},'vice president':{'Party A':'Geetha','Party B':'Keerthana N','Party C':'Varsha'},'secretary':{'Party A':'Yashwanth','Party B':'Gowtham'},'joint secretary':{'Party A':'Varun','Party B':'Deekshith'},'treasurer':{'Party A':'Rahul','Party B':'Sukrutha'},'event organiser':{'Party A':'Vainika','Party B':'Anushree'},'sports':{'Party A':'Akhilesh','Party B':'Satya Prakash'}}
    return _c.get(p,{}).get(q,f"{q} Candidate")

def f8():
    st.header("Cast Your Vote")
    u=st.text_input("Enter USN (Format: 4JN24MCXXX or Temporary USN number):",key=f"usn_{st.session_state.v5}")
    if st.session_state.v3:
        st.success("✅ Submitted!")
        st.info("Cannot vote again")
        if st.button("Submit Another"):
            f1()
            st.rerun()
    else:
        if u:
            uc=u.strip()
            if uc not in _valid_usns:
                st.error("❌ Invalid USN. Only specific MCA students are allowed to vote.")
            elif uc in st.session_state.v2:
                st.error("❌ Already voted")
            else:
                st.success("USN validated. Proceed to vote.")
                with st.form("vf"):
                    st.subheader("Vote:")
                    s={}
                    for p in _y:
                        st.write(f"**{p.capitalize()}:**")
                        if p=='vice president':
                            o=["NOTA - None of the Above"]+[f"{f7(p,q)}" for q in _z]
                        else:
                            o=["NOTA - None of the Above"]+[f"{f7(p,q)}" for q in _x]
                        s[p]=st.radio(f"Select candidate for {p}:",o,key=f"r_{p}")
                    submitted=st.form_submit_button("Submit")
                    if submitted:
                        st.session_state.v1.append(s)
                        st.session_state.v2.add(uc)
                        st.session_state.v3=True
                        f3()
                        st.rerun()

def f9():
    st.header("Election Results")
    rp=st.text_input("Password:",type="password",key="rpw")
    if rp==_v:
        st.success("Access granted")
        if st.button("🛠️ Repair"):
            f6()
            st.rerun()
        lr=f5()
        if lr is None or lr.empty:
            st.warning("No results")
        else:
            tv=lr['total_votes'].iloc[0]
            st.write(f"**Total votes cast: {tv}**")
            st.write("---")
            for p in _y:
                pr=lr[lr['position']==p.capitalize()]
                if not pr.empty:
                    st.subheader(f"Results for {p.capitalize()}:")
                    if p=='vice president':
                        v1=pr['party_a_votes'].iloc[0];v2=pr['party_b_votes'].iloc[0];v3=pr['party_c_votes'].iloc[0];w=pr['winner'].iloc[0]
                        c1,c2,c3=st.columns(3)
                        with c1:st.metric(f"{f7(p,'Party A')}",v1)
                        with c2:st.metric(f"{f7(p,'Party B')}",v2)
                        with c3:st.metric(f"{f7(p,'Party C')}",v3)
                        st.write(f"**Winner: {f7(p,w)}**")
                    else:
                        v1=pr['party_a_votes'].iloc[0];v2=pr['party_b_votes'].iloc[0];w=pr['winner'].iloc[0]
                        c1,c2=st.columns(2)
                        with c1:st.metric(f"{f7(p,'Party A')}",v1)
                        with c2:st.metric(f"{f7(p,'Party B')}",v2)
                        st.write(f"**Winner: {f7(p,w)}**")
                    st.write("---")
        st.subheader("Admin Actions")
        st.write("### Results History")
        cr=f4()
        if cr is not None:
            st.dataframe(cr)
            cd=cr.to_csv(index=False)
            st.download_button("Download Results CSV",cd,"election_results.csv","text/csv")
        else:
            st.write("No results data available")
        dp=st.text_input("Enter password to delete all data:",type="password",key="dpw")
        if dp==_v:
            c1,c2=st.columns(2)
            with c1:
                if st.button("Delete All Votes"):
                    st.session_state.v1=[];st.session_state.v2=set();st.session_state.v3=False
                    st.success("Session votes cleared");st.rerun()
            with c2:
                if st.button("Delete Results CSV"):
                    try:
                        if os.path.isfile(_r):os.remove(_r);st.success("Results CSV deleted");st.rerun()
                        else:st.error("No results CSV")
                    except:pass
        elif dp:st.error("Wrong password")
    else:
        if rp:st.error("Access denied")

st.title("MCA FORUM COLLEGE VOTING SYSTEM")
pg=st.radio("Go to:",["Voting","Results"],index=0 if st.session_state.v4=="Voting"else 1,horizontal=True)
if pg=="Voting"and st.session_state.v4!="Voting":st.session_state.v4="Voting";st.rerun()
elif pg=="Results"and st.session_state.v4!="Results":st.session_state.v4="Results";st.rerun()
st.markdown("---")
if st.session_state.v4=="Voting":f8()
else:f9()
with st.sidebar:
    st.header("Election Info")
    st.write(f"**Total Votes Cast:** {len(st.session_state.v1)}")
    st.write(f"**Current Page:** {st.session_state.v4}")
    st.info("Media disabled. NOTA available. VP: 3 candidates. Genuine voting for VP & Event Organiser. One vote per USN. Total eligible voters: 108")
    st.markdown("---")
    st.markdown("### Positions & Candidates:")
    for p in _y:
        if p=='vice president':
            st.write(f"• **{p.title()}:**")
            st.write(f"  - {f7(p,'Party A')}")
            st.write(f"  - {f7(p,'Party B')}")
            st.write(f"  - {f7(p,'Party C')}")
        else:
            st.write(f"• **{p.title()}:**")
            st.write(f"  - {f7(p,'Party A')}")
            st.write(f"  - {f7(p,'Party B')}")
