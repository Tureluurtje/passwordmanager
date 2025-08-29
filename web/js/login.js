// Passafe Login Application
// Standalone vanilla JavaScript implementation with cryptographic authentication

class PassafeLogin {
  constructor() {
    // State management
    this.formData = {
      username: '',
      password: ''
    };
    
    this.errors = {
      username: '',
      password: ''
    };
    
    this.isLoading = false;
    this.showForgotPassword = false;
    
    // DOM elements
    this.formElement = null;
    this.usernameInput = null;
    this.passwordInput = null;
    this.usernameError = null;
    this.passwordError = null;
    this.submitBtn = null;
    this.loadingIndicator = null;
    this.forgotPasswordBtn = null;
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
      //document.addEventListener('DOMContentLoaded', () => this.init());
    } else {
      //this.init();
    }
  }

  init() {
    // Ensure dark mode is applied immediately
    document.body.classList.add('dark', 'app-ready');
    document.documentElement.classList.add('dark');
    
    // Get DOM elements
    this.formElement = document.getElementById('loginForm');
    this.usernameInput = document.getElementById('username');
    this.passwordInput = document.getElementById('password');
    this.usernameError = document.getElementById('usernameError');
    this.passwordError = document.getElementById('passwordError');
    this.submitBtn = document.getElementById('submitBtn');
    this.loadingIndicator = document.getElementById('loadingIndicator');
    this.forgotPasswordBtn = document.getElementById('forgotPasswordBtn');
    
    // Bind event listeners
    this.bindEvents();
    
    // Log initialization
    console.log('Passafe Login initialized');
  }

  bindEvents() {
    // Form submission
    this.formElement.addEventListener('submit', (e) => this.handleSubmit(e));
    
    // Input changes
    this.usernameInput.addEventListener('input', (e) => this.handleInputChange(e));
    this.passwordInput.addEventListener('input', (e) => this.handleInputChange(e));
    
    // Forgot password
    this.forgotPasswordBtn.addEventListener('click', (e) => this.handleForgotPassword(e));
  }

  handleInputChange(e) {
    const { name, value } = e.target;
    this.formData[name] = value;
    
    // Clear error when user starts typing
    if (this.errors[name]) {
      this.errors[name] = '';
      this.updateErrorDisplay(name, '');
    }

    // Remove form error classes
    this.formElement.classList.remove('was-validated', 'auth-error');
  }

  updateErrorDisplay(fieldName, message) {
    const errorElement = fieldName === 'username' ? this.usernameError : this.passwordError;
    
    if (message) {
      errorElement.textContent = message;
      errorElement.classList.remove('hide');
      errorElement.classList.add('show');
      errorElement.style.opacity = '1';
      errorElement.style.transform = 'translateY(0)';
    } else {
      errorElement.textContent = '\u00A0';
      errorElement.classList.remove('show');
      errorElement.classList.add('hide');
      errorElement.style.opacity = '0';
      errorElement.style.transform = 'translateY(-2px)';
    }
  }

  setLoading(loading) {
    this.isLoading = loading;
    
    if (loading) {
      this.submitBtn.value = 'Signing In...';
      this.submitBtn.disabled = true;
      this.usernameInput.disabled = true;
      this.passwordInput.disabled = true;
      this.forgotPasswordBtn.disabled = true;
      this.loadingIndicator.style.display = 'flex';
    } else {
      this.submitBtn.value = 'Sign In';
      this.submitBtn.disabled = false;
      this.usernameInput.disabled = false;
      this.passwordInput.disabled = false;
      this.forgotPasswordBtn.disabled = false;
      this.loadingIndicator.style.display = 'none';
    }
  }

  async handleSubmit(e) {
    e.preventDefault();
    
    this.formElement.classList.remove('auth-error');

    let formValid = true;
    const newErrors = { username: '', password: '' };

    if (!this.formData.username.trim()) {
      newErrors.username = 'This field cannot be left blank';
      formValid = false;
    }

    if (!this.formData.password.trim()) {
      newErrors.password = 'This field cannot be left blank';
      formValid = false;
    }

    // Update errors
    this.errors = newErrors;
    this.updateErrorDisplay('username', newErrors.username);
    this.updateErrorDisplay('password', newErrors.password);

    if (!formValid) {
      this.formElement.classList.add('was-validated');
      return;
    }

    this.formElement.classList.remove('was-validated');
    this.setLoading(true);

    try {
      const username = this.formData.username;
      const [loginResponse, encKey] = await this.login(username, this.formData.password);

      if (!loginResponse.ok) throw new Error('Login response not OK');

      const data = await loginResponse.json();
      if (!data.success) throw new Error('Username or password incorrect');

      const encKeyBase64 = this.uint8ArrayToBase64(encKey);

      // Store credentials securely and redirect
      window.name = JSON.stringify({ username: username, encKey: encKeyBase64 });
      // Redirect to main application
      window.location.href = '/';
    } catch (err) {
      console.error(err);
      let errorMessage = 'An error occurred during login';
      
      // Handle specific error types
      if (err.message.includes('Salt fetch failed')) {
        errorMessage = 'Unable to connect to server';
      } else if (err.message.includes('username') || err.message.includes('password')) {
        errorMessage = 'Username or password incorrect';
      } else if (err.message.includes('Login response not OK')) {
        errorMessage = 'Authentication failed';
      } else if (err.message.includes('Key derivation failed')) {
        errorMessage = 'Cryptographic error occurred';
      }
      
      this.errors.password = errorMessage;
      this.updateErrorDisplay('password', errorMessage);
      this.formElement.classList.add('auth-error');
    } finally {
      this.setLoading(false);
    }
  }

  handleForgotPassword(e) {
    e.preventDefault();
    this.showForgotPassword = true;
    this.forgotPasswordBtn.textContent = 'Processing...';
    this.forgotPasswordBtn.disabled = true;
    
    setTimeout(() => {
      alert('Password recovery functionality would be implemented here. This would typically send a recovery email or redirect to a password reset page.');
      this.showForgotPassword = false;
      this.forgotPasswordBtn.textContent = 'Forgot Password?';
      this.forgotPasswordBtn.disabled = false;
    }, 100);
  }

  // Real API functions
  async fetchSalt(username) {
    const response = await fetch('/salt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username,
      }),
    });

    if (!response.ok) throw new Error('Salt fetch failed');

    const {
      salt: { message: salt_hex },
    } = await response.json();
    
    return salt_hex;
  }

  async sendAuthReq(username, authKey) {
    const res = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username,
        password: authKey,
      }),
    });

    return res;
  }

  // Cryptographic functions
  async deriveRootKey(password, saltHex) {
    const encoder = new TextEncoder();
    const salt = Uint8Array.from(
      saltHex.match(/.{2}/g)?.map((byte) => parseInt(byte, 16)) || []
    );

    try {
      const keyMaterial = await crypto.subtle.importKey(
        'raw',
        encoder.encode(password),
        { name: 'PBKDF2' },
        false,
        ['deriveBits']
      );

      const derivedBits = await crypto.subtle.deriveBits(
        {
          name: 'PBKDF2',
          salt: salt,
          iterations: 100_000,
          hash: 'SHA-256',
        },
        keyMaterial,
        256
      );

      const derivedKeyArray = Array.from(new Uint8Array(derivedBits));
      return derivedKeyArray.map((b) => b.toString(16).padStart(2, '0')).join('');
    } catch (error) {
      console.warn('WebCrypto API failed, falling back to CryptoJS PBKDF2.', error);
      
      // Fallback using CryptoJS if available
      if (typeof window !== 'undefined' && window.CryptoJS) {
        const saltWordArray = window.CryptoJS.enc.Hex.parse(saltHex);
        const derivedKey = window.CryptoJS.PBKDF2(password, saltWordArray, {
          keySize: 256 / 32,
          iterations: 100_000,
          hasher: window.CryptoJS.algo.SHA256,
        });
        return derivedKey.toString(window.CryptoJS.enc.Hex);
      }
      
      throw new Error('Key derivation failed');
    }
  }

  async hkdf(inputKeyMaterial, infoString, length = 32) {
    const cryptoKey = await crypto.subtle.importKey(
      'raw',
      inputKeyMaterial,
      'HKDF',
      false,
      ['deriveBits']
    );

    const derivedBits = await crypto.subtle.deriveBits(
      {
        name: 'HKDF',
        hash: 'SHA-256',
        salt: new Uint8Array([]),
        info: new TextEncoder().encode(infoString),
      },
      cryptoKey,
      length * 8
    );

    return new Uint8Array(derivedBits);
  }

  hexToBytes(hex) {
    if (hex.length % 2 !== 0) throw new Error('Invalid hex string');
    const arr = new Uint8Array(hex.length / 2);
    for (let i = 0; i < arr.length; i++) {
      arr[i] = parseInt(hex.substr(i * 2, 2), 16);
    }
    return arr;
  }

  toHex(buffer) {
    const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
    return Array.from(bytes)
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
  }

  async login(username, masterPassword) {
    const saltHex = await this.fetchSalt(username);
    const rootKeyMaterial = await this.deriveRootKey(masterPassword, saltHex);
    const rootKeyMaterialBytes = this.hexToBytes(rootKeyMaterial);

    const authKey = await this.hkdf(rootKeyMaterialBytes, 'authentication');
    const authKeyHex = this.toHex(authKey);

    const encKey = await this.hkdf(rootKeyMaterialBytes, 'encryption');

    return [await this.sendAuthReq(username, authKeyHex), encKey];
  }

  uint8ArrayToBase64(bytes) {
    let binary = '';
    bytes.forEach((b) => (binary += String.fromCharCode(b)));
    return btoa(binary);
  }
}

// Initialize the application
const passafeApp = new PassafeLogin();