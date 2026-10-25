export const viewPaths={catalog:'/',impact:'/impact',account:'/account',admin:'/admin'};
export const authModes={'/auth/login':'login','/auth/register':'signup','/auth/forgot-password':'reset'};
export function pageFor(path){return Object.keys(viewPaths).find(key=>viewPaths[key]===path)|| (authModes[path]?'auth':path==='/auth/reset-password'?'password':'notfound')}
export function safeReturnPath(value){return typeof value==='string'&&['/','/impact','/account','/admin'].includes(value)?value:'/account'}
