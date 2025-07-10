const form = document.querySelector('form');
form.addEventListener('submit', async function(event) {
    event.preventDefault();
    const username = form.elements['username'].value;
    const password = form.elements['password'].value;

    async function hashPassword(password, saltHex) {
        const encoder = new TextEncoder();
        const salt = Uint8Array.from(saltHex.match(/.{2}/g).map(byte => parseInt(byte, 16)));

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
        const derivedKeyHex = derivedKeyArray.map(b => b.toString(16).padStart(2, '0')).join('');

        return derivedKeyHex;
    }

    const response_salt = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            method: 'salt',
            username: username,
        })
    });

    let salt_hex;
    if (response_salt.ok) {
        const response_json = await response_salt.json();
        salt_hex = response_json.salt.message;
    } else {
        console.error("Failed to fetch salt");
        return;
    }

    const hashedPassword = await hashPassword(password, salt_hex);
    console.log("Derived Key:", hashedPassword);

    const response_authenticate = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            method: 'authenticate',
            username: username,
            password: hashedPassword
        })
    });

    if (response_authenticate.ok) {
        const data = await response_authenticate.json();
        console.log(data);

        if (data.success) {
            window.location.href = '/';
        } else {
            console.log('Login failed:', data.message);
        }
    } else {
        console.error("Failed to authenticate");
    }
});
