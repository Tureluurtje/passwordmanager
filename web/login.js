const form = document.querySelector('form');
form.addEventListener('submit', async function(event) {
    event.preventDefault();
    const username = form.elements['username'].value;
    const password = form.elements['password'].value;

    async function hashPassword(password) {
        const encoder = new TextEncoder();
        const data = encoder.encode(password);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    const hashedPassword = await hashPassword(password)

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
        username: username,
        password: hashedPassword
        })
    });
    
    if (response.ok) {
        const data = await response.json();
        console.log(data);

        if (data.success) {
            window.location.href = '/';
        } else {
            console.log('Login failed:', data.message);
        }
    }
    
});