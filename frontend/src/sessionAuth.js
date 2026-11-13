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
    // Share only the short-lived PKCE proof, never access/refresh tokens.
    storage: emailLinkStorage(storage, browser.localStorage, legacyKey + '-' + tabId + '-code-verifier',
      'patikitap-' + project + '-email-proof', browser),
    // Supabase also uses this key for its cross-tab auth broadcast channel.
    storageKey: `${legacyKey}-${tabId}`,
  };
}

export const EMAIL_PROOF_TTL = 60 * 60 * 1000;

export function emailLinkStorage(tabStorage, sharedStorage, verifierKey, sharedKey, browser, now = Date.now) {
  let observed = null;
  let ownsProof = false;
  const isCallback = () => new URLSearchParams(browser.location?.search || '').has('code');
  return {
    getItem(key) {
      if (key !== verifierKey) return tabStorage.getItem(key);
      if (!ownsProof && !isCallback()) return tabStorage.getItem(key);
      const raw = sharedStorage.getItem(sharedKey);
      if (!raw) return tabStorage.getItem(key);
      try {
        const entry = JSON.parse(raw);
        if (typeof entry.value !== 'string' || !Number.isFinite(entry.expiresAt) || entry.expiresAt <= now()) {
          sharedStorage.removeItem(sharedKey);
          return null;
        }
        observed = raw;
        return entry.value;
      } catch {
        sharedStorage.removeItem(sharedKey);
        return null;
      }
    },
    setItem(key, value) {
      if (key !== verifierKey) return tabStorage.setItem(key, value);
      observed = JSON.stringify({value, expiresAt: now() + EMAIL_PROOF_TTL});
      sharedStorage.setItem(sharedKey, observed);
      ownsProof = true;
    },
    removeItem(key) {
      if (key !== verifierKey) return tabStorage.removeItem(key);
      tabStorage.removeItem(key);
      if (observed && (ownsProof || isCallback()) && sharedStorage.getItem(sharedKey) === observed) {
        sharedStorage.removeItem(sharedKey);
      }
      observed = null;
      ownsProof = false;
    },
  };
}
