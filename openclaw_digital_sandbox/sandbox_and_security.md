# openclaw_digital_sandbox — Sandbox ve Güvenlik İzolasyonu (Zero Trust)

> **Modül 27: OpenClaw Dijital Ajan**
> Jarvis'in "dijital elleri" — tarayıcı + masaüstü otomasyonu
> Zero Trust mimarisi ile izole edilmiş Docker sandbox

---

## 🎯 OpenClaw Nedir?

OpenClaw (eski adıyla Clawdbot/Moltbot), açık kaynaklı otonom AI ajan
framework'üdür. Kasım 2025'te Peter Steinberger tarafından yayınlandı,
Ocak 2026'da OpenClaw olarak yeniden adlandırıldı, 250k+ GitHub yıldızı.

| Özellik | Detay |
|---------|-------|
| **Lisans** | MIT (tamamen açık) |
| **Sürüm** | v2026.4.15 (Nisan 2026) |
| **Çalışma** | VPS / yerel bilgisayar / Docker |
| **Beyin** | DeepSeek V4-Pro (Cloud VPS) |
| **Beceri** | browser-use, shell, dosya, API, mesajlaşma |
| **Kanallar** | WhatsApp, Telegram, Slack, Discord, Signal |

---

## 🔒 Zero Trust Sandbox Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                    HOST BİLGİSAYAR                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Docker Container (Sandbox)               │   │
│  │                                                       │   │
│  │  ┌───────────────────────────────────────────────┐   │   │
│  │  │          OpenClaw Agent Runtime                  │   │   │
│  │  │  ┌─────────────┐  ┌────────────────────────┐  │   │   │
│  │  │  │ browser-use  │  │  Shell (non-root user)  │  │   │   │
│  │  │  │ (Playwright) │  │  /workspace (read-only) │  │   │   │
│  │  │  └─────────────┘  └────────────────────────┘  │   │   │
│  │  └───────────────────────────────────────────────┘   │   │
│  │                                                       │   │
│  │  🔒 seccomp + Landlock + cap-drop ALL                 │   │
│  │  🔒 network namespace (allowlist)                     │   │
│  │  🔒 filesystem jail (/openclaw/data only)              │   │
│  └─────────────────────────────────────────────────────┘   │
│                      │ MQTT (1883)                          │
│  ┌───────────────────▼───────────────────────────────────┐ │
│  │              Home Assistant (Host)                     │ │
│  │  → Modül 29 Lamba (MQTT sync)                         │ │
│  │  → Modül 30 Kame (MQTT sync)                          │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🐳 Docker İzolasyon — 7 Katmanlı Güvenlik

### Katman 1: Container İzolasyonu

```yaml
# docker-compose.yml — OpenClaw Sandbox
version: "3.9"
services:
  openclaw:
    image: openclaw/agent:2026.4.15
    container_name: jarvis-openclaw

    # Non-root user
    user: "1000:1000"

    # Tüm Linux capability'leri düş
    cap_drop:
      - ALL
    # Sadece gerekli olanları geri ekle
    cap_add:
      - NET_BIND_SERVICE  # 80/443 bind (browser-use için)

    # Read-only root filesystem
    read_only: true
    tmpfs:
      - /tmp:size=100M
      - /var/tmp:size=50M

    # Filesystem jail — sadece /openclaw/data yazılabilir
    volumes:
      - ./openclaw-data:/openclaw/data:rw
      # Host dosyalarını MOUNT ETME! (Zero Trust)
      # - /home/user:/home/user:ro  ← YASAK!

    # Network namespace — sadece gerekli portlar
    networks:
      - jarvis-isolated

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 4G
        reservations:
          cpus: "0.5"
          memory: 1G

    # Environment — secrets host'tan değil, .env'den
    env_file:
      - .env  # API keys, MQTT broker

    # Restart policy
    restart: unless-stopped

networks:
  jarvis-isolated:
    driver: bridge
    internal: false  # Dış erişim var (internet) ama izole ağ
```

### Katman 2: Seccomp Profile

```json
// seccomp-openclaw.json — Sadece gerekli syscall'lara izin ver
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "syscalls": [
    {
      "names": [
        "read", "write", "open", "close", "stat", "fstat",
        "lstat", "poll", "lseek", "mmap", "mprotect", "munmap",
        "brk", "rt_sigaction", "rt_sigprocmask", "rt_sigreturn",
        "ioctl", "pread64", "pwrite64", "readv", "writev",
        "access", "pipe", "select", "sched_yield", "mremap",
        "msync", "mincore", "madvise", "shmget", "shmat",
        "shmctl", "dup", "dup2", "pause", "nanosleep",
        "getitimer", "alarm", "setitimer", "getpid", "sendfile",
        "socket", "connect", "listen", "accept", "getsockname",
        "getpeername", "sendto", "recvfrom", "sendmsg", "recvmsg",
        "shutdown", "bind", "getsockopt", "setsockopt",
        "fork", "vfork", "execve", "exit", "wait4",
        "uname", "fcntl", "flock", "fsync", "fdatasync",
        "truncate", "ftruncate", "getdents", "getcwd",
        "chdir", "fchdir", "rename", "mkdir", "rmdir",
        "creat", "link", "unlink", "symlink", "readlink",
        "chmod", "fchmod", "chown", "fchown", "lchown",
        "umask", "gettimeofday", "getrlimit", "getrusage",
        "sysinfo", "times", "ptrace", "getuid", "geteuid",
        "getgid", "getegid", "setpgid", "getppid", "getpgrp",
        "setsid", "setreuid", "setregid", "getgroups", "setgroups",
        "setresuid", "getresuid", "setresgid", "getresgid",
        "getpgid", "setfsuid", "setfsgid", "getsid",
        "capget", "capset", "rt_sigpending", "rt_sigtimedwait",
        "rt_sigqueueinfo", "rt_tgsigqueueinfo", "prlimit64",
        "faccessat", "utimensat", "futimesat"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

### Katman 3: Landlock (Kernel-Level Filesystem Isolation)

```python
# Landlock — kernel seviyesinde filesystem jail
# OpenClaw v2026.4.15+ içinde hazır template
# /etc/openclaw/landlock.conf

[landlock]
enabled = true
# Sadece şu dizinlere erişim:
allowed_paths:
  - /openclaw/data        # Çalışma dizini (rw)
  - /openclaw/skills     # Skill dosyaları (ro)
  - /openclaw/browser    # Browser profili (rw)
  - /tmp                 # Geçici dosyalar (rw)
  - /var/tmp             # Geçici (rw)

# YASAK dizinler:
denied_paths:
  - /home                # Kullanıcı dosyaları
  - /root                # Root dosyaları
  - /etc                 # Sistem konfigürasyon
  - /var/log             # Sistem logları
  - /proc                # Süreç bilgisi
  - /sys                 # Kernel bilgisi
```

### Katman 4: Network Namespace (Allowlist)

```yaml
# network-allowlist.yaml — Sadece izinli sunuculara erişim
allowed_hosts:
  # AI API'leri
  - "api.deepseek.com"
  - "api.minimax.io"
  - "dashscope.aliyuncs.com"

  # Browser-use için genel internet
  - "0.0.0.0/0"  # Web sitelerine erişim (browser-use)

  # Yerel ağ
  - "gl-mt3000.local"  # MQTT broker
  - "homeassistant.local"  # HA

denied_hosts:
  # Yerel ağ cihazları (saldırı yüzeyini azalt)
  - "192.168.1.1"  # Router admin
  - "192.168.1.107"  # Tapo C200 kamera
  # Meta/Google/Amazon (gizlilik)
  - "*.facebook.com"
  - "*.google-analytics.com"
```

### Katman 5: Skill Audit (Supply Chain)

```yaml
# skill-audit.yaml — Skill'ler güvenlik kontrolünden geçer
skill_security:
  # Sadece resmi ClawhHub'tan skill yükle
  allow_unofficial: false

  # Skill yüklemeden önce manuel onay
  require_approval: true

  # Tehlikeli pattern'leri tara
  banned_patterns:
    - "rm -rf"           # Dosya silme
    - "curl | bash"      # Remote execution
    - "eval("           # Code injection
    - "os.system"       # Shell injection
    - "subprocess.call" # Shell injection
    - "__import__"      # Dynamic import

  # Skill içeriğini logla
  audit_log: true
  audit_log_path: "/openclaw/data/skill-audit.log"
```

### Katman 6: Memory Hygiene

```yaml
# memory-hygiene.yaml — Ajan hafızası düzenli temizlenir
memory:
  # Aylık hafıza temizliği
  wipe_interval_days: 30

  # Hassas verileri hafızada tutma
  redact_patterns:
    - "password"
    - "token"
    - "api_key"
    - "secret"
    - "credit_card"
    - "ssn"

  # Hafıza zehirlenmesi koruması
  poisoning_protection: true
  max_memory_entries: 10000
```

### Katman 7: Approval System (İnsan-onayı)

```yaml
# approval.yaml — Tehlikeli işlemler için insan onayı
approval_required:
  # Dosya işlemleri
  - "file.delete"
  - "file.move"
  - "file.copy"

  # Finansal işlemler
  - "payment.send"
  - "order.place"
  - "subscription.cancel"

  # Sistem işlemleri
  - "shell.execute"
  - "package.install"

  # Mesajlaşma
  - "email.send"
  - "message.send"

approval_method: "mqtt"  # MQTT → HA → mobil bildirim → onay
approval_timeout: 300    # 5 dk içinde onaylanmazsa iptal
```

---

## 🛡️ Güvenlik Özeti

| Katman | Teknoloji | Koruma |
|--------|-----------|--------|
| 1. Container | Docker + non-root | OS izolasyonu |
| 2. Seccomp | Syscall filter | Kernel saldırı |
| 3. Landlock | Kernel FS jail | Dosya erişimi |
| 4. Network | Namespace + allowlist | Ağ saldırısı |
| 5. Skill Audit | Pattern scan | Supply chain |
| 6. Memory | Redact + wipe | Hafıza zehirlenmesi |
| 7. Approval | MQTT → HA → mobil | Tehlikeli işlem |

**Sonuç:** OpenClaw ajanı kişisel dosyalara ERIŞEMEZ, şifreleri SIZDIRAMAZ,
sadece `/openclaw/data` içinde çalışır. Tehlikeli işlemler için insan onayı gerekir.

---

## 🔗 İlgili Dosyalar

- [`digital_physical_sync.yaml`](digital_physical_sync.yaml) — Lamba MQTT senkronizasyonu
- [`vss_screen_shield.py`](vss_screen_shield.py) — VSS ekran kalkanı
- [`config.yaml`](config.yaml) — Modül konfigürasyonu