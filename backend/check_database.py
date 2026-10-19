"""Read-only connection probe; does not create schemas or copy local data."""
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine

def main():
    try:
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
    except SQLAlchemyError:
        print('Bağlantı kurulamadı. Backend .env dosyasını, parolayı ve ağ erişimini kontrol edin.')
        return 1
    print(f'Bağlantı başarılı ({engine.dialect.name}).')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
