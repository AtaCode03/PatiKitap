# Render üzerinden canlı yayın

Hazırlanan yapı: tek Docker web servisi React arayüzünü ve FastAPI'yi aynı HTTPS adresinden sunar. Veritabanı, kimlik ve görseller mevcut Supabase projesinde kalır. `render.yaml` ücretsiz plan, Frankfurt bölgesi, 8000 portu ve `/api/ready` kontrolünü tanımlar. Otomatik dağıtım kapalıdır; güncellemeler kontrollü yayınlanır.

## Kurulum

1. Render hesabını aç ve GitHub'daki `AtaCode03/PatiKitap` deposuna erişim ver.
2. Test edilen son kaynakların `main` dalına gönderildiğini doğrula. Render → New → Blueprint üzerinden depoyu ve `render.yaml` dosyasını seç.
3. İstenen sunucu değişkenlerini Render'ın gizli ortam değişkenleri alanına gir:
   - `DATABASE_URL`: yerelde çalışan **patikitap_runtime** hesabının Supabase Session pooler bağlantısı.
   - `SUPABASE_URL`: kullanılan Supabase proje adresi.
   - `SUPABASE_PUBLISHABLE_KEY`: aynı projenin publishable anahtarı.
4. `ADMIN_DATABASE_URL`, yönetici parolası veya service-role anahtarı ekleme. `.env` ve yedekler dağıtım paketine dahil edilmez. Yeni veritabanı oluşturulmaz, başlangıçta migration çalıştırılmaz.
5. Dağıtımı başlat; Docker build ve `/api/ready` kontrolünün başarılı olmasını bekle. Gerçek canlı adresi Render sonucundan al; isim müsaitliğini varsayma.

## Supabase giriş bağlantıları

Supabase → Authentication → URL Configuration:

- Site URL: Render'ın verdiği tam HTTPS adresi.
- Redirect URLs: aynı adresin kökü ve `/auth/reset-password` yolu.
- Yerel test devam edecekse mevcut `http://127.0.0.1:5173` izinlerini koru.

Kayıt ve parola yenileme e-postalarını canlı adresten yeniden iste. Eski localhost bağlantıları canlı adresi doğrulamaz. Sekme bazlı PKCE nedeniyle e-postadaki bağlantıyı işlemi başlatan açık sekmenin adres çubuğunda aç.

## Yayın doğrulaması

- `/api/ready`: HTTP 200 ve `status: ready`.
- `/`, `/books`, `/books/new`, `/account`: doğrudan açma ve F5 doğru çalışır; özel sayfalar oturum ister.
- `/api/olmayan`: 404; HTML ile gizlenmez.
- İki test hesabıyla giriş, fotoğraf yükleme, demo satış, ödeme ve teslimat akışını `site-ici-test-akisi.md` üzerinden çalıştır.
- Gerçek e-posta ve iki hesap akışı bitmeden kullanıcı kabul testini tamamlandı sayma.

## İşletim notları

Ücretsiz web servisi hareketsizlikte uyur; ilk istek gecikebilir. Ücretli plana geçiş ayrı bir seçimdir. Veriler Supabase'de olduğundan servisin yeniden başlaması onları silmez. Yerel uygulama ile canlı yayın aynı veritabanını kullanır.

Mevcut hız sınırı süreç/IP başınadır; Docker proxy başlıklarını güvenilir kabul etmez. Render üzerinde gerçek istemci IP ayrımı doğrulanmadan yoğun kullanıma açma; proxy arkasındaki kullanıcılar aynı sınırı paylaşabilir. Bu ilk kurulum küçük pilot içindir.

Kaynak: https://render.com/docs/blueprint-spec · https://render.com/docs/docker · https://render.com/docs/your-first-deploy
