"""Bounded per-process request controls and privacy-preserving operational logs."""
import json,logging,time,uuid,threading
from collections import OrderedDict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
logger=logging.getLogger('patikitap.http')
if not logger.handlers:
    handler=logging.StreamHandler();handler.setFormatter(logging.Formatter('%(message)s'));logger.addHandler(handler)
logger.propagate=False
class WindowLimiter:
    def __init__(self,read_limit=300,write_limit=60,window=60,capacity=10000,clock=time.monotonic):
        self.read_limit,self.write_limit,self.window,self.capacity=read_limit,write_limit,window,capacity
        self.clock=clock;self.entries=OrderedDict();self.lock=threading.Lock()
    def allow(self,key,write=False):
        current=self.clock();bucket=int(current//self.window);limit=self.write_limit if write else self.read_limit
        key=(key,write)
        with self.lock:
            previous,count=self.entries.pop(key,(bucket,0))
            count=count+1 if previous==bucket else 1
            self.entries[key]=(bucket,count)
            while len(self.entries)>self.capacity:self.entries.popitem(last=False)
        return count<=limit,max(1,int(self.window-current%self.window))
class OperationalMiddleware(BaseHTTPMiddleware):
    def __init__(self,app,limiter=None,supabase_url="https://lmyxrjxchswlqvdshaob.supabase.co"):
        super().__init__(app);self.limiter=limiter or WindowLimiter();self.supabase_url=supabase_url
    async def dispatch(self,request,call_next):
        rid=uuid.uuid4().hex;start=time.monotonic()
        peer=request.client.host if request.client else 'unknown'
        if request.url.path.startswith('/api/') and request.url.path not in ('/api/health','/api/ready'):
            allowed,retry=self.limiter.allow(peer,request.method not in ('GET','HEAD','OPTIONS'))
            if not allowed:
                response=JSONResponse({'detail':'Çok fazla istek. Biraz bekleyip yeniden dene.','request_id':rid},status_code=429,headers={'Retry-After':str(retry)})
            else: response=await self._call(request,call_next,rid)
        else: response=await self._call(request,call_next,rid)
        response.headers['X-Request-ID']=rid
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
        response.headers['Content-Security-Policy']=("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: "+self.supabase_url+"; connect-src 'self' "+self.supabase_url+"; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        if request.url.path.startswith('/api/'):response.headers['Cache-Control']='no-store'
        logger.info(json.dumps({'request_id':rid,'method':request.method,'path':request.url.path,'status':response.status_code,'elapsed_ms':round((time.monotonic()-start)*1000)}))
        return response
    async def _call(self,request,call_next,rid):
        try:return await call_next(request)
        except Exception as exc:
            logger.error(json.dumps({'request_id':rid,'error_type':type(exc).__name__}))
            return JSONResponse({'detail':'Beklenmeyen bir hata oluştu. İstek koduyla destek isteyebilirsin.','request_id':rid},status_code=500)
