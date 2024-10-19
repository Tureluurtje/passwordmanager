import pyotp
import qrcode
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import Tk, Label

# Step 1: Generate a secret key
secret = pyotp.random_base32()
print(f"Your secret key is: {secret}")

# Step 2: Create TOTP and provisioning URL
totp = pyotp.TOTP(secret)
provisioning_url = totp.provisioning_uri("user@example.com", issuer_name="YourAppName")

# Step 3: Generate QR code and keep it in memory
qr = qrcode.make(provisioning_url)

# Store the QR code in memory using BytesIO
buffer = BytesIO()
qr.save(buffer, format="PNG")
buffer.seek(0)

# Step 4: Create a Tkinter window to display the QR code
root = Tk()
root.title("Scan QR Code with Google Authenticator")

# Load the QR code from the buffer and convert it to an image Tkinter can display
image = Image.open(buffer)
tk_image = ImageTk.PhotoImage(image)

# Create a Label widget in Tkinter to hold the QR code
label = Label(root, image=tk_image)
label.pack()

# Step 5: Run the Tkinter event loop
root.mainloop()

# Step 6: Verify the user's code after scanning
user_code = input("Enter the 6-digit code from Google Authenticator: ")

if totp.verify(user_code):
    print("Code is valid!")
else:
    print("Invalid code!")