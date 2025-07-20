const token = window.name;
window.name = '';

if (token) {
  console.log('Received token: ', token);
} else {
  console.log('No token received')
}




class AddPassword {
  constructor(username, encKey) {
    this.username = username;
    this.password = password;
  };

  generateNonce() {
    const iv = crypto.getRandomValues(new Uint8Array(16));
    return iv;
  }
};