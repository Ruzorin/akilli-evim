# 🛠️ OPENCLAW_SKILLS.md — Modül 27 Yetenek (Skill) Kütüphanesi

> **Jarvis Executive Edition — OpenClaw Digital Sandbox**
> OpenClaw'un 6 otonom yeteneği: Python fonksiyon taslakları, kullanım
> senaryoları, System Prompt entegrasyonları ve Zero-Trust güvenlik kilitleri.
>
> **Kullanıcı profili:** Kıbrıs'ta DAÜ'de YBS okuyan öğrenci/sporcu.
> **Kısıt:** VSS (Visual Snow) ile ilgili hiçbir özellik bu modülde yer almaz.

---

## 📋 İçindekiler

1. [mealie_recipe_hunter](#1-mealie_recipe_hunter)
2. [flight_and_price_sniper](#2-flight_and_price_sniper)
3. [academic_research_agent](#3-academic_research_agent)
4. [auto_order_and_booking](#4-auto_order_and_booking)
5. [financial_sentinel](#5-financial_sentinel)
6. [career_and_gig_sniper](#6-career_and_gig_sniper)

---

## 🔒 Zero-Trust Güvenlik Mimarisi (Tüm Skill'ler için Ortak)

```
┌─────────────────────────────────────────────────────────────┐
│                    OPENCLAW SANDBOX                           │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Skill 1 │  │ Skill 2 │  │ Skill 3 │  │ Skill 4 │       │
│  │ Recipe  │  │ Flight  │  │ Academic│  │ Order   │       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
│       │            │            │            │              │
│  ┌────▼────────────▼────────────▼────────────▼────┐        │
│  │           APPROVAL GATEWAY (MQTT → HA)         │        │
│  │  Ödeme/Login/İptal → Mobil onay ZORUNLU        │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
│  İzinler:                                                   │
│  ✅ Browser (headless, ekranda pencere AÇILMAZ)             │
│  ✅ Mealie API POST (tarif ekleme)                          │
│  ✅ MQTT publish (Lamba, Life OS, Magic Mirror)             │
│  ❌ DELETE/PUT (mevcut verileri silemez)                    │
│  ❌ Login (onaysız)                                         │
│  ❌ Ödeme (onaysız)                                         │
│  ❌ Shell komutları (skill modunda)                         │
└─────────────────────────────────────────────────────────────┘
```

### Onay Gerektiren İşlemler

| İşlem | Onay Yöntemi | MQTT Topic |
|-------|-------------|------------|
| Ödeme (sipariş, bilet) | Mobil push → HA Companion | `openclaw/approval/payment` |
| Login (site girişi) | Mobil push → HA Companion | `openclaw/approval/login` |
| İptal (abonelik) | Mobil push → HA Companion | `openclaw/approval/cancel` |
| Başvuru (iş/staj) | Mobil push → HA Companion | `openclaw/approval/apply` |
| Tarif kayıt (Mealie) | Otomatik (onaysız) | — |
| PDF özet (Magic Mirror) | Otomatik (onaysız) | — |

---

## 1. mealie_recipe_hunter

> **İnternetten tarif bul → Context7 ile doğrula → Mealie REST API'ye enjekte et**

### Kullanım Senaryosu

```
Kullanıcı: "Jarvis, bana yüksek proteinli Ege usulü tarifler bul"
    ↓ (arka planda, ekranda pencere AÇILMAZ)
ADIM 1: Browser MCP → 10+ kaynak tara (allrecipes, seriouseats, yemek.com...)
ADIM 2: Context7 MCP → her tarifin protein oranı + malzeme kalitesini doğrula
ADIM 3: Çöp tarifleri ele (düşük protein, sentetik malzeme, clickbait)
ADIM 4: Mealie API POST /api/recipes/create/url → veritabanına kaydet
ADIM 5: MQTT → Lamba (Modül 29) başını salla + yeşil ışık
ADIM 6: MiniMax → "7 tarif bulundu, 5 doğrulandı, 5 kaydedildi"
```

### Python Fonksiyon Taslağı

```python
@skill(
    name="mealie_recipe_hunter",
    description="İnternetten tarif bul, Context7 ile doğrula, Mealie'ye kaydet",
    category="kitchen",
    requires_approval=False,  # Tarif kayıt onaysız
    allowed_tools=["browser_mcp", "context7_mcp", "mealie_api"],
    blocked_actions=["delete", "put", "login", "payment"],
)
async def mealie_recipe_hunter(
    concept: str,           # "Ege usulü yüksek protein"
    min_protein_g: float = 25.0,  # Minimum protein/porsiyon
    max_results: int = 10,  # Max taranan kaynak
    athlete_weight_kg: float = 125,  # Sporcu kilosu (makro hesabı için)
) -> HuntResult:
    """
    Otonom tarif avcısı.

    Returns:
        HuntResult: total_found, total_verified, total_imported
    """
    # 1. Browser MCP → tarif ara
    candidates = await browser_mcp.search_recipes(concept, max_results)

    # 2. Context7 MCP → doğrula
    verified = []
    for candidate in candidates:
        if await context7_mcp.verify_protein(candidate, min_protein_g):
            if await context7_mcp.verify_ingredients(candidate):
                verified.append(candidate)

    # 3. Mealie API → kaydet
    imported_slugs = []
    for recipe in verified:
        slug = await mealie_api.scrape_url(recipe.url)
        if slug:
            imported_slugs.append(slug)

    # 4. MQTT → Lamba
    if imported_slugs:
        await mqtt.publish("jarvis/lamp/motion/command",
            json.dumps({"action": "nod", "color": "green", "brightness": 50}))

    # 5. MiniMax → sesli özet
    await minimax.speak(f"{len(verified)} tarif doğrulandı, "
                        f"{len(imported_slugs)} kaydedildi.")

    return HuntResult(
        total_found=len(candidates),
        total_verified=len(verified),
        total_imported=len(imported_slugs),
    )
```

### System Prompt Entegrasyonu

```markdown
## SKILL: mealie_recipe_hunter

Sen bir spor beslenme uzmanısın. Kullanıcı sana bir konsept verir
(örn: "Ege usulü yüksek protein"). Senin görevin:

1. Browser MCP ile en az 10 farklı kaynak tara
2. Context7 MCP ile her tarifin protein oranı ve malzeme kalitesini doğrula
3. Çöp tarifleri ele (düşük protein, sentetik malzeme, clickbait)
4. Doğrulanan tarifleri Mealie API'ye POST et
5. Lamba'ya (Modül 29) "Görev Tamamlandı" sinyali gönder
6. Ekrana uzun metin YAZMA — sadece MiniMax'a kısa sesli özet gönder

GÜVENLİK:
- Sadece POST /api/recipes/create/url iznin var
- DELETE/PUT yasak (mevcut tarifleri silemezsin)
- Login/ödeme yasak
- Ekranda pencere AÇMA — headless mode
```

### Zero-Trust Kilitleri

| Kilit | Açıklama |
|-------|----------|
| `requires_approval=False` | Tarif kayıt onaysız (güvenli işlem) |
| `allowed_tools=["browser_mcp", "context7_mcp", "mealie_api"]` | Sadece bu 3 araç |
| `blocked_actions=["delete", "put", "login", "payment"]` | Bu işlemler yasak |
| `max_results=10` | Bir seferde max 10 kaynak (aşırı tarama koruması) |
| `headless=True` | Ekranda pencere AÇILMAZ |

---

## 2. flight_and_price_sniper

> **Arka planda uçak bileti/ürün fiyatı takip → eşik altına düşerse mobil onay → rezervasyon**

### Kullanım Senaryosu

```
Kullanıcı: "Jarvis, önümüzdeki ay Cuma gidiş Pazar dönüş en ucuz
           İzmir-Kıbrıs biletlerini takibe al, 1500₺ altına düşerse al"
    ↓ (arka planda, günde 2 kez)
ADIM 1: Browser MCP → Pegasus/AnadoluJet/THY sitelerini tara
ADIM 2: Fiyatları karşılaştır → en ucuzu belirle
ADIM 3: Eşik kontrolü → fiyat 1500₺ altında mı?
ADIM 4: EVET → Mobil push: "İzmir-Ercan 1350₺ buldum, alayım mı?"
ADIM 5: Kullanıcı onayla → OpenClaw tarayıcıda rezervasyon yapar
ADIM 6: MQTT → Lamba başını salla + MiniMax "Biletiniz alındı"
```

### Python Fonksiyon Taslağı

```python
@skill(
    name="flight_and_price_sniper",
    description="Uçak bileti/ürün fiyatı takip → eşik → mobil onay → rezervasyon",
    category="finance",
    requires_approval=True,   # Ödeme/onay ZORUNLU
    approval_type="payment",  # Ödeme onayı
    allowed_tools=["browser_mcp", "deepseek", "mqtt"],
    blocked_actions=["payment_without_approval", "login_without_approval"],
    schedule="0 9,21 * * *",  # Günde 2 kez (09:00, 21:00)
)
async def flight_and_price_sniper(
    route: str,              # "İzmir-ERCAN"
    departure_date: str,     # "2026-09-05"
    return_date: str,        # "2026-09-07"
    price_threshold_try: float,  # 1500.0 (₺)
    airlines: list = None,   # ["pegasus", "anadolujet", "thy"]
) -> SniperResult:
    """
    Arka planda uçak bileti fiyat takibi.

    Schedule: Günde 2 kez (09:00, 21:00) otomatik çalışır.
    Fiyat eşik altına düşerse mobil onay ister.
    """
    airlines = airlines or ["pegasus", "anadolujet", "thy"]

    # 1. Browser MCP → havayolu sitelerini tara (headless)
    results = []
    for airline in airlines:
        flights = await browser_mcp.search_flights(
            airline=airline,
            route=route,
            departure=departure_date,
            return=return_date,
            headless=True,  # Ekranda pencere AÇILMAZ
        )
        results.extend(flights)

    # 2. En ucuzu bul
    cheapest = min(results, key=lambda f: f.price_try)
    log.info(f"En ucuz: {cheapest.airline} {cheapest.price_try}₺ "
             f"({departure_date} → {return_date})")

    # 3. Eşik kontrolü
    if cheapest.price_try <= price_threshold_try:
        # 4. Mobil onay iste
        approved = await request_approval(
            action="payment",
            description=f"{cheapest.airline} {route} "
                        f"{cheapest.price_try}₺ (eşik: {price_threshold_try}₺)",
            amount_try=cheapest.price_try,
        )

        if approved:
            # 5. Rezervasyon yap (tarayıcıda)
            booking = await browser_mcp.book_flight(
                airline=cheapest.airline,
                flight_id=cheapest.flight_id,
                headless=True,
            )

            # 6. MQTT → Lamba + MiniMax
            await mqtt.publish("jarvis/lamp/motion/command",
                json.dumps({"action": "nod", "color": "green"}))
            await minimax.speak(
                f"Biletiniz alındı efendim. {cheapest.airline} "
                f"{route} {cheapest.price_try} lira."
            )
            return SniperResult(booked=True, price=cheapest.price_try)
        else:
            await minimax.speak("Onay vermediniz, takibe devam ediyorum.")
            return SniperResult(booked=False, price=cheapest.price_try)

    # Eşik altında değil → logla, bekle
    log.info(f"Eşik altında değil: {cheapest.price_try}₺ > {price_threshold_try}₺")
    return SniperResult(booked=False, price=cheapest.price_try)
```

### System Prompt Entegrasyonu

```markdown
## SKILL: flight_and_price_sniper

Sen bir seyahat asistanısın. Kullanıcı sana bir rota ve fiyat eşiği verir.
Senin görevin:

1. Günde 2 kez (09:00, 21:00) havayolu sitelerini tara (headless)
2. Fiyatları karşılaştır, en ucuzu belirle
3. Fiyat eşik altına düşerse mobil onay iste
4. Onay gelirse rezervasyon yap (tarayıcıda, headless)
5. Onay gelmezse takibe devam et

GÜVENLİK:
- Ödeme ONAYSIZ yapılamaz — mutlaka mobil onay iste
- Login ONAYSIZ yapılamaz
- Ekranda pencere AÇMA — headless mode
- Sadece belirlenen havayolları sitelerine gir
```

### Zero-Trust Kilitleri

| Kilit | Açıklama |
|-------|----------|
| `requires_approval=True` | Ödeme onayı ZORUNLU |
| `approval_type="payment"` | Ödeme tipi onay |
| `schedule="0 9,21 * * *"` | Günde 2 kez otomatik (cron) |
| `blocked_actions=["payment_without_approval"]` | Onaysız ödeme yasak |
| `headless=True` | Ekranda pencere AÇILMAZ |

---

## 3. academic_research_agent

> **Akademik PDF'leri oku → Context7 ile analiz et → özet çıkar → Magic Mirror'a gönder**

### Kullanım Senaryosu

```
Kullanıcı: "Jarvis, Veritabanı dersi notlarını oku, yarın sınav"
    ↓ (arka planda)
ADIM 1: OpenClaw → /documents/veritabani.pdf dosyasını oku
ADIM 2: Context7 MCP → PDF içeriğini analiz et
ADIM 3: DeepSeek → özet çıkar, "hap bilgileri" belirle
ADIM 4: MQTT → Modül 15 (Magic Mirror) "Bugünün Hap Bilgileri"
ADIM 5: Magic Mirror'da günlük çalışma notu belirir
ADIM 6: MiniMax → "Veritabanı notlarını özetledim, aynada görebilirsin"
```

### Python Fonksiyon Taslağı

```python
@skill(
    name="academic_research_agent",
    description="PDF oku → analiz et → özet → Magic Mirror'a gönder",
    category="education",
    requires_approval=False,  # Okuma/özet onaysız
    allowed_tools=["file_read", "context7_mcp", "deepseek", "mqtt"],
    blocked_actions=["file_write", "file_delete", "login", "payment"],
)
async def academic_research_agent(
    pdf_paths: list,         # ["/documents/veritabani.pdf", ...]
    course_name: str,         # "Veritabanı"
    exam_date: str = None,   # "2026-09-15" (sınava kaç gün kaldı?)
    summary_length: str = "brief",  # "brief" | "detailed"
) -> ResearchResult:
    """
    Akademik PDF'leri oku, özet çıkar, Magic Mirror'a gönder.

    Returns:
        ResearchResult: summary, key_points, mirror_sent
    """
    all_text = ""

    # 1. PDF'leri oku (sandbox içinde, sadece okuma)
    for pdf_path in pdf_paths:
        text = await file_read.extract_text(pdf_path)
        all_text += f"\n\n=== {pdf_path} ===\n{text}"

    # 2. Context7 MCP → analiz et
    analysis = await context7_mcp.analyze_document(
        content=all_text,
        course=course_name,
    )

    # 3. DeepSeek → özet + hap bilgileri
    prompt = (
        f"Sen bir akademik asistansın. {course_name} dersi notlarını "
        f"özetle. Sınava {exam_date}'e kadar çalışacak bir öğrenci için "
        f"en kritik 5 'hap bilgi' çıkar.\n\n"
        f"Notlar:\n{all_text[:8000]}\n\n"
        f"JSON döndür:\n"
        f'{{"summary": "...", "key_points": ["...", "..."], '
        f'"study_plan": "..."}}'
    )

    result = await deepseek.chat(prompt)

    # 4. MQTT → Magic Mirror (Modül 15)
    mirror_payload = json.dumps({
        "module": "daily_study_notes",
        "course": course_name,
        "summary": result["summary"],
        "key_points": result["key_points"],
        "exam_date": exam_date,
        "days_until_exam": _days_until(exam_date),
    })

    await mqtt.publish("jarvis/mirror/study_notes", mirror_payload)

    # 5. MiniMax → sesli onay
    await minimax.speak(
        f"{course_name} notlarını özetledim efendim. "
        f"Aynada günlük çalışma notlarını görebilirsiniz."
    )

    return ResearchResult(
        summary=result["summary"],
        key_points=result["key_points"],
        mirror_sent=True,
    )
```

### System Prompt Entegrasyonu

```markdown
## SKILL: academic_research_agent

Sen bir akademik asistansın. Kullanıcı sana ders notlarını (PDF) verir.
Senin görevin:

1. PDF'leri oku (sandbox içinde, sadece okuma — yazma/silme yasak)
2. Context7 MCP ile içeriği analiz et
3. DeepSeek ile özet + 5 kritik "hap bilgi" çıkar
4. Magic Mirror'a (Modül 15) günlük çalışma notu olarak gönder
5. MiniMax ile sesli onay ver

GÜVENLİK:
- Sadece dosya OKUMA iznin var (yazma/silme yasak)
- Login/ödeme yasak
- Magic Mirror'a sadece MQTT ile veri gönder (UI değiştirme yasak)
```

### Zero-Trust Kilitleri

| Kilit | Açıklama |
|-------|----------|
| `requires_approval=False` | Okuma/özet onaysız (güvenli) |
| `allowed_tools=["file_read", "context7_mcp", "deepseek", "mqtt"]` | Sadece okuma + analiz |
| `blocked_actions=["file_write", "file_delete"]` | Yazma/silme yasak |
| `text_limit=8000` | DeepSeek'e max 8000 karakter (token koruması) |

---

## 4. auto_order_and_booking

> **Yemeksepeti/Getir'den otonom sipariş → kalori/makro → Life OS (Modül 16)**

### Kullanım Senaryosu

```
Kullanıcı: "Jarvis, çok yorgunum, Yemeksepeti'nden her zamanki
           yüksek proteinli menümü sipariş et"
    ↓ (arka planda)
ADIM 1: Browser MCP → Yemeksepeti'ye gir (headless)
ADIM 2: "Her zamanki" menüyü bul → sepete ekle
ADIM 3: Mobil onay: "Yüksek proteinli menü 350₺, onaylıyor musun?"
ADIM 4: Kullanıcı onayla → ödeme yap
ADIM 5: Sepet içeriğini oku (DOM) → DeepSeek makro tahmini
ADIM 6: MQTT → Modül 16 (Life OS) günlük kaloriye ekle
ADIM 7: MiniMax → "Sipariş verildi, 700 kalori eklendi"
```

### Python Fonksiyon Taslağı

```python
@skill(
    name="auto_order_and_booking",
    description="Yemeksepeti/Getir otonom sipariş + makro → Life OS",
    category="daily_life",
    requires_approval=True,   # Ödeme onayı ZORUNLU
    approval_type="payment",
    allowed_tools=["browser_mcp", "deepseek", "mqtt"],
    blocked_actions=["payment_without_approval", "login_without_approval"],
)
async def auto_order_and_booking(
    platform: str,           # "yemeksepeti" | "getir"
    order_description: str,  # "her zamanki yüksek proteinli menüm"
    budget_limit_try: float = 500.0,  # Max bütçe (güvenlik)
) -> OrderResult:
    """
    Otonom sipariş + makro enjeksiyonu.

    Returns:
        OrderResult: ordered, total_try, calories, protein_g
    """
    # 1. Browser MCP → platforma gir (headless)
    await browser_mcp.navigate(f"https://www.{platform}.com", headless=True)

    # 2. Sipariş içeriğini belirle
    cart = await browser_mcp.search_and_add(
        query=order_description,
        headless=True,
    )

    # 3. Bütçe kontrolü
    total = sum(item.price for item in cart)
    if total > budget_limit_try:
        await minimax.speak(
            f"Bütçe aşımı: {total} lira, limit {budget_limit_try} lira."
        )
        return OrderResult(ordered=False, total_try=total)

    # 4. Mobil onay iste
    approved = await request_approval(
        action="payment",
        description=f"{platform}: {order_description} — {total}₺",
        amount_try=total,
    )

    if not approved:
        await minimax.speak("Onay vermediniz, sipariş iptal edildi.")
        return OrderResult(ordered=False, total_try=total)

    # 5. Ödeme yap (tarayıcıda, headless)
    await browser_mcp.checkout(headless=True)

    # 6. Sepet içeriğini oku (DOM scraping)
    cart_items = await browser_mcp.read_cart_dom()

    # 7. DeepSeek → makro tahmini
    macros = await deepseek.estimate_macros(cart_items)

    # 8. MQTT → Modül 16 (Life OS) günlük kaloriye ekle
    await mqtt.publish("jarvis/lifeos/nutrition/inject", json.dumps({
        "source": platform,
        "items": [{"name": i.name, "quantity": i.quantity} for i in cart_items],
        "nutrition": {
            "calories": macros.calories,
            "protein_g": macros.protein_g,
            "carbs_g": macros.carbs_g,
            "fat_g": macros.fat_g,
        },
        "action": "add_to_daily_intake",
    }))

    # 9. MQTT → Lamba (Modül 29) başını salla
    await mqtt.publish("jarvis/lamp/motion/command",
        json.dumps({"action": "nod", "color": "green"}))

    # 10. MiniMax → sesli onay
    await minimax.speak(
        f"Sipariş verildi efendim. {macros.calories} kalori, "
        f"{int(macros.protein_g)} gram protein günlük hedefinize eklendi."
    )

    return OrderResult(
        ordered=True,
        total_try=total,
        calories=macros.calories,
        protein_g=macros.protein_g,
    )
```

### System Prompt Entegrasyonu

```markdown
## SKILL: auto_order_and_booking

Sen bir kişisel asistansın. Kullanıcı sana bir sipariş verir.
Senin görevin:

1. Browser MCP ile platforma gir (Yemeksepeti/Getir) — headless
2. Sipariş içeriğini sepete ekle
3. Bütçe kontrolü yap (limit aşımı → iptal)
4. Mobil onay iste (ödeme ONAYSIZ yapılamaz)
5. Onay gelirse ödeme yap
6. Sepet içeriğini oku → DeepSeek makro tahmini
7. Modül 16 (Life OS) günlük kaloriye ekle (MQTT)
8. Lamba'ya (Modül 29) sinyal gönder
9. MiniMax ile sesli onay ver

GÜVENLİK:
- Ödeme ONAYSIZ yapılamaz — mutlaka mobil onay iste
- Login ONAYSIZ yapılamaz
- Bütçe limiti aşılırsa sipariş iptal
- Ekranda pencere AÇMA — headless mode
- Sadece belirlenen platformlara gir (Yemeksepeti, Getir)
```

### Zero-Trust Kilitleri

| Kilit | Açıklama |
|-------|----------|
| `requires_approval=True` | Ödeme onayı ZORUNLU |
| `approval_type="payment"` | Ödeme tipi onay |
| `budget_limit_try=500.0` | Max bütçe (güvenlik limiti) |
| `blocked_actions=["payment_without_approval"]` | Onaysız ödeme yasak |
| `headless=True` | Ekranda pencere AÇILMAZ |

---

## 5. financial_sentinel

> **Faturaları/döviz kurlarını oku → bütçe güncelle → kullanılmayan abonelikleri tespit et → iptal et**

### Kullanım Senaryosu

```
Kullanıcı: "Jarvis, bu ayki harcamalarımı analiz et"
    ↓ (arka planda)
ADIM 1: Browser MCP → banka uygulaması/mailleri tara (headless)
ADIM 2: Giderleri kategorize et (kira, yemek, abonelik, ulaşım)
ADIM 3: Kullanılmayan abonelikleri tespit et
    → "Patron, 3 aydır kullanmadığın Netflix var, iptal edeyim mi?"
ADIM 4: Kullanıcı onayla → OpenClaw iptal butonuna tıklar
ADIM 5: Döviz kuru çek → Kıbrıs bütçesini güncelle
ADIM 6: MQTT → Modül 16 (Life OS) bütçe verisi
ADIM 7: MiniMax → "Netflix iptal edildi, ayda 200₺ tasarruf"
```

### Python Fonksiyon Taslağı

```python
@skill(
    name="financial_sentinel",
    description="Fatura/döviz oku → bütçe → kullanılmayan abonelik iptal",
    category="finance",
    requires_approval=True,   # İptal onayı ZORUNLU
    approval_type="cancel",  # İptal tipi onay
    allowed_tools=["browser_mcp", "deepseek", "mqtt"],
    blocked_actions=["cancel_without_approval", "payment", "login_without_approval"],
    schedule="0 8 1 * *",  # Her ayın 1'i 08:00 (aylık bütçe analizi)
)
async def financial_sentinel(
    analyze_subscriptions: bool = True,  # Abonelik analizi yap
    currency_update: bool = True,        # Döviz kuru güncelle
    unused_threshold_months: int = 3,   # 3 ay kullanılmayan = iptal öner
) -> FinancialResult:
    """
    Otonom bütçe analizi ve abonelik iptali.

    Schedule: Her ayın 1'i 08:00 otomatik çalışır.
    """
    result = FinancialResult()

    # 1. Browser MCP → banka/mailleri tara (headless)
    expenses = await browser_mcp.scan_expenses(headless=True)

    # 2. DeepSeek → kategorize et
    categorized = await deepseek.categorize_expenses(expenses)

    # 3. Kullanılmayan abonelikleri tespit et
    if analyze_subscriptions:
        unused = await _detect_unused_subscriptions(
            categorized, unused_threshold_months
        )

        for sub in unused:
            # 4. Mobil onay iste
            approved = await request_approval(
                action="cancel",
                description=f"{sub.name}: {unused_threshold_months} aydır "
                            f"kullanılmıyor, {sub.monthly_try}₺/ay. İptal?",
            )

            if approved:
                # 5. İptal et (tarayıcıda, headless)
                await browser_mcp.cancel_subscription(
                    service=sub.name,
                    headless=True,
                )
                result.cancelled.append(sub.name)
                result.monthly_savings_try += sub.monthly_try

    # 6. Döviz kuru çek
    if currency_update:
        rates = await browser_mcp.get_exchange_rates(
            currencies=["USD/TRY", "EUR/TRY"],
            headless=True,
        )
        result.exchange_rates = rates

    # 7. MQTT → Modül 16 (Life OS) bütçe verisi
    await mqtt.publish("jarvis/lifeos/budget/update", json.dumps({
        "monthly_expenses": categorized,
        "cancelled_subscriptions": result.cancelled,
        "monthly_savings_try": result.monthly_savings_try,
        "exchange_rates": result.exchange_rates,
    }))

    # 8. MiniMax → sesli özet
    if result.cancelled:
        await minimax.speak(
            f"Patron, {len(result.cancelled)} abonelik iptal edildi. "
            f"Ayda {result.monthly_savings_try} lira tasarruf."
        )
    else:
        await minimax.speak("Bütçe analizi tamamlandı. Tasarruf fırsatı yok.")

    return result
```

### System Prompt Entegrasyonu

```markdown
## SKILL: financial_sentinel

Sen bir finansal asistansın. Kullanıcının harcamalarını analiz edersin.
Senin görevin:

1. Browser MCP ile banka/mailleri tara (headless)
2. Giderleri kategorize et (kira, yemek, abonelik, ulaşım)
3. Kullanılmayan abonelikleri tespit et (3+ ay aktif kullanım yok)
4. Mobil onay iste: "Patron, X aboneliği 3 aydır kullanılmıyor, iptal?"
5. Onay gelirse iptal et (tarayıcıda, headless)
6. Döviz kuru çek → Kıbrıs bütçesini güncelle
7. Modül 16 (Life OS) bütçe verisi gönder (MQTT)

GÜVENLİK:
- İptal ONAYSIZ yapılamaz — mutlaka mobil onay iste
- Ödeme YAPAMAZSIN (sadece iptal)
- Login ONAYSIZ yapılamaz
- Banka hesap bilgilerini SAKLA (log'a yazma, MQTT'ye gönderme)
- Ekranda pencere AÇMA — headless mode
```

### Zero-Trust Kilitleri

| Kilit | Açıklama |
|-------|----------|
| `requires_approval=True` | İptal onayı ZORUNLU |
| `approval_type="cancel"` | İptal tipi onay |
| `blocked_actions=["cancel_without_approval", "payment"]` | Onaysız iptal + ödeme yasak |
| `schedule="0 8 1 * *"` | Her ayın 1'i 08:00 (aylık) |
| `headless=True` | Ekranda pencere AÇILMAZ |
| `redact_sensitive=True` | Banka bilgilerini log'da gizle |

---

## 6. career_and_gig_sniper

> **LinkedIn/Upwork'te YBS odaklı staj/iş tara → ön yazı hazırla → başvuru yap**

### Kullanım Senaryosu

```
Kullanıcı: "Jarvis, bana veri analizi veya web otomasyonu alanında
           remote staj/freelance iş bul"
    ↓ (arka planda)
ADIM 1: Browser MCP → LinkedIn/Upwork/iş ilanı sitelerini tara (headless)
ADIM 2: YBS odaklı ilanları filtrele (veri analizi, web otomasyonu, Python)
ADIM 3: DeepSeek → her ilana özel "Ön Yazı (Cover Letter)" hazırla
ADIM 4: Mobil onay: "5 uygun ilan buldum, başvurayım mı?"
ADIM 5: Kullanıcı onayla → OpenClaw başvuru yapar
ADIM 6: MQTT → Lamba başını salla + MiniMax "5 başvuru yapıldı"
```

### Python Fonksiyon Taslağı

```python
@skill(
    name="career_and_gig_sniper",
    description="LinkedIn/Upwork YBS iş tara → ön yazı → başvuru",
    category="career",
    requires_approval=True,   # Başvuru onayı ZORUNLU
    approval_type="apply",    # Başvuru tipi onay
    allowed_tools=["browser_mcp", "deepseek", "mqtt"],
    blocked_actions=["apply_without_approval", "login_without_approval"],
    schedule="0 10 * * 1-5",  # Hafta içi her gün 10:00 (iş saati)
)
async def career_and_gig_sniper(
    keywords: list,           # ["veri analizi", "web otomasyonu", "Python"]
    job_type: str = "remote", # "remote" | "hybrid" | "onsite"
    platforms: list = None,   # ["linkedin", "upwork"]
    max_applications: int = 5, # Günlük max başvuru
    user_profile: dict = None, # {"skills": [...], "education": "DAÜ YBS"}
) -> CareerResult:
    """
    Otonom staj/iş arama ve başvuru.

    Schedule: Hafta içi her gün 10:00.
    """
    platforms = platforms or ["linkedin", "upwork"]
    user_profile = user_profile or {
        "skills": ["Python", "SQL", "veri analizi", "web otomasyonu"],
        "education": "DAÜ YBS (devam ediyor)",
        "location": "Kıbrıs",
    }

    # 1. Browser MCP → platformları tara (headless)
    jobs = []
    for platform in platforms:
        results = await browser_mcp.search_jobs(
            platform=platform,
            keywords=keywords,
            job_type=job_type,
            headless=True,
        )
        jobs.extend(results)

    # 2. DeepSeek → YBS odaklı filtrele
    relevant_jobs = await deepseek.filter_relevant_jobs(
        jobs=jobs,
        user_profile=user_profile,
    )

    # 3. DeepSeek → her ilana özel ön yazı hazırla
    applications = []
    for job in relevant_jobs[:max_applications]:
        cover_letter = await deepseek.generate_cover_letter(
            job=job,
            user_profile=user_profile,
        )
        applications.append({
            "job": job,
            "cover_letter": cover_letter,
        })

    # 4. Mobil onay iste
    approved = await request_approval(
        action="apply",
        description=f"{len(applications)} uygun ilan buldum. "
                    f"Başvuruları yapayım mı?",
    )

    if not approved:
        await minimax.speak("Onay vermediniz, başvuru yapılmadı.")
        return CareerResult(applied=0)

    # 5. Başvuru yap (tarayıcıda, headless)
    applied = 0
    for app in applications:
        success = await browser_mcp.submit_application(
            platform=app["job"].platform,
            job_id=app["job"].id,
            cover_letter=app["cover_letter"],
            headless=True,
        )
        if success:
            applied += 1

    # 6. MQTT → Lamba + MiniMax
    await mqtt.publish("jarvis/lamp/motion/command",
        json.dumps({"action": "nod", "color": "green"}))
    await minimax.speak(
        f"{applied} başvuru yapıldı efendim. "
        f"Ön yazılar profilinize uygun hazırlandı."
    )

    return CareerResult(
        applied=applied,
        applications=applications,
    )
```

### System Prompt Entegrasyonu

```markdown
## SKILL: career_and_gig_sniper

Sen bir kariyer asistanısın. Kullanıcı DAÜ'de YBS okuyor.
Senin görevin:

1. Browser MCP ile LinkedIn/Upwork'i tara (headless)
2. YBS odaklı ilanları filtrele (veri analizi, web otomasyonu, Python)
3. DeepSeek ile her ilana özel mükemmel "Ön Yazı" hazırla
4. Mobil onay iste: "5 uygun ilan buldum, başvurayım mı?"
5. Onay gelirse başvuru yap (tarayıcıda, headless)
6. Lamba'ya sinyal gönder + MiniMax sesli onay

KULLANICI PROFİLİ:
- DAÜ YBS öğrencisi
- Yetenekler: Python, SQL, veri analizi, web otomasyonu
- Konum: Kıbrıs (remote tercih)

GÜVENLİK:
- Başvuru ONAYSIZ yapılamaz — mutlaka mobil onay iste
- Login ONAYSIZ yapılamaz
- CV/kişisel bilgileri sadece başvuru formuna gir (başka yere gönderme)
- Ekranda pencere AÇMA — headless mode
- Günlük max 5 başvuru (spam koruması)
```

### Zero-Trust Kilitleri

| Kilit | Açıklama |
|-------|----------|
| `requires_approval=True` | Başvuru onayı ZORUNLU |
| `approval_type="apply"` | Başvuru tipi onay |
| `max_applications=5` | Günlük max 5 başvuru (spam koruması) |
| `blocked_actions=["apply_without_approval"]` | Onaysız başvuru yasak |
| `schedule="0 10 * * 1-5"` | Hafta içi 10:00 (iş saati) |
| `headless=True` | Ekranda pencere AÇILMAZ |

---

## 📊 Skill Özeti

| # | Skill | Kategori | Onay | Schedule | Araçlar |
|---|-------|----------|------|----------|---------|
| 1 | mealie_recipe_hunter | kitchen | ❌ (onaysız) | Manuel | browser, context7, mealie |
| 2 | flight_and_price_sniper | finance | ✅ (ödeme) | Günde 2x | browser, deepseek, mqtt |
| 3 | academic_research_agent | education | ❌ (onaysız) | Manuel | file_read, context7, deepseek |
| 4 | auto_order_and_booking | daily_life | ✅ (ödeme) | Manuel | browser, deepseek, mqtt |
| 5 | financial_sentinel | finance | ✅ (iptal) | Aylık | browser, deepseek, mqtt |
| 6 | career_and_gig_sniper | career | ✅ (başvuru) | Hafta içi günlük | browser, deepseek, mqtt |

---

## 🔗 Modül Bağlantıları

| Skill → Modül | Bağlantı Tipi |
|---------------|---------------|
| mealie_recipe_hunter → Modül 28 (Mealie) | REST API POST |
| mealie_recipe_hunter → Modül 29 (Lamba) | MQTT (nod + green) |
| flight_and_price_sniper → Modül 29 (Lamba) | MQTT (nod + green) |
| academic_research_agent → Modül 15 (Magic Mirror) | MQTT (study notes) |
| auto_order_and_booking → Modül 16 (Life OS) | MQTT (nutrition inject) |
| auto_order_and_booking → Modül 29 (Lamba) | MQTT (nod + green) |
| financial_sentinel → Modül 16 (Life OS) | MQTT (budget update) |
| career_and_gig_sniper → Modül 29 (Lamba) | MQTT (nod + green) |
| Tüm skill'ler → jarvis_core (MiniMax) | HA REST API (tts.speak) |
| Tüm skill'ler → jarvis_core (DeepSeek) | DeepSeek API (chat) |

---

*Bu dosya, OpenClaw (Modül 27) yetenek kütüphanesinin anayasasıdır. Yeni skill'ler eklendikçe güncellenir.*