import React, {useEffect, useState} from 'react';
import {calculateDemoPayment, demoReceipt} from './demoPayment.js';
import './demo-checkout.css';

const steps=['Sipariş','Teslimat','Ödeme','Onay'];
const initial={fullName:'',phone:'',city:'',district:'',neighborhood:'',address:'',postalCode:'',note:''};
const required=['fullName','phone','city','district','neighborhood','address'];
const labels={fullName:'Ad soyad',phone:'Telefon',city:'İl',district:'İlçe',neighborhood:'Mahalle',address:'Açık adres',postalCode:'Posta kodu',note:'Teslimat notu'};
const sample={fullName:'Örnek Kullanıcı',phone:'0500 000 00 00',city:'Konya',district:'Selçuklu',neighborhood:'Örnek Mahallesi',address:'Örnek Sokak No: 12 Daire: 3',postalCode:'42000',note:'Bu adres tamamen örnektir.'};
const fmt=n=>new Intl.NumberFormat('tr-TR',{style:'currency',currency:'TRY'}).format(n);
const Field=({name,value,onChange,multiline=false})=><label className="checkout-field"><span>{labels[name]}{required.includes(name)?' *':''}</span>{multiline?<textarea rows={3} value={value} onChange={e=>onChange(name,e.target.value)}/>:<input autoComplete="off" value={value} onChange={e=>onChange(name,e.target.value)} placeholder={labels[name]} />}</label>;

export default function DemoCheckout({transaction,userId,api,onPaymentRecorded}){
  const [step,setStep]=useState(0),[delivery,setDelivery]=useState(initial),[deliveryMode,setDeliveryMode]=useState('cargo'),[method,setMethod]=useState('card'),[cardSample,setCardSample]=useState('visa'),[accepted,setAccepted]=useState(false),[result,setResult]=useState(null),[receipt,setReceipt]=useState(null),[errors,setErrors]=useState([]);
  const [submitting,setSubmitting]=useState(false);
  const [serverError,setServerError]=useState('');

  const eligible=transaction?.requester_id===userId && transaction?.kind==='Satış' && ['accepted','in_delivery'].includes(transaction?.status);
  useEffect(()=>{setStep(0);setDelivery(initial);setDeliveryMode('cargo');setMethod('card');setAccepted(false);setResult(null);setReceipt(null);setErrors([])},[transaction?.id]);
  if(!eligible)return null;
  const totals=calculateDemoPayment(transaction.price_cents,transaction.support_cents,transaction.fee_cents);
  const shipping=0; // Demo teslimat ücretsizdir.
  const total=transaction.price_cents / 100 + shipping;
  function validate(){const missing=required.filter(k=>!delivery[k].trim());if(delivery.phone && delivery.phone.replace(/\D/g,'').length!==11)missing.push('phone');setErrors([...new Set(missing)]);return missing.length===0;}
  function next(){if(step===1&&!validate())return;setErrors([]);setStep(s=>Math.min(3,s+1));}
  async function finish(outcome){
    if(submitting) return;
    if(outcome !== 'cancelled' && !accepted) return;

    setSubmitting(true);
    setServerError('');

    try {
      if(api){
        const payment = await api(
          `/transactions/${transaction.id}/demo-payment`,
          {
            method:'POST',
            body:{method,outcome}
          }
        );

        setReceipt(payment);
        setResult(payment.outcome);
        if(onPaymentRecorded) {
          try {
            await onPaymentRecorded();
          } catch {
            // Ödeme kaydı başarılıysa sonuç ekranını koru.
          }
        }
      }else{
        setReceipt(demoReceipt(transaction.id,outcome,method));
        setResult(outcome);
      }
    }catch(error){
      setServerError(error.message || 'Demo ödeme tamamlanamadı.');
    }finally{
      setSubmitting(false);
    }
  }
  function reset(){
    setStep(0);
    setDelivery({...initial});
    setDeliveryMode('cargo');
    setMethod('card');
    setCardSample('visa');
    setAccepted(false);
    setResult(null);
    setReceipt(null);
    setErrors([]);
  }
  return <section className="checkout" aria-label="Demo satın alma akışı">
    <div className="checkout-top"><div><small>PATİKİTAP · ÖRNEK SATIN ALMA</small><h2>Güvenli demo ödeme</h2></div><span className="checkout-demo">Gerçek ödeme yapılmaz</span></div>
    <p className="checkout-intro">Bu ekran bir eğitim simülasyonudur. Gerçek kişisel veya finansal bilgi girmeyin; örnek veriler kullanın. Bilgiler sunucuya gönderilmez.</p>
    {!result?<>
      <ol className="checkout-steps">{steps.map((s,i)=><li key={s} className={i===step?'active':i<step?'done':''}><span>{i<step?'✓':i+1}</span>{s}</li>)}</ol>
      <div className="checkout-body"><div className="checkout-main">
        {step===0&&<><h3>Sipariş özeti</h3><div className="checkout-book"><div className="checkout-book-icon">📚</div><div><strong>{transaction.book_title||'Örnek kitap'}</strong><p>İşlem #{transaction.id} · Satış</p><small>Bu bir demo sipariştir.</small></div></div><p>Kitabın bedelinden ayrılan mama desteği ayrıca tahsil edilmez. Sonraki adımlarda örnek teslimat ve ödeme yöntemini seçeceksin.</p></>}
        {step===1&&<><h3>Teslimat bilgileri</h3><div className="checkout-choice"><label><input type="radio" checked={deliveryMode==='cargo'} onChange={()=>setDeliveryMode('cargo')}/> Kargo ile teslim (demo)</label><label><input type="radio" checked={deliveryMode==='hand'} onChange={()=>setDeliveryMode('hand')}/> Elden teslim (demo)</label></div><div className="checkout-row"><p>Yalnızca örnek bilgiler kullan. Gerçek adres veya telefon girmene gerek yok.</p><button type="button" className="checkout-link" onClick={()=>{setDelivery(sample);setErrors([])}}>Örnek bilgileri doldur</button></div><div className="checkout-fields">{Object.keys(initial).map(k=><Field key={k} name={k} value={delivery[k]} onChange={(name,v)=>setDelivery(p=>({...p,[name]:v}))} multiline={k==='address'||k==='note'}/>)}</div>{errors.length>0&&<p role="alert" className="checkout-error">Eksik veya geçersiz alanlar: {errors.map(k=>labels[k]).join(', ')}. Telefon için 11 rakam kullan.</p>}</>}
        {step===2&&<><h3>Ödeme yöntemi</h3><div className="checkout-choice"><label><input type="radio" checked={method==='card'} onChange={()=>setMethod('card')}/> Kartla ödeme simülasyonu</label><label><input type="radio" checked={method==='transfer'} onChange={()=>setMethod('transfer')}/> Havale / EFT simülasyonu</label></div>{method==='card'?<div className="checkout-method"><strong>Örnek kart seç</strong><p>Gerçek kart numarası, son kullanma tarihi veya CVV girilmez.</p><select value={cardSample} onChange={e=>setCardSample(e.target.value)}><option value="visa">Örnek Visa kartı</option><option value="mastercard">Örnek Mastercard kartı</option></select><div className="checkout-fake-card"><span>DEMO CARD</span><strong>•••• •••• •••• 0000</strong><small>{cardSample==='visa'?'VISA DEMO':'MASTERCARD DEMO'} · Gerçek kart değildir</small></div></div>:<div className="checkout-method"><strong>Örnek havale / EFT</strong><p>Bu senaryoda gerçek banka, IBAN veya hesap bilgisi gösterilmez. Onay aşamasında transfer sonucunu simüle edebilirsin.</p><div className="checkout-fake-card"><span>DEMO TRANSFER</span><strong>Örnek işlem</strong><small>Para transferi gerçekleşmeyecek</small></div></div>}</>}
        {step===3&&<><h3>Siparişi kontrol et</h3><div className="checkout-review"><strong>Teslim alacak kişi</strong><p>{delivery.fullName} · {delivery.phone}</p><p>{delivery.address}, {delivery.neighborhood}, {delivery.district}/{delivery.city} {delivery.postalCode}</p><strong>Teslimat</strong><p>{deliveryMode==='cargo'?'Kargo ile teslim':'Elden teslim'} (demo)</p><strong>Ödeme</strong><p>{method==='card'?'Örnek kart':'Örnek havale / EFT'}</p></div><label className="checkout-consent"><input type="checkbox" checked={accepted} onChange={e=>setAccepted(e.target.checked)}/><span>Bu işlemin yalnızca simülasyon olduğunu, gerçek sipariş, ödeme veya teslimat oluşturmayacağını anladım.</span></label>{serverError&&<p role="alert" className="checkout-error">{serverError}</p>}<div className="checkout-outcomes"><button type="button" className="primary" disabled={!accepted||submitting} onClick={()=>finish('success')}>Demo ödemeyi tamamla</button><button type="button" className="secondary" disabled={!accepted||submitting} onClick={()=>finish('failed')}>Başarısız sonucu dene</button><button type="button" className="secondary" disabled={submitting} onClick={()=>finish('cancelled')}>İptal et</button></div></>}
      </div><aside className="checkout-summary"><h3>Tutar özeti</h3><div><span>Kitap bedeli</span><b>{fmt(transaction.price_cents / 100)}</b></div><div><span>Bedelden ayrılan mama desteği (%20)</span><b>{fmt(transaction.support_cents / 100)}</b></div><div><span>Örnek işlem gideri</span><b>{fmt(transaction.fee_cents / 100)}</b></div><div><span>Teslimat (demo)</span><b>{fmt(shipping)}</b></div><div className="checkout-total"><strong>Ödenecek toplam (demo)</strong><strong>{fmt(total)}</strong></div><small>Mama desteği fiyata dahildir; ayrıca eklenmez. Gerçek tahsilat yapılmaz.</small></aside></div>
      {step<3&&<div className="checkout-nav"><button type="button" className="secondary" disabled={step===0} onClick={()=>setStep(s=>s-1)}>Geri</button><button type="button" className="primary" onClick={next}>Devam et</button></div>}
    </>:<div className="checkout-result" role="status"><div className="checkout-result-icon">{result==='success'?'✓':result==='failed'?'!':'×'}</div><h3>{result==='success'?'Demo ödeme başarılı':result==='failed'?'Demo ödeme başarısız':'Demo ödeme iptal edildi'}</h3><p>{api
  ? 'Gerçek ödeme veya teslimat oluşturulmadı. Demo işlem sonucu kaydedildi.'
  : 'Gerçek ödeme, sipariş veya teslimat kaydı oluşturulmadı.'
}</p><div className="checkout-review"><strong>Örnek işlem referansı</strong><p>{receipt?.reference}</p><strong>Demo toplam</strong><p>{fmt(total)}</p><strong>Sonuç</strong><p>{result==='success'?'Başarılı':result==='failed'?'Başarısız':'İptal'}</p></div>{result !== 'success' &&
  <button type="button" className="primary" onClick={reset}>
    Yeni demo denemesi
  </button>
}</div>}
  </section>;
}
