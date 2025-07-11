const form = document.querySelector('form');
const usernameInput = form.elements['username'];
const passwordInput = form.elements['password'];
const usernameError = document.getElementById('username-input');
const passwordError = document.getElementById('password-input');

async function hashPassword(password, saltHex) {
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
        const response_salt = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: 'salt',
                username: usernameInput.value,
            })
        });

        if (!response_salt.ok) throw new Error('Salt fetch failed');

        const { salt: { message: salt_hex } } = await response_salt.json();

        const hashedPassword = await hashPassword(passwordInput.value, salt_hex);

        const response_authenticate = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: 'authenticate',
                username: usernameInput.value,
                password: hashedPassword
            })
        });

        if (response_authenticate.ok) {
            const data = await response_authenticate.json();
            if (data.success) {
                window.location.href = '/';
            } else {
                passwordError.textContent = 'Username or password incorrect';
                form.classList.add('auth-error');
            }
        } else {
            passwordError.textContent = 'Username or password incorrect';
            form.classList.add('auth-error');
        }
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
