// Live code execution for MACRO-AI-COMP
// Connects directly to Binder's Jupyter kernel (no external dependencies)

document.addEventListener('DOMContentLoaded', function() {
  var hasCode = document.querySelector('.md-content pre');
  if (!hasCode) return;

  var content = document.querySelector('.md-content__inner');
  if (!content) return;

  // Build kernel selector bar
  var bar = document.createElement('div');
  bar.id = 'kernel-bar';
  bar.style.cssText = 'background:#f0f4ff; border:1px solid #d0d8f0; border-radius:6px; padding:12px 16px; margin-bottom:20px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; font-size:14px;';

  var label = document.createElement('strong');
  label.textContent = '🔌 Ejecutar código en vivo:';
  label.style.color = '#004C97';
  bar.appendChild(label);

  var btnPy = document.createElement('button');
  btnPy.textContent = '🐍 Activar Python';
  btnPy.style.cssText = 'background:#004C97;color:white;border:none;padding:8px 18px;border-radius:4px;cursor:pointer;font-weight:bold;font-size:14px';
  bar.appendChild(btnPy);

  var btnJl = document.createElement('button');
  btnJl.textContent = '🔢 Activar Julia';
  btnJl.style.cssText = 'background:#8EAD3A;color:white;border:none;padding:8px 18px;border-radius:4px;cursor:pointer;font-weight:bold;font-size:14px';
  bar.appendChild(btnJl);

  var status = document.createElement('span');
  status.id = 'kernel-status';
  status.style.cssText = 'color:#666;margin-left:8px;font-size:13px';
  bar.appendChild(status);

  var spacer = document.createElement('span');
  spacer.style.flex = '1';
  bar.appendChild(spacer);

  var binderLink = document.createElement('small');
  binderLink.innerHTML = '<a href="https://mybinder.org/v2/gh/OcBSmith/PIE-Economics/main?labpath=practicas" target="_blank" style="color:#666">🎮 Binder (sliders)</a>';
  bar.appendChild(binderLink);

  content.insertBefore(bar, content.firstChild);

  // Button click handlers
  btnPy.addEventListener('click', function() { connectKernel('python'); });
  btnJl.addEventListener('click', function() { connectKernel('julia'); });

  // Store code blocks
  var codeBlocks = document.querySelectorAll('.md-content pre code');
  codeBlocks.forEach(function(block, i) {
    block.parentElement.setAttribute('data-code-idx', i);
  });
});

var ws = null;
var sessionId = null;
var execCount = 0;

function connectKernel(kernel) {
  var status = document.getElementById('kernel-status');
  var buttons = document.querySelectorAll('#kernel-bar button');
  buttons.forEach(function(b) { b.disabled = true; b.style.opacity = '0.5'; });

  status.textContent = '⏳ Contactando Binder...';
  status.style.color = '#D95319';

  // Step 1: Ask Binder to start a server for this repo
  var binderUrl = 'https://mybinder.org/build/gh/OcBSmith/PIE-Economics/main';
  fetch(binderUrl, {method: 'POST'})
    .then(function(r) { return r.json(); })
    .then(function(data) {
      status.textContent = '⏳ Arrancando servidor (1-2 min)...';
      // Poll until ready
      return waitForBinder(data.url, kernel);
    })
    .catch(function(err) {
      status.textContent = '❌ Error: ' + (err.message || 'Binder no disponible');
      status.style.color = '#D95319';
      buttons.forEach(function(b) { b.disabled = false; b.style.opacity = '1'; });
    });
}

function waitForBinder(url, kernel, attempt) {
  attempt = attempt || 0;
  var status = document.getElementById('kernel-status');

  return fetch(url + 'api')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.status === 'ready') {
        status.textContent = '⏳ Conectando kernel ' + kernel.toUpperCase() + '...';
        return launchKernel(url, kernel);
      } else if (attempt < 60) {
        return new Promise(function(resolve) {
          setTimeout(function() {
            status.textContent = '⏳ Arrancando servidor (' + Math.floor(attempt / 6) + ' min aprox)...';
            resolve(waitForBinder(url, kernel, attempt + 1));
          }, 10000);
        });
      } else {
        throw new Error('Timeout: el servidor no arrancó tras 10 min');
      }
    });
}

function launchKernel(serverUrl, kernel) {
  var status = document.getElementById('kernel-status');
  var kernelName = kernel === 'python' ? 'python3' : 'julia-1.10';

  // Create a kernel via Jupyter API
  return fetch(serverUrl + 'api/kernels', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: kernelName})
  })
    .then(function(r) { return r.json(); })
    .then(function(kernelInfo) {
      sessionId = kernelInfo.id;
      // Connect WebSocket to kernel
      var wsUrl = serverUrl.replace('https://', 'wss://').replace('http://', 'ws://');
      ws = new WebSocket(wsUrl + 'api/kernels/' + sessionId + '/channels');

      ws.onopen = function() {
        status.innerHTML = '🟢 Kernel ' + kernel.toUpperCase() + ' listo | <a href="#" id="reload-kernel" style="color:#004C97">🔄 Reiniciar</a>';
        status.style.color = '#2E7D32';
        document.getElementById('reload-kernel').addEventListener('click', function(e) {
          e.preventDefault(); location.reload();
        });
        addRunButtons();
      };

      ws.onmessage = function(event) {
        var msg = JSON.parse(event.data);
        var outDiv = document.querySelector('.thebe-output[data-session="' + sessionId + '"][data-exec="' + (execCount - 1) + '"]');
        if (!outDiv) return;

        if (msg.msg_type === 'stream') {
          outDiv.textContent = msg.content.text;
        } else if (msg.msg_type === 'execute_result' || msg.msg_type === 'display_data') {
          var data = msg.content.data;
          if (data && data['text/plain']) {
            outDiv.textContent = data['text/plain'];
          }
        } else if (msg.msg_type === 'error') {
          outDiv.textContent = msg.content.ename + ': ' + msg.content.evalue;
          outDiv.style.borderLeftColor = '#D95319';
          outDiv.style.color = '#D95319';
        }
      };

      ws.onerror = function() {
        status.textContent = '❌ Error de conexión WebSocket. El kernel puede estar caído.';
        status.style.color = '#D95319';
      };
    })
    .catch(function(err) {
      status.textContent = '❌ Error: ' + (err.message || 'No se pudo lanzar el kernel');
      status.style.color = '#D95319';
    });
}

function addRunButtons() {
  document.querySelectorAll('.md-content pre').forEach(function(pre) {
    if (pre.querySelector('.kernel-run')) return;

    var runBtn = document.createElement('button');
    runBtn.textContent = '▶ Run';
    runBtn.classList.add('kernel-run');
    runBtn.style.cssText = 'position:absolute; top:4px; right:4px; background:#004C97; color:white; border:none; padding:4px 12px; border-radius:3px; cursor:pointer; font-size:12px; font-weight:bold; z-index:10; opacity:0.9';
    runBtn.onmouseover = function() { this.style.opacity = '1'; };
    runBtn.onmouseout = function() { this.style.opacity = '0.9'; };

    runBtn.addEventListener('click', function() {
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('Kernel no conectado. Pulsa "Activar Python" o "Activar Julia" primero.');
        return;
      }

      var code = pre.querySelector('code').textContent;
      var outDiv = pre.nextElementSibling;
      if (!outDiv || !outDiv.classList.contains('thebe-output')) {
        outDiv = document.createElement('div');
        outDiv.classList.add('thebe-output');
        outDiv.style.cssText = 'background:#f8f8f8; border-left:3px solid #004C97; padding:8px 12px; margin-top:4px; margin-bottom:12px; font-family:monospace; font-size:13px; white-space:pre-wrap; max-height:400px; overflow:auto';
        pre.parentNode.insertBefore(outDiv, pre.nextSibling);
      }
      outDiv.textContent = '⏳ Ejecutando...';
      outDiv.style.borderLeftColor = '#004C97';
      outDiv.style.color = '#333';

      execCount++;
      outDiv.setAttribute('data-session', sessionId);
      outDiv.setAttribute('data-exec', execCount);

      var msg = {
        header: {
          msg_id: 'exec_' + execCount,
          username: 'alumno',
          session: sessionId,
          msg_type: 'execute_request',
          version: '5.3'
        },
        content: {
          code: code,
          silent: false,
          store_history: true,
          allow_stdin: false,
          stop_on_error: false
        },
        parent_header: {},
        metadata: {}
      };
      ws.send(JSON.stringify(msg));
    });

    pre.style.position = 'relative';
    pre.appendChild(runBtn);
  });
}
