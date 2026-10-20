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

PostgreSQL'de şema başlangıçta otomatik değiştirilmez; migration uygulanmalıdır. Uygulama için PostgreSQL DATABASE_URL zorunludur; bağlantı yokken SQLite’a geçilmez. SQLite yalnızca izole otomatik testlerin bellek içi veritabanıdır. Gerçek Supabase verisine test verisi yazılmaz.

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

## Teknik tamamlamalar (20 Ekim 2026)

- API çalışma hesabı `patikitap_runtime` oluşturuldu ve yerel DATABASE_URL bu hesaba geçirildi. Auth/Storage SQL tablolarına, tablo oluşturmaya/silmeye veya rol yönetimine erişemez. Denetim kayıtlarını değiştiremez; DELETE yalnızca favoriler içindir. Yönetim bağlantısı sadece yerel yönetim araçları için `ADMIN_DATABASE_URL` içinde saklanır; bunu dağıtıma taşımayın.
- 6 eksik foreign-key indeksi Supabase migration ile eklendi. Başlangıç şeması ve sonraki değişiklikler Supabase migration geçmişinde tutulur; `docs/business-schema.sql` yeniden çalıştırılmaz.
- Tüm sınırlı listeler `offset`/`limit` kabul eder. Arayüz 200 satırlık sayfaları birleştirir (10.000 kayıt güvenli sınırı); katalog 24'er kitap gösterir. Bu sürüm küçük kampüs pilotu içindir; çok büyük katalogda sunucu tarafında arama/sayfalama arayüzü tercih edilmelidir.
- API'de işlem başına istek kimliği, JSON erişim logları, güvenli hata yanıtı, CSP ve güvenlik başlıkları bulunur. Parola, token, istek gövdesi veya URL query'si loglanmaz. Sınırlar tek süreç ve IP başına dakikada 300 okuma / 60 yazmadır. Reverse proxy headers varsayılan kapalıdır. Birden fazla instance için ortak rate-limit deposu kullanılmalıdır.
- Görseller thread pool'da işlenir, EXIF kaldırılır; referans yollarında başka kullanıcı klasörü veya path traversal kabul edilmez. İmzalı fotoğraf bağlantıları arayüzün 4 dakikalık yenilemesiyle güncellenir.
- Bağış/takas talebindeki kitap düzenleme ve kapatılmış hesaplara işlem açma kontrolleri sıkılaştırıldı.
- Tek origin production: `Dockerfile` React'i derler ve FastAPI üzerinden sunar. Container root kullanıcısıyla çalışmaz; `/api/ready` şema/veritabanı kontrolü yapar. Production ortamında PostgreSQL DATABASE_URL zorunludur.
- `backend/requirements.lock` Python sürümlerini sabitler. Frontend lockfile mevcuttur; npm güvenlik taramasında açık bulunmadı. GitHub Actions SQLite ve PostgreSQL testlerini, frontend test/derlemesini ve production bağımlılık güvenlik taramasını çalıştıracak biçimde eklendi.

### Production paketi

```powershell
docker build -t patikitap .
docker run --rm -p 8000:8000 --env-file .env.production patikitap
```

`.env.production` dosyasında yalnızca runtime `DATABASE_URL`, `APP_ENV=production` ve gerekiyorsa Supabase URL/publishable key bulunmalıdır; ADMIN_DATABASE_URL dağıtılmaz. TLS/alan adı ve SMTP hizmeti hosting ortamında yapılandırılır. Docker bu bilgisayarda kurulu olmadığı için image build yerelde çalıştırılamadı.

### Uygulama yedeği

Backend Python ortamında:

```powershell
python backup.py export
python backup.py verify --file ../.backups/patikitap-TARIH.json
```

Bu işlem uygulama tablolarını yedekler; Auth şifrelerini, kullanıcı oturumlarını veya Storage dosyalarını içermez. Supabase'in proje yedeğinin/PITR'ın yerine geçmez. `.backups` git ve Docker kapsamı dışındadır; içeriği kullanıcı verisi olarak korunmalıdır.

Geri yükleme yalnızca **ayrı, boş ve şeması kurulmuş** hedefe mümkündür. `RESTORE_DATABASE_URL` açıkça belirtilmelidir. Auth kullanıcı UUID'leri hedefte ayrıca mevcut olmalıdır. Dolu hedef reddedilir ve hiçbir kayıt silinmez. Transaction içindeki hata tüm yazmayı geri alır:

```powershell
python backup.py restore --file ../.backups/patikitap-TARIH.json
```

### PostgreSQL testleri

`TEST_DATABASE_URL` verilirse API testleri her senaryoda rastgele `patikitap_test_...` şeması oluşturur ve sonunda yalnızca o test şemasını temizler. Normal `patikitap` verisine dokunmaz. CI bu testleri ayrı PostgreSQL 17 servisinde çalıştırır. Eşzamanlı iki kabulün aynı kitabı iki kez ayıramadığı burada test edilir; SQLite koşusunda bu tek test atlanır.

### Harici doğrulama durumu

20 Ekim kontrolünde Supabase yönetim bağlantısı çalışırken bu bilgisayardan pooler 5432 ve 6543 portlarına TCP bağlantısı reddedildi. Bu yüzden yeni runtime hesabının doğrudan oturum açması ve gerçek üyeli fotoğraf yükleme bu ağda doğrulanamadı; migration ve yetkiler yönetim bağlantısı üzerinden kontrol edildi. `/api/health` süreç kontrolüdür; `/api/ready` veritabanı erişimini de denetler. Canlı pilot öncesi readiness başarılı olmalıdır.

İlk yönetici için kullanıcı tarafından bir e-posta adresi seçildi; Supabase'de doğrulanmış üyelik kaydı oluşmadan yönetici yetkisi verilmez. Hesap doğrulandıktan sonra yerel yönetim aracıyla bu hesaba atanır.

### Son doğrulama

GitHub Actions çalışması `39432552431` başarılı tamamlandı: SQLite backend, PostgreSQL backend (eşzamanlı kabul testi dahil) ve frontend kontrolleri yeşil. Yerelde 25 backend testi ve 3 frontend testi geçti; yalnızca PostgreSQL'e özgü tek test SQLite koşusunda atlandı. Frontend üretim derlemesi başarılı. npm güvenlik taraması ve OSV üzerinden 33 sabit Python bağımlılığı kontrolünde bilinen açık bulunmadı.

Kullanıcının açık onayıyla Supabase yönetim bağlantısından tek sorguda uygulama verisi anlık görüntüsü alındı; `.backups/patikitap-20261020.json` dosyasına kaydedildi. 6 kayıtlı bu yedek doğrulandı ve izole, geçici SQLite hedefinde geri yükleme denenerek 6 kitabın korunduğu kontrol edildi. Yedek ve bütün `.env` dosyaları GitHub kapsamı dışındadır.

### Bağlantı yeniden doğrulandı

20 Ekim sonraki kontrolde doğrudan Supabase bağlantısı yeniden başarılı oldu. `patikitap_runtime` hesabıyla 6 kitap okundu; DATABASE_URL bu doğrulanmış sınırlı hesaba ayarlandı. Önceki ağ hatasının kesin kaynağı belirlenemedi. Uygulamanın otomatik SQLite geçişi tamamen kaldırıldı: DATABASE_URL eksik veya PostgreSQL dışında olduğunda uygulama hata verir. SQLite yalnızca açıkça kurulan izole otomatik testlerde kullanılır. Rolün parola ve izin yönetimi Supabase yönetim kanalıyla yapılır; uygulama hesabına rol yönetim yetkisi verilmez.
