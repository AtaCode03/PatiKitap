"""Provision the explicitly approved backend login; never log its password."""
import os,secrets
from dotenv import set_key
from sqlalchemy import text
from sqlalchemy.engine import make_url
from psycopg import sql
from database import ROOT,build_engine

def main():
    source=os.getenv('ADMIN_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not source: raise SystemExit('Yönetim bağlantısı gerekli.')
    admin=build_engine(source)
    password=secrets.token_urlsafe(40)
    with admin.begin() as connection:
        role=connection.execute(text("select rolname from pg_roles where rolname='patikitap_runtime'")).scalar_one_or_none()
        if role is None: raise SystemExit('Önce runtime-role migration uygulanmalı.')
        connection.exec_driver_sql(sql.SQL('ALTER ROLE patikitap_runtime LOGIN PASSWORD {}').format(sql.Literal(password)).as_string())
    url=make_url(source)
    suffix='.'+url.username.split('.',1)[1] if '.pooler.supabase.com' in (url.host or '') and '.' in (url.username or '') else ''
    target=url.set(drivername='postgresql+psycopg',username='patikitap_runtime'+suffix,password=password).render_as_string(hide_password=False)
    runtime=build_engine(target)
    try:
        with runtime.connect() as connection:
            assert connection.execute(text('select current_user')).scalar_one()=='patikitap_runtime'
            assert not connection.execute(text("select has_schema_privilege(current_user,'patikitap','create')")).scalar_one()
            assert not connection.execute(text("select has_table_privilege(current_user,'auth.users','select')")).scalar_one()
            connection.execute(text('select count(*) from patikitap.books')).scalar_one()
        set_key(ROOT/'.env','ADMIN_DATABASE_URL',source,encoding='utf-8')
        set_key(ROOT/'.env','DATABASE_URL',target,encoding='utf-8')
        print('Runtime bağlantısı doğrulandı; .env güncellendi. Kimlik bilgileri yazdırılmadı.')
    finally:
        runtime.dispose();admin.dispose()
if __name__=='__main__':
    try:main()
    except Exception as exc:raise SystemExit('Kurulum tamamlanamadı: '+type(exc).__name__+'. Bağlantıyı kontrol edin; .env güncellenmediyse mevcut bağlantı korunur.') from None
