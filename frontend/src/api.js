import {createClient} from '@supabase/supabase-js';
export async function bootstrap(){
 const r=await fetch('/api/config',{signal:AbortSignal.timeout(20000)});
 if(!r.ok)throw Error('API sunucusuna ulaşılamıyor. Sunucuyu başlatıp sayfayı yenile.');
 const config=await r.json();
 return createClient(config.supabase_url,config.supabase_publishable_key);
}
export function makeApi(client){
 const api=async(path,options={})=>{
  const {data:{session}}=await client.auth.getSession();
  const headers={...options.headers};
  if(session)headers.Authorization=`Bearer ${session.access_token}`;
  let body=options.body;
  if(body&&!(body instanceof Blob)){headers['Content-Type']='application/json';body=JSON.stringify(body)}
  let r;
  try{r=await fetch('/api'+path,{...options,body,headers,signal:options.signal||AbortSignal.timeout(30000)})}
  catch(e){throw Error(e.name==='TimeoutError'?'İşlem zaman aşımına uğradı. Yenileyip durumu kontrol et.':'Sunucuya ulaşılamıyor. Bağlantını kontrol et.')}
  if(!r.ok){let error;try{error=await r.json()}catch{};throw Error(typeof error?.detail==='string'?error.detail:r.status===422?'Formdaki alanları kontrol et.':'İşlem tamamlanamadı. Yeniden dene.')}
  if(options.raw)return r;
  return r.status===204?null:r.json();
 };
 api.list=async(path)=>{
  const items=[],separator=path.includes('?')?'&':'?';
  for(let offset=0;offset<10000;offset+=200){
   const batch=await api(`${path}${separator}offset=${offset}&limit=200`);
   if(!Array.isArray(batch))throw Error('Liste yanıtı beklenen biçimde değil.');
   items.push(...batch);
   if(batch.length<200)return items;
  }
  throw Error('Bu liste 10.000 kaydı aşıyor. Sonuçları daraltarak yeniden dene.');
 };
 return api;
}
