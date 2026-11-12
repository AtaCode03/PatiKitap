// Keep refreshes signed in without restoring a login from a previous tab.
export function sessionAuthOptions(supabaseUrl, browser = window) {
  const project = new URL(supabaseUrl).hostname.split('.')[0];
  const legacyKey = `sb-${project}-auth-token`;
  const tabKey = `patikitap-${project}-tab`;
  const storage = browser.sessionStorage;
  let tabId = storage.getItem(tabKey);
  if (!tabId) {
    tabId = browser.crypto.randomUUID();
    storage.setItem(tabKey, tabId);
  }
  // Remove only this project's old persistent login, not other site data.
  browser.localStorage.removeItem(legacyKey);
  browser.localStorage.removeItem(`${legacyKey}-user`);
  browser.localStorage.removeItem(`${legacyKey}-code-verifier`);
  return {
    flowType: 'pkce',
    persistSession: true,
    storage,
    // Supabase also uses this key for its cross-tab auth broadcast channel.
    storageKey: `${legacyKey}-${tabId}`,
  };
}
