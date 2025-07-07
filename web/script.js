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
    // @CRITICAL This line MUST be optimized before release
    const url = new URL('http://127.0.0.1:5000/api/');
    url.searchParams.set('requestMethod', 'authenticate');
    url.searchParams.set('action', 'login');
    url.searchParams.set('username', username);
    url.searchParams.set('password', hashedPassword);

    fetch(url)
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(err => console.error('Error:', err));

});