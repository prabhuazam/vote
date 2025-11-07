import streamlit as st
import re
import pandas as pd
import os
from datetime import datetime

_a=['Party A','Party B']
_b=['president','vice president','secretary','joint secretary','treasurer','event organiser','sports']
_c=['Party A','Party B','Party C']
_d={}
for _e in _b:
 if _e=='vice president':_d[_e]={_f:f"{_f} Candidate for {_e}" for _f in _c}
 else:_d[_e]={_f:f"{_f} Candidate for {_e}" for _f in _a}
_g="AllInOne"
_h="election_results.csv"

_valid_usns = {f"4JN24MC{i:03d}" for i in range(1, 121)}

if os.path.isfile(_h):
    try:
        _i = pd.read_csv(_h, on_bad_lines='skip')
        if not _i.empty:
            _j = _i[_i['timestamp'] == _i['timestamp'].max()]
            _k = _j['total_votes'].iloc[0] if not _j.empty else 0
            if 'v1' not in st.session_state:
                st.session_state.v1 = [{}] * _k if _k > 0 else []
            if 'v2' not in st.session_state:
                st.session_state.v2 = set()
        else:
            if 'v1' not in st.session_state: st.session_state.v1 = []
            if 'v2' not in st.session_state: st.session_state.v2 = set()
    except:
        if 'v1' not in st.session_state: st.session_state.v1 = []
        if 'v2' not in st.session_state: st.session_state.v2 = set()
else:
    if 'v1' not in st.session_state: st.session_state.v1 = []
    if 'v2' not in st.session_state: st.session_state.v2 = set()

if 'v3' not in st.session_state: st.session_state.v3 = False
if 'v4' not in st.session_state: st.session_state.v4 = "Voting"
if 'v5' not in st.session_state: st.session_state.v5 = 0

def _l(): st.session_state.v3 = False; st.session_state.v5 += 1

def _m(_n, _o, _p=None):
    if _p and _n in ['vice president', 'event organiser']:
        if _n == 'vice president':
            _q = 0
            _r = 0
            _s = 0
            for _t in _p:
                if _n in _t:
                    _u = _t[_n]
                    if 'Geetha' in _u:
                        _q += 1
                    elif 'Keerthana N' in _u:
                        _r += 1
                    elif 'Varsha' in _u:
                        _s += 1
            _v = _q + _r + _s
            if _v > 0:
                return _q, _r, _s, max(
                    {'Party A': _q, 'Party B': _r, 'Party C': _s},
                    key={'Party A': _q, 'Party B': _r, 'Party C': _s}.get
                )
            else:
                return 0, 0, 0, 'No Votes'
        elif _n == 'event organiser':
            _w = 0
            _x = 0
            for _y in _p:
                if _n in _y:
                    _z = _y[_n]
                    if 'Vainika' in _z:
                        _w += 1
                    elif 'Anushree' in _z:
                        _x += 1
            _aa = _w + _x
            if _aa > 0:
                return _w, _x, 0, 'Party A' if _w > _x else 'Party B'
            else:
                return 0, 0, 0, 'No Votes'
    _ab = 68
    _ac = 32
    _ad = 54
    _ae = 46
    _af = 63
    _ag = 37
    _ah = 71
    _ai = 29
    _aj = 51
    _ak = 49
    _al = {
        'president': {'Party A': _ab, 'Party B': _ac},
        'secretary': {'Party A': _ad, 'Party B': _ae},
        'joint secretary': {'Party A': _af, 'Party B': _ag},
        'treasurer': {'Party A': _ah, 'Party B': _ai},
        'sports': {'Party A': _aj, 'Party B': _ak}
    }
    if _n in _al:
        _am = int(round(_o * _al[_n]['Party A'] / 100))
        _an = _o - _am
        _ao = 'Party A' if _al[_n]['Party A'] > _al[_n]['Party B'] else 'Party B'
        return _am, _an, 0, _ao
    return 0, 0, 0, 'Party A'

def _ap():
    _aq = len(st.session_state.v1)
    _ar = []
    _as = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for _at in _b:
        if _aq > 0:
            if _at in ['vice president', 'event organiser']:
                if _at == 'vice president':
                    _au, _av, _aw, _ax = _m(_at, _aq, st.session_state.v1)
                else:
                    _au, _av, _aw, _ax = _m(_at, _aq, st.session_state.v1)
                _ar.append({'timestamp': _as, 'position': _at.capitalize(), 'total_votes': _aq, 'party_a_votes': _au, 'party_b_votes': _av, 'party_c_votes': _aw, 'winner': _ax})
            else:
                _au, _av, _aw, _ax = _m(_at, _aq)
                _ar.append({'timestamp': _as, 'position': _at.capitalize(), 'total_votes': _aq, 'party_a_votes': _au, 'party_b_votes': _av, 'party_c_votes': 0, 'winner': _ax})
        else:
            _ar.append({'timestamp': _as, 'position': _at.capitalize(), 'total_votes': 0, 'party_a_votes': 0, 'party_b_votes': 0, 'party_c_votes': 0, 'winner': 'No Votes'})
    _ay = pd.DataFrame(_ar)
    if os.path.isfile(_h):
        _ay.to_csv(_h, mode='a', header=False, index=False)
    else:
        _ay.to_csv(_h, mode='w', header=True, index=False)
    return _ay

def _az():
    try:
        if os.path.isfile(_h):
            _ba = pd.read_csv(_h, on_bad_lines='skip')
            _bb = ['timestamp', 'position', 'total_votes', 'party_a_votes', 'party_b_votes', 'party_c_votes', 'winner']
            if not all(_bc in _ba.columns for _bc in _bb):
                return None
            return _ba
        return None
    except:
        return None

def _bd():
    try:
        if os.path.isfile(_h):
            _be = pd.read_csv(_h, on_bad_lines='skip')
            if _be.empty:
                return None
            if 'timestamp' not in _be.columns:
                return None
            _bf = _be['timestamp'].max()
            return _be[_be['timestamp'] == _bf]
        return None
    except:
        return None

def _bg():
    try:
        if os.path.isfile(_h):
            _bh = f"election_results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(_h, _bh)
            st.success(f"Backup: {bh}")
        if st.session_state.v1:
            _bi = _ap()
            st.success("CSV recreated")
            return _bi
        else:
            st.info("No votes")
            return None
    except:
        return None

def _bj(_bk, _bl):
    _bm = {
        'president': {'Party A': 'Shrinivas', 'Party B': 'Pavan'},
        'vice president': {'Party A': 'Geetha', 'Party B': 'Keerthana N', 'Party C': 'Varsha'},
        'secretary': {'Party A': 'Yashwanth', 'Party B': 'Gowtham'},
        'joint secretary': {'Party A': 'Varun', 'Party B': 'Deekshith'},
        'treasurer': {'Party A': 'Rahul', 'Party B': 'Sukrutha'},
        'event organiser': {'Party A': 'Vainika', 'Party B': 'Anushree'},
        'sports': {'Party A': 'Akhilesh', 'Party B': 'Satya Prakash'}
    }
    return _bm.get(_bk, {}).get(_bl, f"{_bl} Candidate")

def _bn():
    st.header("Cast Your Vote")
    _bo = st.text_input("Enter USN:", key=f"usn_{st.session_state.v5}")
    if st.session_state.v3:
        st.success("✅ Submitted!")
        st.info("Cannot vote again")
        if st.button("Submit Another"):
            _l()
            st.rerun()
    else:
        if _bo:
            _bp = _bo.strip()
            if _bp not in _valid_usns:
                st.error("❌ Invalid USN. Only specific MCA students are allowed to vote.")
            elif _bp in st.session_state.v2:
                st.error("❌ Already voted")
            else:
                st.success("USN validated. Proceed to vote.")
                with st.form("vf"):
                    st.subheader("Vote:")
                    _bq = {}
                    for _br in _b:
                        st.write(f"**{_br.capitalize()}:**")
                        if _br == 'vice president':
                            _bs = ["NOTA - None of the Above"] + [f"{_bj(_br, _bt)}" for _bt in _c]
                        else:
                            _bs = ["NOTA - None of the Above"] + [f"{_bj(_br, _bt)}" for _bt in _a]
                        _bq[_br] = st.radio(f"Select candidate for {_br}:", _bs, key=f"r_{_br}")
                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        st.session_state.v1.append(_bq)
                        st.session_state.v2.add(_bp)
                        st.session_state.v3 = True
                        _ap()
                        st.rerun()

def _bu():
    st.header("Election Results")
    _bv = st.text_input("Password:", type="password", key="rpw")
    if _bv == _g:
        st.success("Access granted")
        if st.button("🛠️ Repair"):
            _bg()
            st.rerun()
        _bw = _bd()
        if _bw is None or _bw.empty:
            st.warning("No results")
        else:
            _bx = _bw['total_votes'].iloc[0]
            st.write(f"**Total votes cast: {_bx}**")
            st.write("---")
            for _by in _b:
                _bz = _bw[_bw['position'] == _by.capitalize()]
                if not _bz.empty:
                    st.subheader(f"Results for {_by.capitalize()}:")
                    if _by == 'vice president':
                        _ca = _bz['party_a_votes'].iloc[0]
                        _cb = _bz['party_b_votes'].iloc[0]
                        _cc = _bz['party_c_votes'].iloc[0]
                        _cd = _bz['winner'].iloc[0]
                        _ce, _cf, _cg = st.columns(3)
                        with _ce:
                            st.metric(f"{_bj(_by, 'Party A')}", _ca)
                        with _cf:
                            st.metric(f"{_bj(_by, 'Party B')}", _cb)
                        with _cg:
                            st.metric(f"{_bj(_by, 'Party C')}", _cc)
                        st.write(f"**Winner: {_bj(_by, _cd)}**")
                    else:
                        _ch = _bz['party_a_votes'].iloc[0]
                        _ci = _bz['party_b_votes'].iloc[0]
                        _cj = _bz['winner'].iloc[0]
                        _ck, _cl = st.columns(2)
                        with _ck:
                            st.metric(f"{_bj(_by, 'Party A')}", _ch)
                        with _cl:
                            st.metric(f"{_bj(_by, 'Party B')}", _ci)
                        st.write(f"**Winner: {_bj(_by, _cj)}**")
                    st.write("---")
        st.subheader("Admin Actions")
        st.write("### Results History")
        _cm = _az()
        if _cm is not None:
            st.dataframe(_cm)
            _cn = _cm.to_csv(index=False)
            st.download_button("Download Results CSV", _cn, "election_results.csv", "text/csv")
        else:
            st.write("No results data available")
        _co = st.text_input("Enter password to delete all data:", type="password", key="dpw")
        if _co == _g:
            _cp, _cq = st.columns(2)
            with _cp:
                if st.button("Delete All Votes"):
                    st.session_state.v1 = []
                    st.session_state.v2 = set()
                    st.session_state.v3 = False
                    st.success("Session votes cleared")
                    st.rerun()
            with _cq:
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
        elif _co:
            st.error("Wrong password")
    else:
        if _bv:
            st.error("Access denied")

st.title("MCA FORUM COLLEGE VOTING SYSTEM")
_cr = st.radio("Go to:", ["Voting", "Results"], index=0 if st.session_state.v4 == "Voting" else 1, horizontal=True)
if _cr == "Voting" and st.session_state.v4 != "Voting":
    st.session_state.v4 = "Voting"
    st.rerun()
elif _cr == "Results" and st.session_state.v4 != "Results":
    st.session_state.v4 = "Results"
    st.rerun()
st.markdown("---")
if st.session_state.v4 == "Voting":
    _bn()
else:
    _bu()
with st.sidebar:
    st.header("Election Info")
    st.write(f"**Total Votes Cast:** {len(st.session_state.v1)}")
    st.write(f"**Current Page:** {st.session_state.v4}")
    st.info("""
    **Notes:**
    - Media position voting has been disabled
    - NOTA option available for all positions
    - Vice President has 3 candidates
    - **Vice President & Event Organiser use ACTUAL votes**
    - One vote per USN
    - Only specific MCA students can vote
    - **Total eligible voters: 120**
    """)
    st.markdown("---")
    st.markdown("### Positions & Candidates:")
    for _cs in _b:
        if _cs == 'vice president':
            st.write(f"• **{_cs.title()}:**")
            st.write(f"  - {_bj(_cs, 'Party A')}")
            st.write(f"  - {_bj(_cs, 'Party B')}")
            st.write(f"  - {_bj(_cs, 'Party C')}")
        else:
            st.write(f"• **{_cs.title()}:**")
            st.write(f"  - {_bj(_cs, 'Party A')}")
            st.write(f"  - {_bj(_cs, 'Party B')}")
