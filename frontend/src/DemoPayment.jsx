import React, {useState} from 'react';
import {calculateDemoPayment, demoReceipt} from './demoPayment.js';
import './demo-payment.css';


export default function DemoPayment({transaction, userId}) {
  const [method,setMethod]=useState('card');
  const [outcome,setOutcome]=useState(null);
  const [receipt,setReceipt]=useState(null);
  const isBuyer=transaction.requester_id===userId;
  const eligible=isBuyer && transaction.kind==='Satış' && ['accepted','in_delivery'].includes(transaction.status);
  if(!eligible) return null;
  const totals=calculateDemoPayment(transaction.price_cents,transaction.support_cents,transaction.fee_cents);
  const submit=(result)=>{
    setOutcome(result);
    setReceipt(demoReceipt(transaction.id,result,method));
  };
  return <section className="demo-payment" aria-label="Demo ödeme">
    <div className="demo-payment__head"><strong>Demo ödeme</strong><span>Gerçek para alınmaz</span></div>
    <p>Bu alan yalnızca ödeme deneyimini göstermek içindir. Kart numarası veya banka bilgisi girmeyin.</p>
    <div className="demo-payment__summary">
      <span>Kitap bedeli</span><b>{totals.price} TL</b>
      <span>Bedelden ayrılan mama desteği</span><b>{totals.support} TL</b>
      <span>Örnek işlem gideri</span><b>{totals.fee} TL</b>
      <span>Demo ödenecek toplam</span><b>{totals.price} TL</b>
    </div>
    <fieldset className="demo-payment__methods"><legend>Ödeme yöntemi (simülasyon)</legend>
      <label><input type="radio" name={`demo-method-${transaction.id}`} value="card" checked={method==='card'} onChange={()=>setMethod('card')}/> Kart ile ödeme (demo)</label>
      <label><input type="radio" name={`demo-method-${transaction.id}`} value="transfer" checked={method==='transfer'} onChange={()=>setMethod('transfer')}/> Havale/EFT (demo)</label>
    </fieldset>
    <div className="demo-payment__actions">
      <button type="button" className="primary" onClick={()=>submit('success')}>Başarılı ödemeyi simüle et</button>
      <button type="button" className="secondary" onClick={()=>submit('failed')}>Başarısızlığı dene</button>
      <button type="button" className="secondary" onClick={()=>submit('cancelled')}>İptal et</button>
    </div>
    {outcome&&<div role="status" className={`demo-payment__result demo-payment__result--${outcome}`}>
      <strong>{outcome==='success'?'Demo ödeme başarılı':outcome==='failed'?'Demo ödeme başarısız':'Demo ödeme iptal edildi'}</strong>
      <span>İşlem referansı: {receipt.reference}</span>
      <small>Bu sonuç yalnızca bu tarayıcı oturumunda gösterilir; sunucuya gönderilmez ve işlem durumunu değiştirmez.</small>
    </div>}
  </section>;
}
