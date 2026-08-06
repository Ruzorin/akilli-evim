/* =============================================================================
 * magic_mirror_comm_and_grooming — Grooming Checklist Mirror UI
 * =============================================================================
 * MagicMirror² arayüzüne, kullanıcı aynaya baktığında sağ alt köşede
 * beliren minimalist bir "Grooming & Routine Checklist" modülü.
 *
 * 🎨 UX (Kullanıcı Deneyimi):
 * =============================================================================
 * Ayna sağ alt köşede:
 *   📋 GÜNÜN RUTİNİ
 *   ✅ Diş ipi
 *   ✅ Yüz yıkama
 *   ☐ Saç spreyi
 *   ☐ D vitamini
 *   ☐ B12
 *
 *   👔 KOMBİN PUANI: 75/100
 *   "Lacivert ceket giymelisin"
 *
 * Kullanıcı telefonundan onayladıkça maddeler listeden silinir.
 * Grooming puanı, Qwen-VL Max analizinden güncellenir.
 *
 * Kurulum:
 *   ~/MagicMirror/modules/MMM-Grooming-Checklist/MMM-Grooming-Checklist.js
 *   magicmirror_config.js modules dizisine ekle
 * =============================================================================
 */

Module.register("MMM-Grooming-Checklist", {
  defaults: {
    position: "bottom_right",
    updateInterval: 60000,          // 1 dakikada bir güncelle
    fadeSpeed: 2000,
    showGroomingScore: true,        // Kombin puanı göster
    showRoutineChecklist: true,     // Sabah/akşam rutini
    routineTime: "morning",         // "morning" veya "evening"
    mqttTopicScore: "jarvis/mirror/grooming_score",
    mqttTopicChecklist: "jarvis/mirror/grooming_checklist",
  },

  start: function () {
    this.checklist = [];
    this.groomingScore = 0;
    this.groomingSuggestion = "";
    this.eventType = "none";
    this.loaded = false;
    this.visible = false;

    // MQTT dinle — grooming score + checklist
    this.sendSocketNotification("MQTT_SUBSCRIBE", {
      topics: [
        this.config.mqttTopicScore,
        this.config.mqttTopicChecklist
      ]
    });

    // İlk checklist'i yükle
    this.loadChecklist();
  },

  // -------------------------------------------------------------------------
  // Checklist yükle (sabah/akşam rutini)
  // -------------------------------------------------------------------------
  loadChecklist: function () {
    var self = this;

    // Sabah rutini
    if (this.config.routineTime === "morning") {
      this.checklist = [
        { id: "teeth_floss", name: "Diş ipi", done: false, icon: "🦷" },
        { id: "face_wash", name: "Yüz yıkama", done: false, icon: "🧼" },
        { id: "hair_spray", name: "Saç spreyi", done: false, icon: "💇" },
        { id: "vitamin_d", name: "D vitamini", done: false, icon: "💊" },
        { id: "vitamin_b12", name: "B12", done: false, icon: "💊" },
        { id: "shower", name: "Duş", done: false, icon: "🚿" }
      ];
    } else {
      // Akşam rutini
      this.checklist = [
        { id: "teeth_brush", name: "Diş fırçalama", done: false, icon: "🦷" },
        { id: "face_wash", name: "Yüz yıkama", done: false, icon: "🧼" },
        { id: "skincare", name: "Cilt bakımı", done: false, icon: "✨" },
        { id: "vitamin_d", name: "D vitamini", done: false, icon: "💊" }
      ];
    }

    this.loaded = true;
    this.updateDom(this.config.fadeSpeed);
  },

  // -------------------------------------------------------------------------
  // MQTT mesajı geldiğinde
  // -------------------------------------------------------------------------
  socketNotificationReceived: function (notification, payload) {
    if (notification === "MQTT_MESSAGE") {
      if (payload.topic === this.config.mqttTopicScore) {
        // Grooming score güncelle
        try {
          var data = JSON.parse(payload.payload);
          this.groomingScore = data.score || 0;
          this.groomingSuggestion = data.suggestion || "";
          this.eventType = data.event_type || "none";
          this.visible = true;
          this.updateDom(this.config.fadeSpeed);
        } catch (e) {
          console.error("[MMM-Grooming] Score parse hatası:", e);
        }
      } else if (payload.topic === this.config.mqttTopicChecklist) {
        // Checklist güncelle (telefondan onaylanan maddeler)
        try {
          var data = JSON.parse(payload.payload);
          if (data.checked_item) {
            var item = this.checklist.find(function (c) {
              return c.id === data.checked_item;
            });
            if (item) {
              item.done = true;
              this.updateDom(this.config.fadeSpeed);
            }
          }
        } catch (e) {
          console.error("[MMM-Grooming] Checklist parse hatası:", e);
        }
      }
    }
  },

  // -------------------------------------------------------------------------
  // DOM oluştur
  // -------------------------------------------------------------------------
  getDom: function () {
    var wrapper = document.createElement("div");
    wrapper.className = "MMM-Grooming-Checklist";

    if (!this.loaded) {
      wrapper.innerHTML = "Yükleniyor...";
      return wrapper;
    }

    // -------------------------------------------------------------------------
    // Başlık
    // -------------------------------------------------------------------------
    var header = document.createElement("div");
    header.className = "grooming-header";
    header.innerHTML = "📋 GÜNÜN RUTİNİ";
    header.style.fontSize = "14px";
    header.style.fontWeight = "300";
    header.style.opacity = "0.6";
    header.style.marginBottom = "8px";
    wrapper.appendChild(header);

    // -------------------------------------------------------------------------
    // Checklist
    // -------------------------------------------------------------------------
    if (this.config.showRoutineChecklist) {
      var list = document.createElement("div");
      list.className = "grooming-checklist";

      this.checklist.forEach(function (item) {
        var row = document.createElement("div");
        row.className = "grooming-item";
        row.style.fontSize = "15px";
        row.style.fontWeight = "200";
        row.style.marginBottom = "4px";
        row.style.opacity = item.done ? "0.3" : "0.85";

        var check = document.createElement("span");
        check.innerHTML = item.done ? "✅" : "☐";
        check.style.marginRight = "8px";
        row.appendChild(check);

        var icon = document.createElement("span");
        icon.innerHTML = item.icon;
        icon.style.marginRight = "6px";
        row.appendChild(icon);

        var name = document.createElement("span");
        name.innerHTML = item.name;
        if (item.done) {
          name.style.textDecoration = "line-through";
        }
        row.appendChild(name);

        list.appendChild(row);
      });

      wrapper.appendChild(list);
    }

    // -------------------------------------------------------------------------
    // Kombin puanı + öneri
    // -------------------------------------------------------------------------
    if (this.config.showGroomingScore && this.groomingScore > 0) {
      var scoreDiv = document.createElement("div");
      scoreDiv.className = "grooming-score";
      scoreDiv.style.marginTop = "12px";
      scoreDiv.style.paddingTop = "8px";
      scoreDiv.style.borderTop = "1px solid rgba(255,255,255,0.1)";

      // Puan
      var scoreLabel = document.createElement("div");
      scoreLabel.innerHTML = "👔 KOMBİN PUANI: " + this.groomingScore + "/100";
      scoreLabel.style.fontSize = "15px";
      scoreLabel.style.fontWeight = "300";
      scoreLabel.style.opacity = "0.85";
      scoreLabel.style.marginBottom = "4px";

      // Puan rengi
      if (this.groomingScore >= 80) {
        scoreLabel.style.color = "#4CAF50"; // Yeşil
      } else if (this.groomingScore >= 60) {
        scoreLabel.style.color = "#FF9800"; // Turuncu
      } else {
        scoreLabel.style.color = "#F44336"; // Kırmızı
      }
      scoreDiv.appendChild(scoreLabel);

      // Öneri
      if (this.groomingSuggestion) {
        var suggestion = document.createElement("div");
        suggestion.innerHTML = '"' + this.groomingSuggestion + '"';
        suggestion.style.fontSize = "13px";
        suggestion.style.fontWeight = "200";
        suggestion.style.opacity = "0.5";
        suggestion.style.fontStyle = "italic";
        suggestion.style.marginTop = "2px";
        scoreDiv.appendChild(suggestion);
      }

      // Etkinlik tipi
      if (this.eventType && this.eventType !== "none") {
        var eventLabel = document.createElement("div");
        eventLabel.innerHTML = "📅 " + this.eventType;
        eventLabel.style.fontSize = "12px";
        eventLabel.style.opacity = "0.4";
        eventLabel.style.marginTop = "4px";
        scoreDiv.appendChild(eventLabel);
      }

      wrapper.appendChild(scoreDiv);
    }

    return wrapper;
  },

  // -------------------------------------------------------------------------
  // CSS (Calm Technology — saf beyaz, siyah arka plan)
  // -------------------------------------------------------------------------
  getStyles: function () {
    return ["MMM-Grooming-Checklist.css"];
  },
});

/* =============================================================================
 * MMM-Grooming-Checklist.css (Calm Technology stilleri)
 * =============================================================================
 *
 * .MMM-Grooming-Checklist {
 *   text-align: left;
 *   padding: 10px;
 *   max-width: 250px;
 * }
 * .MMM-Grooming-Checklist .grooming-header {
 *   font-size: 14px;
 *   font-weight: 300;
 *   opacity: 0.6;
 *   margin-bottom: 8px;
 * }
 * .MMM-Grooming-Checklist .grooming-item {
 *   font-size: 15px;
 *   font-weight: 200;
 *   margin-bottom: 4px;
 *   opacity: 0.85;
 * }
 * .MMM-Grooming-Checklist .grooming-score {
 *   margin-top: 12px;
 *   padding-top: 8px;
 *   border-top: 1px solid rgba(255,255,255,0.1);
 * }
 * =============================================================================
 *
 * magicmirror_config.js (Modül 4) İÇİNE EKLENECEK:
 *
 *   {
 *     module: "MMM-Grooming-Checklist",
 *     position: "bottom_right",
 *     config: {
 *       showGroomingScore: true,
 *       showRoutineChecklist: true,
 *       routineTime: "morning",
 *       updateInterval: 60000
 *     }
 *   },
 * =============================================================================
 */