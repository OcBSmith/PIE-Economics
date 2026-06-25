// Live code execution for MACRO-AI-COMP.
//
// Python runs locally in the browser via Pyodide (Python compiled to
// WebAssembly) -- no server, no Binder, no network round-trip per cell.
// Julia has no comparable production-ready WASM runtime, so it still
// goes through a Binder-launched Jupyter kernel over WebSocket, exactly
// as before.

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
  btnPy.addEventListener('click', function() { connectPython(); });
  btnJl.addEventListener('click', function() { connectKernel('julia'); });
});

var ws = null;
var sessionId = null;
var execCount = 0;
var activeKernel = null; // 'python' (Pyodide, local) or 'julia' (Binder)
var pyodide = null;
var pyodideLoading = null;

function setButtonsDisabled(disabled) {
  document.querySelectorAll('#kernel-bar button').forEach(function(b) {
    b.disabled = disabled;
    b.style.opacity = disabled ? '0.5' : '1';
  });
}

// ---------------------------------------------------------------------
// Python: Pyodide, runs locally in the browser (no Binder involved)
// ---------------------------------------------------------------------

var PYODIDE_VERSION = 'v0.26.4';
var PYODIDE_INDEX_URL = 'https://cdn.jsdelivr.net/pyodide/' + PYODIDE_VERSION + '/full/';

// cvxpy needs compiled solvers (ECOS/SCS/OSQP) with no WebAssembly build,
// so it cannot run under Pyodide. Used only in P3/P4/P5 (consumption
// savings/leisure, fiscal policy) as an alternative to the fsolve-based
// solver -- those specific cells get a friendly message instead of a
// confusing Python traceback.
var CVXPY_RE = /\bcvxpy\b/;

function loadPyodideScript() {
  if (window.loadPyodide) return Promise.resolve();
  return new Promise(function(resolve, reject) {
    var script = document.createElement('script');
    script.src = PYODIDE_INDEX_URL + 'pyodide.js';
    script.onload = resolve;
    script.onerror = function() { reject(new Error('No se pudo cargar pyodide.js')); };
    document.head.appendChild(script);
  });
}

function connectPython() {
  var status = document.getElementById('kernel-status');
  setButtonsDisabled(true);
  status.textContent = '⏳ Cargando Python en tu navegador (Pyodide)...';
  status.style.color = '#D95319';

  if (!pyodideLoading) {
    pyodideLoading = loadPyodideScript()
      .then(function() {
        return loadPyodide({indexURL: PYODIDE_INDEX_URL});
      })
      .then(function(py) {
        pyodide = py;
        status.textContent = '⏳ Instalando numpy/scipy/matplotlib...';
        return pyodide.loadPackage(['numpy', 'scipy', 'matplotlib']);
      })
      .then(function() {
        // Agg: render to an in-memory buffer, no GUI event loop. We grab
        // the figures ourselves after each cell via _capture_figures().
        return pyodide.runPythonAsync(
          'import matplotlib\n' +
          'matplotlib.use("AGG")\n' +
          'import matplotlib.pyplot as plt, base64, io\n' +
          'def _capture_figures():\n' +
          '    figs = []\n' +
          '    for n in plt.get_fignums():\n' +
          '        buf = io.BytesIO()\n' +
          '        plt.figure(n).savefig(buf, format="png", bbox_inches="tight")\n' +
          '        figs.append(base64.b64encode(buf.getvalue()).decode("ascii"))\n' +
          '    plt.close("all")\n' +
          '    return figs\n'
        );
      });
  }

  pyodideLoading
    .then(function() {
      activeKernel = 'python';
      status.innerHTML = '🟢 Python listo (en tu navegador) | <a href="#" id="reload-kernel" style="color:#004C97">🔄 Reiniciar</a>';
      status.style.color = '#2E7D32';
      document.getElementById('reload-kernel').addEventListener('click', function(e) {
        e.preventDefault(); location.reload();
      });
      addRunButtons();
    })
    .catch(function(err) {
      status.textContent = '❌ Error cargando Python: ' + (err.message || err);
      status.style.color = '#D95319';
      pyodideLoading = null;
      setButtonsDisabled(false);
    });
}

function runPythonCell(code, outDiv) {
  outDiv.textContent = '';
  pyodide.setStdout({batched: function(msg) { outDiv.textContent += msg + '\n'; }});
  pyodide.setStderr({batched: function(msg) { outDiv.textContent += msg + '\n'; }});

  return pyodide.runPythonAsync(code)
    .then(function() {
      return pyodide.runPythonAsync('_capture_figures()');
    })
    .then(function(figsProxy) {
      var figs = figsProxy.toJs();
      figsProxy.destroy();
      figs.forEach(function(b64) {
        var img = document.createElement('img');
        img.src = 'data:image/png;base64,' + b64;
        img.style.maxWidth = '100%';
        outDiv.appendChild(img);
      });
      if (!outDiv.textContent && figs.length === 0) {
        outDiv.textContent = '(sin salida)';
      }
    })
    .catch(function(err) {
      outDiv.textContent += (err.message || String(err));
      outDiv.style.borderLeftColor = '#D95319';
      outDiv.style.color = '#D95319';
    });
}

// ---------------------------------------------------------------------
// Julia: unchanged -- Binder-launched Jupyter kernel over WebSocket
// ---------------------------------------------------------------------

function connectKernel(kernel) {
  var status = document.getElementById('kernel-status');
  setButtonsDisabled(true);

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
      setButtonsDisabled(false);
    } else {
      status.textContent = '⏳ ' + (data.message || data.phase || 'Arrancando...');
    }
  };

  es.onerror = function() {
    es.close();
    status.textContent = '❌ Error de conexión con Binder';
    status.style.color = '#D95319';
    setButtonsDisabled(false);
  };
}

function launchKernel(serverUrl, token, kernel) {
  var status = document.getElementById('kernel-status');
  var kernelName = 'julia-1.10';
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
        activeKernel = 'julia';
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
      setButtonsDisabled(false);
    });
}

// ---------------------------------------------------------------------
// Shared: "▶ Run" buttons on every input cell, dispatching to whichever
// kernel (Pyodide or Binder/Julia) is currently active.
// ---------------------------------------------------------------------

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
    // `pre` below -- otherwise pre.textContent at click time would also
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
      if (!activeKernel) {
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

      if (activeKernel === 'python') {
        if (CVXPY_RE.test(code)) {
          outDiv.textContent = 'Esta celda usa cvxpy, que no está disponible en el modo de ejecución en el navegador (sin build para WebAssembly). Pruébala en Binder (🎮, arriba a la derecha) o en tu entorno local.';
          outDiv.style.borderLeftColor = '#D95319';
          outDiv.style.color = '#D95319';
          return;
        }
        runPythonCell(code, outDiv);
        return;
      }

      // Julia path: unchanged Binder/WebSocket flow.
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('Kernel no conectado. Pulsa "Activar Julia" primero.');
        return;
      }

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
