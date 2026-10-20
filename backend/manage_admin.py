"""Explicit local admin-role management. Never invoked by the application."""
import argparse
from uuid import UUID
from sqlalchemy import text
import os
from database import build_engine

def main():
    parser=argparse.ArgumentParser(description='Verified Supabase user admin-role management')
    parser.add_argument('user_id',type=UUID)
    parser.add_argument('--action',choices=['grant','revoke'],required=True)
    args=parser.parse_args()
    admin_url=os.getenv('ADMIN_DATABASE_URL')
    if not admin_url: raise SystemExit('ADMIN_DATABASE_URL gerekli; uygulama hesabı yönetici atayamaz.')
    engine=build_engine(admin_url)
    if engine.dialect.name!='postgresql': raise SystemExit('Supabase PostgreSQL bağlantısı gerekir.')
    with engine.begin() as connection:
        confirmed=connection.execute(text('select email_confirmed_at is not null from auth.users where id=:id'),{'id':str(args.user_id)}).scalar_one_or_none()
        if not confirmed: raise SystemExit('Doğrulanmış kullanıcı bulunamadı.')
        if args.action=='grant':
            connection.execute(text("update auth.users set raw_app_meta_data=coalesce(raw_app_meta_data,'{}'::jsonb)||jsonb_build_object('role','admin') where id=:id"),{'id':str(args.user_id)})
        else:
            connection.execute(text("update auth.users set raw_app_meta_data=raw_app_meta_data-'role' where id=:id and raw_app_meta_data->>'role'='admin'"),{'id':str(args.user_id)})
    print('Yönetici rolü güncellendi. İlgili kullanıcı uygulamada oturumunu yenilemelidir.')
if __name__=='__main__': main()
