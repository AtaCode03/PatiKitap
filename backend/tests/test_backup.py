import pytest
from sqlalchemy import create_engine,select,func
from models import Base,Book
from backup import export_data,validate,restore_data
from datetime import datetime,timezone

def test_backup_roundtrip_and_nonempty_target_is_protected():
    source=create_engine('sqlite://').execution_options(schema_translate_map={'app':None})
    target=create_engine('sqlite://').execution_options(schema_translate_map={'app':None})
    Base.metadata.create_all(source);Base.metadata.create_all(target)
    try:
        with source.begin() as c:
            c.execute(Book.__table__.insert(),dict(title='Yedek Kitap',author='Yazar',category='Roman',kind='Bağış',condition='İyi',location='Konya'))
        with source.connect() as c:data=export_data(c)
        assert validate(data)==1
        with target.begin() as c:restore_data(c,data)
        with target.begin() as c:
            assert c.scalar(select(func.count()).select_from(Book))==1
            with pytest.raises(ValueError,match='boş olmalı'):restore_data(c,data)
        data['tables'].pop('books')
        with pytest.raises(ValueError):validate(data)
    finally:source.dispose();target.dispose()
