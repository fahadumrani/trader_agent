import os, sys, json, types, tempfile, base64
os.environ['MPLBACKEND']='Agg'
import numpy as np
import pandas as pd

class DummyYF:
    def __init__(self): self.frame=None
    def download(self,*args,**kwargs): return self.frame.copy()
dummy_yf=DummyYF()
sys.modules['yfinance']=dummy_yf

NB='/data/crypto_sentinel_self_learning_github_FIXED.ipynb'
nb=json.load(open(NB))
ns={}
for idx in [2,3,4,5,6]:
    exec(''.join(nb['cells'][idx]['source']),ns)
# Define report/loop without launching it.
loop=''.join(line for line in nb['cells'][7]['source'] if line.strip()!='run_sentinel()')
exec(loop,ns)

with tempfile.TemporaryDirectory() as td:
    ns['BASE_DIR']=td
    ns['STATE_FILE']=os.path.join(td,'state.json')
    ns['TRADES_FILE']=os.path.join(td,'trades.csv')
    ns['SIGNALS_FILE']=os.path.join(td,'signals.csv')
    ns['EQUITY_FILE']=os.path.join(td,'equity.csv')
    ns['REPORT_PNG']=os.path.join(td,'report.png')

    # Realistic synthetic candles with multiple regimes and both target classes.
    n=2600
    rng=np.random.default_rng(9)
    returns=0.00008+0.0025*np.sin(np.arange(n)/17)+rng.normal(0,0.0022,n)
    close=60000*np.exp(np.cumsum(returns))
    index=pd.date_range('2026-01-01',periods=n,freq='5min',tz='UTC')
    frame=pd.DataFrame({
        'Open':close*(1+rng.normal(0,0.0002,n)),
        'High':close*(1+np.abs(rng.normal(0.0012,0.0005,n))),
        'Low':close*(1-np.abs(rng.normal(0.0012,0.0005,n))),
        'Close':close,
        'Volume':rng.lognormal(8,0.55,n),
    },index=index)

    features=ns['indicators'](frame)
    assert features.index[-1]==frame.index[-1], 'Latest feature row was dropped'
    assert pd.isna(features.target.iloc[-1]), 'Latest row must be inference-only'
    labeled=features.target.notna().sum()
    assert labeled < len(features) and labeled >= len(features)-ns['TARGET_HORIZON_BARS']
    assert features.loc[features.target.notna(),'target'].nunique()==2

    probability,accuracy,auc,rows=ns['ml_probability'](features,'BTC-USD')
    assert rows==labeled
    assert all(np.isfinite(x) for x in [probability,accuracy,auc])
    assert all(0<=x<=1 for x in [probability,accuracy,auc])
    model_path=os.path.join(td,'model_BTC_USD.json')
    assert os.path.exists(model_path)
    model=json.load(open(model_path))
    assert model['labeled_rows']==rows and model['horizon_bars']==3

    # Timezone-safe download + history merge + dedup.
    dummy_yf.frame=frame.tail(2100).copy()
    old=frame.head(700).copy(); old.index=old.index.tz_convert('Asia/Karachi')
    old.to_csv(os.path.join(td,'market_BTC_USD_5m.csv'))
    merged=ns['download_5m']('BTC-USD')
    assert isinstance(merged.index,pd.DatetimeIndex) and str(merged.index.tz)=='UTC'
    assert merged.index.is_unique and merged.index.is_monotonic_increasing
    assert len(merged)>2000

    setup=ns['score_symbol']('BTC-USD',merged)
    assert 0<=setup['score']<=100 and setup['learning_rows']>500
    assert isinstance(setup['learned_ready'],bool)

    # Accounting invariants: no negative cash; round-trip reconciles.
    state=ns['fresh_state']()
    entry_setup={'symbol':'BTC-USD','price':float(merged.Close.iloc[-1]),'atr':float(setup['atr']),'score':75}
    ns['enter'](state,entry_setup)
    assert state['position'] is not None and state['cash']>=0
    before_equity=ns['total_equity'](state,{'BTC-USD':entry_setup['price']})
    ns['exit_position'](state,entry_setup['price']*1.02,'unit_test')
    assert state['position'] is None and state['cash']>0 and os.path.exists(ns['TRADES_FILE'])
    assert np.isfinite(before_equity)

    # GitHub URL and large-file download fallback.
    assert ns['GITHUB_REPO_API']=='https://api.github.com/repos/fahadumrani/trader_agent'
    class Resp:
        def __init__(self,status=200,obj=None,content=b''):
            self.status_code=status; self._obj=obj; self.content=content; self.ok=200<=status<300
        def json(self): return self._obj
        def raise_for_status(self):
            if not self.ok: raise RuntimeError(f'HTTP {self.status_code}')
    class FakeRequests:
        def __init__(self): self.calls=[]
        def get(self,url,**kwargs):
            self.calls.append(('GET_DIRECT',url))
            return Resp(obj={'default_branch':'main'})
        def request(self,method,url,**kwargs):
            self.calls.append((method,url))
            if method=='GET' and 'download.example' in url: return Resp(content=b'large-data')
            if method=='GET': return Resp(obj={'sha':'abc','encoding':'none','content':None,'download_url':'https://download.example/file'})
            if method=='PUT': return Resp(status=200,obj={'content':{'sha':'new'}})
            raise AssertionError(method)
    fake=FakeRequests(); ns['requests']=fake; ns['GITHUB_TOKEN']='secret-for-test'
    ns['github_resolve_branch']()
    content,sha=ns['github_get']('runtime/large.csv')
    assert content==b'large-data' and sha=='abc'
    assert ns['github_put']('runtime/test.json',b'{}','test') is True
    assert all(not url.startswith('{') for _,url in fake.calls), fake.calls

print('ALL TESTS PASSED')
