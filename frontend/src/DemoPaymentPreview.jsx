import React, { useState } from 'react';
import DemoCheckout from './DemoCheckout.jsx';

const buyerId = 101;
const sellerId = 202;

export default function DemoPaymentPreview() {
  const [role, setRole] = useState('buyer');
  const [status, setStatus] = useState('accepted');
  const [kind, setKind] = useState('Satış');

  const transaction = {
    id: 9001,
    book_title: 'Küçük Prens',
    requester_id: buyerId,
    owner_id: sellerId,
    kind,
    status,
    price_cents: 20000,
    support_cents: 4000,
    fee_cents: 0,
  };

  const userId = role === 'buyer' ? buyerId : sellerId;
  const visible =
    role === 'buyer' &&
    kind === 'Satış' &&
    ['accepted', 'in_delivery'].includes(status);

  return (
    <main style={{ maxWidth: 760, margin: '40px auto', padding: 24 }}>
      <h1>PatiKitap — Demo Ödeme Testi</h1>
      <p>
        Geliştirme önizlemesidir. Gerçek ödeme yapılmaz ve
        veritabanına kayıt gönderilmez.
      </p>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, marginBottom: 24 }}>
        <label>
          Kullanıcı rolü
          <select value={role} onChange={e => setRole(e.target.value)}>
            <option value="buyer">Alıcı</option>
            <option value="seller">Satıcı</option>
          </select>
        </label>

        <label>
          İşlem durumu
          <select value={status} onChange={e => setStatus(e.target.value)}>
            <option value="accepted">Kabul edildi</option>
            <option value="in_delivery">Teslimatta</option>
            <option value="completed">Tamamlandı</option>
            <option value="cancelled">İptal edildi</option>
          </select>
        </label>

        <label>
          İşlem türü
          <select value={kind} onChange={e => setKind(e.target.value)}>
            <option value="Satış">Satış</option>
            <option value="Bağış">Bağış</option>
            <option value="Takas">Takas</option>
          </select>
        </label>
      </div>

      <article className="transaction-card">
        <h2>#{transaction.id} · {transaction.book_title}</h2>
        <p>{kind} · 200 TL</p>

        <DemoCheckout
          key={`${role}-${status}-${kind}`}
          transaction={transaction}
          userId={userId}
        />
      </article>

      {!visible && (
        <p className="muted" style={{ marginTop: 16 }}>
          Bu senaryoda ödeme paneli gösterilmez.
        </p>
      )}
    </main>
  );
}
