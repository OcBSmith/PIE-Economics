// Thebe configuration for MACRO-AI-COMP
// Modern Thebe API (v0.9+) — provides kernel activation and live code execution

document.addEventListener('DOMContentLoaded', function() {
  // Only run on notebook pages
  var hasCode = document.querySelector('.md-content pre');
  if (!hasCode) return;

  var content = document.querySelector('.md-content__inner');
  if (!content) return;

  // Build kernel selector bar
  var bar = document.createElement('div');
  bar.id = 'thebe-bar';
  bar.style.cssText = 'background:#f0f4ff; border:1px solid #d0d8f0; border-radius:6px; padding:12px 16px; margin-bottom:20px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; font-size:14px; font-family: system-ui, sans-serif;';
  bar.innerHTML =
    '<strong style="color:#004C97">🔌 Ejecutar código en vivo:</strong>' +
    '<button id="btn-python" style="background:#004C97;color:white;border:none;padding:8px 18px;border-radius:4px;cursor:pointer;font-weight:bold;font-size:14px">🐍 Activar Python</button>' +
    '<button id="btn-julia" style="background:#8EAD3A;color:white;border:none;padding:8px 18px;border-radius:4px;cursor:pointer;font-weight:bold;font-size:14px">🔢 Activar Julia</button>' +
    '<span id="thebe-status" style="color:#666;margin-left:8px;font-size:13px"></span>' +
    '<span style="flex:1"></span>' +
    '<small><a href="https://mybinder.org/v2/gh/OcBSmith/PIE-Economics/main?labpath=practicas" target="_blank" style="color:#666;text-decoration:underline">🎮 Binder (sliders)</a></small>';
  content.insertBefore(bar, content.firstChild);

  // Store original HTML content of all code blocks
  var codeBlocks = document.querySelectorAll('.md-content pre code');
  codeBlocks.forEach(function(block, i) {
    block.parentElement.setAttribute('data-code-index', i);
  });
});

var thebeInstance = null;

function activateThebe(kernel) {
  var status = document.getElementById('thebe-status');
  var btnPy = document.getElementById('btn-python');
  var btnJl = document.getElementById('btn-julia');
  
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
  document.head.appendChild(script);
}

function initThebe(kernel) {
  var status = document.getElementById('thebe-status');
  
  thebeInstance = new Thebe({
    kernelOptions: {
      name: kernel === 'python' ? 'python3' : 'julia-1.10',
      kernelName: kernel === 'python' ? 'python3' : 'julia-1.10',
      path: kernel === 'python' ? 'practicas/01-is-lm-dinamico' : '.',
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
      status.innerHTML = '🟢 Kernel ' + kernel.toUpperCase() + ' listo | <a href="#" onclick="location.reload()" style="color:#004C97">🔄 Reiniciar</a>';
      status.style.color = '#2E7D32';
    } else if (data.status === 'failed') {
      status.innerHTML = '❌ Error al conectar. <a href="#" onclick="location.reload()" style="color:#D95319">Reintentar</a>';
      status.style.color = '#D95319';
    }
  });

  thebeInstance.on('error', function(evt, error) {
    status.innerHTML = '❌ Error: ' + (error.message || 'desconocido') + ' <a href="#" onclick="location.reload()" style="color:#D95319">Reintentar</a>';
    status.style.color = '#D95319';
  });

  // Mount Thebe on all code blocks
  document.querySelectorAll('.md-content pre').forEach(function(pre) {
    pre.classList.add('thebe-code');
  });

  thebeInstance.mount();
  
  // Add Run buttons to code cells
  setTimeout(function() {
    document.querySelectorAll('.thebe-code').forEach(function(pre) {
      var runBtn = document.createElement('button');
      runBtn.textContent = '▶ Run';
      runBtn.style.cssText = 'position:absolute; top:4px; right:4px; background:#004C97; color:white; border:none; padding:4px 12px; border-radius:3px; cursor:pointer; font-size:12px; font-weight:bold; z-index:10';
      runBtn.onclick = function() {
        var code = pre.querySelector('code').textContent;
        thebeInstance.execute(code, function(output) {
          var outDiv = pre.nextElementSibling;
          if (!outDiv || !outDiv.classList.contains('thebe-output')) {
            outDiv = document.createElement('div');
            outDiv.classList.add('thebe-output');
            outDiv.style.cssText = 'background:#f8f8f8; border-left:3px solid #004C97; padding:8px 12px; margin-top:4px; margin-bottom:12px; font-family:monospace; font-size:13px; white-space:pre-wrap; max-height:400px; overflow:auto';
            pre.parentNode.insertBefore(outDiv, pre.nextSibling);
          }
          if (output.text) outDiv.textContent = output.text;
          if (output.error) {
            outDiv.textContent = output.error;
            outDiv.style.borderLeftColor = '#D95319';
            outDiv.style.color = '#D95319';
          }
        });
      };
      pre.style.position = 'relative';
      pre.appendChild(runBtn);
    });
  }, 3000);
}
