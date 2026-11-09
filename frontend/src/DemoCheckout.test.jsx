import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {test, expect, vi} from 'vitest';
import DemoCheckout from './DemoCheckout.jsx';

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

test('alıcı demo satın alma adımlarını tamamlar', async () => {
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
    real_payment: false
  };

  const api = vi.fn().mockResolvedValue(payment);
  const onPaymentRecorded = vi.fn().mockResolvedValue(undefined);

  render(
    <DemoCheckout
      transaction={transaction}
      userId={buyerId}
      api={api}
      onPaymentRecorded={onPaymentRecorded}
    />
  );

  expect(screen.getByText('Güvenli demo ödeme')).toBeInTheDocument();

  // Sipariş -> Teslimat
  fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));

  // Örnek teslimat bilgileri
  fireEvent.click(screen.getByRole('button', {
    name: 'Örnek bilgileri doldur'
  }));

  // Teslimat -> Ödeme
  fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));

  expect(screen.getByText('Ödeme yöntemi')).toBeInTheDocument();

  // Ödeme -> Onay
  fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));

  // Demo onayı
  fireEvent.click(screen.getByRole('checkbox'));

  fireEvent.click(screen.getByRole('button', {
    name: 'Demo ödemeyi tamamla'
  }));

  await waitFor(() => {
    expect(api).toHaveBeenCalledWith(
      '/transactions/101/demo-payment',
      {
        method: 'POST',
        body: {method: 'card', outcome: 'success'}
      }
    );
  });

  expect(await screen.findByText('Demo ödeme başarılı'))
    .toBeInTheDocument();

  expect(screen.getByText('DEMO-101-TEST'))
    .toBeInTheDocument();

  expect(onPaymentRecorded).toHaveBeenCalledTimes(1);

  expect(screen.queryByRole('button', {
    name: 'Yeni demo denemesi'
  })).not.toBeInTheDocument();
});

test('satıcı demo ödeme ekranını göremez', () => {
  render(
    <DemoCheckout
      transaction={transaction}
      userId="11111111-1111-4111-8111-111111111111"
    />
  );

  expect(screen.queryByText('Güvenli demo ödeme'))
    .not.toBeInTheDocument();
});

test('başarısız demo ödeme sonrasında yeniden denenebilir', async () => {
  const api = vi.fn().mockResolvedValue({
    id: 2,
    transaction_id: 101,
    reference: 'DEMO-101-FAILED',
    method: 'card',
    outcome: 'failed',
    price_cents: 10000,
    support_cents: 2000,
    fee_cents: 0,
    total_cents: 10000,
    real_payment: false
  });

  render(
    <DemoCheckout
      transaction={transaction}
      userId={buyerId}
      api={api}
    />
  );

  fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));
  fireEvent.click(screen.getByRole('button', {
    name: 'Örnek bilgileri doldur'
  }));
  fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));
  fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));
  fireEvent.click(screen.getByRole('checkbox'));

  fireEvent.click(screen.getByRole('button', {
    name: 'Başarısız sonucu dene'
  }));

  expect(await screen.findByText('Demo ödeme başarısız'))
    .toBeInTheDocument();

  fireEvent.click(screen.getByRole('button', {
    name: 'Yeni demo denemesi'
  }));

  expect(screen.getByText('Sipariş özeti'))
    .toBeInTheDocument();
});

test('demo ödeme API hatasında kullanıcıya uyarı gösterilir', async () => {
  const api = vi.fn().mockRejectedValue(
    new Error('Demo ödeme sunucusuna ulaşılamadı.')
  );

  render(
    <DemoCheckout
      transaction={transaction}
      userId={buyerId}
      api={api}
    />
  );

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

  expect(await screen.findByRole('alert'))
    .toHaveTextContent('Demo ödeme sunucusuna ulaşılamadı.');

  expect(screen.queryByText('Demo ödeme başarılı'))
    .not.toBeInTheDocument();
});

test('başarısız ödemeden sonra ikinci deneme başarılı olur', async () => {
  const api = vi.fn()
    .mockResolvedValueOnce({
      reference: 'DEMO-FIRST-FAILED',
      outcome: 'failed'
    })
    .mockResolvedValueOnce({
      reference: 'DEMO-SECOND-SUCCESS',
      outcome: 'success'
    });

  render(
    <DemoCheckout
      transaction={transaction}
      userId={buyerId}
      api={api}
    />
  );

  async function goToConfirmation() {
    fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));

    fireEvent.click(screen.getByRole('button', {
      name: 'Örnek bilgileri doldur'
    }));

    fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));
    fireEvent.click(screen.getByRole('button', {name: 'Devam et'}));
    fireEvent.click(screen.getByRole('checkbox'));
  }

  await goToConfirmation();

  fireEvent.click(screen.getByRole('button', {
    name: 'Başarısız sonucu dene'
  }));

  expect(await screen.findByText('Demo ödeme başarısız'))
    .toBeInTheDocument();

  fireEvent.click(screen.getByRole('button', {
    name: 'Yeni demo denemesi'
  }));

  await goToConfirmation();

  fireEvent.click(screen.getByRole('button', {
    name: 'Demo ödemeyi tamamla'
  }));

  expect(await screen.findByText('Demo ödeme başarılı'))
    .toBeInTheDocument();

  expect(screen.getByText('DEMO-SECOND-SUCCESS'))
    .toBeInTheDocument();

  expect(api).toHaveBeenCalledTimes(2);

  expect(api).toHaveBeenNthCalledWith(
    1,
    '/transactions/101/demo-payment',
    {
      method: 'POST',
      body: {method: 'card', outcome: 'failed'}
    }
  );

  expect(api).toHaveBeenNthCalledWith(
    2,
    '/transactions/101/demo-payment',
    {
      method: 'POST',
      body: {method: 'card', outcome: 'success'}
    }
  );
});
