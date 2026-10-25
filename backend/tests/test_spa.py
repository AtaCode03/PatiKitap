from fastapi import FastAPI
from fastapi.testclient import TestClient
from spa import SPAStaticFiles

def test_history_fallback_preserves_api_and_asset_errors(tmp_path):
    (tmp_path/'index.html').write_text('<html>PatiKitap</html>',encoding='utf-8')
    (tmp_path/'main.js').write_text('console.log(1)',encoding='utf-8')
    app=FastAPI()
    @app.get('/api/health')
    def health(): return {'ok':True}
    app.mount('/',SPAStaticFiles(directory=tmp_path,html=True))
    with TestClient(app) as client:
        for path in ['/','/account','/admin','/impact','/auth/login','/auth/register','/auth/forgot-password','/auth/reset-password']:
            result=client.get(path)
            assert result.status_code==200
            assert 'text/html' in result.headers['content-type']
        assert client.head('/admin').status_code==200
        assert client.get('/api/health').json()=={'ok':True}
        for path in ['/api/missing','/assets/missing.js','/missing','/auth/missing']:
            assert client.get(path).status_code==404
        assert client.post('/admin').status_code==405
        assert client.get('/main.js').status_code==200
