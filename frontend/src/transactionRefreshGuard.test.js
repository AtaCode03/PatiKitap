import test from 'node:test';
import assert from 'node:assert/strict';
import {isCurrentTransactionRefresh} from './transactionRefreshGuard.js';

const request = {
  requestGeneration: 3,
  currentGeneration: 3,
  requestId: 2,
  currentRequestId: 2,
  requestUserId: 'user-a',
  currentUserId: 'user-a'
};

test('güncel kullanıcı ve güncel istek kabul edilir', () => {
  assert.equal(isCurrentTransactionRefresh(request), true);
});

test('oturum değişikliğinden önceki yanıt reddedilir', () => {
  assert.equal(isCurrentTransactionRefresh({
    ...request,
    currentUserId: 'user-b'
  }), false);
});

test('eski yenileme isteğinin yanıtı reddedilir', () => {
  assert.equal(isCurrentTransactionRefresh({
    ...request,
    currentRequestId: 3
  }), false);
});

test('eski sayfa yenilemesinin yanıtı reddedilir', () => {
  assert.equal(isCurrentTransactionRefresh({
    ...request,
    currentGeneration: 4
  }), false);
});
