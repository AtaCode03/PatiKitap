import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {test, expect, vi} from 'vitest';
import DemoPaymentHistory from './DemoPaymentHistory.jsx';

const buyerId = '22222222-2222-4222-8222-222222222222';

const transaction = {
  id: 101,
  requester_id: buyerId,
  kind: 'Satış',
  status: 'accepted',
  book_title: 'Test Kitabı',
  price_cents: 10000,
  support_cents: 2000,
  fee_cents: 0
};

test('başarılı ödeme dekontu gösterilir ve ikinci ödeme engellenir', async () => {
  const payment = {
    id: 1,
    transaction_id: 101,
    buyer_id: buyerId,
    reference: 'DEMO-101-TEST',
    method: 'card',
    outcome: 'success',
    price_cents: 10000,
    support_cents: 2000,
    fee_cents: 0,
    total_cents: 10000,
    created_at: '2026-11-09T12:00:00Z'
  };

  const api = vi.fn();
  api.list = vi.fn().mockResolvedValue([payment]);

  render(
    <DemoPaymentHistory
      api={api}
      transaction={transaction}
      userId={buyerId}
    />
  );

  expect(await screen.findByText('Demo ödeme geçmişi'))
    .toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByRole('button', {
      name: 'Demo dekontu görüntüle'
    })).toBeInTheDocument();
  });

  fireEvent.click(screen.getByRole('button', {
    name: 'Demo dekontu görüntüle'
  }));

  expect(screen.getByText('PATİKİTAP · DEMO ÖDEME DEKONTU'))
    .toBeInTheDocument();

  expect(screen.getByText('DEMO-101-TEST'))
    .toBeInTheDocument();

  expect(screen.getByText(/Aynı işlem için yeniden başarılı ödeme oluşturulamaz/))
    .toBeInTheDocument();

  expect(screen.queryByText('Güvenli demo ödeme'))
    .not.toBeInTheDocument();

  expect(api.list).toHaveBeenCalledWith('/me/demo-payments');
});

test('satıcı alıcının demo ödeme geçmişini göremez', () => {
  const api = vi.fn();
  api.list = vi.fn();

  render(
    <DemoPaymentHistory
      api={api}
      transaction={transaction}
      userId="11111111-1111-4111-8111-111111111111"
    />
  );

  expect(screen.queryByText('Demo ödeme geçmişi'))
    .not.toBeInTheDocument();

  expect(api.list).not.toHaveBeenCalled();
});

test('ödeme kaydedildikten sonra geçmiş yenilenir ve checkout kapanır', async () => {
  const payment = {
    id: 5,
    transaction_id: 101,
    buyer_id: buyerId,
    reference: 'DEMO-101-NEW',
    method: 'card',
    outcome: 'success',
    price_cents: 10000,
    support_cents: 2000,
    fee_cents: 0,
    total_cents: 10000,
    created_at: '2026-11-09T12:00:00Z'
  };

  const api = vi.fn().mockResolvedValue(payment);
  api.list = vi.fn()
    .mockResolvedValueOnce([])
    .mockResolvedValueOnce([payment]);

  render(
    <DemoPaymentHistory
      api={api}
      transaction={transaction}
      userId={buyerId}
    />
  );

  expect(await screen.findByText('Güvenli demo ödeme'))
    .toBeInTheDocument();

  fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));
  fireEvent.click(screen.getByRole('button', {
    name: 'Örnek bilgileri doldur'
  }));
  fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));
  fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));
  fireEvent.click(screen.getByRole('checkbox'));

  fireEvent.click(screen.getByRole('button', {
    name: 'Demo ödemeyi tamamla'
  }));

  await waitFor(() => {
    expect(api.list).toHaveBeenCalledTimes(2);
  });

  expect(await screen.findByRole('button', {
    name: 'Demo dekontu görüntüle'
  })).toBeInTheDocument();

  expect(screen.queryByText('Güvenli demo ödeme'))
    .not.toBeInTheDocument();

  expect(screen.getByText(/Aynı işlem için yeniden başarılı ödeme oluşturulamaz/))
    .toBeInTheDocument();
});
