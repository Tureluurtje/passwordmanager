const worker = new SharedWorker('js/worker.js'); 
worker.port.start(); //Initialise worker

function requestEncKey() {
  return new Promise((resolve, reject) => {
    worker.port.postMessage({ action: 'getKey' });

    worker.port.onmessage = (event) => {
      if (event.data.status === 'ok') {
        // Got key from worker
        const encryptionKeyBytes = new Uint8Array(event.data.key);
        resolve(encryptionKeyBytes);
      } else {
        reject(new Error(event.data.message));
      }
    };
  });
};

requestEncKey().then(encKey => {
  console.log(encKey);
});
