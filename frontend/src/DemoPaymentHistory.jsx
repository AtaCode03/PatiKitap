import React, {useCallback, useEffect, useState} from 'react';
import DemoCheckout from './DemoCheckout.jsx';

const money = cents => new Intl.NumberFormat('tr-TR', {
  style: 'currency',
  currency: 'TRY'
}).format(cents / 100);

const outcomes = {
  success: 'Başarılı',
  failed: 'Başarısız',
  cancelled: 'İptal edildi'
};

const methods = {
  card: 'Demo kart',
  transfer: 'Demo havale / EFT'
};

function Receipt({payment, bookTitle}) {
  const [open, setOpen] = useState(false);

  return <div className="row-card">
    <div>
      <strong>{outcomes[payment.outcome] || payment.outcome}</strong>
      <p>{methods[payment.method] || payment.method}</p>
      <small>
        {payment.created_at
          ? new Date(payment.created_at).toLocaleString('tr-TR')
          : 'Tarih belirtilmemiş'}
      </small>
    </div>

    <button
      type="button"
      className="secondary"
      onClick={() => setOpen(v => !v)}
    >
      {open ? 'Dekontu kapat' : 'Demo dekontu görüntüle'}
    </button>

    {open && <div className="checkout-review">
      <h3>PATİKİTAP · DEMO ÖDEME DEKONTU</h3>
      <p>Bu belge bir eğitim simülasyonudur. Gerçek tahsilat yapılmamıştır.</p>

      <strong>Kitap</strong>
      <p>{bookTitle}</p>

      <strong>İşlem referansı</strong>
      <p>{payment.reference}</p>

      <strong>Demo ödeme yöntemi</strong>
      <p>{methods[payment.method] || payment.method}</p>

      <strong>Kitap bedeli</strong>
      <p>{money(payment.price_cents)}</p>

      <strong>Bedelin içindeki mama desteği</strong>
      <p>{money(payment.support_cents)}</p>

      <strong>Demo işlem gideri</strong>
      <p>{money(payment.fee_cents)}</p>

      <strong>Demo toplam</strong>
      <p>{money(payment.total_cents)}</p>

      <strong>Sonuç</strong>
      <p>{outcomes[payment.outcome] || payment.outcome}</p>
    </div>}
  </div>;
}

export default function DemoPaymentHistory({api, transaction, userId, onPaymentRecorded}) {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const isBuyer = transaction.requester_id === userId;
  const isSale = transaction.kind === 'Satış';

  const refresh = useCallback(async () => {
    if (!api || !isBuyer || !isSale) return;

    setError('');

    try {
      const all = await api.list('/me/demo-payments');
      setPayments(all.filter(
        p => p.transaction_id === transaction.id
      ));
    } catch (e) {
      setError(e.message || 'Ödeme geçmişi yüklenemedi.');
    } finally {
      setLoading(false);
    }
  }, [api, isBuyer, isSale, transaction.id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  if (!isBuyer || !isSale) return null;

  const successful = payments.some(p => p.outcome === 'success');
  const eligible = ['accepted', 'in_delivery'].includes(transaction.status);

  return <section aria-label="Demo ödeme ve dekont geçmişi">
    <h3>Demo ödeme geçmişi</h3>

    {loading && <p className="muted">Demo ödeme kayıtları yükleniyor...</p>}

    {error && <p role="alert" className="checkout-error">{error}</p>}

    {error && <button
      type="button"
      className="secondary"
      onClick={refresh}
    >
      Yeniden dene
    </button>}

    {!loading && !error && payments.length === 0 &&
      <p className="muted">Bu satış için henüz demo ödeme kaydı yok.</p>
    }

    {!loading && !error && payments.map(payment =>
      <Receipt
        key={payment.id}
        payment={payment}
        bookTitle={transaction.book_title}
      />
    )}

    {!loading && !error && successful &&
      <p className="muted">
        Bu satış için başarılı demo ödeme kaydı bulunmaktadır.
        Aynı işlem için yeniden başarılı ödeme oluşturulamaz.
      </p>
    }

    {!loading && !error && !successful && eligible &&
      <DemoCheckout
        transaction={transaction}
        userId={userId}
        api={api}
        onPaymentRecorded={async () => { await refresh(); await onPaymentRecorded?.(); }}
      />
    }
  </section>;
}
