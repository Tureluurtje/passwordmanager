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

  preparePayload(encryptedPassword, nonce, metadata) {
    const UUID = this.generateUUID();
    const Base64Password = uint8ArrayToBase64(encryptedPassword);
    const base64Nonce = uint8ArrayToBase64(nonce);
    const payload = {
      "id": UUID,
      "password": Base64Password,
      "nonce": base64Nonce,
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

  async uploadPayload(username, payload) {
    const res = await fetch('/password', {
      method: 'POST',
      headers: { 
      'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username,
        payload: payload,
      })
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

export async function handleAddPassword(name, url, username, password, notes, category, datetime) {
  try {
    let metadata_name, metadata_url, metadata_username, metadata_notes, metadata_category, metadata_datetime;
    try {
      metadata_name = typeof name !== 'undefined' && name ? name : null;
      metadata_url = typeof url !== 'undefined' && url ? url : null;
      metadata_username = typeof username !== 'undefined' && username ? username : null;
      metadata_notes = typeof notes !== 'undefined' && notes ? notes : null;
      metadata_category = typeof category !== 'undefined' && category ? category : null;
      metadata_datetime = typeof datetime !== 'undefined' && datetime ? datetime : null;
    } catch (err) {
      console.error(err);
    }

    let user, encKeyBase64;
    try {
      const data = JSON.parse(window.name);
      user = data.username;
      encKeyBase64 = data.encKey;
    } catch (e) {
      console.error('Failed to parse window.name JSON:', e);
    }

    if (!encKeyBase64) {
      console.error('No token received');
    } else if (!user) {
      console.error('No username received');
    }
    window.name = '';
    const encKey = base64ToUint8Array(encKeyBase64);

    const obj = new AddPassword();
    const { ciphertext, nonce } = await obj.encryptPassword(encKey, password);

    const metadata = {
      "name": metadata_name,
      "url": metadata_url,
      "username": metadata_username,
      "notes": metadata_notes,
      "category": metadata_category,
      "datetime": metadata_datetime,
    }
    const payload = obj.preparePayload(ciphertext, nonce, metadata);
    const response = await obj.uploadPayload(user, payload);
    if (!response || !response.success) {
      throw new Error('Invalid response from server');
    }
  } catch (err) {
    console.error(err);
  }
}
