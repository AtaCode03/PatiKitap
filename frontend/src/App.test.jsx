import React from 'react';
import {act, render, screen, waitFor} from '@testing-library/react';
import {MemoryRouter} from 'react-router';
import {test, expect, vi} from 'vitest';
import {App} from './App.jsx';

test('anonymous initial auth event cannot strand the catalog in loading state', async () => {
  let finishAuth;
  let authChanged;
  const pendingAuth = new Promise(resolve => { finishAuth = resolve; });
  const client = {auth: {
    getSession: () => pendingAuth,
    onAuthStateChange: callback => {
      authChanged = callback;
      return {data: {subscription: {unsubscribe() {}}}};
    },
  }};
  const request = vi.fn(async url => new Response(JSON.stringify(
    url.startsWith('/api/books') ? [{id:1,title:'Açılış test kitabı',author:'Yazar',kind:'Bağış',category:'Roman',condition:'İyi',location:'Konya',status:'active'}]
      : url.startsWith('/api/support') ? [] : {}
  )));
  vi.stubGlobal('fetch', request);
  try {
    render(<MemoryRouter initialEntries={['/books']}><App client={client}/></MemoryRouter>);
    expect(screen.getByText('Kitaplar yükleniyor…')).toBeInTheDocument();
    await act(async () => {
      authChanged('INITIAL_SESSION', null);
      finishAuth({data:{session:null}});
    });
    await waitFor(() => expect(screen.queryByText('Kitaplar yükleniyor…')).not.toBeInTheDocument());
    expect(screen.getByRole('button', {name:'Açılış test kitabı', exact:true})).toBeInTheDocument();
    expect(request.mock.calls.some(([url]) => url.startsWith('/api/books'))).toBe(true);
  } finally {
    vi.unstubAllGlobals();
  }
});
