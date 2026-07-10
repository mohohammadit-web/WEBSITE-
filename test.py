# وارد کردن کتابخانه سوکت برای برقراری ارتباط شبکه‌ای در لایه پایین (TCP)
import socket
# وارد کردن ابزار آنالیز URL برای استخراج آسان نام دامنه، پورت و مسیر
from urllib.parse import urlparse

def simple_http_client():
    # ۱. دریافت آدرس URL از کاربر
    url = input("enter url------> ")
    
    # ۲. تجزیه و تحلیل آدرس URL
    parsed_url = urlparse(url)
    
    # استخراج نام میزبان (Hostname) مثل: example.com
    hostname = parsed_url.hostname
    
    # استخراج مسیر فایل (Path)، اگر مسیر خالی بود علامت اسلش "/" به معنی صفحه اصلی قرار می‌گیرد
    path = parsed_url.path if parsed_url.path else "/"
    
    # استخراج پورت؛ اگر کاربر پورتی مشخص نکرده بود، پورت پیش‌فرض وب یعنی 80 قرار می‌گیرد
    port = parsed_url.port if parsed_url.port else 80
    
    # بررسی امنیتی: اگر آدرس وارد شده معتبر نبود و نام میزبان استخراج نشد، برنامه متوقف می‌شود
    if not hostname:
        print("خطا: آدرس وارد شده معتبر نیست!")
        return

    try:
        # ۳. ایجاد یک اتصال TCP به وب‌سرور
        # ایجاد شیء سوکت (AF_INET برای استفاده از IPv4 و SOCK_STREAM برای پروتکل مطمئن TCP)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # برقراری اتصال سخت‌افزاری/نرم‌افزاری به سرور مقصد روی پورت مشخص شده
        client_socket.connect((hostname, port))
        
        # ۴. ساخت دستی درخواست GET از نوع HTTP/1.0
        # تعریف ساختار استاندارد درخواست HTTP (هر خط با r\n\ یعنی رفتن به خط جدید پایان می‌یابد)
        request = f"GET {path} HTTP/1.0\r\n"      # خط شروع: متد GET، مسیر فایل و نسخه پروتکل
        request += f"Host: {hostname}\r\n"        # هدر Host: اعلام نام دامنه به سرور (برای سرورهای اشتراکی ضروری است)
        request += "Connection: close\r\n"        # هدر Connection: اعلام اینکه بعد از پاسخ، اتصال بسته شود
        request += "\r\n"                         # خط خالی انتهایی: نشان‌دهنده پایان یافتن بخش هدرهای درخواست
        
        # ارسال درخواست به سرور (تبدیل متن رشته‌ای به بایت‌های قابل فهم در شبکه با فرمت UTF-8)
        client_socket.sendall(request.encode('utf-8'))
        
        # ۵. دریافت پاسخ سرور به صورت بایت به بایت
        response = b""  # ایجاد یک ظرف خالی از نوع بایت برای جمع‌آوری پاسخ
        while True:
            # دریافت داده‌ها در بسته‌های کوچک ۴۰۹۶ بایتی (۴ کیلوبایت)
            data = client_socket.recv(4096)
            # اگر دیگر داده‌ای از سمت سرور فرستاده نشد (پایان انتقال)، حلقه متوقف می‌شود
            if not data:
                break
            # اضافه کردن تکه داده دریافت شده به انتهای کل پاسخ
            response += data
        
        # بستن اتصال سوکت جهت آزاد کردن منابع سیستم
        client_socket.close()
        
        # تفکیک هدرها از بدنه اصلی پاسخ
        # در پروتکل HTTP، هدرها همیشه با دو بار خط جدید (b"\r\n\r\n") از بدنه جدا می‌شوند
        header_bytes, body_bytes = response.split(b"\r\n\r\n", 1)
        
        # تبدیل بایت‌های هدر به متن رشته‌ای قابل خواندن و تقسیم خطوط آن بر اساس r\n\
        headers_list = header_bytes.decode('utf-8', errors='ignore').split("\r\n")
        
        # ۶. نمایش اطلاعات در خروجی (کنسول)
        print("\n" + "="*50)
        
        # الف) نمایش خط وضعیت پاسخ (خط اول همیشه وضعیت است مثل HTTP/1.1 200 OK)
        print("--- Status Line ---")
        print(headers_list[0])
        
        # ب) نمایش تمام هدرهای پاسخ (از خط دوم به بعد لیست هدرها قرار دارد)
        print("\n--- Response Headers ---")
        for header in headers_list[1:]:
            print(header)
            
        # ج) نمایش ۵۰۰ کاراکتر اول بدنه پاسخ
        print("\n--- Body (First 500 characters) ---")
        # تبدیل بایت‌های بدنه به متن جهت نمایش در ترمینال
        body_text = body_bytes.decode('utf-8', errors='ignore')
        # چاپ ۵۰۰ کاراکتر اول متن (یا کل آن اگر از ۵۰۰ کاراکتر کمتر بود)
        print(body_text[:500])
        
        # ۷. ذخیره کل بدنه پاسخ در فایلی با نام downloaded.html
        # باز کردن فایل به صورت Write Binary (wb) برای ذخیره دقیق بایت‌های اصلی بدنه
        with open("download.html", "wb") as file:
            file.write(body_bytes)
            
        print("\n" + "="*50)
        print("عملیات موفقیت‌آمیز بود! کل بدنه پاسخ در فایل 'download.html' ذخیره شد.")

    # مدیریت خطاهای احتمالی (مانند در دسترس نبودن سرور یا قطع بودن اینترنت)
    except Exception as error:
        print(f"خطایی در حین ارتباط رخ داد: {error}")

# شرط استاندارد پایتون برای اجرای برنامه در صورت فراخوانی مستقیم فایل
if __name__ == "__main__":
    simple_http_client()
