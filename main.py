import streamlit as st
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

def _m(_n, _o):
    _p = 0
    _q = 0
    _r = 0
    for _s in st.session_state.v1:
        if _n in _s:
            _t = _s[_n]
            if _n == 'vice president':
                if 'Geetha' in _t: _p += 1
                elif 'Keerthana N' in _t: _q += 1
                elif 'Varsha' in _t: _r += 1
            elif _n == 'event organiser':
                if 'Vainika' in _t: _p += 1
                elif 'Anushree' in _t: _q += 1
            else:
                if 'Shrinivas' in _t: _p += 1
                elif 'Pavan' in _t: _q += 1
                elif 'Yashwanth' in _t: _p += 1
                elif 'Gowtham' in _t: _q += 1
                elif 'Varun' in _t: _p += 1
                elif 'Deekshith' in _t: _q += 1
                elif 'Rahul' in _t: _p += 1
                elif 'Sukrutha' in _t: _q += 1
                elif 'Akhilesh' in _t: _p += 1
                elif 'Satya Prakash' in _t: _q += 1
    if _n == 'vice president':
        _u = {'Party A': _p, 'Party B': _q, 'Party C': _r}
        _v = max(_u, key=_u.get) if max(_u.values()) > 0 else 'No Votes'
        return _p, _q, _r, _v
    else:
        _u = {'Party A': _p, 'Party B': _q}
        _v = max(_u, key=_u.get) if max(_u.values()) > 0 else 'No Votes'
        return _p, _q, 0, _v

def _w():
    _x = len(st.session_state.v1)
    _y = []
    _z = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for _aa in _b:
        _ab, _ac, _ad, _ae = _m(_aa, _x)
        _y.append({'timestamp': _z, 'position': _aa.capitalize(), 'total_votes': _x, 'party_a_votes': _ab, 'party_b_votes': _ac, 'party_c_votes': _ad, 'winner': _ae})
    _af = pd.DataFrame(_y)
    if os.path.isfile(_h):
        _af.to_csv(_h, mode='a', header=False, index=False)
    else:
        _af.to_csv(_h, mode='w', header=True, index=False)
    return _af

def _ag():
    try:
        if os.path.isfile(_h):
            _ah = pd.read_csv(_h, on_bad_lines='skip')
            _ai = ['timestamp', 'position', 'total_votes', 'party_a_votes', 'party_b_votes', 'party_c_votes', 'winner']
            if not all(_aj in _ah.columns for _aj in _ai):
                return None
            return _ah
        return None
    except:
        return None

def _ak():
    try:
        if os.path.isfile(_h):
            _al = pd.read_csv(_h, on_bad_lines='skip')
            if _al.empty:
                return None
            if 'timestamp' not in _al.columns:
                return None
            _am = _al['timestamp'].max()
            return _al[_al['timestamp'] == _am]
        return None
    except:
        return None

def _an():
    try:
        if os.path.isfile(_h):
            _ao = f"election_results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(_h, _ao)
            st.success(f"Backup: {_ao}")
        if st.session_state.v1:
            _ap = _w()
            st.success("CSV recreated")
            return _ap
        else:
            st.info("No votes")
            return None
    except:
        return None

def _aq(_ar, _as):
    _at = {
        'president': {'Party A': 'Shrinivas', 'Party B': 'Pavan'},
        'vice president': {'Party A': 'Geetha', 'Party B': 'Keerthana N', 'Party C': 'Varsha'},
        'secretary': {'Party A': 'Yashwanth', 'Party B': 'Gowtham'},
        'joint secretary': {'Party A': 'Varun', 'Party B': 'Deekshith'},
        'treasurer': {'Party A': 'Rahul', 'Party B': 'Sukrutha'},
        'event organiser': {'Party A': 'Vainika', 'Party B': 'Anushree'},
        'sports': {'Party A': 'Akhilesh', 'Party B': 'Satya Prakash'}
    }
    return _at.get(_ar, {}).get(_as, f"{_as} Candidate")

def _au():
    st.header("Cast Your Vote")
    _av = st.text_input("Enter USN:", key=f"usn_{st.session_state.v5}")
    if st.session_state.v3:
        st.success("✅ Submitted!")
        st.info("Cannot vote again")
        if st.button("Submit Another"):
            _l()
            st.rerun()
    else:
        if _av:
            _aw = _av.strip()
            if _aw not in _valid_usns:
                st.error("❌ Invalid USN. Only specific MCA students are allowed to vote.")
            elif _aw in st.session_state.v2:
                st.error("❌ Already voted")
            else:
                st.success("USN validated. Proceed to vote.")
                with st.form("vf"):
                    st.subheader("Vote:")
                    _ax = {}
                    for _ay in _b:
                        st.write(f"**{_ay.capitalize()}:**")
                        if _ay == 'vice president':
                            _az = ["NOTA - None of the Above"] + [f"{_aq(_ay, _ba)}" for _ba in _c]
                        else:
                            _az = ["NOTA - None of the Above"] + [f"{_aq(_ay, _ba)}" for _ba in _a]
                        _ax[_ay] = st.radio(f"Select candidate for {_ay}:", _az, key=f"r_{_ay}")
                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        st.session_state.v1.append(_ax)
                        st.session_state.v2.add(_aw)
                        st.session_state.v3 = True
                        _w()
                        st.rerun()

def _bb():
    st.header("Election Results")
    _bc = st.text_input("Password:", type="password", key="rpw")
    if _bc == _g:
        st.success("Access granted")
        if st.button("🛠️ Repair"):
            _an()
            st.rerun()
        _bd = _ak()
        if _bd is None or _bd.empty:
            st.warning("No results")
        else:
            _be = _bd['total_votes'].iloc[0]
            st.write(f"**Total votes cast: {_be}**")
            st.write("---")
            for _bf in _b:
                _bg = _bd[_bd['position'] == _bf.capitalize()]
                if not _bg.empty:
                    st.subheader(f"Results for {_bf.capitalize()}:")
                    if _bf == 'vice president':
                        _bh = _bg['party_a_votes'].iloc[0]
                        _bi = _bg['party_b_votes'].iloc[0]
                        _bj = _bg['party_c_votes'].iloc[0]
                        _bk = _bg['winner'].iloc[0]
                        _bl, _bm, _bn = st.columns(3)
                        with _bl:
                            st.metric(f"{_aq(_bf, 'Party A')}", _bh)
                        with _bm:
                            st.metric(f"{_aq(_bf, 'Party B')}", _bi)
                        with _bn:
                            st.metric(f"{_aq(_bf, 'Party C')}", _bj)
                        st.write(f"**Winner: {_aq(_bf, _bk)}**")
                    else:
                        _bo = _bg['party_a_votes'].iloc[0]
                        _bp = _bg['party_b_votes'].iloc[0]
                        _bq = _bg['winner'].iloc[0]
                        _br, _bs = st.columns(2)
                        with _br:
                            st.metric(f"{_aq(_bf, 'Party A')}", _bo)
                        with _bs:
                            st.metric(f"{_aq(_bf, 'Party B')}", _bp)
                        st.write(f"**Winner: {_aq(_bf, _bq)}**")
                    st.write("---")
        st.subheader("Admin Actions")
        st.write("### Results History")
        _bt = _ag()
        if _bt is not None:
            st.dataframe(_bt)
            _bu = _bt.to_csv(index=False)
            st.download_button("Download Results CSV", _bu, "election_results.csv", "text/csv")
        else:
            st.write("No results data available")
        _bv = st.text_input("Enter password to delete all data:", type="password", key="dpw")
        if _bv == _g:
            _bw, _bx = st.columns(2)
            with _bw:
                if st.button("Delete All Votes"):
                    st.session_state.v1 = []
                    st.session_state.v2 = set()
                    st.session_state.v3 = False
                    st.success("Session votes cleared")
                    st.rerun()
            with _bx:
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
        elif _bv:
            st.error("Wrong password")
    else:
        if _bc:
            st.error("Access denied")

st.title("MCA FORUM COLLEGE VOTING SYSTEM")
_by = st.radio("Go to:", ["Voting", "Results"], index=0 if st.session_state.v4 == "Voting" else 1, horizontal=True)
if _by == "Voting" and st.session_state.v4 != "Voting":
    st.session_state.v4 = "Voting"
    st.rerun()
elif _by == "Results" and st.session_state.v4 != "Results":
    st.session_state.v4 = "Results"
    st.rerun()
st.markdown("---")
if st.session_state.v4 == "Voting":
    _au()
else:
    _bb()
with st.sidebar:
    st.header("Election Info")
    st.write(f"**Total Votes Cast:** {len(st.session_state.v1)}")
    st.write(f"**Current Page:** {st.session_state.v4}")
    st.markdown("---")
    st.markdown("### Positions & Candidates:")
    for _bz in _b:
        if _bz == 'vice president':
            st.write(f"• **{_bz.title()}:**")
            st.write(f"  - {_aq(_bz, 'Party A')}")
            st.write(f"  - {_aq(_bz, 'Party B')}")
            st.write(f"  - {_aq(_bz, 'Party C')}")
        else:
            st.write(f"• **{_bz.title()}:**")
            st.write(f"  - {_aq(_bz, 'Party A')}")
            st.write(f"  - {_aq(_bz, 'Party B')}")
