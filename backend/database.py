"""Server-only database configuration. Never expose DATABASE_URL to Vite."""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env', override=False, encoding='utf-8-sig')

def build_engine(connection_string=None):
    raw = connection_string or os.getenv('DATABASE_URL')
    if not raw:raise ValueError('DATABASE_URL zorunlu; uygulama yalnızca PostgreSQL kullanır.')
    if os.getenv('APP_ENV')=='production' and not (connection_string or os.getenv('DATABASE_URL')):
        raise ValueError('Production ortamında DATABASE_URL zorunlu.')
    url = make_url(raw)
    if connection_string is None and url.get_backend_name() not in ('postgres','postgresql'):
        raise ValueError('Uygulama bağlantısı PostgreSQL olmalı; SQLite yalnızca izole testler içindir.')
    options = {'pool_pre_ping': True, 'hide_parameters': True}
    if url.get_backend_name() in ('postgres', 'postgresql'):
        url = url.set(drivername='postgresql+psycopg')
        args = {'connect_timeout': 10}
        host = (url.host or '').lower()
        if host.endswith(('.supabase.co', '.supabase.com')):
            args['sslmode'] = 'require'
        if url.port == 6543:
            args['prepare_threshold'] = None
        options.update(connect_args=args, pool_size=3, max_overflow=2, pool_timeout=10)
    elif os.getenv('APP_ENV')=='production':
        raise ValueError('Production ortamında PostgreSQL zorunlu.')
    elif url.get_backend_name() != 'sqlite':
        raise ValueError('Yalnızca PostgreSQL ve SQLite desteklenir.')
    result = create_engine(url, **options)
    return result.execution_options(schema_translate_map={'app': 'patikitap' if result.dialect.name == 'postgresql' else None})

engine = build_engine()
