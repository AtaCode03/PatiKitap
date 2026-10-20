from operations import WindowLimiter
from fastapi import FastAPI
from fastapi.testclient import TestClient
from operations import OperationalMiddleware

def test_rate_limiter_expires_and_is_bounded():
    current=[0]
    limiter=WindowLimiter(read_limit=2,write_limit=1,capacity=2,clock=lambda:current[0])
    assert limiter.allow('a')[0]
    assert limiter.allow('a')[0]
    assert not limiter.allow('a')[0]
    assert limiter.allow('a',True)[0]
    assert not limiter.allow('a',True)[0]
    current[0]=61
    assert limiter.allow('a')[0]
    limiter.allow('b');limiter.allow('c')
    assert len(limiter.entries)<=2

def test_operational_headers_429_and_safe_error():
    app=FastAPI();app.add_middleware(OperationalMiddleware,limiter=WindowLimiter(read_limit=1))
    @app.get('/api/test')
    def test():return {'ok':True}
    @app.get('/broken')
    def broken():raise RuntimeError('private credential should never be returned')
    with TestClient(app,raise_server_exceptions=False) as c:
        r=c.get('/api/test');assert r.status_code==200
        assert r.headers['x-request-id'] and r.headers['cache-control']=='no-store'
        assert r.headers['x-content-type-options']=='nosniff'
        r=c.get('/api/test');assert r.status_code==429 and int(r.headers['retry-after'])>0
        r=c.get('/broken');assert r.status_code==500 and 'private credential' not in r.text
