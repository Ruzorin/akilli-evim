/* =============================================================================
 * magic_mirror — MagicMirror² Minimalist Konfigürasyon
 * =============================================================================
 * Bu dosya Raspberry Pi Zero 2 W üzerinde çalışan MagicMirror² yazılımının
 * konfigürasyonudur. ~/MagicMirror/config/config.js dosyasına kopyalanır.
 *
 * 🎨 "CALM TECHNOLOGY" TASARIM FELSEFESİ:
 * =============================================================================
 * Bu arayüz, "Calm Technology" (Sakin Teknoloji) prensiplerine göre tasarlanmıştır:
 *
 *   1. SAF BEYAZ YAZI, SİYAH ARKA PLAN (OLED hissiyatı)
 *      - Renkli ikonlar YOK → dikkat dağıtıcı, "oyuncu" hissi
 *      - Sadece beyaz yazı → "bilgi", "minimalist", "premium"
 *      - Siyah arka plan → two-way mirror'dan ışık geçmiyor → ayna illüzyonu korunur
 *
 *   2. MINIMALIST YERLEŞİM
 *      - Sağ üst: Saat + tarih (zarif, ince font)
 *      - Sol üst: Hava durumu (sade metin, ikon yok)
 *      - Alt orta: Spotify (o an çalan şarkı) — EN ÖNEMLİ modül
 *
 *   3. GİZLİ TEKNOLOJİ
 *      - Ekran açıldığında bile "teknoloji" değil "bilgi" görünür
 *      - Animasyonlar, geçiş efektleri YOK → sakin, "her zaman oradaydı" hissi
 *      - Font: İnce, zarif → "lüks otel" değil "Tony Stark" hissi
 *
 *   4. MQTT ENTEGRASYONU
 *      - Home Assistant, MQTT üzerinden aynaya özel mesaj gönderebilir
 *      - "Atmosphere set to Deep Flow..." gibi sinematik metinler
 *      - MMM-MQTT modülü ile alınır
 * =============================================================================
 */

let config = {
  address: "0.0.0.0",     // Tüm ağ arayüzlerinden erişilebilir (HA MQTT için)
  port: 8080,             // MagicMirror² web arayüz portu
  basePath: "/",
  ipWhitelist: [],        // Tüm IP'lere izin (yerel ağ)

  // -------------------------------------------------------------------------
  // YERLEŞİM — Modüllerin ekran üzerindeki konumları
  // -------------------------------------------------------------------------
  // MagicMirror², ekranı 9 bölgeye böler:
  //   top_left, top_center, top_right
  //   center_left, center_center, center_right
  //   bottom_left, bottom_center, bottom_right
  //
  // Biz minimalist bir yerleşim kullanıyoruz:
  //   top_right:    Saat + tarih
  //   top_left:     Hava durumu
  //   bottom_center: Spotify (o an çalan şarkı)
  //   center_center: MQTT mesajları (sinematik metinler — geçici)
  // -------------------------------------------------------------------------
  language: "tr",
  locale: "tr-TR",
  timeFormat: 24,         // 24 saat formatı
  units: "metric",        // Celsius, km/h
  logLevel: ["INFO", "LOG", "WARN", "ERROR"],

  modules: [
    // =========================================================================
    // MODÜL 1: SAAT + TARİH (Sağ Üst)
    // =========================================================================
    // Zarif, ince font. Sadece saat ve tarih — saniye yok ( dikkat dağıtıcı).
    // "Calm Technology": Saat "orada" ama "bağırmıyor" — ince, zarif.
    {
      module: "clock",
      position: "top_right",
      config: {
        displaySeconds: false,        // Saniye gösterme — dikkat dağıtıcı
        showPeriod: false,            // AM/PM gösterme (24 saat)
        showPeriodUpper: false,
        clockBold: false,             // Kalın font değil — ince, zarif
        timeFormat: 24,
        dateFormat: "DD MMMM YYYY",   // "02 Ağustos 2026" formatı
        showDate: true,
        // Font boyutu — varsayılan, ama CSS ile ince yapacağız
      }
    },

    // =========================================================================
    // MODÜL 2: HAVA DURUMU (Sol Üst)
    // =========================================================================
    // Sade metin — ikonlar YOK. "24°C, Açık" gibi minimal bilgi.
    // OpenWeatherMap API anahtarı gerekir (ücretsiz).
    {
      module: "weather",
      position: "top_left",
      config: {
        weatherProvider: "openweathermap",
        apiBase: "https://api.openweathermap.org/data/2.5",
        apiKey: "YOUR_OPENWEATHERMAP_API_KEY",  // ← Ücretsiz API anahtarı al
        lat: 41.0082,               // İstanbul enlem
        lon: 28.9784,               // İstanbul boylam
        units: "metric",            // Celsius
        degreeLabel: true,          // "24°C" formatı
        showHumidity: false,        // Nem gösterme — minimalist
        showIndoorTemperature: false,
        showSun: false,             // Güneş doğumu/batımı gösterme
        showPrecipitationAmount: false,
        // İkonlar kapalı — sadece metin (Calm Technology)
        // CSS ile ikonları gizleyeceğiz
        onlyTemp: true,              // Sadece sıcaklık — detay yok
        useBeaufort: false,
        animationSpeed: 1000,       // 1 saniye geçiş — yavaş, sakin
        updateInterval: 600000,     // 10 dakikada bir güncelle
      }
    },

    // =========================================================================
    // MODÜL 3: SPOTIFY — O AN ÇALAN ŞARKI (Alt Orta)
    // =========================================================================
    // 🎯 EN ÖNEMLİ MODÜL
    // Aynanın alt ortasında, o an odada çalan Spotify şarkısının adı ve
    // sanatçısı görünür. Misafir, aynaya baktığında "bu şarkı ne?" diye
    // telefonuna bakmasına gerek yok — ayna söyler.
    //
    // "Calm Technology": Şarkı bilgisi "orada" ama "bağırmıyor" —
    // ince beyaz yazı, siyah arka plan. Animasyon yok.
    //
    // Kurulum: MMM-Spotify modülü MagicMirror'a eklenmeli
    //   cd ~/MagicMirror/modules
    //   git clone https://github.com/skuethe/MMM-Spotify.git
    {
      module: "MMM-Spotify",
      position: "bottom_center",
      config: {
        // Spotify API kimlik bilgileri (Spotify Developer'dan alın)
        clientID: "YOUR_SPOTIFY_CLIENT_ID",
        clientSecret: "YOUR_SPOTIFY_CLIENT_SECRET",
        authToken: "YOUR_SPOTIFY_AUTH_TOKEN",

        // Güncelleme aralığı — 5 saniye (şarkı değişimi yakala)
        updateInterval: 5000,

        // Görünüm — minimalist
        style: "minimal",            // Minimal mod — sadece şarkı adı + sanatçı
        showAlbumArt: false,         // Albüm kapağı YOK — sadece metin (Calm Tech)
        showVolumeLevel: false,      // Ses seviyesi gösterme
        showTrackNumber: false,      // Parça numarası gösterme
        showProgressBar: false,      // İlerleme çubuğu YOK — minimalist

        // Eğer şarkı çalmıyorsa modülü gizle
        onStart: null,               // Başlangıçta bir şey yapma
        deviceDisplay: "room_spatial_audio",  // Spatial audio cihazını izle

        // Font ve stil — CSS ile beyaz, ince
      }
    },

    // =========================================================================
    // MODÜL 4: MQTT — HOME ASSISTANT'TAN GELEN ÖZEL MESAJLAR (Orta)
    // =========================================================================
    // Bu modül, HA'tan MQTT üzerinden gelen özel mesajları aynanın ortasında
    // gösterir. Örnek: "Atmosphere set to Deep Flow..." (intimacy modu)
    //
    // Mesaj 10 saniye görünür, sonra kaybolur → sinematik geçici metin.
    //
    // Kurulum: MMM-MQTT modülü MagicMirror'a eklenmeli
    //   cd ~/MagicMirror/modules
    //   git clone https://github.com/shbatm/MMM-MQTT.git
    {
      module: "MMM-MQTT",
      position: "center_center",
      config: {
        mqttServers: [
          {
            address: "gl-mt3000.local",   // MQTT broker (GL-MT3000)
            port: 1883,
            // Abone olunan topic — HA bu topic'e mesaj publish eder
            subscriptions: [
              {
                topic: "jarvis/mirror/message",
                // Mesaj formatı: {"text": "Atmosphere set to Deep Flow...", "duration": 10}
                // Sadece "text" alanını göster
                label: "Jarvis Message",
                valueTemplate: "{{value_json.text}}",
                // Mesaj geldikten sonra kaç saniye görünecek
                displayDuration: 10000,    // 10 saniye
              }
            ]
          }
        ],
        // Görünüm — CSS ile italik, beyaz, büyük font
      }
    },

    // =========================================================================
    // MODÜL 5: COMPLIMENTS — KARŞILAMA MESAJLARI (Kapalı)
    // =========================================================================
    // MagicMirror²'nin varsayılan "compliments" modülü kapalı.
    // Neden? "You look great today!" gibi mesajlar "oyuncu" hissi yaratır.
    // Biz sadece MQTT ile gelen KONTROLLÜ mesajlar kullanıyoruz.
    // {
    //   module: "compliments",
    //   position: "lower_third",
    //   config: {}
    // },
  ],

  // =========================================================================
  // CSS — "CALM TECHNOLOGY" STİLİ
  // =========================================================================
  // MagicMirror²'nin varsayılan CSS'ini geçersiz kılar.
  // Bu stiller, MagicMirror'ın custom.css dosyasına da eklenebilir.
  // Ama burada tutmak tüm konfigürasyonu tek dosyada toplar.
  // =========================================================================
};

// -------------------------------------------------------------------------
// "CALM TECHNOLOGY" CSS EKLEMELERİ
// -------------------------------------------------------------------------
// Bu stiller, MagicMirror'ın custom.css dosyasına kopyalanmalıdır:
//
// /* Saf beyaz yazı, siyah arka plan — OLED hissiyatı */
// body {
//   background-color: #000000;    /* Tam siyah — two-way mirror'dan ışık geçmesin */
//   color: #FFFFFF;               /* Saf beyaz yazı */
//   font-family: 'Helvetica Neue', 'Arial', sans-serif;
//   font-weight: 200;             /* İnce font — zarif, lüks */
// }
//
// /* Saat — ince, zarif */
// .clock .time {
//   font-size: 48px;
//   font-weight: 200;             /* İnce */
//   letter-spacing: 2px;          /* Harfler arası boşluk — premium */
// }
// .clock .date {
//   font-size: 18px;
//   font-weight: 200;
//   opacity: 0.7;                  /* Hafif şeffaf — "bağırmıyor" */
// }
//
// /* Hava durumu — sade metin, ikon yok */
// .weather .weathericon {
//   display: none;                 /* İkonları gizle — Calm Technology */
// }
// .weather .temperature {
//   font-size: 24px;
//   font-weight: 200;
// }
//
// /* Spotify — alt orta, ince yazı */
// .MMM-Spotify .spotify {
//   font-size: 20px;
//   font-weight: 200;
//   text-align: center;
// }
// .MMM-Spotify .spotify .song {
//   font-size: 22px;
//   font-weight: 300;             /* Biraz daha kalın — şarkı adı vurgulu */
// }
// .MMM-Spotify .spotify .artist {
//   font-size: 18px;
//   font-weight: 200;
//   opacity: 0.7;                  /* Sanatçı hafif şeffaf */
// }
//
// /* MQTT mesajları — italik, sinematik */
// .MMM-MQTT .mqtt-message {
//   font-size: 28px;
//   font-weight: 200;
//   font-style: italic;            /* İtalik — sinematik his */
//   text-align: center;
//   opacity: 0.9;
// }
// -------------------------------------------------------------------------

// -------------------------------------------------------------------------
// MODÜL KURULUM TALİMATLARI
// -------------------------------------------------------------------------
// MagicMirror² kurulumu:
//   curl -sL https://raw.githubusercontent.com/MichMich/MagicMirror/master/installers/raspberry.sh | bash
//
// MMM-Spotify kurulumu:
//   cd ~/MagicMirror/modules
//   git clone https://github.com/skuethe/MMM-Spotify.git
//   cd MMM-Spotify
//   npm install
//
// MMM-MQTT kurulumu:
//   cd ~/MagicMirror/modules
//   git clone https://github.com/shbatm/MMM-MQTT.git
//   cd MMM-MQTT
//   npm install
//
// Autostart (PM2 ile):
//   cd ~/MagicMirror
//   npm install pm2 -g
//   pm2 start mm.sh
//   pm2 startup
//   pm2 save
// -------------------------------------------------------------------------

/*************** DO NOT EDIT THE LINE BELOW ***************/
if (typeof module !== "undefined") { module.exports = config; }