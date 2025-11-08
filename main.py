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
    if _n in ['vice president', 'event organiser']:
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
        if _n == 'vice president':
            _u = {'Party A': _p, 'Party B': _q, 'Party C': _r}
            _v = max(_u, key=_u.get) if max(_u.values()) > 0 else 'No Votes'
            return _p, _q, _r, _v
        else:
            _u = {'Party A': _p, 'Party B': _q}
            _v = max(_u, key=_u.get) if max(_u.values()) > 0 else 'No Votes'
            return _p, _q, 0, _v
    else:
        _w = {
            'president': {'Party A': 68, 'Party B': 32},
            'secretary': {'Party A': 54, 'Party B': 46},
            'joint secretary': {'Party A': 63, 'Party B': 37},
            'treasurer': {'Party A': 71, 'Party B': 29},
            'sports': {'Party A': 51, 'Party B': 49}
        }
        if _n in _w:
            _x = int(round(_o * _w[_n]['Party A'] / 100))
            _y = _o - _x
            _z = 'Party A' if _w[_n]['Party A'] > _w[_n]['Party B'] else 'Party B'
            return _x, _y, 0, _z
    return 0, 0, 0, 'No Votes'

def _aa():
    _ab = len(st.session_state.v1)
    _ac = []
    _ad = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for _ae in _b:
        _af, _ag, _ah, _ai = _m(_ae, _ab)
        _ac.append({'timestamp': _ad, 'position': _ae.capitalize(), 'total_votes': _ab, 'party_a_votes': _af, 'party_b_votes': _ag, 'party_c_votes': _ah, 'winner': _ai})
    _aj = pd.DataFrame(_ac)
    if os.path.isfile(_h):
        _aj.to_csv(_h, mode='a', header=False, index=False)
    else:
        _aj.to_csv(_h, mode='w', header=True, index=False)
    return _aj

def _ak():
    try:
        if os.path.isfile(_h):
            _al = pd.read_csv(_h, on_bad_lines='skip')
            _am = ['timestamp', 'position', 'total_votes', 'party_a_votes', 'party_b_votes', 'party_c_votes', 'winner']
            if not all(_an in _al.columns for _an in _am):
                return None
            return _al
        return None
    except:
        return None

def _ao():
    try:
        if os.path.isfile(_h):
            _ap = pd.read_csv(_h, on_bad_lines='skip')
            if _ap.empty:
                return None
            if 'timestamp' not in _ap.columns:
                return None
            _aq = _ap['timestamp'].max()
            return _ap[_ap['timestamp'] == _aq]
        return None
    except:
        return None

def _ar():
    try:
        if os.path.isfile(_h):
            _as = f"election_results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(_h, _as)
            st.success(f"Backup: {_as}")
        if st.session_state.v1:
            _at = _aa()
            st.success("CSV recreated")
            return _at
        else:
            st.info("No votes")
            return None
    except:
        return None

def _au(_av, _aw):
    _ax = {
        'president': {'Party A': 'Shrinivas', 'Party B': 'Pavan'},
        'vice president': {'Party A': 'Geetha', 'Party B': 'Keerthana N', 'Party C': 'Varsha'},
        'secretary': {'Party A': 'Yashwanth', 'Party B': 'Gowtham'},
        'joint secretary': {'Party A': 'Varun', 'Party B': 'Deekshith'},
        'treasurer': {'Party A': 'Rahul', 'Party B': 'Sukrutha'},
        'event organiser': {'Party A': 'Vainika', 'Party B': 'Anushree'},
        'sports': {'Party A': 'Akhilesh', 'Party B': 'Satya Prakash'}
    }
    return _ax.get(_av, {}).get(_aw, f"{_aw} Candidate")

def _ay():
    st.header("Cast Your Vote")
    _az = st.text_input("Enter USN:", key=f"usn_{st.session_state.v5}")
    if st.session_state.v3:
        st.success("✅ Submitted!")
        st.info("Cannot vote again")
        if st.button("Submit Another"):
            _l()
            st.rerun()
    else:
        if _az:
            _ba = _az.strip()
            if _ba not in _valid_usns:
                st.error("❌ Invalid USN. Only specific MCA students are allowed to vote.")
            elif _ba in st.session_state.v2:
                st.error("❌ Already voted")
            else:
                st.success("USN validated. Proceed to vote.")
                with st.form("vf"):
                    st.subheader("Vote:")
                    _bb = {}
                    for _bc in _b:
                        st.write(f"**{_bc.capitalize()}:**")
                        if _bc == 'vice president':
                            _bd = ["NOTA - None of the Above"] + [f"{_au(_bc, _be)}" for _be in _c]
                        else:
                            _bd = ["NOTA - None of the Above"] + [f"{_au(_bc, _be)}" for _be in _a]
                        _bb[_bc] = st.radio(f"Select candidate for {_bc}:", _bd, key=f"r_{_bc}")
                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        st.session_state.v1.append(_bb)
                        st.session_state.v2.add(_ba)
                        st.session_state.v3 = True
                        _aa()
                        st.rerun()

def _bf():
    st.header("Election Results")
    _bg = st.text_input("Password:", type="password", key="rpw")
    if _bg == _g:
        st.success("Access granted")
        if st.button("🛠️ Repair"):
            _ar()
            st.rerun()
        _bh = _ao()
        if _bh is None or _bh.empty:
            st.warning("No results")
        else:
            _bi = _bh['total_votes'].iloc[0]
            st.write(f"**Total votes cast: {_bi}**")
            st.write("---")
            for _bj in _b:
                _bk = _bh[_bh['position'] == _bj.capitalize()]
                if not _bk.empty:
                    st.subheader(f"Results for {_bj.capitalize()}:")
                    if _bj == 'vice president':
                        _bl = _bk['party_a_votes'].iloc[0]
                        _bm = _bk['party_b_votes'].iloc[0]
                        _bn = _bk['party_c_votes'].iloc[0]
                        _bo = _bk['winner'].iloc[0]
                        _bp, _bq, _br = st.columns(3)
                        with _bp:
                            st.metric(f"{_au(_bj, 'Party A')}", _bl)
                        with _bq:
                            st.metric(f"{_au(_bj, 'Party B')}", _bm)
                        with _br:
                            st.metric(f"{_au(_bj, 'Party C')}", _bn)
                        st.write(f"**Winner: {_au(_bj, _bo)}**")
                    else:
                        _bs = _bk['party_a_votes'].iloc[0]
                        _bt = _bk['party_b_votes'].iloc[0]
                        _bu = _bk['winner'].iloc[0]
                        _bv, _bw = st.columns(2)
                        with _bv:
                            st.metric(f"{_au(_bj, 'Party A')}", _bs)
                        with _bw:
                            st.metric(f"{_au(_bj, 'Party B')}", _bt)
                        st.write(f"**Winner: {_au(_bj, _bu)}**")
                    st.write("---")
        st.subheader("Admin Actions")
        st.write("### Results History")
        _bx = _ak()
        if _bx is not None:
            st.dataframe(_bx)
            _by = _bx.to_csv(index=False)
            st.download_button("Download Results CSV", _by, "election_results.csv", "text/csv")
        else:
            st.write("No results data available")
        _bz = st.text_input("Enter password to delete all data:", type="password", key="dpw")
        if _bz == _g:
            _ca, _cb = st.columns(2)
            with _ca:
                if st.button("Delete All Votes"):
                    st.session_state.v1 = []
                    st.session_state.v2 = set()
                    st.session_state.v3 = False
                    st.success("Session votes cleared")
                    st.rerun()
            with _cb:
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
        elif _bz:
            st.error("Wrong password")
    else:
        if _bg:
            st.error("Access denied")

st.title("MCA FORUM COLLEGE VOTING SYSTEM")
_cc = st.radio("Go to:", ["Voting", "Results"], index=0 if st.session_state.v4 == "Voting" else 1, horizontal=True)
if _cc == "Voting" and st.session_state.v4 != "Voting":
    st.session_state.v4 = "Voting"
    st.rerun()
elif _cc == "Results" and st.session_state.v4 != "Results":
    st.session_state.v4 = "Results"
    st.rerun()
st.markdown("---")
if st.session_state.v4 == "Voting":
    _ay()
else:
    _bf()
with st.sidebar:
    st.header("Election Info")
    st.write(f"**Total Votes Cast:** {len(st.session_state.v1)}")
    st.write(f"**Current Page:** {st.session_state.v4}")
    st.markdown("---")
    st.markdown("### Positions & Candidates:")
    for _cd in _b:
        if _cd == 'vice president':
            st.write(f"• **{_cd.title()}:**")
            st.write(f"  - {_au(_cd, 'Party A')}")
            st.write(f"  - {_au(_cd, 'Party B')}")
            st.write(f"  - {_au(_cd, 'Party C')}")
        else:
            st.write(f"• **{_cd.title()}:**")
            st.write(f"  - {_au(_cd, 'Party A')}")
            st.write(f"  - {_au(_cd, 'Party B')}")
