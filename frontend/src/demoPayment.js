// Pure presentation-only helpers. No payment credentials, network calls or persistence.
export function calculateDemoPayment(priceCents, supportCents, feeCents) {
  const values=[priceCents,supportCents,feeCents];
  if(values.some(v=>!Number.isSafeInteger(v)||v<0)||supportCents+feeCents>priceCents) {
    throw new RangeError('Geçersiz demo ödeme tutarı');
  }
  const format=v=>(v/100).toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2});
  return {price:format(priceCents),support:format(supportCents),fee:format(feeCents),remaining:format(priceCents-supportCents-feeCents)};
}
export function demoReceipt(transactionId,outcome,method) {
  if(!['success','failed','cancelled'].includes(outcome)||!['card','transfer'].includes(method)) throw new RangeError('Geçersiz demo sonucu');
  return {reference:`DEMO-${String(transactionId).replace(/[^a-zA-Z0-9-]/g,'').slice(0,24)}-${crypto.randomUUID().slice(0,8).toUpperCase()}`,outcome,method};
}
