const worker = new SharedWorker('js/worker.js');
worker.port.start();

const form = document.querySelector('form');
const usernameInput = form.elements['username'];
const passwordInput = form.elements['password'];
const usernameError = document.getElementById('username-input');
const passwordError = document.getElementById('password-input');

async function fetchSalt(username) {
    const response_salt = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: 'salt',
                username: username,
            })
        });

        if (!response_salt.ok) throw new Error('Salt fetch failed');

        const { salt: { message: salt_hex } } = await response_salt.json();
        return salt_hex;
}

async function deriveRootKey(password, saltHex) {
    const encoder = new TextEncoder();
    const salt = Uint8Array.from(saltHex.match(/.{2}/g).map(byte => parseInt(byte, 16)));

    try {
        const keyMaterial = await crypto.subtle.importKey(
            "raw",
            encoder.encode(password),
            { name: "PBKDF2" },
            false,
            ["deriveBits"]
        );

        const derivedBits = await crypto.subtle.deriveBits(
            {
                name: "PBKDF2",
                salt: salt,
                iterations: 100_000,
                hash: "SHA-256",
            },
            keyMaterial,
            256
        );

        const derivedKeyArray = Array.from(new Uint8Array(derivedBits));
        return derivedKeyArray.map(b => b.toString(16).padStart(2, '0')).join('');
    } catch (error) {
        console.warn("WebCrypto API failed, falling back to CryptoJS PBKDF2.", error);
        // Fallback using CryptoJS PBKDF2
        const saltWordArray = CryptoJS.enc.Hex.parse(saltHex);
        const derivedKey = CryptoJS.PBKDF2(password, saltWordArray, {
            keySize: 256 / 32,
            iterations: 100_000,
            hasher: CryptoJS.algo.SHA256
        });
        return derivedKey.toString(CryptoJS.enc.Hex);
    }
}

async function hkdf(inputKeyMaterial, infoString, length = 32) {
  const cryptoKey = await crypto.subtle.importKey(
    "raw",
    inputKeyMaterial,
    "HKDF",
    false,
    ["deriveBits"]
  );

  const derivedBits = await crypto.subtle.deriveBits(
    {
      name: "HKDF",
      hash: "SHA-256",
      salt: new Uint8Array([]),
      info: new TextEncoder().encode(infoString),
    },
    cryptoKey,
    length * 8
  );

  return new Uint8Array(derivedBits);
}

function hexToBytes(hex) {
  if (hex.length % 2 !== 0) throw new Error("Invalid hex string");
  const arr = new Uint8Array(hex.length / 2);
  for (let i = 0; i < arr.length; i++) {
    arr[i] = parseInt(hex.substr(i * 2, 2), 16);
  }
  return arr;
}

function toHex(buffer) {
  // Accepts Uint8Array or ArrayBuffer
  const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
  return Array.from(bytes)
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

async function sendAuthReq(username, authKey) {
        const res = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: 'authenticate',
                username: username,
                password: authKey
            })
        });

        return res
}

async function login(username, masterPassword) {
    const saltHex = await fetchSalt(username);
    const rootKeyMaterial = await deriveRootKey(masterPassword, saltHex);
    const rootKeyMaterialBytes = hexToBytes(rootKeyMaterial);

    const authKey = await hkdf(rootKeyMaterialBytes, "authentication");
    const authKeyHex = toHex(authKey);

    return [await sendAuthReq(username, authKeyHex), authKeyHex];
}


form.addEventListener('submit', async function(event) {
    event.preventDefault();

    form.classList.remove('auth-error');

    let formValid = true;

    if (!usernameInput.value) {
        usernameError.textContent = 'This field cannot be left blank';
        formValid = false;
    } else {
        usernameError.textContent = '\u00A0';
    }

    if (!passwordInput.value) {
        passwordError.textContent = 'This field cannot be left blank';
        formValid = false;
    } else {
        passwordError.textContent = '\u00A0';
    }

    if (!formValid) {
        form.classList.add('was-validated');
        return;
    }

    form.classList.remove('was-validated');

    try {
        const [loginSucces, authKeyHex] = await login(usernameInput.value, passwordInput.value);
            if (loginSucces.ok) {
                const data = await loginSucces.json();
                if (data.success) {
                    worker.port.postMessage({ action : 'setKey', data: Array.from(authKeyHex) })
                    worker.port.onmessage = (event) => {
                        if (event.data.status == "ok") {
                            window.location.href = '/';
                        } else {
                            console.log('Worker response: ', event.data)
                        }
                    };
                } else {
                    passwordError.textContent = 'Username or password incorrect';
                    form.classList.add('auth-error');
                }
            } else {
                passwordError.textContent = 'Username or password incorrect';
                form.classList.add('auth-error');
            };
    } catch (err) {
        console.error(err);
        passwordError.textContent = 'An error occurred';
        form.classList.add('auth-error');
    }
});

usernameInput.addEventListener('input', () => {
    usernameError.textContent = '\u00A0';
    form.classList.remove('was-validated');
});

passwordInput.addEventListener('input', () => {
    passwordError.textContent = '\u00A0';
    form.classList.remove('was-validated');
    form.classList.remove('auth-error');
});
