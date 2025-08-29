class AddPassword {
  async encryptPassword(encKeyBytes, plaintext) {
    const cryptoKey = await crypto.subtle.importKey(
      "raw",
      encKeyBytes,
      { name: "AES-GCM" },
      false,
      ["encrypt"]
    );
    const nonce = crypto.getRandomValues(new Uint8Array(12)); // 12 bytes nonce
    const data = new TextEncoder().encode(plaintext);
    const ciphertext = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv: nonce },
      cryptoKey,
      data
    );
    return {
      ciphertext: new Uint8Array(ciphertext),
      nonce: nonce,
    };
  }

  generateUUID() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
      const r = crypto.getRandomValues(new Uint8Array(1))[0] % 16;
      const v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  preparePayload(encryptedPassword, nonce, metadata) {
    const UUID = this.generateUUID();
    const Base64Password = uint8ArrayToBase64(encryptedPassword);
    const base64Nonce = uint8ArrayToBase64(nonce);
    const payload = {
      id: UUID,
      password: Base64Password,
      nonce: base64Nonce,
      metadata: {
        name: metadata.name,
        url: metadata.url,
        username: metadata.username,
        notes: metadata.notes,
        category: metadata.category,
        isFavorite: metadata.isFavorite,
        isBreached: metadata.isBreached,
        created: metadata.datetime,
        modified: metadata.datetime,
      },
    };
    return payload;
  }

  async uploadPayload(username, payload) {
    const res = await fetch("/password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        method: "ADD",
        username: username,
        payload: payload,
      }),
    });
    if (!res.ok) {
      throw new Error(`Failed to upload password: ${res.statusText}`);
    }
    return res.json();
  }
}

class GetPassword {
  async downloadVault(user) {
    const res = await fetch("/password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        method: "GET",
        username: user,
      }),
    });
    if (!res.ok) {
      throw new Error(`Failed to download vault: ${res.statusText}`);
    }
    return res.json();
  }

  async decryptPassword(encKeyBytes, ciphertext, nonce) {
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
}

class UpdatePassword {
  constructor (user, passwordId, replacements) {
    this.user = user;
    this.passwordId = passwordId;
    this.replacements = replacements;
     return this.sendRequest();
  }
  async sendRequest() {
    const res = await fetch("/password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        method: "UPDATE",
        username: this.user,
        passwordId: this.passwordId,
        replacements: this.replacements
      }),
    });
    if (!res.ok) {
      throw new Error(`Failed to update password: ${res.statusText}`);
    }
    return res.json();
  }
}

class RemovePassword {
  constructor (user, passwordId) {
    this.user = user;
    this.passwordId = passwordId;
     return this.sendRequest();
  }
  async sendRequest() {
    const res = await fetch("/password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        method: "DELETE",
        username: this.user,
        passwordId: this.passwordId
      }),
    });
    if (!res.ok) {
      throw new Error(`Failed to remove password: ${res.statusText}`);
    }
    return res.json();
  }
}

function uint8ArrayToBase64(bytes) {
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
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

// Module-level cache so callers don't need to rely on `window.name` order.
let cachedUser = null;
let cachedEncKey = null; // Uint8Array

// Allow explicitly setting the cached context (username and/or encKey).
// encKey may be a base64 string, a Uint8Array, or an ArrayBufferView.
export function setEncContext(user, encKey) {
  if (user) cachedUser = user;
  if (!encKey) return;

  if (typeof encKey === "string") {
    try {
      cachedEncKey = base64ToUint8Array(encKey);
    } catch (e) {
      console.error("Failed to parse encKey base64 string:", e);
    }
  } else if (encKey instanceof Uint8Array) {
    cachedEncKey = encKey;
  } else if (encKey && encKey.buffer instanceof ArrayBuffer) {
    cachedEncKey = new Uint8Array(encKey.buffer);
  } else {
    console.error("Unsupported encKey type passed to setEncContext");
  }
}

export function getCachedUser() {
  return cachedUser;
}

export function getCachedEncKey() {
  return cachedEncKey;
}

export function retrieveEncKey() {
  // Return cached value if present
  if (cachedEncKey) return { user: cachedUser, encKey: cachedEncKey };

  let encKeyBase64 = null;
  try {
    if (window.name) {
      const data = JSON.parse(window.name);
      if (data.username) cachedUser = data.username;
      if (data.encKey) encKeyBase64 = data.encKey;
    }
  } catch (e) {
    console.error("Failed to parse window.name JSON:", e);
  }

  if (!encKeyBase64) {
    if (!cachedEncKey) console.error("No token received");
    console.log("Error with routing, resetting...")
    return "sendBeacon", null;
  } else {
    cachedEncKey = base64ToUint8Array(encKeyBase64);
  }

  // Clear window.name for safety if it existed
  if (window.name) window.name = "";

  return { user: cachedUser, encKey: cachedEncKey };
}

export async function handleAddPassword(
  { user, encKey },
  name,
  url,
  username,
  password,
  notes,
  category,
  isFavorite,
  isBreached,
  datetime
) {
  try {
    let metadata_name,
      metadata_url,
      metadata_username,
      metadata_notes,
      metadata_category,
      metadata_isFavorite,
      metadata_isBreached,
      metadata_datetime;
    try {
      metadata_name = typeof name !== "undefined" && name ? name : null;
      metadata_url = typeof url !== "undefined" && url ? url : null;
      metadata_username =
        typeof username !== "undefined" && username ? username : null;
      metadata_notes = typeof notes !== "undefined" && notes ? notes : null;
      metadata_category =
        typeof category !== "undefined" && category ? category : null;
      metadata_isFavorite = isFavorite ?? false;
      metadata_isBreached = isBreached ?? false;
      metadata_datetime =
        typeof datetime !== "undefined" && datetime ? datetime : null;
    } catch (err) {
      console.error(err);
    }

    // Resolve encKey: prefer explicit argument, then cachedEncKey, then try retrieveEncKey()
    if (!encKey) encKey = (await retrieveEncKey()).encKey;
    if (!encKey) throw new Error("No encryption key available");

    // Normalize encKey to Uint8Array
    if (typeof encKey === "string") {
      encKey = base64ToUint8Array(encKey);
    } else if (
      !(encKey instanceof Uint8Array) &&
      encKey &&
      encKey.buffer instanceof ArrayBuffer
    ) {
      encKey = new Uint8Array(encKey.buffer);
    }

    const obj = new AddPassword();
    const { ciphertext, nonce } = await obj.encryptPassword(encKey, password);

    const metadata = {
      name: metadata_name,
      url: metadata_url,
      username: metadata_username,
      notes: metadata_notes,
      category: metadata_category,
      isFavorite: metadata_isFavorite,
      isBreached: metadata_isBreached,
      datetime: metadata_datetime,
    };
    const payload = obj.preparePayload(ciphertext, nonce, metadata);
    if (!cachedUser) throw new Error("No username available to upload payload");
    const response = await obj.uploadPayload(cachedUser, payload);
    if (!response || !response.success) {
      throw new Error("Invalid response from server");
    }
  } catch (err) {
    console.error(err);
  }
}

export async function handleGetPassword({ user, encKey }) {
  try {
    const obj = new GetPassword();
    const jsonVault = await obj.downloadVault(user);
    const vaultData = JSON.parse(jsonVault.data.message);

    let formattedVault = {};
    for (const entry of vaultData) {
      const hashedPassword = base64ToUint8Array(entry.password);
      const nonce = base64ToUint8Array(entry.nonce);
      const decryptedPassword = await obj.decryptPassword(
        encKey,
        hashedPassword,
        nonce
      );
      delete entry.nonce;
      entry.password = decryptedPassword;
      formattedVault[entry.id] = entry;
    }
    return formattedVault;
  } catch (e) {
    return e;
  }
}

export async function handleUpdatePassword(username, passwordId, replacements) {
  return new UpdatePassword(username, passwordId, replacements);
}

export async function handleDeletePassword(username, passwordId) {
  return new RemovePassword(username, passwordId);
}