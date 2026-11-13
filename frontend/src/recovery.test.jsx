import React from 'react';
import {test,expect,vi} from 'vitest';
import {render,screen} from '@testing-library/react';
import {MemoryRouter} from 'react-router';
import {createClient} from '@supabase/supabase-js';
import {createHash} from 'node:crypto';
import {sessionAuthOptions} from './sessionAuth.js';
import {App} from './App.jsx';
import {bootstrap} from './api.js';

function storage(){const m=new Map();return {getItem:k=>m.get(k)??null,setItem:(k,v)=>m.set(k,v),removeItem:k=>m.delete(k)}}

test('real Supabase SDK exchanges a recovery email code in a fresh tab',async()=>{
  vi.stubGlobal('BroadcastChannel',undefined);
  localStorage.clear();sessionStorage.clear();
  const shared=localStorage;
  let challenge;
  const fetch=vi.fn(async (url,options)=>{
    if(url==='/api/config')return new Response(JSON.stringify({supabase_url:'https://example.supabase.co',supabase_publishable_key:'test-key'}));
    const body=JSON.parse(options.body);
    if(String(url).includes('/recover')){challenge=body.code_challenge;return new Response('{}')}
    expect(String(url)).toContain('/token?grant_type=pkce');
    expect(body.auth_code).toBe('test-recovery-code');
    expect(createHash('sha256').update(body.code_verifier).digest('base64url')).toBe(challenge);
    return new Response(JSON.stringify({access_token:'test-access',refresh_token:'test-refresh',token_type:'bearer',expires_in:3600,user:{id:'test-user',aud:'authenticated'}}));
  });
  window.history.replaceState({},'','/auth/forgot-password');
  const senderOptions=sessionAuthOptions('https://example.supabase.co');
  const sender=createClient('https://example.supabase.co','test-key',{auth:{...senderOptions,autoRefreshToken:false},global:{fetch}});
  let receiver,subscription;
  try {
    await sender.auth.initialize();
    expect((await sender.auth.resetPasswordForEmail('test@example.com',{redirectTo:window.location.origin+'/auth/reset-password'})).error).toBeNull();
    window.history.replaceState({},'','/auth/reset-password?code=test-recovery-code');
    sessionStorage.clear(); // New tab has no previous tab ID, verifier or session.
    vi.stubGlobal('fetch',fetch);
    receiver=await bootstrap();
    expect(receiver.authCallbackError).toBe(false);
    expect(receiver.passwordRecovery).toBe(true);
    expect((await receiver.auth.getSession()).data.session.user.id).toBe('test-user');
    expect((await sender.auth.getSession()).data.session).toBeNull();
    expect(shared.getItem('patikitap-example-email-proof')).toBeNull();
    expect([...Array(shared.length)].map((_,i)=>shared.key(i)).some(k=>k.includes('auth-token'))).toBe(false);
    expect(window.location.search).not.toContain('code=');
  } finally {subscription?.unsubscribe();await sender.auth.stopAutoRefresh();await receiver?.auth.stopAutoRefresh();vi.unstubAllGlobals();window.history.replaceState({},'','/')}
});

test('invalid recovery link stays on recovery screen and offers a fresh link',async()=>{
 const client={authCallbackError:true,auth:{getSession:async()=>({data:{session:null}}),onAuthStateChange:()=>({data:{subscription:{unsubscribe(){}}}})}};
 vi.stubGlobal('fetch',vi.fn(async()=>new Response('[]')));
 try{
 render(<MemoryRouter initialEntries={['/auth/reset-password']}><App client={client}/></MemoryRouter>);
 expect(await screen.findByRole('heading',{name:'Yeni parola bağlantısı iste'})).toBeInTheDocument();
 expect(screen.queryByRole('heading',{name:'Hesabına eriş'})).not.toBeInTheDocument();
 expect(screen.getByRole('button',{name:'Yeni bağlantı iste'})).toBeInTheDocument();
 }finally{vi.unstubAllGlobals()}
});


test.each(['missing-proof','expired-code'])('bootstrap rejects invalid recovery: %s',async scenario=>{
 localStorage.clear();sessionStorage.clear();vi.stubGlobal('BroadcastChannel',undefined);
 window.history.replaceState({},'','/auth/reset-password?code=bad-code');
 if(scenario==='expired-code'){
   const options=sessionAuthOptions('https://example.supabase.co');
   options.storage.setItem(options.storageKey+'-code-verifier',JSON.stringify('proof/PASSWORD_RECOVERY'));
   sessionStorage.clear();
 }
 const request=vi.fn(async url=>url==='/api/config'
  ?new Response(JSON.stringify({supabase_url:'https://example.supabase.co',supabase_publishable_key:'test-key'}))
  :new Response(JSON.stringify({code:'otp_expired',msg:'Email link is invalid or has expired'}),{status:403}));
 vi.stubGlobal('fetch',request);
 let client;
 try{
   client=await bootstrap();
   expect(client.authCallbackError).toBe(true);
   expect(client.passwordRecovery).not.toBe(true);
   expect((await client.auth.getSession()).data.session).toBeNull();
 }finally{await client?.auth.stopAutoRefresh();vi.unstubAllGlobals();window.history.replaceState({},'','/')}
});
