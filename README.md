# PatiKitap

React + FastAPI + Supabase tabanlı kitap paylaşımı ve örnek mama desteği uygulaması.

## Şimdiki durum

- İlk Supabase kurulumu: `patikitap.books` ve 6 örnek kitap mevcut.
- Genişletilmiş iş akışı şeması kullanıcı onayıyla Supabase’e uygulandı: `complete_business_workflows`. Yeni API ve yerel arayüz başlatıldı.
- Revize paket: toplam 10 uygulama tablosu (9 yeni tablo + mevcut kitap tablosuna alanlar), RLS, yabancı anahtarlar, durum ve tutar kısıtları, indeksler, özel fotoğraf bucket'ı ve üye erişim politikaları. Mevcut kayıtlar silinmez. Var olan sahipsiz örnek ilanlar `is_demo=true` olarak işaretlenir.

## Özellikler

- Supabase Auth: e-posta/parola kaydı, doğrulama, giriş, çıkış, parola yenileme.
- Profil, ilan sahipliği, ilan ekleme/düzenleme/arşivleme, ISBN, kategori, arama ve sıralama.
- Kalıcı favoriler, uygulama içi bildirimler ve okundu işareti.
- Bağış, takas ve simülasyon satış talepleri; kabul, ret ve geri çekme.
- Kabulde kitap rezervasyonu; takasta iki kitap için tutarlı rezervasyon ve iki teslimat.
- Elden, kampüs veya kargo teslimatı; takip bilgileri, kargo bedeli ve ödeyen taraf.
- İki taraflı teslim onayı; tamamlanınca tek bir simülasyon destek kaydı.
- Şikâyet/ihtilaf açma, süreç durdurma, yönetici kararı ve iptal.
- Yönetim: ilan moderasyonu, hesap erişimini kapatma/açma, destek belgesi bağlantıları, denetim kaydı, CSV etki raporu.
- Fotoğraflar boyut ve biçim kontrolünden geçip JPEG'e dönüştürülür, EXIF bilgisi kaldırılır. Özel Supabase Storage alanında tutulur; giriş yapan üyelere kısa süreli imzalı bağlantıyla gösterilir.

## Başlatma

Backend klasöründe:

```powershell
./start.ps1
```

Frontend klasöründe:

```powershell
npm install
npm run dev
```

Arayüz: http://127.0.0.1:5173 · API: http://127.0.0.1:8000/docs

Bu bilgisayarda Python bağımlılıkları `backend/.packages` içindedir. Yeni bilgisayarda Python 3.11+ ile sanal ortam oluşturup `pip install -r requirements.txt` kullanın. Node 20.19+ veya 22.12+ önerilir. `start.ps1 -PythonExecutable <yol>` ile Python yolu seçilebilir.

## Yapılandırma

`backend/.env` içindeki `DATABASE_URL` Supabase Session pooler URI'sidir. Veritabanı parolası frontend'e gönderilmez. İsteğe bağlı `SUPABASE_URL` ve `SUPABASE_PUBLISHABLE_KEY` sunucu değişkenleri mevcut projenin varsayılan değerlerini değiştirebilir. Servis rolü anahtarı gerekmez. Frontend sadece publishable anahtarı ve kullanıcının oturum token'ını kullanır.

Supabase Dashboard → Authentication → URL Configuration bölümünde Site URL ve izin verilen redirect adreslerinin yerel geliştirme için `http://127.0.0.1:5173` ile uyumlu olduğunu kontrol edin. Dağıtımda kendi HTTPS alan adınızı kullanın. Varsayılan Supabase e-posta gönderim kısıtları geçerlidir; e-posta/SMTP ayarları bu değişiklikte değiştirilmedi.

PostgreSQL'de şema başlangıçta otomatik değiştirilmez; migration uygulanmalıdır. SQLite sadece izole geliştirme/test için desteklenir; eski prototip SQLite dosyası otomatik taşınmaz, yeni bir dosya seçilmelidir. Gerçek Supabase verisine test verisi yazılmaz.

## Yetkiler

FastAPI her özel istekte token'ı Supabase `/auth/v1/user` üzerinden doğrular. E-posta doğrulaması gerekir. İlan sahipliği, işlem katılımcılığı, bildirim sahipliği ve yönetici rolü sunucuda denetlenir. `user_metadata` yetki kaynağı değildir; yalnızca Supabase `app_metadata.role=admin` yönetici yetkisi verir. Yeni üyeler yönetici olamaz.

İlk yönetici otomatik atanmaz. Doğrulanmış hesap oluşturulduktan sonra, yalnızca açıkça seçtiğiniz kullanıcı için backend ortamında:

```powershell
python manage_admin.py KULLANICI_UUID --action grant
# Yetkiyi geri almak için:
python manage_admin.py KULLANICI_UUID --action revoke
```

Bu komut ayrı bir yerel yönetim aracıdır; uygulama kullanıcılarına sunulmaz. Şu an kullanıcı tarafından sağlanan yetkili PostgreSQL bağlantısı kullanılmaktadır. İnternete dağıtmadan önce çalışma rolü ile migration rolünü ayırın; rate limiting ve işletimsel gözlem ekleyin.

## Test

```powershell
# Backend, kendi Python ortamında
python -m pytest -q
# Frontend
npm run build
```

Testler ayrı, geçici SQLite veritabanı ve taklit edilmiş Supabase kimlikleri kullanır. Gerçek e-posta göndermez, ödeme yapmaz, canlı kullanıcı oluşturmaz. Canlı PostgreSQL’de 10 tablonun ORM eşleşmesi, mevcut 6 kitabın korunması, özel fotoğraf bucket’ı ve yetkisiz API isteklerinin reddi doğrulandı. PostgreSQL eşzamanlı satır kilidi davranışı, Supabase Auth e-posta teslimi, üyeli fotoğraf yükleme ve tarayıcı uçtan uca akışı henüz canlı doğrulanmadı.

## Sınırlar

Satış, işlem gideri ve mama desteği simülasyondur. Örnek destek oranı %20, gider 0; kabul anında kuruş cinsinden sabitlenir. Gerçek para tahsilatı, banka/ödeme altyapısı, mama satın alma ve gerçek kargo entegrasyonu yoktur. Destek belgesi bir HTTPS bağlantısı olarak yönetici tarafından kaydedilir ve kayıt simülasyon olarak kalır. Bildirimler uygulama içidir; e-posta/SMS gönderilmez.

Liste uçları sınırlı sonuç döndürür (katalog/işlemler 200, bildirimler 100). Gerçek kullanım büyüdüğünde sayfalama arayüzü ve yaşam döngüsü/saklama planı geliştirilmelidir.
