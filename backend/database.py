"""Server-only database configuration. Never expose DATABASE_URL to Vite."""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env', override=False, encoding='utf-8-sig')

def build_engine(connection_string=None):
    raw = connection_string or os.getenv('DATABASE_URL') or f"sqlite:///{(ROOT / 'patikitap.db').as_posix()}"
    url = make_url(raw)
    options = {'pool_pre_ping': True}
    if url.get_backend_name() in ('postgres', 'postgresql'):
        url = url.set(drivername='postgresql+psycopg')
        args = {'connect_timeout': 10}
        host = (url.host or '').lower()
        if host.endswith(('.supabase.co', '.supabase.com')):
            args['sslmode'] = 'require'
        if url.port == 6543:
            args['prepare_threshold'] = None
        options.update(connect_args=args, pool_size=3, max_overflow=2)
    elif url.get_backend_name() != 'sqlite':
        raise ValueError('Yalnızca PostgreSQL ve SQLite desteklenir.')
    result = create_engine(url, **options)
    return result.execution_options(schema_translate_map={'app': 'patikitap' if result.dialect.name == 'postgresql' else None})

engine = build_engine()
