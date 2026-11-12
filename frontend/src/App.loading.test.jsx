import React from 'react';
import {render, screen, act, cleanup} from '@testing-library/react';
import {MemoryRouter} from 'react-router';
import {afterEach, expect, test, vi} from 'vitest';
import {App} from './App.jsx';

const {api} = vi.hoisted(()=>({api:vi.fn()}));
vi.mock('./api',()=>({makeApi:()=>api}));
afterEach(()=>{cleanup();vi.resetAllMocks()});
const pending=()=>new Promise(()=>{});
const book={id:1,title:'Hızlı Kitap',author:'Yazar',kind:'Bağış',category:'Roman',isbn:'',price:0};
function mount(session=null){
 const client={auth:{getSession:vi.fn().mockResolvedValue({data:{session}}),onAuthStateChange:()=>({data:{subscription:{unsubscribe:vi.fn()}}})}};
 render(<MemoryRouter initialEntries={['/books']}><App client={client}/></MemoryRouter>);
 return client;
}
test('catalogue renders while profile and reports are still pending',async()=>{
 api.mockImplementation(pending);
 api.list=vi.fn(path=>path==='/books'?Promise.resolve([book]):pending());
 mount({user:{id:'reader'},access_token:'token'});
 expect(await screen.findByRole('button',{name:'Hızlı Kitap',exact:true})).toBeInTheDocument();
 expect(screen.queryByText('Kitaplar yükleniyor…')).not.toBeInTheDocument();
 expect(api).toHaveBeenCalledWith('/me');
});
test('failed impact request does not hide successfully loaded books',async()=>{
 api.mockRejectedValue(new Error('Rapor yüklenemedi'));
 api.list=vi.fn(path=>Promise.resolve(path==='/books'?[book]:[]));
 mount();
 expect(await screen.findByRole('button',{name:'Hızlı Kitap',exact:true})).toBeInTheDocument();
 expect(await screen.findByText('Rapor yüklenemedi')).toBeInTheDocument();
});
test('a response from before sign-out cannot replace the current catalogue',async()=>{
 let finishOld;
 api.mockImplementation(pending);
 api.list=vi.fn(path=>path==='/books'?new Promise(resolve=>{finishOld=resolve}):pending());
 let authChanged;
 const client={auth:{getSession:vi.fn().mockResolvedValue({data:{session:{user:{id:'reader'},access_token:'token'}}}),onAuthStateChange:callback=>{authChanged=callback;return {data:{subscription:{unsubscribe:vi.fn()}}}}}};
 render(<MemoryRouter initialEntries={['/books']}><App client={client}/></MemoryRouter>);
 await act(async()=>{});
 client.auth.getSession.mockResolvedValue({data:{session:null}});
 api.list.mockImplementation(path=>Promise.resolve(path==='/books'?[{...book,title:'Güncel Kitap'}]:[]));
 await act(async()=>{authChanged('SIGNED_OUT',null)});
 expect(await screen.findByRole('button',{name:'Güncel Kitap',exact:true})).toBeInTheDocument();
 await act(async()=>{finishOld([book])});
 expect(screen.queryByText('Hızlı Kitap')).not.toBeInTheDocument();
});
