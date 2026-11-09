import React from 'react';
import {render, screen, fireEvent} from '@testing-library/react';
import {test, expect, vi} from 'vitest';
import {Account} from './Workspace.jsx';

const sellerId = '11111111-1111-4111-8111-111111111111';
const buyerId = '22222222-2222-4222-8222-222222222222';

function makeTransaction(kind, paymentStatus) {
  return {
    id: 101,
    kind,
    status: 'accepted',
    demo_payment_status: paymentStatus,
    book_title: 'Test Kitabı',
    owner_id: sellerId,
    requester_id: buyerId,
    price_cents: kind === 'Satış' ? 10000 : 0,
    support_cents: kind === 'Satış' ? 2000 : 0,
    fee_cents: 0,
    created_at: '2026-11-09T12:00:00Z',
    owner_confirmed: false,
    requester_confirmed: false,
    deliveries: [{
      id: 201,
      sender_id: sellerId,
      recipient_id: buyerId,
      method: 'campus',
      status: 'pending',
      meeting_point: null,
      cost_cents: 0
    }]
  };
}

function renderAccount(transaction) {
  const setModal = vi.fn();
  const api = vi.fn();
  api.list = vi.fn().mockResolvedValue([]);

  render(
    <Account
      api={api}
      me={{id: sellerId, display_name: 'Test Satıcı'}}
      own={[]}
      requests={[]}
      transactions={[transaction]}
      notifications={[]}
      complaints={[]}
      favorites={[]}
      busy={false}
      run={vi.fn()}
      setModal={setModal}
      done={vi.fn()}
    />
  );

  fireEvent.click(screen.getByRole('button', {name: 'İşlemler'}));

  return {setModal};
}

test('ödeme bekleyen satışta teslimat butonu gösterilmez', () => {
  renderAccount(makeTransaction('Satış', 'pending'));

  expect(screen.getByText(/Alıcının başarılı demo ödemesi bekleniyor/))
    .toBeInTheDocument();

  expect(screen.queryByRole('button', {name: 'Teslimat bilgisi gir'}))
    .not.toBeInTheDocument();
});

test('başarılı demo ödeme sonrası teslimat butonu gösterilir', () => {
  const {setModal} = renderAccount(makeTransaction('Satış', 'success'));

  const button = screen.getByRole('button', {
    name: 'Teslimat bilgisi gir'
  });

  expect(button).toBeInTheDocument();

  fireEvent.click(button);

  expect(setModal).toHaveBeenCalledWith({
    type: 'delivery',
    delivery: expect.objectContaining({id: 201})
  });
});

test('bağışta demo ödeme olmadan teslimat yapılabilir', () => {
  renderAccount(makeTransaction('Bağış', null));

  expect(screen.getByRole('button', {
    name: 'Teslimat bilgisi gir'
  })).toBeInTheDocument();

  expect(screen.queryByText(/Alıcının başarılı demo ödemesi bekleniyor/))
    .not.toBeInTheDocument();
});

test('ödeme durumu bilinmiyorsa satış teslimatı kapalı kalır', () => {
  renderAccount(makeTransaction('Satış', undefined));

  expect(screen.queryByRole('button', {
    name: 'Teslimat bilgisi gir'
  })).not.toBeInTheDocument();
});
