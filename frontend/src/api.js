import {createClient} from '@supabase/supabase-js';
export async function bootstrap(){
 const r=await fetch('/api/config');
 if(!r.ok)throw Error('API sunucusuna ulaşılamıyor. Sunucuyu başlatıp sayfayı yenile.');
 const config=await r.json();
 return createClient(config.supabase_url,config.supabase_publishable_key);
}
export function makeApi(client){
 return async(path,options={})=>{
  const {data:{session}}=await client.auth.getSession();
  const headers={...options.headers};
  if(session)headers.Authorization=`Bearer ${session.access_token}`;
  if(options.body&&!(options.body instanceof Blob)){headers['Content-Type']='application/json';options.body=JSON.stringify(options.body)}
  const r=await fetch('/api'+path,{...options,headers});
  if(!r.ok){let error;try{error=await r.json()}catch{};throw Error(typeof error?.detail==='string'?error.detail:r.status===422?'Formdaki alanları kontrol et.':'İşlem tamamlanamadı. Yeniden dene.')}
  if(options.raw)return r;
  return r.status===204?null:r.json();
 }
}
