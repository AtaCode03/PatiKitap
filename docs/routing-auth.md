# Temiz URL ve oturum mimarisi

React 19 + Vite, FastAPI ve Supabase Auth kullanılır. Eski uygulama HashRouter kullanmıyordu; sayfalar state ile seçiliyordu. BrowserRouter artık HTML5 History API ile adresi, geri/ileri düğmelerini ve doğrudan sayfa açmayı yönetir.

## Sayfalar ve servisler

| Adres | İşlev | Erişim |
|---|---|---|
| `/` | Kitap kataloğu | Herkes |
| `/impact` | Etki ve simülasyon kayıtları | Herkes |
| `/account` | Hesabım | Üye |
| `/admin` | Yönetim | Yönetici |
| `/auth/login` | Giriş formu | Herkes |
| `/auth/register` | Kayıt formu | Herkes |
| `/auth/forgot-password` | Yenileme e-postası isteme | Herkes |
| `/auth/reset-password` | Yeni parola formu | Geçerli oturum |
| `GET /api/me` | Sunucudan doğrulanmış profil/yetki | Üye |
| `/api/admin/*` | Yönetim işlemleri | Sunucuda doğrulanan yönetici |

`/auth/login` bir HTML sayfasıdır; token üreten API değildir. Supabase SDK giriş, kayıt, çıkış ve yenileme için Supabase Auth servisinin `/auth/v1/*` endpoint'lerini kullanır. Yeni bir `/api/token` servisi kurulmadı: uygulamanın ikinci bir token üreticisine ihtiyacı yoktur. İleride sunucuda cookie oturumu kurulursa `/api/auth/login`, `/api/auth/logout`, `/api/auth/session` gibi ayrı bir BFF tasarlanabilir; mevcut Bearer mimarisiyle yarım şekilde karıştırılmamalıdır.

Kaynak endpoint'lerinde çoğul isim (`/api/books`, `/api/transactions`), kaynak kimliği (`/api/books/42`), GET okuma, POST oluşturma/eylem, PATCH kısmi güncelleme, DELETE silme kullanılır. Mevcut tam kitap güncellemesi PUT kullanır. Giriş yok/geçersiz token 401, yetki yok 403, bulunamayan kaynak 404, iş kuralı çatışması 409 döner. Sürümleme kırıcı API değişikliği olduğunda planlanır; yalnızca profesyonel görünmesi için mevcut adresler değiştirilmez.

## Frontend

```jsx
import { BrowserRouter, Routes, Route } from 'react-router';

<BrowserRouter>
  <Routes>
    <Route path="*" element={<App client={client} />} />
  </Routes>
</BrowserRouter>
```

Mevcut ortak App içinde `useLocation` ile sayfa seçilir, `useNavigate` ile geçilir. Yol eşlemeleri `frontend/src/routing.js` dosyasındadır. Daha büyük uygulamada sayfalar ayrı Route bileşenlerine bölünebilir. React state URL'nin yerine geçmez. Yeni bir gezinme bağlantısı yazarken `<Link to="/account">Hesabım</Link>` kullanılabilir. Bölüme kaydırma `scrollIntoView` ile yapılır, URL'ye hash eklenmez.

Korumalı sayfa açılışında oturum kontrolü beklenir; giriş yoksa `/auth/login` açılır. Giriş sonrası dönüş yalnızca uygulamanın izin verdiği dört yerel sayfadan birine yapılır. İstemcide menü gizlemek güvenlik sınırı değildir: FastAPI her korumalı istekte Supabase `/auth/v1/user` üzerinden kullanıcıyı doğrular, rolü app_metadata'dan okur ve işleme özgü yetkiyi kontrol eder.

## Token ve e-posta dönüşleri

```js
const { data: { session }, error } = await client.auth.getSession();
if (error || !session) throw new Error('Giriş yapmalısın.');
const response = await fetch('/api/me', {
  headers: { Authorization: `Bearer ${session.access_token}` }
});
if (!response.ok) throw new Error('İstek tamamlanamadı.');
```

Projede ortak `makeApi` bu işlemi yapar; token URL'ye veya loglara yazılmaz. Token yenilemesi SDK'ya bırakılır; başarısız POST istekleri otomatik tekrarlanmaz. `getSession` istemcide token almak içindir, sunucuda yetki kanıtı değildir.

Auth client `flowType: 'pkce'` kullanır. Yeni doğrulama/yenileme bağlantıları geçici `code` ile döner ve SDK bu kodu oturuma çevirir. Kullanıcı bağlantıyı kayıt/yenileme isteğini yaptığı aynı tarayıcı ve origin üzerinde açmalıdır; code verifier bu tarayıcıdadır. `localhost` ile `127.0.0.1` farklı origin'dir. Eski implicit bağlantılar geçici olarak hash içerebilir; yeni testlerde yeni bağlantı isteyin. SDK doğrulamadan kodları/hash'i elle temizlemeyin. PKCE tek başına XSS'e karşı token koruması sağlamaz.

Mevcut SPA'da SDK varsayılan olarak oturumu localStorage'da saklar: bu JavaScript tarafından okunabilir. Ek bir manuel token deposu oluşturulmaz. HTTPS, CSP, güvenilmeyen HTML'i çalıştırmama ve token loglamama gerekir. Daha güçlü koruma gerektiğinde refresh token'ı sunucuda tutan HttpOnly + Secure + SameSite cookie/BFF ve CSRF koruması birlikte tasarlanmalıdır. Service role, veritabanı parolası ve ADMIN_DATABASE_URL istemciye veya yayın paketine konmaz.

Dashboard → Authentication → URL Configuration bölümünde geliştirme Site URL ve Redirect URLs için `http://127.0.0.1:5173` adresini kullanın. Formlar halen origin'e döner; callback olayı parola formuna `/auth/reset-password` üzerinden yönlendirir. Üretimde gerçek HTTPS origin'i ekleyin ve Site URL'yi değiştirin; gelişigüzel üretim wildcard'ları kullanmayın. Bu Dashboard ayarları bu değişiklikle otomatik değiştirilmedi.

## Sunucu ve yayın

Vite dev server SPA fallback sağlar; `/api` proxy'si FastAPI'ye gider. `vite.config.js` mevcut proxy'yi korur. Vite geliştirme sunucusu üretim sunucusu olarak kullanılmaz.

FastAPI'nin `SPAStaticFiles` sınıfı derlenmiş frontend varsa bilinen sayfalara `index.html` döndürür. `/api/missing`, eksik JS/CSS ve bilinmeyen yollar 404 kalır. Yeni frontend yolu eklendiğinde backend izin listesi de güncellenmelidir. Backend değişikliğini yüklemek için sunucuyu yeniden başlatın.

Statik frontend + ayrı FastAPI kullanılırsa Nginx örneği:

```nginx
# TLS server bloğunun içinde; sertifika ve alan adı hostingde ayrıca yapılandırılır.
root /srv/patikitap/frontend/dist;
index index.html;
client_max_body_size 6m;

location = /api { proxy_pass http://127.0.0.1:8000; }
location ^~ /api/ {
    proxy_pass http://127.0.0.1:8000; # sonuna / eklemeyin: /api korunmalı
    proxy_set_header Host $host;
    proxy_set_header Authorization $http_authorization;
}
location ^~ /assets/ { try_files $uri =404; }
location / { try_files $uri $uri/ /index.html; }
```

Bu örnek yalnızca yönlendirme parçasıdır. HTTPS sertifikası, HTTP→HTTPS yönlendirmesi ve statik HTML için CSP/no-store gibi güvenlik başlıkları hostingde ayrıca uygulanır. Statik dosyaları Nginx sunduğunda FastAPI middleware'i o yanıtlara başlık ekleyemez.

Apache alternatifinde (VirtualHost/.htaccess, mod_rewrite etkin):

```apache
RewriteEngine On
RewriteRule ^api(?:/|$) - [L]
RewriteRule ^assets/ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^ index.html [L]
```

Apache API proxy'si ayrıca yapılandırılmalıdır. Netlify/Vercel seçilirse önce `/api/*` için gerçek FastAPI upstream rewrite'ı, ardından frontend SPA rewrite'ı tanımlanır. Yalnızca `/* → /index.html` kuralı eklemek API'yi çalıştırmaz. Bu sağlayıcılara deployment yapılmadı; hesap, alan adı ve backend adresi seçilince sağlayıcı ayarları somutlaştırılmalıdır.

## Kabul adımları

1. Frontend terminalinde `npm ci`, `npm run dev`; backend terminalinde `start.ps1` ile yeniden başlatın.
2. `/account` ve `/admin` adreslerini doğrudan açın, F5 yapın; HTML yüklenmeli. Oturumsuz kullanıcı giriş sayfasına yönlenmeli.
3. Normal üye `/admin` açtığında yetki hatası, yönetici yükleme görünümünden sonra yönetim verilerini görmeli. Başarısız veri isteğinde boş ekran yerine hata ve Yenile görünmeli.
4. Menü geçişlerinde URL değişmeli; geri/ileri düğmeleri doğru sayfayı açmalı. `/#` açıldığında boş hash kaldırılmalı.
5. İki gerçek hesapla yeni kayıt ve parola yenileme bağlantılarını aynı tarayıcıda deneyin. Süresi dolmuş/kullanılmış bağlantı ve yanlış parola da denenmeli. Gerçek e-posta akışı bu kod testleriyle tamamlanmış sayılmaz.
6. `/api/missing` ve `/assets/missing.js` HTML yerine 404 vermeli. API isteğinin Authorization başlığı olmalı, URL'sinde token bulunmamalı. Tokenı ekran görüntüsüne veya rapora koymayın.
7. Gerçek hostingde HTTPS, yeni Site URL/redirect listesi ve F5 testlerini tekrar edin; sağlayıcı bazında yayına alma henüz yapılmadı.

Kaynaklar: [React Router](https://reactrouter.com/start/declarative/routing), [Supabase PKCE](https://supabase.com/docs/guides/auth/sessions/pkce-flow), [Supabase sessions](https://supabase.com/docs/guides/auth/sessions), [Nginx try_files](https://nginx.org/en/docs/http/ngx_http_core_module.html#try_files).
