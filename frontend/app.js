// Frontend estático (sem build): fala com a API na mesma origem.
// Rate-limit (429) e validação (400) já vêm no envelope da API.
(function () {
  "use strict";

  const form = document.getElementById("shorten-form");
  const urlInput = document.getElementById("url-input");
  const submitBtn = document.getElementById("submit-btn");
  const errorMsg = document.getElementById("error-msg");
  const result = document.getElementById("result");
  const shortLink = document.getElementById("short-link");
  const captchaNote = document.getElementById("captcha-note");

  let widgetId = null;
  let captchaEnabled = false;
  let captchaReady = false;

  function showError(message) {
    errorMsg.textContent = message;
    errorMsg.hidden = false;
    result.hidden = true;
  }

  function showResult(shortCode) {
    const href = window.location.origin + "/" + shortCode;
    shortLink.href = href;
    shortLink.textContent = href;
    result.hidden = false;
    errorMsg.hidden = true;
  }

  function loadTurnstile(siteKey) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
      script.async = true;
      script.onload = () => {
        let attempts = 0;
        const timer = setInterval(() => {
          attempts += 1;
          if (window.turnstile) {
            clearInterval(timer);
            widgetId = window.turnstile.render("#captcha-widget", { sitekey: siteKey });
            captchaReady = true;
            resolve();
          } else if (attempts > 100) {
            clearInterval(timer);
            reject(new Error("captcha não carregou (rede ou bloqueador?)"));
          }
        }, 100);
      };
      script.onerror = () => reject(new Error("Falha ao carregar o captcha"));
      document.head.appendChild(script);
      captchaEnabled = true;
    });
  }

  async function initCaptcha() {
    try {
      const res = await fetch("/api/config");
      const cfg = await res.json();
      if (cfg.turnstile_site_key) {
        await loadTurnstile(cfg.turnstile_site_key);
      } else {
        captchaNote.hidden = false;
      }
    } catch (err) {
      showError("Não foi possível carregar a configuração (" + err.message + ")");
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorMsg.hidden = true;
    submitBtn.disabled = true;
    try {
      let token = null;
      if (captchaEnabled) {
        if (!captchaReady || !window.turnstile) {
          showError("Aguarde o captcha carregar e tente de novo.");
          return;
        }
        token = window.turnstile.getResponse(widgetId);
        if (!token) {
          showError("Confirme o captcha antes de encurtar.");
          return;
        }
      }
      const res = await fetch("/urls/shorten", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlInput.value, captcha_token: token }),
      });
      const body = await res.json();
      if (res.status === 201) {
        showResult(body.data.short_code);
      } else if (res.status === 429) {
        showError("Muitas tentativas. Aguarde um pouco e tente de novo.");
      } else {
        showError(body.message || ("Erro inesperado (" + res.status + ")"));
      }
    } catch (err) {
      showError("Falha de rede: " + err.message);
    } finally {
      submitBtn.disabled = false;
      if (captchaReady && window.turnstile && widgetId !== null) {
        window.turnstile.reset(widgetId);
      }
    }
  });

  initCaptcha();
})();
