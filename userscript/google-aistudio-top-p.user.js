// ==UserScript==
// @name         Google AI Studio - Deslizador Gris Nativo Top P (0.95)
// @namespace    https://github.com/adri22235
// @version      4.0
// @description  Inserta la barra deslizante gris nativa de Top P dentro de la barra lateral (Advanced settings) de AI Studio e inyecta top_p=0.95.
// @author       Adrián & Debian 12 Crew
// @match        https://aistudio.google.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=aistudio.google.com
// @run-at       document-start
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    let savedTopP = localStorage.getItem('ai_studio_native_top_p') || '0.95';

    // Interceptor de red para forzar topP en cada llamada
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        let [resource, config] = args;
        if (config && config.body && typeof config.body === 'string') {
            try {
                let data = JSON.parse(config.body);
                const currentVal = parseFloat(localStorage.getItem('ai_studio_native_top_p') || '0.95');

                function forceTopP(obj) {
                    if (!obj || typeof obj !== 'object') return;
                    if (obj.generationConfig) obj.generationConfig.topP = currentVal;
                    if ('topP' in obj) obj.topP = currentVal;
                    for (let k in obj) {
                        if (typeof obj[k] === 'object') forceTopP(obj[k]);
                    }
                }

                if (data.contents || data.generationConfig || (typeof resource === 'string' && resource.includes('generate'))) {
                    if (!data.generationConfig) data.generationConfig = {};
                    data.generationConfig.topP = currentVal;
                    forceTopP(data);
                    config.body = JSON.stringify(data);
                    console.log(`%c[Top P Nativo] Inyectado -> topP = ${currentVal}`, 'color: #c4c7c5; font-weight: bold;');
                }
            } catch (e) {}
        }
        return originalFetch.apply(this, [resource, config]);
    };

    // Estilos CSS de la rueda gris
    const style = document.createElement('style');
    style.textContent = `
        .native-topp-container { padding: 8px 0 16px 0; font-family: 'Google Sans', Roboto, sans-serif; color: #c4c7c5; user-select: none; }
        .native-topp-header { display: flex; justify-content: space-between; align-items: center; font-size: 13px; font-weight: 400; margin-bottom: 6px; }
        .native-topp-header span:first-child { color: #e3e3e3; }
        .native-topp-header .val-display { color: #c4c7c5; font-variant-numeric: tabular-nums; }
        .native-topp-slider { -webkit-appearance: none; appearance: none; width: 100%; height: 4px; border-radius: 2px; background: #444746; outline: none; cursor: pointer; margin: 6px 0; }
        .native-topp-slider::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 14px; height: 14px; border-radius: 50%; background: #c4c7c5; cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.4); }
        .native-topp-slider::-webkit-slider-thumb:hover { background: #ffffff; transform: scale(1.15); }
        .native-topp-slider::-moz-range-thumb { width: 14px; height: 14px; border-radius: 50%; background: #c4c7c5; border: none; cursor: pointer; }
    `;
    document.head.appendChild(style);

    // Inyector en Advanced Settings
    function injectNativeSlider() {
        if (document.getElementById('native-topp-row')) return;
        const labels = Array.from(document.querySelectorAll('label, div, span'));
        const outputLengthEl = labels.find(el => el.textContent && el.textContent.trim() === 'Output length');
        if (!outputLengthEl) return;

        let parentRow = outputLengthEl.closest('.setting-row, mat-form-field, .form-field') || outputLengthEl.parentElement.parentElement;
        if (!parentRow) parentRow = outputLengthEl.parentElement;

        const container = document.createElement('div');
        container.id = 'native-topp-row';
        container.className = 'native-topp-container';

        const header = document.createElement('div');
        header.className = 'native-topp-header';
        header.innerHTML = `<span>Top P</span><span class="val-display" id="native-topp-val">${savedTopP}</span>`;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '0.00';
        slider.max = '1.00';
        slider.step = '0.01';
        slider.value = savedTopP;
        slider.className = 'native-topp-slider';

        slider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value).toFixed(2);
            document.getElementById('native-topp-val').textContent = val;
            localStorage.setItem('ai_studio_native_top_p', val);
        });

        container.appendChild(header);
        container.appendChild(slider);
        parentRow.insertAdjacentElement('afterend', container);
    }
    setInterval(injectNativeSlider, 500);
})();
