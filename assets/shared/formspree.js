(function () {
  function getThankYouUrl(form) {
    var nextInput = form.querySelector('input[name="_next"]');
    if (nextInput && nextInput.value) return nextInput.value;
    return "/obrigado.html";
  }

  function setSubmitting(button, submitting) {
    if (!button) return;
    var label = button.querySelector("span");
    button.disabled = submitting;
    if (!label) return;
    if (submitting) {
      if (!label.dataset.originalText) {
        label.dataset.originalText = label.textContent;
      }
      label.textContent = "Enviando…";
      return;
    }
    if (label.dataset.originalText) {
      label.textContent = label.dataset.originalText;
    }
  }

  function toggleMessage(box, show) {
    if (!box) return;
    box.classList.toggle("hidden", !show);
  }

  function initContactForms() {
    document
      .querySelectorAll('form.contact-form, form[action*="formspree.io/f/"]')
      .forEach(function (form) {
        if (form.dataset.formspreeInit === "true") return;
        form.dataset.formspreeInit = "true";

        form.addEventListener("submit", function (event) {
          event.preventDefault();

          var submitButton = form.querySelector('button[type="submit"]');
          var errorBox = form.querySelector(".form-error");
          var successBox = form.querySelector(".form-success");
          var thankYouUrl = getThankYouUrl(form);

          toggleMessage(errorBox, false);
          toggleMessage(successBox, false);
          setSubmitting(submitButton, true);

          fetch(form.action, {
            method: "POST",
            body: new FormData(form),
            headers: { Accept: "application/json" },
          })
            .then(function (response) {
              if (response.ok) {
                window.location.href = thankYouUrl;
                return;
              }
              return response.json().then(function (data) {
                throw new Error(
                  (data && (data.error || data.message)) ||
                    "Não foi possível enviar o formulário."
                );
              });
            })
            .catch(function () {
              toggleMessage(errorBox, true);
              setSubmitting(submitButton, false);
            });
        });
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initContactForms);
  } else {
    initContactForms();
  }
})();
