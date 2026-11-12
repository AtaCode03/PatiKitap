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
