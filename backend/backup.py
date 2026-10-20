"""Application-data backup, validation and transactional restore to an EMPTY target."""
import argparse,json,os
from datetime import datetime,timezone
from pathlib import Path
from sqlalchemy import select,func,DateTime,text
from database import ROOT,engine,build_engine
from models import Base
TABLES=list(Base.metadata.sorted_tables)
def export_data(connection):
    return {'format':'patikitap-v1','created_at':datetime.now(timezone.utc).isoformat(),
            'tables':{t.name:[dict(r) for r in connection.execute(select(t)).mappings()] for t in TABLES}}
def validate(data):
    if data.get('format')!='patikitap-v1' or set(data.get('tables',{}))!={t.name for t in TABLES}:raise ValueError('Desteklenmeyen veya eksik yedek.')
    for t in TABLES:
        rows=data['tables'][t.name]
        if not isinstance(rows,list):raise ValueError('Geçersiz kayıt listesi.')
        for row in rows:
            if set(row)!={c.name for c in t.columns}:raise ValueError('Yedek şeması uyuşmuyor: '+t.name)
    return sum(len(rows) for rows in data['tables'].values())
def restore_data(connection,data):
    validate(data)
    if any(connection.scalar(select(func.count()).select_from(t)) for t in TABLES):raise ValueError('Geri yükleme hedefi boş olmalı. Mevcut verilere dokunulmadı.')
    for t in TABLES:
        rows=[dict(r) for r in data['tables'][t.name]]
        for r in rows:
            for col in t.columns:
                if isinstance(col.type,DateTime) and isinstance(r[col.name],str):r[col.name]=datetime.fromisoformat(r[col.name])
        if rows:connection.execute(t.insert(),rows)
        if rows and connection.dialect.name=='postgresql' and 'id' in t.c and str(t.c.id.type)=='INTEGER':
            seq=connection.scalar(text("select pg_get_serial_sequence(:table_name,'id')"),{'table_name':'patikitap.'+t.name})
            if seq:connection.execute(text('select setval(cast(:seq as regclass),:maximum,true)'),{'seq':seq,'maximum':max(r['id'] for r in rows)})
def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['export','verify','restore']);parser.add_argument('--file',type=Path);args=parser.parse_args()
    if args.action=='export':
        output=args.file or ROOT.parent/'.backups'/('patikitap-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'.json')
        with engine.connect() as c:
            if c.dialect.name=='postgresql':c=c.execution_options(isolation_level='REPEATABLE READ')
            data=export_data(c)
        output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(data,default=str,ensure_ascii=False),encoding='utf-8')
        print('Yedek oluşturuldu. Kayıt:',validate(data));return
    if not args.file:raise SystemExit('--file gerekli.')
    data=json.loads(args.file.read_text(encoding='utf-8-sig'));count=validate(data)
    if args.action=='verify':print('Yedek doğrulandı. Kayıt:',count);return
    target=os.getenv('RESTORE_DATABASE_URL')
    if not target:raise SystemExit('RESTORE_DATABASE_URL ile ayrı ve boş hedef seçilmeli.')
    target_engine=build_engine(target)
    try:
        with target_engine.begin() as c:restore_data(c,data)
        print('Boş hedefe geri yükleme tamamlandı. Kayıt:',count)
    finally:target_engine.dispose()
if __name__=='__main__':
    try:main()
    except Exception as exc:raise SystemExit('Yedek işlemi tamamlanamadı: '+type(exc).__name__+'. Hedef ve bağlantı ayarlarını kontrol edin.') from None
