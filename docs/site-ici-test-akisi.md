# PatiKitap — adım adım site içi test akışı

Hazırlanma: 12 Kasım 2026 · Sürüm: `adca526` · Tahmini süre: 45–60 dakika.

Bu belge elle uygulayacağın test planıdır; aşağıdaki akışların senin hesaplarınla geçtiğine dair sonuç raporu değildir. Testler, belirtilen başlangıç komutları dışında site üzerinden yapılır.

## 1. Hazırlık ve siteyi açma

Yerel sunucular kapatıldı. Teste başlayacağında iki ayrı PowerShell penceresi aç:

**Birinci pencere — backend:**

```powershell
cd "C:\Users\ataka\OneDrive\Desktop\ToplumHizmet\patikitap\backend"
.\start.ps1
```

**İkinci pencere — frontend:**

```powershell
cd "C:\Users\ataka\OneDrive\Desktop\ToplumHizmet\patikitap\frontend"
npm run dev
```

Her iki pencere açık kalsın. Site: http://127.0.0.1:5173

- A hesabı: ilan sahibi / satıcı. Chrome normal profili gibi bir tarayıcıda aç.
- B hesabı: talep sahibi / alıcı. Edge gibi ayrı bir tarayıcıda aç. Aynı profilin iki sekmesi bağımsız oturum değildir.
- İki hesabın da doğrulanmış e-postası olsun. Yeni hesap oluşturursan doğrulama bağlantısını kaydı başlattığın açık sekmenin adres çubuğunda aç; yeni sekme kullanma.
- Oturum sekmeye özeldir: F5 girişini korur; sekmeyi normal şekilde kapatıp yeni bir sekme açınca yeniden giriş gerekir. Tarayıcının kapalı sekmeyi geri yükleme veya sekme çoğaltma özelliği sekme verisini geri getirebilir; kesin çıkış için Çıkış düğmesini kullan.
- Test ilanlarının başına `TEST-20261112-` ekle; tekrar testte farklı bir son ek kullan.
- Site yerelde çalışsa da ilanlar ve işlemler bağlı Supabase veritabanına kaydedilir. Demo ödeme için yalnızca ekrandaki örnek bilgileri kullan.
- Her bölüm için alttaki sonuç tablosunu doldur. Bir adım başarısızsa beklenen ve gördüğün sonucu not al.

## 2. Giriş, ana sayfa ve profil

1. Oturum açmadan ana sayfayı aç. Yeni eklenen kitaplar alanını ve kitap kataloğunu incele.
   **Beklenen:** Sayfa açılır; kitap varsa kartlar, yoksa anlaşılır boş liste mesajı görünür.
2. Oturumsuzken `http://127.0.0.1:5173/account` adresine git.
   **Beklenen:** Giriş sayfasına yönlendirilirsin; özel hesap bilgileri görünmez.
3. A hesabıyla önce yanlış, sonra doğru parolayla giriş yap.
   **Beklenen:** Yanlış parola hata verir; doğru parola hesabı açar.
4. Hesabım → Profil bölümünde görünen adı ve şehri değiştirip **Profilimi güncelle** düğmesine bas. F5 yap.
   **Beklenen:** Kaydettiğin bilgiler korunur.
5. B hesabını diğer tarayıcıda aç.
   **Beklenen:** İki tarayıcıda farklı hesaplar görünür.

## 3. İlan oluşturma, arama ve favori

1. A hesabında `http://127.0.0.1:5173/books/new` adresini aç.
2. Kitap adı `TEST-20261112-BAGIS`, yazar `Test Yazar`, kategori `Roman`, durum `İyi`, paylaşım türü `Bağış`, teslim bölgesi `Konya Kampüs` gir. İstersen kişisel bilgi içermeyen küçük bir kitap fotoğrafı ekle.
3. **Kitabı paylaş** düğmesine bas.
   **Beklenen:** Başarı bildirimi ve katalog görünür. Kitap, Hesabım → İlanlarım bölümünde de bulunur.
4. B hesabında `/books` sayfasına git; kitabı adıyla ara, Bağış filtresini seç ve detayını aç.
   **Beklenen:** Başlık, yazar, paylaşım türü ve varsa fotoğraf doğru görünür. F5 sonrasında ilan kaybolmaz.
5. B kitabı favorile; Hesabım → Favoriler bölümüne geç, ardından sayfayı yenile.
   **Beklenen:** Kitap favorilerde kalır; A'nın favorilerine eklenmez.

## 4. Bağış: talep → kabul → teslimat → karşılıklı onay

1. **B:** Bağış kitabının detayında **Talep oluştur** düğmesine bas. Teslimat olarak kampüs seç, kısa bir not yaz ve **Bağış talebi gönder** düğmesine bas.
   **Beklenen:** Hesabım → Talepler → Gönderdiklerim altında bekleyen talep görünür. Henüz tamamlanmış işlem oluşmaz.
2. **A:** Hesabım → Talepler → Bana gelenler bölümünü aç. Gerekirse sayfayı yenile. İlgili talepte **Kabul et** düğmesine bas.
   **Beklenen:** Her iki hesapta İşlemler bölümünde aynı kitap için işlem görünür; kitap ayrılır.
3. **A ve B:** İşlemler bölümündeki aşama göstergesini incele.
   **Beklenen:** Bağışta demo ödeme adımı yoktur. Teslimat hazırlanmadan teslim onayı verilmez.
4. **A:** İlgili işlemde **Teslimat bilgisi gir** düğmesine bas. Buluşma / teslim noktası alanına `Test — Kampüs kütüphanesi önü` yaz; **Teslimatı hazır olarak kaydet** düğmesine bas.
   **Beklenen:** Nokta bilgisi iki hesapta da görünür; işlem teslimat aşamasına geçer.
5. Test kitabının teslimini canlandırdıktan sonra **B:** **Teslimi onayla** → **Evet, kendi teslimimi onaylıyorum** düğmelerine bas.
   **Beklenen:** B'nin onayı görünür; yalnızca tek onayla işlem tamamlanmaz.
6. **A:** Aynı onayı ver.
   **Beklenen:** İşlem tamamlanır. Ücretsiz bağış için satış kaynaklı destek tutarı oluşmaz.
7. **İki hesap:** F5 yap.
   **Beklenen:** Tamamlanma ve onay bilgileri korunur.

## 5. Satış: başarısız demo → başarılı demo → teslimat

1. **A:** Yeni kitap oluştur: `TEST-20261112-SATIS`, paylaşım türü `Satış`, fiyat `100` TL. Diğer gerekli alanları doldur.
2. **B:** Kitabı bul → **Talep oluştur** → teslimat `Kargo` → kargo ücretini alıcı karşılasın → **Satış talebi gönder**.
3. **A:** Talepler bölümünden kabul et. İki hesapta İşlemler bölümünü aç.
   **Beklenen:** Ödeme beklenir. Başarılı demo ödeme olmadan satıcıda teslimat giriş düğmesi açılmaz. Satıcı alıcıya ait ödeme formunu/dekont geçmişini görmez.
4. **B:** İşlem içindeki **Güvenli demo ödeme** alanında tutar özetini kontrol et.
   **Beklenen:** Kitap 100 TL, bedelden ayrılan destek 20 TL, işlem gideri 0 TL, demo toplam 100 TL. Destek ayrıca eklenip 120 TL yapılmaz.
5. **B:** Sipariş adımında **Devam et**; Teslimat adımında alanlar boşken tekrar **Devam et**.
   **Beklenen:** Eksik alan uyarısı çıkar; sonraki adıma geçmez.
6. **B:** **Örnek bilgileri doldur** → **Devam et** → **Kartla ödeme simülasyonu** → örnek kart seç → **Devam et**.
   **Beklenen:** Gerçek kart numarası veya CVV istenmez. Onay kutusu işaretlenmeden ödeme tamamlama düğmesi kullanılamaz.
7. **B:** Simülasyon onay kutusunu işaretle → **Başarısız sonucu dene**.
   **Beklenen:** Başarısız demo kaydı geçmişte görünür. Satıcının teslimat adımı hâlâ açılmaz. Yeniden ödeme denenebilir.
8. **B:** Formun durumuna göre **Yeni demo denemesi** düğmesine bas veya yeniden açılan formdan ilerle. Bu kez **Havale / EFT simülasyonu** seç, örnek bilgilerle onaya gel ve **Demo ödemeyi tamamla** düğmesine bas.
   **Beklenen:** Başarılı kayıt ve DEMO referansı görünür. Aynı satış için yeniden başarılı ödeme yapmaya izin verilmez. Yenilemeden sonra geçmişte başarısız ve başarılı denemeler korunur.
9. **A:** İşlemler sekmesini görünür tutup yaklaşık 15 saniye bekle.
   **Beklenen:** Ödeme durumu otomatik yenilenir ve **Teslimat bilgisi gir** açılır. Açılmazsa sonucu not et; F5 ile ayrıca kontrol et.
10. **A:** Teslimat bilgisi gir → firma `Test Kargo`, takip numarası `TEST-20261112-001`, ücret `0` → **Teslimatı hazır olarak kaydet**.
    **Beklenen:** Kargo ve takip bilgileri iki hesapta görünür. Gerçek kargo oluşturulmaz.
11. Test teslimini canlandırdıktan sonra **B**, ardından **A** teslim onaylarını versin.
    **Beklenen:** Yalnızca iki onaydan sonra işlem tamamlanır.
12. `/impact` sayfasını aç ve yenile.
    **Beklenen:** Bu tamamlanan satış için tek bir 20 TL simülasyon destek kaydı oluşur. Sayfayı tekrar yenilemek veya tamamlanmış işlemi tekrar açmak yeni destek kaydı üretmez. Önceki satışların tutarları toplamda bulunabileceğinden yalnızca genel toplamın 20 TL olmasını bekleme.

**Teslimat ekranlarının farkı:** Demo ödeme formundaki adres ve kargo/elden seçimi yalnızca örnek ödeme ekranına aittir; sunucuya gönderilmez. Asıl işlemin teslimat yöntemi B'nin ilk talebinde seçilir; kargo veya buluşma bilgisi A'nın **Teslimat bilgisi gir** ekranında kaydedilir. Demo formda elden teslim seçmek, ilk talepteki kargoyu değiştirmez.

## 6. Takas: iki kitap, iki teslimat

1. **A:** `TEST-20261112-TAKAS-A` adlı, paylaşım türü Takas olan ilan aç.
2. **B:** `TEST-20261112-TAKAS-B` adlı, paylaşım türü Takas olan ilan aç.
3. **B:** A'nın kitabını aç → **Talep oluştur** → Takas edeceğin kitap alanında kendi test kitabını seç → kampüs teslimatı seç → **Takas teklifi gönder**.
4. **A:** Gelen teklifte önerilen kitap adını kontrol et ve kabul et.
   **Beklenen:** İki kitap da ayrılır; işlemde iki teslimat vardır. Demo ödeme bulunmaz.
5. **A:** Kendi göndereceği kitap için teslimat noktasını girip kaydet.
   **Beklenen:** B'nin teslimatı henüz hazırlanmadığı için işlem tamamlanamaz; tüm teslimatlar hazır olmadan onay aşaması açılmaz.
6. **B:** Kendi göndereceği kitap için teslimat noktasını girip kaydet.
7. Test teslimini canlandırdıktan sonra önce **A**, sonra **B** kendi teslim onayını versin.
   **Beklenen:** İki onaydan sonra işlem ve iki kitap tamamlanır. Satış desteği oluşmaz.

## 7. Ret, geri çekme ve işlem iptali

Bu kontroller için yeni bağış ilanları kullan; tamamlanan testleri yeniden kullanma.

1. **A:** `TEST-20261112-RET` ilanı aç. **B:** Talep gönder. **A:** Talebi **Reddet**.
   **Beklenen:** Talep reddedildi görünür; kabul edilmiş işlem oluşmaz.
2. **A:** `TEST-20261112-GERI-CEK` ilanı aç. **B:** Talep gönder; A kabul etmeden **Talebi geri çek**.
   **Beklenen:** Talep iptal olur; A artık bu talebi kabul ederek işlem başlatamaz.
3. **A:** `TEST-20261112-IPTAL` ilanı aç. **B:** Talep gönder. **A:** Kabul et; henüz teslimat hazırlamadan İşlemler → **İşlemi iptal et**.
   **Beklenen:** İşlem iptal olur; kitap yeniden kullanılabilir hâle gelir; destek kaydı oluşmaz.

Demo ödeme formundaki **İptal et**, ödeme denemesini iptal eder. İşlem kartındaki **İşlemi iptal et** ise kitap paylaşım işlemini iptal eder; bunları aynı işlem olarak değerlendirme.

## 8. Favori fiyatı ve ilan kaldırma

1. **A:** `TEST-20261112-FAVORI` adlı 100 TL satış ilanı oluştur. **B:** Favorile; talep gönderme.
2. **A:** İlanlarım bölümünde ilanı düzenleyip fiyatı 80 TL yap.
3. **B:** Favorileri yenile.
   **Beklenen:** Güncel fiyat 80 TL ve favoriye eklendikten sonraki fiyat düşüşü görünür.
4. **A:** Bu geçmişsiz ilanı sil ve istenen onayı ver.
   **Beklenen:** Katalogdan kalkar. B'nin favorilerinde kaldırılmış ilan bilgisi görünür; B favoriden çıkarabilir.
5. **A:** Önceki bölümlerde talep/işlem geçmişi oluşmuş bir ilanı kalıcı silmeyi dene.
   **Beklenen:** Geçmişli ilan silinemez; uygun durumlarda arşivleme kullanılabilir.

## 9. Parola, sayfalar ve mobil kontrol

1. **B:** Çıkış yap → giriş ekranındaki parola yenileme seçeneğinden e-postanı gönder.
2. İsteği başlattığın sekmeyi açık tut; e-postadaki yeni bağlantıyı kopyalayıp o sekmenin adres çubuğunda aç.
   **Beklenen:** Yeni parola formu açılır. `127.0.0.1` adresini `localhost` ile değiştirme.
3. Yeni parolayı kaydet; çıkış yap. Eski parolayla girişin reddedildiğini, yeni parolayla giriş yapılabildiğini kontrol et.
4. `/books`, `/books/new`, `/account` ve `/impact` sayfalarında F5, geri ve ileri düğmelerini dene.
   **Beklenen:** Sayfa bulunamadı hatası oluşmaz; adres ve içerik eşleşir; oturum gerektiren sayfalar korunur.
5. Tarayıcıyı daralt veya mobil görünüm aç; katalog, kitap ekleme, İşlemler ve demo ödeme formunu kontrol et.
   **Beklenen:** Alanlar okunur; düğmelere ulaşılır; zorunlu alanlar ekran dışında kalmaz.
6. Bildirimleri oku, favori ekle/çıkar ve yenile; çıkış yapıp yeniden gir.
   **Beklenen:** Değişiklikler ilgili hesapta korunur; diğer hesaba karışmaz.

## 10. İsteğe bağlı: yöneticiyle sorun çözme

Yönetici hesabın yoksa bu bölümü **Engelli — yönetici hesabı yok** olarak işaretle.

1. Ayrı bir test ilanıyla kabul edilmiş, tamamlanmamış işlem oluştur.
2. Katılımcı hesapla işlemde **Sorun bildir** üzerinden açıklamalı şikâyet gönder.
   **Beklenen:** İşlem inceleme durumuna geçer; normal tamamlama akışı durur.
3. Yönetici hesabıyla `/admin` sayfasını aç; şikâyeti inceleyip uygun devam/iptal kararı ver.
   **Beklenen:** Karar, işlem ve kitap durumuna yansır; iki katılımcı yenilediğinde aynı sonucu görür.
4. Normal A/B hesabıyla `/admin` adresini aç.
   **Beklenen:** Yönetim içeriğine erişilemez; yetki uyarısı görünür.

## Sonuç kaydı ve kapatma

| Bölüm | Durum: Geçti / Kaldı / Engelli / Çalıştırılmadı | İşlem veya ilan no | Gözlem |
|---|---|---|---|
| Giriş ve profil | Çalıştırılmadı | | |
| İlan, arama, favori | Çalıştırılmadı | | |
| Bağış | Çalıştırılmadı | | |
| Demo satış ve destek | Çalıştırılmadı | | |
| Takas | Çalıştırılmadı | | |
| Ret, geri çekme, iptal | Çalıştırılmadı | | |
| Fiyat düşüşü ve silme | Çalıştırılmadı | | |
| Parola, yönlendirme, mobil | Çalıştırılmadı | | |
| Yönetici ve şikâyet | Çalıştırılmadı | | |

Hata bildirirken: **hesap rolü + kitap/işlem no + yaptığın adım + beklediğin sonuç + gördüğün sonuç** yaz. Parola veya e-posta doğrulama bağlantısını ekleme.

Test sonunda bekleyen test taleplerini geri çek; uygun test ilanlarını arşivle veya geçmişsiz olanları sil. Tamamlanmış işlemlerin geçmişini koru. İki PowerShell penceresinde de **Ctrl+C** ile yerel sunucuları kapat.
