# Smoke test case hazırlama ve kabul uyarıları

Bu belge test hazırlayan ekip içindir. Bir test sonuç raporu değildir; aşağıdaki senaryoların canlı ortamda geçtiğini göstermez.

## Ortam ve ön koşullar

- Birbirinden farklı, e-postası doğrulanmış iki normal kullanıcı: A ve B.
- Ayrı bir yönetici hesabı ve oturumsuz tarayıcı profili.
- Her kullanıcı için ayrı tarayıcı profili veya ayrı tarayıcı kullanın. Aynı profilin sekmeleri oturum paylaşır.
- E-posta kutularına erişim; kişisel bilgi içermeyen JPEG/PNG/WebP fotoğrafı ve 5 MB üzeri örnek dosya.
- Çalışan frontend, FastAPI ve Supabase bağlantısı. Yerel uygulama kullanılması yerel veritabanı kullanıldığı anlamına gelmez; kayıtlar Supabase'dedir.
- PKCE e-posta bağlantılarını isteğin başlatıldığı aynı tarayıcı/profil ve origin üzerinde açın. `localhost` ve `127.0.0.1` farklı origin'dir.
- Test edilen commit, ortam adresi, tarih, tarayıcı/sürüm ve cihaz genişliğini rapora yazın.

## Her test case için zorunlu alanlar

```text
ID / Başlık:
Öncelik: P0 / P1
Ön koşul ve kullanıcı rolü:
Test verisi:
Adımlar:
Beklenen sonuç:
Gerçekleşen sonuç:
Durum: Çalıştırılmadı / Geçti / Kaldı / Engelli
İlan-talep-işlem ID'leri / güvenli kanıt / hata kaydı:
Test eden / tarih / commit / ortam:
Temizlik veya bırakılan kayıtlar:
```

## Zorunlu P0 senaryoları

| ID | Senaryo / adımlar | Beklenen sonuç |
|---|---|---|
| SM-01 | `GET /api/ready` isteği at; kataloğu aç. | Readiness 200 döner; katalog hata vermeden yüklenir. Sadece `/api/health` başarısı veritabanı bağlantısını kanıtlamaz. |
| SM-02 | Yeni e-postayla kayıt ol; doğrulama e-postasını aç; giriş yap. | E-posta ulaşır; hesap doğrulanır; giriş ve korumalı işlem başarılıdır. |
| SM-03 | Yanlış parolayla giriş dene; doğrulanmamış hesapla korumalı işlem dene. | Hatalı giriş reddedilir; doğrulanmamış kullanıcı korumalı işlem yapamaz; anlaşılır hata görünür. |
| SM-04 | Parolamı unuttum isteği gönder; yeni bağlantıyı aç; parolayı değiştir; çıkış yap; eski ve yeni parolayla ayrı ayrı giriş dene. | Yeni parola formu açılır; yeni parola çalışır; eski parola reddedilir. |
| SM-05 | Çıkış yap; `/account` aç; tokensız korumalı API isteği at. | Sayfa girişe yönlenir; korumalı API 401 döner; özel veriler ekranda kalmaz. |
| SM-06 | Yönetici ve normal kullanıcı ile ayrı ayrı `/admin` aç; normal kullanıcı token'ıyla `/api/admin/overview` çağır. | Yönetici verileri görür; normal kullanıcı yetki hatası görür ve API 403 döner. Menünün gizli olması tek başına yeterli değildir. |
| SM-07 | `/account`, `/admin`, `/impact` adreslerini doğrudan aç; F5, geri ve ileri düğmelerini kullan. | Sayfa 404 vermeden yüklenir; oturum ve rol kuralları korunur; adresle içerik eşleşir. |
| SM-08 | A fotoğraflı ilan oluştursun; sayfayı yenilesin; B giriş yapıp ilanı açsın. | İlan Supabase'e, fotoğraf özel Storage bucket'ına kaydolur; yenileme ve ikinci kullanıcıda görüntülenir. |
| SM-09 | B, A'nın ilanını değiştirmeyi/arşivlemeyi API üzerinden denesin; A kendi ilanına talep göndersin. | Sahiplik kuralları istekleri reddeder; kayıt değişmez. |
| SM-10 | A bağış ilanı açsın; B talep etsin; A kabul etsin; A teslimatı hazırlasın; iki taraf ayrı ayrı onaylasın. | Kitap kabulde ayrılır; işlem yalnızca iki onay sonrası tamamlanır; kitap tamamlanmış duruma geçer. |
| SM-11 | A ve B takas ilanları açsın; B kendi kitabını teklif etsin; A kabul etsin; iki taraf kendi teslimatını hazırlayıp onaylasın. | İki kitap ayrılır; iki teslimat oluşur; gerekli teslimatlar ve karşılıklı onay sonrası işlem ve iki kitap tamamlanır. |
| SM-12 | 100 TL örnek satışını talep, kabul, teslimat ve iki onayla tamamla. | Tek bir 20 TL simülasyon destek kaydı oluşur; gerçek ödeme veya mama teslimatı yapılmış gibi gösterilmez. |
| SM-13 | Aynı talebi/kabulü/onayı iki kez tetikle; aynı kitap için iki bekleyen talebi kabul etmeyi dene. | Kitap iki ayrı işleme ayrılamaz; yinelenen istekler ek işlem veya destek kaydı oluşturmaz. Beklenen iş kuralı hatası kabul edilebilir. |
| SM-14 | İşlem sonrası yenile; çıkış ve tekrar giriş yap. | İlan, talep, işlem ve onay durumları Supabase'den doğru yüklenir; sadece tarayıcı belleğinde kalmaz. |

## Eklenmesi gereken negatif ve kullanılabilirlik kontrolleri

| ID | Öncelik | Senaryo | Beklenen sonuç |
|---|---|---|---|
| NG-01 | P0 | Görsel olmayan dosya veya 5 MB üzeri fotoğraf yükle. | Yükleme reddedilir; anlaşılır hata görünür; bozuk ilan oluşmaz. |
| NG-02 | P0 | Teslimat hazırlanmadan onayla; ardından yalnızca tek tarafla onayla. | Erken onay reddedilir; tek tarafın onayı işlemi tamamlamaz veya destek oluşturmaz. |
| NG-03 | P0 | Kabul edilen işlemi gönderimden önce iptal et. | İşlem iptal olur; ilgili kitap/kitaplar tekrar kullanılabilir duruma gelir. |
| NG-04 | P0 | Devam eden işlemde şikâyet aç; yöneticiyle sonuçlandır. | İşlem inceleme süresince durur; devam/iptal kararı doğru duruma ve kitaplara yansır. |
| NG-05 | P0 | Başka kullanıcının işlem veya bildirim ID'siyle okuma/değiştirme isteği at. | Yetkisiz işlem engellenir; özel veri sızmaz. Genel kitap kataloğunun okunması bu kapsamda değildir. |
| NG-06 | P0 | `/api/olmayan` ve `/assets/olmayan.js` isteği at. | 404 döner; başarılı HTML yanıtıyla hata maskelenmez. |
| NG-07 | P0 | Test ortamında API erişimini kes veya isteği engelle. | Hata ve yeniden deneme olanağı görünür; boş ekran veya yanlış başarı mesajı oluşmaz. Canlı ortak veritabanını kapatmayın. |
| NG-08 | P1 | Mobil genişlikte giriş, fotoğraflı ilan, talep ve teslimat ekranlarını kullan. | Formlar ve düğmeler görünür, kullanılabilir; kritik alanlar taşmaz. |
| NG-09 | P1 | Kullanılmış/süresi dolmuş doğrulama veya parola bağlantısını aç. | Uygulama başarı iddiasında bulunmaz; anlaşılır hata/yeni bağlantı isteme yolu sunar. |
| NG-10 | P1 | Favori ekle/çıkar; bildirim oku; yenile. | Değişiklikler doğru kullanıcıya ait olarak kalıcıdır. |

## Veri ve kanıt güvenliği

- Test ilanlarını `SMOKE-YYYYMMDD-...` ile adlandırın; gerçek adres, telefon, kimlik veya kişisel fotoğraf kullanmayın.
- Raporda parola, JWT, refresh token, doğrulama bağlantısı, tam Authorization başlığı veya veritabanı bağlantı adresi bulunmamalıdır. Ekran görüntülerini kontrol edin.
- API isteklerinde JWT'nin Authorization Bearer başlığında taşındığını doğrulayın; tokenı kopyalayıp rapora koymayın. URL veya uygulama loglarında token olmamalıdır.
- Gerçek ödeme yapmayın: satış ve destek bu sürümde simülasyondur.
- Paylaşılan Supabase projesinde toplu silme, tablo sıfırlama veya kullanıcı silme yapmayın. Test kayıtlarının ID'lerini raporlayın; normal uygulama arşiv/iptal akışlarını kullanın.
- Hosting ortamında HTTPS, Auth Site URL/redirect listesi ve yeni e-posta bağlantıları ayrıca denenmelidir. Yerelde geçmesi üretimde geçtiği anlamına gelmez.

## Kabul ve uyarı kuralları

1. Pilot/yayın kabulü için bütün P0 senaryoları geçmelidir. P0 Kaldı, Engelli veya Çalıştırılmadı ise kabul tamamlanmış değildir.
2. P1 sonuçları ve kalan kusurlar sorumlusu ile raporlanmalıdır; ertelenen kusur varsa proje sorumlusu açıkça kabul etmelidir.
3. Gerçek e-posta, özel Storage fotoğraf yükleme ve iki gerçek kullanıcı akışı çalıştırılmadıysa **test edilmedi** yazın. Birim testleri ve başarılı build bunların yerine geçmez.
4. Önceki sürümün sonucu yeni commit için otomatik geçerli değildir. Düzeltmeden sonra ilgili senaryo ve etkilenen temel akış yeniden çalıştırılmalıdır.
5. Smoke test, kapsamlı güvenlik/yük testi veya kusursuzluk garantisi değildir. Eşzamanlı kabulün gerçek yarış koşulu ayrıca otomatik PostgreSQL testinde doğrulanmalıdır; sırayla iki tıklama eşzamanlılık kanıtı değildir.

## Sonuç özeti şablonu

```text
Commit / Ortam / Tarih:
P0: Toplam __ | Geçti __ | Kaldı __ | Engelli __ | Çalıştırılmadı __
P1: Toplam __ | Geçti __ | Kaldı __ | Engelli __ | Çalıştırılmadı __
Gerçek e-posta / fotoğraf / iki kullanıcı: __ / __ / __
Açık kusurlar ve sorumluları:
Kabul: Uygun / Uygun değil
Test eden:
```
