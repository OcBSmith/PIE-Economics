// Thebe configuration for MACRO-AI-COMP
// Provides kernel activation and live code execution directly in the page

document.addEventListener('DOMContentLoaded', function() {
  // Only run on notebook pages (they have code blocks in content)
  var hasCode = document.querySelector('.md-content pre');
  if (!hasCode) return;

  var content = document.querySelector('.md-content__inner');
  if (!content) return;

  // Build kernel selector bar
  var bar = document.createElement('div');
  bar.id = 'thebe-bar';
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
  status.id = 'thebe-status';
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
  btnPy.addEventListener('click', function() { activateThebe('python'); });
  btnJl.addEventListener('click', function() { activateThebe('julia'); });

  // Store code block indices
  var codeBlocks = document.querySelectorAll('.md-content pre code');
  codeBlocks.forEach(function(block, i) {
    block.parentElement.setAttribute('data-code-index', i);
  });
});

var thebeInstance = null;

function activateThebe(kernel) {
  var status = document.getElementById('thebe-status');
  var btnPy = document.querySelector('#thebe-bar button:nth-child(2)');
  var btnJl = document.querySelector('#thebe-bar button:nth-child(3)');

  status.textContent = '⏳ Conectando a Binder (1-2 min la primera vez)...';
  status.style.color = '#D95319';
  btnPy.disabled = true;
  btnJl.disabled = true;
  btnPy.style.opacity = '0.5';
  btnJl.style.opacity = '0.5';

  // Dynamically load Thebe from CDN
  var script = document.createElement('script');
  script.src = 'https://unpkg.com/thebe@latest/lib/index.js';
  script.onload = function() {
    initThebe(kernel);
  };
  script.onerror = function() {
    status.textContent = '❌ Error al cargar Thebe (problema de red).';
    status.style.color = '#D95319';
    btnPy.disabled = false;
    btnJl.disabled = false;
    btnPy.style.opacity = '1';
    btnJl.style.opacity = '1';
  };
  document.head.appendChild(script);
}

function initThebe(kernel) {
  var status = document.getElementById('thebe-status');

  thebeInstance = new Thebe({
    kernelOptions: {
      name: kernel === 'python' ? 'python3' : 'julia-1.10',
      kernelName: kernel === 'python' ? 'python3' : 'julia-1.10',
      path: '.',
    },
    binderOptions: {
      repo: 'OcBSmith/PIE-Economics',
      ref: 'main',
      repoProvider: 'github',
    },
    codeMirrorConfig: {
      theme: 'default',
      lineNumbers: true,
    },
  });

  thebeInstance.on('status', function(evt, data) {
    if (data.status === 'building') {
      status.textContent = '⏳ Binder construyendo imagen...';
    } else if (data.status === 'launching') {
      status.textContent = '⏳ Arrancando kernel ' + kernel.toUpperCase() + '...';
    } else if (data.status === 'ready') {
      status.innerHTML = '🟢 Kernel ' + kernel.toUpperCase() + ' listo | <a href="#" id="reload-link" style="color:#004C97">🔄 Reiniciar</a>';
      status.style.color = '#2E7D32';
      document.getElementById('reload-link').addEventListener('click', function(e) {
        e.preventDefault();
        location.reload();
      });
    } else if (data.status === 'failed') {
      status.innerHTML = '❌ Error al conectar. <a href="#" id="retry-link" style="color:#D95319">Reintentar</a>';
      status.style.color = '#D95319';
      document.getElementById('retry-link').addEventListener('click', function(e) {
        e.preventDefault();
        location.reload();
      });
    }
  });

  thebeInstance.on('error', function(evt, error) {
    status.textContent = '❌ Error: ' + (error.message || 'desconocido');
    status.style.color = '#D95319';
  });

  // Mount Thebe on all code blocks
  document.querySelectorAll('.md-content pre').forEach(function(pre) {
    pre.classList.add('thebe-code');
  });

  thebeInstance.mount();

  // Add Run buttons to code cells after Thebe has initialized
  setTimeout(function() {
    addRunButtons();
  }, 4000);
}

function addRunButtons() {
  document.querySelectorAll('.thebe-code').forEach(function(pre) {
    // Skip if already has a button
    if (pre.querySelector('.thebe-run')) return;

    var runBtn = document.createElement('button');
    runBtn.textContent = '▶ Run';
    runBtn.classList.add('thebe-run');
    runBtn.style.cssText = 'position:absolute; top:4px; right:4px; background:#004C97; color:white; border:none; padding:4px 12px; border-radius:3px; cursor:pointer; font-size:12px; font-weight:bold; z-index:10';
    runBtn.addEventListener('click', function() {
      var code = pre.querySelector('code').textContent;
      // Find or create output div
      var outDiv = pre.nextElementSibling;
      if (!outDiv || !outDiv.classList.contains('thebe-output')) {
        outDiv = document.createElement('div');
        outDiv.classList.add('thebe-output');
        outDiv.style.cssText = 'background:#f8f8f8; border-left:3px solid #004C97; padding:8px 12px; margin-top:4px; margin-bottom:12px; font-family:monospace; font-size:13px; white-space:pre-wrap; max-height:400px; overflow:auto';
        if (pre.nextSibling) {
          pre.parentNode.insertBefore(outDiv, pre.nextSibling);
        } else {
          pre.parentNode.appendChild(outDiv);
        }
      }
      outDiv.textContent = '⏳ Ejecutando...';
      outDiv.style.borderLeftColor = '#004C97';
      outDiv.style.color = '#333';

      // Try using Thebe API, fall back to raw kernel
      if (thebeInstance && thebeInstance.session && thebeInstance.session.kernel) {
        var future = thebeInstance.session.kernel.requestExecute({ code: code });
        future.onDone = function() {
          outDiv.textContent = '✅ Ejecutado (ver output en consola del navegador)';
        };
        future.onIOPub = function(msg) {
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
      } else {
        outDiv.textContent = '❌ Kernel no disponible. Pulsa "Activar Python" o "Activar Julia" primero.';
        outDiv.style.borderLeftColor = '#D95319';
        outDiv.style.color = '#D95319';
      }
    });
    pre.style.position = 'relative';
    pre.appendChild(runBtn);
  });
}
