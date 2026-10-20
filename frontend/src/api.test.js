import test from 'node:test';
import assert from 'node:assert/strict';
import {makeApi} from './api.js';
const client={auth:{getSession:async()=>({data:{session:{access_token:'test-token'}}})}};
test('API keeps inputs immutable and adds authentication',async()=>{
 const previous=globalThis.fetch;const options={method:'POST',body:{title:'Kitap'}};
 try{
  globalThis.fetch=async(url,o)=>{assert.equal(o.headers.Authorization,'Bearer test-token');assert.equal(o.body,'{"title":"Kitap"}');return new Response('{"ok":true}')};
  assert.deepEqual(await makeApi(client)('/books',options),{ok:true});assert.deepEqual(options.body,{title:'Kitap'});
 }finally{globalThis.fetch=previous}
});
test('list fetches the next page instead of losing older records',async()=>{
 const previous=globalThis.fetch;const urls=[];
 try{
  globalThis.fetch=async(url)=>{urls.push(url);return new Response(JSON.stringify(url.includes('offset=0&')?Array.from({length:200},(_,i)=>({id:i})): [{id:200}]))};
  const rows=await makeApi(client).list('/me/requests');assert.equal(rows.length,201);assert.equal(urls.length,2);
 }finally{globalThis.fetch=previous}
});
test('API surfaces errors without accepting a failed response',async()=>{
 const previous=globalThis.fetch;
 try{globalThis.fetch=async()=>new Response('{"detail":"Giriş gerekli"}',{status:401});await assert.rejects(makeApi(client)('/me'),/Giriş gerekli/)}finally{globalThis.fetch=previous}
});
