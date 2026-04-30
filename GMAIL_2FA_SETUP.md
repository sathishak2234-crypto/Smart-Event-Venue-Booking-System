# Gmail 2FA and App Password Setup Guide

Complete step-by-step guide to enable 2-Factor Authentication (2FA) on Gmail and generate an App Password for email notifications.

---

## **Step 1: Go to Gmail Security Settings**

1. Open your browser and go to: **https://myaccount.google.com/security**
2. Sign in with your Gmail account: `sathishak2234@gmail.com`
3. You'll see the "Security" page with various security options

---

## **Step 2: Enable 2-Step Verification**

### **2.1 Find the 2-Step Verification Option**
- Look for **"2-Step Verification"** section on the left sidebar
- Click on **"2-Step Verification"**

### **2.2 Start the Setup**
- Click the **"Get Started"** button
- You'll be asked to confirm your password again
- Enter your Gmail password and click **"Next"**

### **2.3 Choose a Verification Method**
You have multiple options:
- **Text message (SMS)** - Receives code via text
- **Authenticator app** - Use Google Authenticator, Authy, or Microsoft Authenticator
- **Security key** - Hardware security key

**Recommended:** Use your phone number (SMS) for simplicity

### **2.4 Verify Your Phone Number**
1. Enter your phone number
2. Select your country code
3. Choose how to receive the code:
   - **Text message** (fastest)
   - **Phone call**
4. Click **"Send code"**
5. Enter the 6-digit code you receive on your phone
6. Click **"Verify"**

### **2.5 Complete 2FA Setup**
- Click **"Turn on 2-Step Verification"**
- You'll get a backup code - **SAVE THIS SAFELY**
- Screenshot or write down the backup codes in case you lose access to your phone

✅ **2-Step Verification is now ENABLED**

---

## **Step 3: Generate App Password**

### **3.1 Go to App Passwords Page**
1. Go to: **https://myaccount.google.com/apppasswords**
2. You must be signed in as `sathishak2234@gmail.com`
3. You'll see a page asking for your app and device

### **3.2 Select App and Device**

**In the first dropdown (Select the app you're using):**
- Click the dropdown
- Select **"Mail"**

**In the second dropdown (Select the device you're using):**
- Click the dropdown
- Select **"Windows Computer"**
- (If you're on Mac, select "Mac" instead)

### **3.3 Generate the Password**
1. Click **"Generate"** button
2. Google will create a 16-character password
3. The password will appear in a popup: **`xxxx xxxx xxxx xxxx`**

### **3.4 Copy the Password**
⚠️ **IMPORTANT:** The password is shown only ONCE

1. **Copy the 16-character password** (without spaces)
   - Example format: `kkiwkqyzxfwwcfoc`
2. Click **"Copy"** or manually highlight and copy it
3. **Save it in a safe place**

### **3.5 Confirm**
- Click **"Done"**
- The app password is now created and ready to use

---

## **Step 4: Update Your System Configuration**

Once you have the 16-character App Password:

### **4.1 Update `backend/config.py`**

Open [backend/config.py](backend/config.py) and update:

```python
# Email Configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'sathishak2234@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '[PASTE_YOUR_16_CHAR_PASSWORD_HERE]')
```

**Replace `[PASTE_YOUR_16_CHAR_PASSWORD_HERE]` with your actual app password**

Example:
```python
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'kkiwkqyzxfwwcfoc')
```

### **4.2 Test Email Sending**

After updating the config, test if emails work:

Run this command from the `backend/` directory:

```bash
python -c "from mailer import send_email; result = send_email('sathishak2234@gmail.com', 'Test Email', '<h1>Success!</h1><p>Your email system is working!</p>', is_html=True); print(f'Email sent: {result}')"
```

**Expected output if successful:**
```
Email sent: True
```

---

## **Troubleshooting**

### **Problem: "App Passwords" option not visible**

**Solution:**
- Make sure 2-Step Verification is ENABLED first
- Go back to https://myaccount.google.com/security
- Enable "2-Step Verification" first, then try app passwords again

### **Problem: "Username and Password not accepted"**

**Solution:**
1. Verify you copied the password correctly (16 characters, no spaces)
2. Delete the old password from config.py and regenerate a new one
3. Go to https://myaccount.google.com/apppasswords and delete the old "Mail - Windows Computer" entry
4. Generate a NEW app password
5. Use the new password in config.py

### **Problem: SMTP Connection Timeout**

**Solution:**
- Check your internet connection
- Make sure port 587 is not blocked by your firewall
- Try again in a few minutes

### **Problem: Different error message**

**Solution:**
- Check the exact error in the terminal logs
- Make sure EMAIL_HOST, EMAIL_PORT, and EMAIL_ADDRESS are correct:
  ```python
  EMAIL_HOST = 'smtp.gmail.com'      # Exactly this
  EMAIL_PORT = 587                    # Exactly this (not 465)
  EMAIL_ADDRESS = 'sathishak2234@gmail.com'  # Your Gmail
  EMAIL_PASSWORD = '[YOUR_APP_PASSWORD]'    # 16-char app password
  ```

---

## **Important Security Notes** 🔒

### **Keep Your App Password Safe:**
- ⚠️ Do NOT share the app password with anyone
- ⚠️ Do NOT post it in public repositories
- ⚠️ Do NOT commit it to GitHub

### **If You Need to Use Environment Variables:**

Instead of hardcoding the password, create a `.env` file:

```env
EMAIL_ADDRESS=sathishak2234@gmail.com
EMAIL_PASSWORD=kkiwkqyzxfwwcfoc
```

Then update config.py to read from `.env`:
```python
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'your-email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')
```

---

## **What's Next?**

After getting your App Password and updating config.py:

1. ✅ Registration emails will be sent automatically
2. ✅ Booking confirmation emails will be sent automatically
3. ✅ Payment confirmation emails will be sent automatically
4. ✅ Users will see real email confirmations instead of just status badges

---

## **Quick Reference**

| Step | URL |
|------|-----|
| Security Settings | https://myaccount.google.com/security |
| 2FA Setup | https://myaccount.google.com/security (find 2-Step Verification) |
| App Passwords | https://myaccount.google.com/apppasswords |

| File to Update | Setting | Value |
|---|---|---|
| `backend/config.py` | EMAIL_ADDRESS | sathishak2234@gmail.com |
| `backend/config.py` | EMAIL_PASSWORD | [Your 16-char app password] |
| `backend/config.py` | EMAIL_HOST | smtp.gmail.com |
| `backend/config.py` | EMAIL_PORT | 587 |

---

## **Still Having Issues?**

If you still have problems after following this guide:

1. Double-check that 2FA is ENABLED (check your Google Security settings)
2. Make sure you're using a **16-character App Password** (not your main Gmail password)
3. Verify the password has no extra spaces or formatting
4. Try generating a new App Password and delete the old one
5. Restart the Python backend server after updating config.py

**Contact Support:** If issues persist, check the terminal logs for specific error messages.
