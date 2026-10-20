# Veri modeli ve iş kuralları

## Tablolar

| Tablo | Görev |
|---|---|
| profiles | Supabase Auth UUID'sine bağlı profil ve hesap erişimi |
| books | İlan sahibi, kitap bilgisi, paylaşım türü, fiyat, fotoğraf ve ilan durumu |
| requests | Talep sahibi, varsa takas kitabı, teslimat koşulları ve karar |
| transactions | Kabul edilen talebin katılımcıları, tutar anlık görüntüsü ve onaylar |
| deliveries | Tek yönlü teslimat; takasta her yön için ayrı kayıt |
| support_records | Tamamlanan örnek satışın tekil simülasyon destek kaydı |
| favorites | Kullanıcı-kitap birleşik anahtarıyla favoriler |
| notifications | Kullanıcıya ait bildirim ve okundu zamanı |
| complaints | İlan veya işleme ait şikâyet ve yönetici kararı |
| audit_logs | İşlem yapan kullanıcı, eylem, hedef kayıt ve zaman |

## İşlem kuralları

1. Doğrulanmış üyeler kendi ilanlarını oluşturur. Örnek ilanların sahibi yoktur ve talep edilemez.
2. Aktif ilan talep edilebilir; kendi ilanına talep veya aynı kitaba ikinci bekleyen talep yasaktır.
3. Takas talebinde teklif kitabı talep sahibinin aktif bir takas ilanı olmalıdır.
4. Talebi yalnızca ilan sahibi kabul/reddeder; talep sahibi geri çeker.
5. Kabul sırasında kitaplar ID sırasıyla kilitlenir. Uygunluk tekrar kontrol edilir. Bir veya iki kitap ayrılır; ilgili diğer talepler kapatılır. Para tutarları ve %20 örnek destek oranı sabitlenir.
6. Satış/bağış bir, takas iki teslimat kaydı oluşturur. Gönderen kargo/takip veya teslim noktasını girer. Kabul edilen teslimat yöntemi ve ödeyen taraf sonradan tek taraflı değiştirilmez.
7. Teslimatlar hazırlanmadan onay verilemez. Her katılımcı kendi onayını verir. İki onay olmadan işlem tamamlanmaz. Son onay tekrarlansa da ikinci destek kaydı oluşmaz.
8. Teslimat başlamadan katılımcı işlemi iptal edebilir; kitaplar yeniden açılır. Teslimat başladıktan sonra ihtilaf süreci kullanılır.
9. İşlem şikâyeti katılımcı tarafından açılır. Süren işlem ihtilaflı hâle gelir, onay ve teslimat güncellemesi durur. Yönetici şikâyeti sonuçlandırır veya işlemi iptal eder. Başka açık şikâyet varsa süreç durmaya devam eder. Tamamlanmış işlem geriye alınmaz.
10. İlan sahibi yalnızca aktif ilanını düzenler; bekleyen talep varsa önce sonuçlandırır. Arşivleme ve moderasyon ilgili bekleyen talepleri kapatır. Ayrılmış kitap doğrudan gizlenemez; ihtilaf akışı kullanılır.
11. Favori/bildirimler yalnızca sahibine, talepler/işlemler yalnızca katılımcılara, şikâyetler sahibine ve yöneticilere açılır. Yönetici rolü kullanıcı tarafından düzenlenebilir metadata'dan okunmaz.
12. Özel şema Data API'ye açılmaz. Tüm tablolarda RLS vardır; anon ve authenticated rollerine uygulama tablosu erişimi verilmez. İş kuralları doğrulanmış FastAPI isteklerinde uygulanır. Storage farklı olarak yalnızca giriş yapmış üyelere fotoğraf okuma; kendi UUID klasörüne yazma/silme izni verir.

## Supabase'e uygulanacak paket

`business-schema.sql` kullanıcı onayıyla Supabase’e `complete_business_workflows` adıyla uygulanan DDL paketinin kaynak kopyasıdır. Mevcut kitap tablosu genişletildi, 9 yeni tablo ve özel `book-media` alanı oluşturuldu. Altı mevcut kitap korundu. Bu dosyayı tekrar çalıştırmayın; sonraki değişiklikler ayrı migration olmalıdır.

## Doğrulama kapsamı

İzole yerel testler: üyelik zorunluluğu, sahiplik/IDOR, rol yükseltme engeli, talep tekilliği, rakip talebin kapanması, bağış/satış/takas akışı, iki yönlü takas teslimatı, iptal, ihtilaf ve yönetici kararı, tekil destek kaydı, favoriler, bildirim gizliliği, moderasyon, hesap kapatma/açma ve oturum servisi hatasında erişimin reddi.

## İlave sağlamlaştırma

Kapalı hesapların ilanlarına yeni talep açılamaz ve kapalı talep sahibinin talebi kabul edilmez. Bekleyen takas teklifi olan kitap düzenlenemez. DB çalışma rolü, yabancı anahtar indeksleri, sayfalama, güvenli fotoğraf referansları ve istek korumaları 20 Ekim 2026 tamamlamalarına dahildir. Gerçek ödeme ve kargo entegrasyonu kapsamı değiştirilmemiştir.
