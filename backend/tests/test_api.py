import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.pool import StaticPool
import main
from auth import Identity, identity
from models import Base, Book, SupportRecord, Transaction, Profile

A='11111111-1111-4111-8111-111111111111'
B='22222222-2222-4222-8222-222222222222'
C='33333333-3333-4333-8333-333333333333'
ADMIN='44444444-4444-4444-8444-444444444444'
@pytest.fixture
def client():
    import os
    from uuid import uuid4
    from sqlalchemy.schema import CreateSchema,DropSchema
    main.app.middleware_stack=None
    previous=main.engine
    url=os.getenv('TEST_DATABASE_URL')
    schema=None
    if url:
        from database import build_engine
        base=build_engine(url)
        if base.dialect.name!='postgresql':raise ValueError('TEST_DATABASE_URL PostgreSQL olmalı.')
        schema='patikitap_test_'+uuid4().hex
        with base.begin() as c:c.execute(CreateSchema(schema))
        main.engine=base.execution_options(schema_translate_map={'app':schema})
    else:
        main.engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool).execution_options(schema_translate_map={'app':None})
        @event.listens_for(main.engine,'connect')
        def enable_fk(conn,record):conn.execute('PRAGMA foreign_keys=ON')
    try:
        if schema:Base.metadata.create_all(main.engine)
        with TestClient(main.app) as client:yield client
    finally:
        main.app.dependency_overrides.clear()
        if schema:
            assert schema.startswith('patikitap_test_') and len(schema)==47
            with main.engine.begin() as c:c.execute(DropSchema(schema,cascade=True))
        main.engine.dispose();main.engine=previous

def as_user(uid,admin=False):
    main.app.dependency_overrides[identity]=lambda:Identity(uid,'Test Okur',admin,'test')

def book(client,kind='Bağış',owner=A):
    as_user(owner)
    payload=dict(title='Test Kitabı',author='Test Yazar',category='Roman',kind=kind,price=100 if kind=='Satış' else 0,condition='İyi',location='Kampüs')
    r=client.post('/api/books',json=payload)
    assert r.status_code==201,r.text
    return r.json()

def request(client,bid,who=B,offered=None,method='campus'):
    as_user(who)
    r=client.post(f'/api/books/{bid}/requests',json={'offered_book_id':offered,'delivery_method':method})
    assert r.status_code==201,r.text
    return r.json()

def accept(client,rid,owner=A):
    as_user(owner)
    r=client.post(f'/api/requests/{rid}/action',json={'action':'accept'})
    assert r.status_code==200,r.text
    return client.get('/api/me/transactions').json()[0]

def test_auth_and_ownership(client):
    assert client.post('/api/books',json={}).status_code==401
    assert client.get('/api/admin/overview').status_code==401
    b=book(client)
    as_user(B)
    assert client.delete(f'/api/books/{b["id"]}').status_code==403
    assert client.get('/api/admin/overview').status_code==403
    assert client.patch('/api/me',json={'display_name':'Yeni Ad','city':'Konya','bio':'','is_admin':True}).status_code==422
    assert client.get('/api/me/books').json()==[]

def test_sale_requires_both_confirmations_and_records_support_once(client):
    b=book(client,'Satış');r=request(client,b['id']);tx=accept(client,r['id'])
    assert tx['price_cents']==10000 and tx['support_cents']==2000 and tx['fee_cents']==0
    assert client.post(f'/api/transactions/{tx["id"]}/confirm').status_code==409
    d=tx['deliveries'][0]
    assert client.patch(f'/api/deliveries/{d["id"]}',json={'meeting_point':'Kampüs kütüphanesi'}).status_code==200
    assert client.post(f'/api/transactions/{tx["id"]}/confirm').json()['status']=='in_delivery'
    as_user(B)
    result=client.post(f'/api/transactions/{tx["id"]}/confirm')
    assert result.json()['status']=='completed',result.text
    assert client.post(f'/api/transactions/{tx["id"]}/confirm').json()['status']=='completed'
    support=client.get('/api/support').json();assert len(support)==1 and support[0]['amount_cents']==2000
    impact=client.get('/api/impact').json();assert impact['real_support_cents']==0 and impact['completed_transactions']==1
    assert client.post(f'/api/transactions/{tx["id"]}/cancel').status_code==409
    assert client.get('/api/books').json()==[]

def test_donation_has_no_support_and_single_party_cannot_complete(client):
    b=book(client);r=request(client,b['id']);tx=accept(client,r['id'])
    client.patch(f'/api/deliveries/{tx["deliveries"][0]["id"]}',json={'meeting_point':'Kütüphane'})
    as_user(B)
    assert client.post(f'/api/transactions/{tx["id"]}/confirm').json()['status']=='in_delivery'
    assert client.get('/api/support').json()==[]
    as_user(A)
    assert client.post(f'/api/transactions/{tx["id"]}/confirm').json()['status']=='completed'
    assert client.get('/api/support').json()==[]

def test_duplicate_and_self_request_and_competing_requests(client):
    b=book(client)
    assert client.post(f'/api/books/{b["id"]}/requests',json={}).status_code==409
    r=request(client,b['id'])
    assert client.post(f'/api/books/{b["id"]}/requests',json={}).status_code==409
    request(client,b['id'],C)
    tx=accept(client,r['id'])
    as_user(C)
    assert client.get('/api/me/requests').json()[0]['status']=='rejected'
    assert client.post(f'/api/books/{b["id"]}/requests',json={}).status_code==409
    assert client.post(f'/api/transactions/{tx["id"]}/confirm').status_code==403
    assert client.get('/api/me/transactions').json()==[]

def test_cancel_releases_reserved_book(client):
    b=book(client);r=request(client,b['id']);tx=accept(client,r['id'])
    as_user(B)
    assert client.post(f'/api/transactions/{tx["id"]}/cancel').status_code==200
    assert client.get('/api/books').json()[0]['status']=='active'
    assert client.post(f'/api/transactions/{tx["id"]}/cancel').status_code==200
    assert client.get('/api/support').json()==[]

def test_exchange_owns_both_books_and_requires_two_deliveries(client):
    target=book(client,'Takas');offer=book(client,'Takas',B)
    assert client.post(f'/api/books/{target["id"]}/requests',json={}).status_code==422
    r=request(client,target['id'],offered=offer['id']);tx=accept(client,r['id'])
    assert len(tx['deliveries'])==2
    assert client.get('/api/books').json()==[]
    d1=next(d for d in tx['deliveries'] if d['sender_id']==A)
    d2=next(d for d in tx['deliveries'] if d['sender_id']==B)
    assert client.patch(f'/api/deliveries/{d2["id"]}',json={'meeting_point':'Nokta'}).status_code==403
    client.patch(f'/api/deliveries/{d1["id"]}',json={'meeting_point':'Nokta'})
    assert client.post(f'/api/transactions/{tx["id"]}/confirm').status_code==409
    as_user(B);client.patch(f'/api/deliveries/{d2["id"]}',json={'meeting_point':'Nokta'})
    client.post(f'/api/transactions/{tx["id"]}/confirm')
    as_user(A)
    assert client.post(f'/api/transactions/{tx["id"]}/confirm').json()['status']=='completed'

def test_cargo_validation_and_dispute_resolution(client):
    b=book(client,'Satış');r=request(client,b['id'],method='cargo');tx=accept(client,r['id'])
    d=tx['deliveries'][0]
    assert client.patch(f'/api/deliveries/{d["id"]}',json={}).status_code==422
    assert client.patch(f'/api/deliveries/{d["id"]}',json={'carrier':'Test Kargo','tracking_number':'123','cost_cents':2000}).status_code==200
    assert client.post(f'/api/transactions/{tx["id"]}/cancel').status_code==409
    as_user(B)
    c=client.post('/api/complaints',json={'transaction_id':tx['id'],'reason':'Teslimat konusunda sorun yaşıyorum'}).json()
    assert client.post(f'/api/transactions/{tx["id"]}/confirm').status_code==409
    assert client.post(f'/api/admin/complaints/{c["id"]}/resolve',json={'resolution':'Sorun çözüldü, devam edilebilir.','outcome':'resolved'}).status_code==403
    as_user(ADMIN,True)
    r=client.post(f'/api/admin/complaints/{c["id"]}/resolve',json={'resolution':'Sorun çözüldü, devam edilebilir.','outcome':'resolved'})
    assert r.status_code==200,r.text
    as_user(B)
    assert client.get('/api/me/transactions').json()[0]['status']=='in_delivery'

def test_favorites_notifications_and_moderation(client):
    b=book(client);request(client,b['id'])
    assert client.put(f'/api/me/favorites/{b["id"]}').status_code==200
    assert client.put(f'/api/me/favorites/{b["id"]}').status_code==200
    assert client.get('/api/me/favorites').json()==[b['id']]
    as_user(A);n=client.get('/api/me/notifications').json()[0]
    as_user(B);assert client.post(f'/api/me/notifications/{n["id"]}/read').status_code==403
    as_user(ADMIN,True)
    assert client.post(f'/api/admin/books/{b["id"]}/moderate',json={'hidden':True,'reason':'İlan kontrol edilene kadar gizlendi.'}).status_code==200
    assert client.get('/api/books').json()==[]
    assert client.get('/api/admin/reports.csv').status_code==200
    assert len(client.get('/api/admin/audit').json())>=3
    as_user(A);assert client.post(f'/api/me/notifications/{n["id"]}/read').json()['read_at']

def test_book_validation_archive_and_demo(client):
    b=book(client)
    as_user(A)
    assert client.put(f'/api/books/{b["id"]}',json={}).status_code==422
    assert client.delete(f'/api/books/{b["id"]}').json()['status']=='archived'
    assert client.get('/api/books').json()==[]
    with main.Session(main.engine) as db:
        demo=Book(title='Demo',author='Yazar',category='Roman',kind='Bağış',price=0,condition='İyi',location='Kampüs',is_demo=True)
        db.add(demo);db.commit();db.refresh(demo);bid=demo.id
    as_user(B)
    assert client.post(f'/api/books/{bid}/requests',json={}).status_code==409

def test_admin_cancellation_and_support_document_validation(client):
    b=book(client,'Satış');r=request(client,b['id']);tx=accept(client,r['id'])
    as_user(B)
    complaint=client.post('/api/complaints',json={'transaction_id':tx['id'],'reason':'Teslimat anlaşmasını iptal etmek istiyorum'}).json()
    as_user(ADMIN,True)
    result=client.post(f'/api/admin/complaints/{complaint["id"]}/resolve',json={'resolution':'İki tarafın anlaşmasıyla işlem iptal edildi.','outcome':'cancel_transaction'})
    assert result.status_code==200,result.text
    assert client.get('/api/books').json()[0]['status']=='active'
    assert client.get('/api/support').json()==[]

def test_support_is_simulation_and_only_admin_can_document(client):
    b=book(client,'Satış');r=request(client,b['id']);tx=accept(client,r['id'])
    client.patch(f'/api/deliveries/{tx["deliveries"][0]["id"]}',json={'meeting_point':'Teslim noktası'})
    client.post(f'/api/transactions/{tx["id"]}/confirm');as_user(B);client.post(f'/api/transactions/{tx["id"]}/confirm')
    sid=client.get('/api/support').json()[0]['id']
    payload={'organization':'Örnek Kuruluş','note':'Örnek simülasyon kaydı','document_url':'https://example.com/sample.pdf'}
    assert client.patch(f'/api/admin/support/{sid}',json=payload).status_code==403
    as_user(ADMIN,True)
    result=client.patch(f'/api/admin/support/{sid}',json=payload)
    assert result.status_code==200 and result.json()['mode']=='simulation'
    payload['document_url']='javascript:alert(1)'
    assert client.patch(f'/api/admin/support/{sid}',json=payload).status_code==422

def test_suspended_users_cannot_write_or_read_private_data(client):
    book(client)
    as_user(ADMIN,True)
    assert client.patch(f'/api/admin/users/{ADMIN}',json={'disabled':True,'reason':'Test gerekçesi'}).status_code==409
    result=client.patch(f'/api/admin/users/{A}',json={'disabled':True,'reason':'Tekrarlanan kural ihlali'})
    assert result.status_code==200,result.text
    as_user(A)
    assert client.get('/api/me').status_code==403
    assert client.get('/api/me/requests').status_code==403
    as_user(ADMIN,True)
    assert client.patch(f'/api/admin/users/{A}',json={'disabled':False,'reason':'İnceleme sonrası erişim açıldı'}).status_code==200
    as_user(A);assert client.get('/api/me').status_code==200

def test_pagination_and_blocked_owners(client):
    b1=book(client);b2=book(client)
    first=client.get('/api/books?limit=1&offset=0').json()
    second=client.get('/api/books?limit=1&offset=1').json()
    assert len(first)==len(second)==1 and first[0]['id']!=second[0]['id']
    assert client.get('/api/books?limit=201').status_code==422
    as_user(ADMIN,True)
    client.patch(f'/api/admin/users/{A}',json={'disabled':True,'reason':'İnceleme için geçici kapatma'})
    as_user(B)
    assert client.post(f'/api/books/{b1["id"]}/requests',json={}).status_code==409

def test_pending_exchange_offer_cannot_change(client):
    target=book(client,'Takas');offer=book(client,'Takas',B)
    request(client,target['id'],offered=offer['id'])
    payload=dict(title='Değişen Kitap',author='Yazar',category='Roman',kind='Bağış',price=0,condition='İyi',location='Kampüs')
    assert client.put(f'/api/books/{offer["id"]}',json=payload).status_code==409


def test_concurrent_acceptance_reserves_book_only_once(client):
    if main.engine.dialect.name!='postgresql':pytest.skip('Gerçek satır kilidi testi PostgreSQL CI jobunda çalışır.')
    from concurrent.futures import ThreadPoolExecutor
    b=book(client);r1=request(client,b['id'],B);r2=request(client,b['id'],C);as_user(A)
    def accept_one(rid):return client.post(f'/api/requests/{rid}/action',json={'action':'accept'}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:statuses=list(pool.map(accept_one,[r1['id'],r2['id']]))
    assert sorted(statuses)==[200,409]
    tx=client.get('/api/me/transactions').json();assert len(tx)==1
