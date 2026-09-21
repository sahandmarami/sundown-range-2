# میدان غروب ۲ (Sundown Range II)

بازی تیراندازی تاکتیکی فارسی — نسخهٔ بهبودیافته با لیدربورد آنلاین مقاوم در برابر خطا، افکت‌های بصری جدید، و پاداش روزانه.

## ساختار پروژه

```
.
├── game-src/                  # سورس اصلی بازی (HTML/CSS/JS)
│   ├── index.html             # فایل کامل بازی (تک‌فایلی)
│   └── vendor/                # Three.js, GLTFLoader, Telegram WebApp (لوکال، برای آفلاین)
├── apk-project/               # پروژه Capacitor برای build APK
│   ├── capacitor.config.json  # تنظیمات Capacitor
│   ├── package.json           # وابستگی‌های npm
│   ├── www/                   # وب اسبت‌ها (همان محتوای game-src)
│   └── android/               # پروژه Android (تولید شده با `cap add android`)
├── scripts/
│   ├── enhance_game.py        # اسکریپت اعمال بهبودها روی HTML
│   └── build_apk.sh           # اسکریپت build APK
└── README.md
```

## بهبودهای این نسخه

### ۱. لیدربورد آنلاین مقاوم
- **Multi-source fallback**: ابتدا jsonbin.io، سپس jsonblob.com به‌عنوان منبع جایگزین
- **Optimistic UI**: امتیاز بلافاصله در UI نمایش داده می‌شود، همگام‌سازی پس‌زمینه
- **Conflict resolution**: در صورت تداخل، آخرین timestamp تصمیم‌گیرنده است
- **دکمهٔ به‌روزرسانی دستی** (`↻`) در هدر پنل رکوردها
- **بدون قفل**: حالت آنلاین از ابتدا باز است (قبلاً نیاز به تکمیل ۱۵ مرحله داشت)

### ۲. بهبودهای بصری
- افکت ذرات شناور در پس‌زمینهٔ منو
- انیمیشن کانفتی هنگام ثبت رکورد جدید
- Screen shake هنگام hit های بزرگ
- Glow pulse روی دکمهٔ شروع و نشان «رکورد جدید»
- انیمیشن‌های نرم‌تر برای tab transitions

### ۳. پاداش روزانه
- ۵۰ سکهٔ رایگان در اولین ورود هر روز
- نمایش modal تبریک

## Build APK

### پیش‌نیازها
- Node.js 18+
- Java JDK 17+ (تست شده با JDK 21)
- Android SDK (Platform 34 + Build Tools 34.0.0)

### مراحل
```bash
cd apk-project
npm install
npx cap sync android
cd android
./gradlew assembleDebug
# خروجی: app/build/outputs/apk/debug/app-debug.apk
```

برای build نسخهٔ release (با امضا):
```bash
cd android
./gradlew assembleRelease
```

## توسعه

اگر می‌خواهی بازی را تغییر دهی:
1. `game-src/index.html` را ویرایش کن
2. `python3 scripts/enhance_game.py` را اجرا کن تا تغییرات به `apk-project/www/` اعمال شود
3. `cd apk-project && npx cap sync android` را اجرا کن
4. APK را دوباره build کن

## امنیت لیدربورد

⚠️ **توجه**: کلید `MASTER_KEY` سرویس jsonbin.io در سمت کلاینت قرار دارد. این یک محدودیت ذاتیِ اپ‌های client-only است. برای جلوگیری از تقلب پیشرفته، باید یک backend سبک (مثل Cloudflare Worker یا Vercel function) راه‌اندازی کنی که کلید را نگه دارد و درخواست‌ها را اعتبارسنجی کند.

## لایسنس
اختصاصی — تمام حقوق محفوظ است.
