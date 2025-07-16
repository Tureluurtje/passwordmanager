// This runs in a separate context
let encryptionKey = null; // kept purely in memory

onconnect = function(e) {
  const port = e.ports[0];

  port.onmessage = async (event) => {
    const { action, data } = event.data;

    if (action === 'setKey') {
      encryptionKey = data; // store in memory
      port.postMessage({ status: 'ok' });
    }

    else if (action === 'getKey') {
      // only send key if we have it
      if (encryptionKey) {
        port.postMessage({ status: 'ok', key: encryptionKey });
      } else {
        port.postMessage({ status: 'error', message: 'No key set' });
      }
    }

    else if (action === 'clearKey') {
      encryptionKey = null;
      port.postMessage({ status: 'ok' });
    }
  };
};
