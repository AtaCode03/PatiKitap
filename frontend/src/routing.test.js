import test from 'node:test';
import assert from 'node:assert/strict';
import {pageFor,safeReturnPath} from './routing.js';
test('history URLs select public, protected and authentication pages',()=>{
 for(const [path,page] of Object.entries({'/':'catalog','/impact':'impact','/account':'account','/admin':'admin','/auth/login':'auth','/auth/register':'auth','/auth/forgot-password':'auth','/auth/reset-password':'password','/missing':'notfound'}))assert.equal(pageFor(path),page);
});
test('login return target cannot navigate to an external origin or auth loop',()=>{
 for(const path of ['https://evil.example','//evil.example','/auth/login',null,'/account?token=secret'])assert.equal(safeReturnPath(path),'/account');
 assert.equal(safeReturnPath('/admin'),'/admin');
});
