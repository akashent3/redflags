# Environment Variables Setup Guide

This guide will help you fill in all the API keys and configuration values in your `.env` file.

## 📋 Checklist

Follow these steps to complete your `.env` file:

### 1. ✅ Supabase (PostgreSQL Database)

**Steps:**
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click on your project: `redflags-db`
3. Go to **Settings** (left sidebar) → **Database**
4. Scroll to **Connection string** section
5. **Select "Transaction" mode** (important!)
6. Copy the connection string

**Format you'll see:**
```
postgresql://postgres.[PROJECT_REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**IMPORTANT - Password Encoding:**
Your password contains `#$%` which are special characters. You must URL-encode them:
- Replace `#` with `%23`
- Replace `$` with `%24`
- Replace `%` with `%25`

**Example:**
- If password is: `MyPass#123$`
- URL-encoded: `MyPass%23123%24`

**Update in .env:**
Replace this line:
```env
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-URL-ENCODED-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

---

### 2. ✅ Upstash (Redis Cache)

**Steps:**
1. Go to [Upstash Console](https://console.upstash.com/)
2. Click on your database: `redflags-redis`
3. Click on **REST API** tab (or scroll down)
4. Copy:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`

**Format:**
```
redis://default:[TOKEN]@[ENDPOINT].upstash.io:6379
```

**Update in .env:**
Replace `[YOUR-UPSTASH-TOKEN]` and `[YOUR-ENDPOINT]` in these three lines:
```env
REDIS_URL=redis://default:[YOUR-TOKEN]@[YOUR-ENDPOINT].upstash.io:6379
CELERY_BROKER_URL=redis://default:[YOUR-TOKEN]@[YOUR-ENDPOINT].upstash.io:6379
CELERY_RESULT_BACKEND=redis://default:[YOUR-TOKEN]@[YOUR-ENDPOINT].upstash.io:6379
```

---

### 3. ✅ Cloudflare R2 (PDF Storage)

**Steps:**
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Click **R2** in left sidebar
3. Click on your bucket: `redflags-pdfs`
4. Click **Manage R2 API Tokens** (top right)
5. Click **Create API Token**
   - Name: `redflags-api-token`
   - Permissions: **Object Read & Write**
   - Click **Create API Token**
6. Copy:
   - `Access Key ID`
   - `Secret Access Key`
7. For endpoint URL:
   - Go back to R2 main page
   - Your Account ID is in the URL or shown on the page
   - Format: `https://[account-id].r2.cloudflarestorage.com`

**Update in .env:**
```env
R2_ACCESS_KEY_ID=your-actual-access-key-id
R2_SECRET_ACCESS_KEY=your-actual-secret-key
R2_ENDPOINT_URL=https://[your-account-id].r2.cloudflarestorage.com
```

---

### 4. ✅ Google Gemini API

**Steps:**
1. You already have this! Just copy your Gemini API key
2. Go to [Google AI Studio](https://makersuite.google.com/app/apikey) if you need to view it again

**Update in .env:**
```env
GEMINI_API_KEY=your-actual-gemini-api-key
```

---

### 5. ✅ JWT Secret Key

**Generate a secure random key:**

**Option 1 - Using OpenSSL (Recommended):**
```bash
openssl rand -hex 32
```

**Option 2 - Using Python:**
```bash
cd D:\redflags\backend
source venv/Scripts/activate
python -c "import secrets; print(secrets.token_hex(32))"
```

**Option 3 - Online (Quick):**
Go to: https://generate-random.org/api-token-generator?count=1&length=64

Copy the generated string and update:
```env
JWT_SECRET_KEY=your-generated-64-character-hex-string
```

---

### 6. ⏭️ Razorpay (Optional - Skip for Now)

You can add this later when you're ready to test payments. For now, leave the default values:
```env
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

---

## 🔍 Quick Verification

After filling in all values, your `.env` file should have:
- ✅ No placeholders like `[YOUR-PASSWORD]` remaining
- ✅ All URLs and keys filled in
- ✅ Special characters in passwords properly encoded
- ✅ No extra spaces around `=` signs

## 🧪 Test Your Configuration

Once you've filled in all the values, we can test the connections:

```bash
cd D:\redflags\backend
source venv/Scripts/activate
python -c "from app.config import settings; print('Config loaded successfully!')"
```

If this runs without errors, your `.env` is correctly configured!

---

## 🆘 Need Help?

**Common Issues:**

1. **Supabase connection fails:**
   - Make sure you're using **Transaction pooler** (port 6543)
   - Verify password is URL-encoded (`#` → `%23`, etc.)

2. **Redis connection fails:**
   - Check that token doesn't have extra quotes
   - Format must be: `redis://default:TOKEN@endpoint:6379`

3. **R2 access denied:**
   - Verify API token has **Read & Write** permissions
   - Check bucket name matches exactly: `redflags-pdfs`

---

Ready to continue? Just let me know when you've filled in the `.env` file!
