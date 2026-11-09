import test from 'node:test';
import assert from 'node:assert/strict';
import {calculateDemoPayment,demoReceipt} from './demoPayment.js';
test('200 TL satışın desteği ayrıca tahsil edilmez',()=>{
 const result=calculateDemoPayment(20000,4000,0);
 assert.equal(result.price,'200,00');assert.equal(result.support,'40,00');assert.equal(result.remaining,'160,00');
});
test('geçersiz ve taşan tutarlar reddedilir',()=>{
 assert.throws(()=>calculateDemoPayment(-1,0,0),RangeError);
 assert.throws(()=>calculateDemoPayment(100,110,0),RangeError);
 assert.throws(()=>calculateDemoPayment(1.5,0,0),RangeError);
});
test('demo referansları eşsizdir ve sonuç doğrulanır',()=>{
 const a=demoReceipt(17,'success','card');const b=demoReceipt(17,'success','card');
 assert.notEqual(a.reference,b.reference);
 assert.throws(()=>demoReceipt(17,'paid','card'),RangeError);
});
