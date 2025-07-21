const urlInput = { value: "https://example.com" };
const usernameInput = { value: "testUser123" };
const notesInput = { value: "This is a note about the password." };
const datetimeInput = { value: "2025-07-20T12:00:00Z" };

async function decryptPassword(encKeyBytes, ciphertext, nonce) {
  const cryptoKey = await crypto.subtle.importKey(
    "raw",
    encKeyBytes,
    { name: "AES-GCM" },
    false,
    ["decrypt"]
  );
  const plaintextBuffer = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: nonce },
    cryptoKey,
    ciphertext
  );
  return new TextDecoder().decode(plaintextBuffer);
}

class AddPassword {
  async encryptPassword(encKeyBytes, plaintext) {
    const cryptoKey = await crypto.subtle.importKey(
      "raw",
      encKeyBytes,
      { name: "AES-GCM" },
      false,
      ["encrypt"]
    );
    const nonce = crypto.getRandomValues(new Uint8Array(12));  // 12 bytes nonce
    const data = new TextEncoder().encode(plaintext);
    const ciphertext = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv: nonce },
      cryptoKey,
      data
    );
    return {
      ciphertext: new Uint8Array(ciphertext),
      nonce: nonce
    };
  };

  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = crypto.getRandomValues(new Uint8Array(1))[0] % 16;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  preparePayload(encryptedPassword, metadata) {
    const UUID = this.generateUUID();
    const Base64Password = uint8ArrayToBase64(encryptedPassword);
    const payload = {
      "id": UUID,
      "password": Base64Password,
      "metadata": {
        "url": metadata.url,
        "username": metadata.username,
        "notes": metadata.notes,
        "created": metadata.datetime,
        "modified": metadata.datetime,
      }
    };
    return payload;
  };

  async uploadPayload(payload) {
    const res = await fetch('/passwords', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      throw new Error(`Failed to upload password: ${res.statusText}`);
    }
    return res.json();

  }
};

function uint8ArrayToBase64(bytes) {
  let binary = '';
  bytes.forEach(b => binary += String.fromCharCode(b));
  return btoa(binary);
}

function base64ToUint8Array(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

(async () => {
  try {
    let url, username, notes, datetime;
    try {
      url = typeof urlInput !== 'undefined' && urlInput ? urlInput.value : null;
      username = typeof usernameInput !== 'undefined' && usernameInput ? usernameInput.value : null;
      notes = typeof notesInput !== 'undefined' && notesInput ? notesInput.value : null;
      datetime = typeof datetimeInput !== 'undefined' && datetimeInput ? datetimeInput.value : null;
    } catch (err) {
      console.error(err);
    }
    const encKeyBase64 = window.name;

    if (!encKeyBase64) {
      console.error('No token received')
    }
    window.name = '';

    const encKey = base64ToUint8Array(encKeyBase64);

    const obj = new AddPassword();
    const { ciphertext, nonce } = await obj.encryptPassword(encKey, 'test');

    const metadata = {
        "url": url,
        "username": username,
        "notes": notes,
        "datetime": datetime,
    }
    const payload = obj.preparePayload(ciphertext, metadata);
    console.log(payload);
    console.log(JSON.stringify(payload, null, 2));
    const response = await obj.uploadPayload(payload);
    if (!response || !response.id) {
      throw new Error('Invalid response from server');
    }
    console.log('Password uploaded successfully:', response);
  } catch (err) {
    console.error(err);
  }
})();
