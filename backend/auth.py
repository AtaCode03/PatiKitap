import os
from dataclasses import dataclass
from uuid import UUID
import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import ROOT

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://lmyxrjxchswlqvdshaob.supabase.co').rstrip('/')
SUPABASE_KEY = os.getenv('SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_88H_kKqvPGFeJTy3LpNTAw_-QuzY8e7')
security = HTTPBearer(auto_error=False)
@dataclass
class Identity:
    id: str
    name: str = 'Kitapsever'
    is_admin: bool = False
    token: str = ''

def identity(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> Identity:
    if not credentials or credentials.scheme.lower() != 'bearer':
        raise HTTPException(401, 'Bu işlem için giriş yapmalısın.')
    try:
        response = httpx.get(f'{SUPABASE_URL}/auth/v1/user', headers={'apikey': SUPABASE_KEY, 'Authorization':f'Bearer {credentials.credentials}'}, timeout=10)
    except httpx.RequestError:
        raise HTTPException(503, 'Oturum servisine ulaşılamadı.') from None
    if response.status_code >= 500:
        raise HTTPException(503, 'Oturum servisi geçici olarak kullanılamıyor.')
    if response.status_code != 200:
        raise HTTPException(401, 'Oturumun geçersiz veya süresi dolmuş. Yeniden giriş yap.')
    user = response.json()
    if not (user.get('email_confirmed_at') or user.get('confirmed_at')):
        raise HTTPException(403, 'Önce e-posta adresini doğrula.')
    try: user_id = str(UUID(user['id']))
    except (KeyError, ValueError): raise HTTPException(401, 'Geçersiz kullanıcı.') from None
    metadata = user.get('user_metadata') or {}
    return Identity(id=user_id, name=str(metadata.get('display_name') or 'Kitapsever')[:80],
                    is_admin=(user.get('app_metadata') or {}).get('role') == 'admin', token=credentials.credentials)
