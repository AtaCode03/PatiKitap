import test from 'node:test';
import assert from 'node:assert/strict';
import {sessionAuthOptions} from './sessionAuth.js';

function storage() {
  const values = new Map();
  return {getItem: key => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
    removeItem: key => values.delete(key)};
}
const url = 'https://example.supabase.co';
const tab = (localStorage, id) => ({localStorage, sessionStorage: storage(), crypto: {randomUUID: () => id}});

test('refresh preserves the tab session; a fresh tab has no session or shared auth channel', () => {
  const persistent = storage();
  const first = tab(persistent, 'first');
  const options = sessionAuthOptions(url, first);
  options.storage.setItem(options.storageKey, 'signed-in');
  const refreshed = sessionAuthOptions(url, first);
  assert.equal(refreshed.storage.getItem(refreshed.storageKey), 'signed-in');
  const reopened = sessionAuthOptions(url, tab(persistent, 'second'));
  assert.equal(reopened.storage.getItem(reopened.storageKey), null);
  assert.notEqual(reopened.storageKey, options.storageKey);
});

test('legacy persistent login is removed without clearing unrelated data', () => {
  const persistent = storage();
  persistent.setItem('sb-example-auth-token', 'old-login');
  persistent.setItem('sb-other-auth-token', 'other-project');
  persistent.setItem('theme', 'dark');
  sessionAuthOptions(url, tab(persistent, 'first'));
  assert.equal(persistent.getItem('sb-example-auth-token'), null);
  assert.equal(persistent.getItem('sb-other-auth-token'), 'other-project');
  assert.equal(persistent.getItem('theme'), 'dark');
});


test('email proof crosses into a fresh callback tab but sessions stay private', () => {
  const shared=storage(), sender=tab(shared,'sender'), receiver=tab(shared,'receiver');
  const a=sessionAuthOptions(url,sender);
  a.storage.setItem(a.storageKey+'-code-verifier','proof/recovery');
  a.storage.setItem(a.storageKey,'sender-session');
  receiver.location={search:'?code=one-use-code'};
  const b=sessionAuthOptions(url,receiver);
  assert.equal(b.storage.getItem(b.storageKey+'-code-verifier'),'proof/recovery');
  assert.equal(b.storage.getItem(b.storageKey),null);
  b.storage.setItem(b.storageKey,'receiver-session');
  b.storage.removeItem(b.storageKey+'-code-verifier');
  assert.equal(shared.getItem('patikitap-example-email-proof'),null);
  assert.equal(a.storage.getItem(a.storageKey),'sender-session');
  assert.equal(shared.getItem(b.storageKey),null);
});

test('ordinary tab logout cannot delete another tabs pending proof', () => {
  const shared=storage();
  const a=sessionAuthOptions(url,tab(shared,'sender'));
  a.storage.setItem(a.storageKey+'-code-verifier','proof');
  const b=sessionAuthOptions(url,tab(shared,'unrelated'));
  assert.equal(b.storage.getItem(b.storageKey+'-code-verifier'),null);
  b.storage.removeItem(b.storageKey+'-code-verifier');
  assert.equal(a.storage.getItem(a.storageKey+'-code-verifier'),'proof');
});

test('expired or malformed shared proof is not accepted', () => {
  const shared=storage(), receiver=tab(shared,'receiver');
  receiver.location={search:'?code=expired'};
  const b=sessionAuthOptions(url,receiver);
  for(const entry of [JSON.stringify({value:'old',expiresAt:0}),'{broken',JSON.stringify({value:42,expiresAt:Date.now()+60000})]) {
    shared.setItem('patikitap-example-email-proof',entry);
    assert.equal(b.storage.getItem(b.storageKey+'-code-verifier'),null);
    assert.equal(shared.getItem('patikitap-example-email-proof'),null);
  }
});

test('finishing an earlier request cannot remove a newer proof', () => {
  const shared=storage();
  const a=sessionAuthOptions(url,tab(shared,'a')), b=sessionAuthOptions(url,tab(shared,'b'));
  a.storage.setItem(a.storageKey+'-code-verifier','first');
  b.storage.setItem(b.storageKey+'-code-verifier','second');
  a.storage.removeItem(a.storageKey+'-code-verifier');
  assert.equal(b.storage.getItem(b.storageKey+'-code-verifier'),'second');
});
