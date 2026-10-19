from unittest.mock import Mock, patch
import httpx
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import pytest
from auth import identity

def credential(): return HTTPAuthorizationCredentials(scheme='Bearer',credentials='not-a-real-token')
def test_user_metadata_cannot_grant_admin():
    response=Mock(status_code=200)
    response.json.return_value={'id':'11111111-1111-4111-8111-111111111111','email_confirmed_at':'2026-01-01','user_metadata':{'role':'admin','display_name':'Okur'},'app_metadata':{}}
    with patch('auth.httpx.get',return_value=response):
        assert identity(credential()).is_admin is False
    response.json.return_value['app_metadata']={'role':'admin'}
    with patch('auth.httpx.get',return_value=response):
        assert identity(credential()).is_admin is True

def test_invalid_or_unconfirmed_auth_is_denied():
    with pytest.raises(HTTPException) as e: identity(None)
    assert e.value.status_code==401
    response=Mock(status_code=401)
    with patch('auth.httpx.get',return_value=response),pytest.raises(HTTPException) as e: identity(credential())
    assert e.value.status_code==401
    response.status_code=200;response.json.return_value={'id':'11111111-1111-4111-8111-111111111111'}
    with patch('auth.httpx.get',return_value=response),pytest.raises(HTTPException) as e: identity(credential())
    assert e.value.status_code==403

def test_auth_network_failure_fails_closed():
    with patch('auth.httpx.get',side_effect=httpx.ConnectError('offline')),pytest.raises(HTTPException) as e: identity(credential())
    assert e.value.status_code==503
