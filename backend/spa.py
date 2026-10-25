"""History routing fallback without masking missing API endpoints or assets."""
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles

class SPAStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            # Only known frontend routes receive HTML; API and asset errors stay 404.
            if exc.status_code != 404 or scope['method'] not in ('GET','HEAD') or path.replace('\\','/').strip('/') not in {
                'impact','account','admin','auth/login','auth/register',
                'auth/forgot-password','auth/reset-password',
            }:
                raise
            return await super().get_response('index.html', scope)
