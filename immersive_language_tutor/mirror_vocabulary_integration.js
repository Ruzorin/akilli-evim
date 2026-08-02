/* =============================================================================
 * immersive_language_tutor — Magic Mirror Vocabulary Integration
 * =============================================================================
 * Bu dosya, Modül 4 (Akıllı Ayna) MagicMirror² konfigürasyonuna eklenecek
 * bir modül parçasıdır. Ayna ekranının alt köşesinde her gün (veya her 4
 * saatte bir) değişen 5 adet İngilizce - Fransızca eşleştirmeli kelime/cümle
 * gösterir.
 *
 * 🎯 "PASİF ÖĞRENME" MANTIĞI:
 * =============================================================================
 * Kullanıcı aynaya baktıkça (sabah tıraş, gece diş fırçalama) kelimeleri
 * görür → bilinçaltı kaydeder → pasif öğrenme gerçekleşir.
 *
 * Ekstra donanım YOK — MagicMirror² (Modül 4) zaten kurulu.
 * Bu modül sadece bir JSON dosyasından kelime çeker ve ekranda gösterir.
 *
 * Kurulum:
 *   1. Bu dosyayı ~/MagicMirror/modules/MMM-Vocabulary/ dizinine koy
 *   2. MMM-Vocabulary.js olarak kaydet
 *   3. magicmirror_config.js (Modül 4) içinde modules dizisine ekle
 *   4. vocabulary.json dosyasını ~/MagicMirror/modules/MMM-Vocabulary/ içine koy
 * =============================================================================
 */

Module.register("MMM-Vocabulary", {
  // -------------------------------------------------------------------------
  // Varsayılan konfigürasyon
  // -------------------------------------------------------------------------
  defaults: {
    updateInterval: 4 * 60 * 60 * 1000,  // 4 saatte bir güncelle (ms)
    fadeSpeed: 2000,                       // 2 saniye fade geçişi
    wordsPerDay: 5,                        // Günde 5 kelime
    language: "both",                      // "english", "french", "both"
    vocabularyFile: "vocabulary.json",    // Kelime listesi dosyası
    showTranslation: true,                // Çeviriyi göster (önce gizle, tıklayınca aç)
    position: "bottom_bar",               // MagicMirror pozisyonu
  },

  // -------------------------------------------------------------------------
  // Başlangıç
  // -------------------------------------------------------------------------
  start: function () {
    this.currentWords = [];
    this.currentIndex = 0;
    this.loaded = false;
    this.visible = false;  // MQTT "jarvis/mirror/vocabulary" ON olunca görünür

    // MQTT dinle — dil eğitmeni modu ON/OFF
    this.sendSocketNotification("MQTT_SUBSCRIBE", {
      topic: "jarvis/mirror/vocabulary"
    });

    // Kelime listesini yükle
    this.loadVocabulary();
  },

  // -------------------------------------------------------------------------
  // Kelime listesini yükle (JSON dosyadan)
  // -------------------------------------------------------------------------
  loadVocabulary: function () {
    var self = this;
    var url = this.config.vocabularyFile;

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
        try {
          self.vocabulary = JSON.parse(xhr.responseText);
          self.loaded = true;
          self.updateWords();
        } catch (e) {
          console.error("[MMM-Vocabulary] JSON parse hatası:", e);
        }
      }
    };
    xhr.send();
  },

  // -------------------------------------------------------------------------
  // Kelimeleri güncelle (her 4 saatte bir)
  // -------------------------------------------------------------------------
  updateWords: function () {
    if (!this.loaded || !this.vocabulary) return;

    // Günün kelimelerini seç (tarihe göre deterministik)
    var today = new Date();
    var dayOfYear = Math.floor(
      (today - new Date(today.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24
    );

    // Kelime havuzundan günün kelimelerini seç
    var pool = this.vocabulary.words || [];
    var selected = [];

    for (var i = 0; i < this.config.wordsPerDay; i++) {
      var index = (dayOfYear * this.config.wordsPerDay + i) % pool.length;
      selected.push(pool[index]);
    }

    this.currentWords = selected;
    this.updateDom(this.config.fadeSpeed);
  },

  // -------------------------------------------------------------------------
  // MQTT mesajı geldiğinde (mod ON/OFF)
  // -------------------------------------------------------------------------
  socketNotificationReceived: function (notification, payload) {
    if (notification === "MQTT_MESSAGE") {
      if (payload.topic === "jarvis/mirror/vocabulary") {
        if (payload.payload === "ON") {
          this.visible = true;
          this.updateDom(this.config.fadeSpeed);
        } else if (payload.payload === "OFF") {
          this.visible = false;
          this.updateDom(this.config.fadeSpeed);
        }
      }
    }
  },

  // -------------------------------------------------------------------------
  // DOM oluştur (ekran arayüzü)
  // -------------------------------------------------------------------------
  getDom: function () {
    var wrapper = document.createElement("div");
    wrapper.className = "MMM-Vocabulary";

    // Mod kapalıysa boş göster
    if (!this.visible || !this.loaded) {
      wrapper.style.display = "none";
      return wrapper;
    }

    // -------------------------------------------------------------------------
    // Başlık
    // -------------------------------------------------------------------------
    var header = document.createElement("div");
    header.className = "vocabulary-header";
    header.innerHTML = "📚 Daily Vocabulary";
    header.style.fontSize = "16px";
    header.style.fontWeight = "300";
    header.style.opacity = "0.6";
    header.style.marginBottom = "8px";
    wrapper.appendChild(header);

    // -------------------------------------------------------------------------
    // Kelime listesi
    // -------------------------------------------------------------------------
    var list = document.createElement("div");
    list.className = "vocabulary-list";

    this.currentWords.forEach(function (word, index) {
      var item = document.createElement("div");
      item.className = "vocabulary-item";
      item.style.fontSize = "18px";
      item.style.fontWeight = "200";
      item.style.marginBottom = "6px";
      item.style.opacity = "0.85";

      // İngilizce kelime
      var en = document.createElement("span");
      en.className = "vocab-en";
      en.innerHTML = word.english;
      en.style.color = "#FFFFFF";
      en.style.marginRight = "12px";
      item.appendChild(en);

      // Ayraç
      var sep = document.createElement("span");
      sep.innerHTML = "—";
      sep.style.opacity = "0.4";
      sep.style.marginRight = "12px";
      item.appendChild(sep);

      // Fransızca karşılık
      var fr = document.createElement("span");
      fr.className = "vocab-fr";
      fr.innerHTML = word.french;
      fr.style.color = "#FFFFFF";
      fr.style.opacity = "0.7";
      fr.style.fontStyle = "italic";
      item.appendChild(fr);

      // Örnek cümle (opsiyonel — küçük font)
      if (word.example) {
        var example = document.createElement("div");
        example.className = "vocab-example";
        example.innerHTML = word.example;
        example.style.fontSize = "13px";
        example.style.opacity = "0.4";
        example.style.marginTop = "2px";
        example.style.marginLeft = "20px";
        item.appendChild(example);
      }

      list.appendChild(item);
    });

    wrapper.appendChild(list);

    return wrapper;
  },

  // -------------------------------------------------------------------------
  // CSS stilleri (Calm Technology — saf beyaz, siyah arka plan)
  // -------------------------------------------------------------------------
  getStyles: function () {
    return ["MMM-Vocabulary.css"];
  },
});

/* =============================================================================
 * vocabulary.json ÖRNEK DOSYA
 * =============================================================================
 * Bu dosyayı ~/MagicMirror/modules/MMM-Vocabulary/vocabulary.json olarak kaydet.
 * İçinde 100+ İngilizce-Fransızca kelime/cümle çifti olmalı.
 * Her gün 5 kelime seçilir, 4 saatte bir güncellenir.
 *
 * {
 *   "words": [
 *     { "english": "to achieve", "french": "atteindre", "example": "I want to achieve my goals." },
 *     { "english": "to accomplish", "french": "accomplir", "example": "She accomplished her dream." },
 *     { "english": "immigration", "french": "l'immigration", "example": "The immigration process takes time." },
 *     { "english": "to apply", "french": "postuler", "example": "I want to apply for a visa." },
 *     { "english": "deadline", "french": "la date limite", "example": "The deadline is next week." },
 *     { "english": "to prepare", "french": "préparer", "example": "I need to prepare for the exam." },
 *     { "english": "interview", "french": "l'entretien", "example": "The job interview went well." },
 *     { "english": "to improve", "french": "améliorer", "example": "I want to improve my French." },
 *     { "english": "opportunity", "french": "l'occasion", "example": "This is a great opportunity." },
 *     { "english": "to succeed", "french": "réussir", "example": "I will succeed in Canada." },
 *     { "english": "to settle", "french": "s'installer", "example": "We settled in Montreal." },
 *     { "english": "province", "french": "la province", "example": "Quebec is a beautiful province." },
 *     { "english": "to require", "french": "exiger", "example": "This job requires French." },
 *     { "english": "to submit", "french": "soumettre", "example": "Submit your application online." },
 *     { "english": "fluently", "french": "couramment", "example": "She speaks French fluently." },
 *     { "english": "to register", "french": "s'inscrire", "example": "I registered for the TEF exam." },
 *     { "english": "certificate", "french": "le certificat", "example": "I need a language certificate." },
 *     { "english": "to express", "french": "exprimer", "example": "Express your ideas clearly." },
 *     { "english": "to practice", "french": "pratiquer", "example": "Practice every day." },
 *     { "english": "confident", "french": "confiant", "example": "I feel confident about the exam." }
 *   ]
 * }
 *
 * =============================================================================
 * magicmirror_config.js (Modül 4) İÇİNE EKLENECEK BÖLÜM
 * =============================================================================
 *
 * modules dizisine şu bloğu ekle:
 *
 *   {
 *     module: "MMM-Vocabulary",
 *     position: "bottom_bar",
 *     config: {
 *       updateInterval: 4 * 60 * 60 * 1000,  // 4 saat
 *       fadeSpeed: 2000,
 *       wordsPerDay: 5,
 *       language: "both",
 *       vocabularyFile: "modules/MMM-Vocabulary/vocabulary.json",
 *       showTranslation: true
 *     }
 *   },
 *
 * =============================================================================
 * MMM-Vocabulary.css (Calm Technology stilleri)
 * =============================================================================
 *
 * .MMM-Vocabulary {
 *   text-align: center;
 *   margin-bottom: 20px;
 * }
 * .MMM-Vocabulary .vocabulary-header {
 *   font-size: 16px;
 *   font-weight: 300;
 *   opacity: 0.6;
 *   margin-bottom: 8px;
 * }
 * .MMM-Vocabulary .vocabulary-item {
 *   font-size: 18px;
 *   font-weight: 200;
 *   margin-bottom: 6px;
 *   opacity: 0.85;
 * }
 * .MMM-Vocabulary .vocab-en {
 *   color: #FFFFFF;
 *   margin-right: 12px;
 * }
 * .MMM-Vocabulary .vocab-fr {
 *   color: #FFFFFF;
 *   opacity: 0.7;
 *   font-style: italic;
 * }
 * .MMM-Vocabulary .vocab-example {
 *   font-size: 13px;
 *   opacity: 0.4;
 *   margin-top: 2px;
 *   margin-left: 20px;
 * }
 * =============================================================================
 */