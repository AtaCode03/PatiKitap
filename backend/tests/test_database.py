from database import build_engine

def test_supabase_connection_configuration():
    engine = build_engine('postgresql://postgres.test:example@aws-0-example.pooler.supabase.com:5432/postgres')
    try:
        assert engine.url.drivername == 'postgresql+psycopg'
        assert engine.get_execution_options()['schema_translate_map'] == {'app': 'patikitap'}
        args, kwargs = engine.dialect.create_connect_args(engine.url)
        assert engine.pool.size() == 3
    finally:
        engine.dispose()

def test_sqlite_has_no_schema():
    engine = build_engine('sqlite://')
    try:
        assert engine.get_execution_options()['schema_translate_map'] == {'app': None}
    finally:
        engine.dispose()

def test_production_requires_postgres(monkeypatch):
    import pytest
    monkeypatch.setenv('APP_ENV','production')
    monkeypatch.delenv('DATABASE_URL',raising=False)
    with pytest.raises(ValueError):build_engine()
    with pytest.raises(ValueError):build_engine('sqlite://')
