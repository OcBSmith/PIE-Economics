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

  // Binder's launch endpoint is a GET that streams Server-Sent Events
  // (phase: waiting/building/launching/ready), not a POST returning a
  // single JSON object. POSTing to it returns an HTML error page, which
  // is why r.json() used to fail with "Unexpected token '<'".
  var binderUrl = 'https://mybinder.org/build/gh/OcBSmith/PIE-Economics/main';
  var es = new EventSource(binderUrl);

  es.onmessage = function(event) {
    var data;
    try {
      data = JSON.parse(event.data);
    } catch (e) {
      return;
    }

    if (data.phase === 'ready') {
      es.close();
      status.textContent = '⏳ Conectando kernel ' + kernel.toUpperCase() + '...';
      launchKernel(data.url, data.token, kernel);
    } else if (data.phase === 'failed') {
      es.close();
      status.textContent = '❌ Binder no pudo construir el entorno: ' + (data.message || '');
      status.style.color = '#D95319';
      buttons.forEach(function(b) { b.disabled = false; b.style.opacity = '1'; });
    } else {
      status.textContent = '⏳ ' + (data.message || data.phase || 'Arrancando...');
    }
  };

  es.onerror = function() {
    es.close();
    status.textContent = '❌ Error de conexión con Binder';
    status.style.color = '#D95319';
    buttons.forEach(function(b) { b.disabled = false; b.style.opacity = '1'; });
  };
}

function launchKernel(serverUrl, token, kernel) {
  var status = document.getElementById('kernel-status');
  var kernelName = kernel === 'python' ? 'python3' : 'julia-1.10';
  var tokenParam = 'token=' + encodeURIComponent(token);

  // Create a kernel via Jupyter API
  return fetch(serverUrl + 'api/kernels?' + tokenParam, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: kernelName})
  })
    .then(function(r) {
      if (!r.ok) {
        throw new Error('No se pudo crear el kernel (HTTP ' + r.status + ')');
      }
      return r.json();
    })
    .then(function(kernelInfo) {
      sessionId = kernelInfo.id;
      // Connect WebSocket to kernel
      var wsUrl = serverUrl.replace('https://', 'wss://').replace('http://', 'ws://');
      ws = new WebSocket(wsUrl + 'api/kernels/' + sessionId + '/channels?' + tokenParam);

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
  // mkdocs-jupyter renders notebook *input* cells as
  // <div class="highlight-ipynb hl-python|hl-julia"><pre>...</pre></div>
  // (Pygments puts the code directly in <pre>, no <code> wrapper) and
  // notebook *output* (already-printed text) as a bare <pre> with no
  // such wrapping div. Scoping to ".highlight-ipynb pre" targets only
  // the executable input cells, not the saved output text.
  document.querySelectorAll('.md-content .highlight-ipynb pre').forEach(function(pre) {
    if (pre.querySelector('.kernel-run')) return;

    // Capture the code now, before the button is appended as a child of
    // `pre` below — otherwise pre.textContent at click time would also
    // include the button's own "▶ Run" label, sent to the kernel as if
    // it were part of the code.
    var code = pre.textContent;

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
