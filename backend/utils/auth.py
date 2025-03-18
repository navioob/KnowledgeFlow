import rsa
import base64

# read Private Key
with open("./static/private.pem", "rb") as f:
    private_key = rsa.PrivateKey.load_pkcs1(f.read())

#decrypt encryption message
def decrypt_text(encrpyted_bytes):
    # Decode base64 to bytes
    print(1)
    encrypted_text = base64.b64decode(encrpyted_bytes + '=' * (-len(encrpyted_bytes) % 4))

    print(2)

    decrypted_text = rsa.decrypt(encrypted_text, private_key)
    
    return decrypted_text.decode()