const qs = s => document.querySelector(s);
const form = qs('#loginForm');
const email = qs('#email');
const password = qs('#password');
const toggle = qs('#togglePwd');
const emailError = qs('#emailError');
const passwordError = qs('#passwordError');

function showError(el, msg){
  el.textContent = msg || '';
  if (msg) el.previousElementSibling?.querySelector('input')?.setAttribute('aria-invalid','true');
}
function clearError(el){
  el.textContent = '';
  el.previousElementSibling?.querySelector('input')?.removeAttribute('aria-invalid');
}

toggle.addEventListener('click', () => {
  const isPwd = password.type === 'password';
  password.type = isPwd ? 'text' : 'password';
  toggle.textContent = isPwd ? 'Hide' : 'Show';
  toggle.setAttribute('aria-pressed', String(isPwd));
  password.focus();
});

email.addEventListener('input', () => clearError(emailError));
password.addEventListener('input', () => clearError(passwordError));

form.addEventListener('submit', (ev) => {
  clearError(emailError); clearError(passwordError);
  let valid = true;

  const mail = email.value.trim();
  if (!mail){
    showError(emailError, "Email is required.");
    valid = false;
  } else {
    const emailPat = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    if (!emailPat.test(mail)){
      showError(emailError, "Enter a valid email address.");
      valid = false;
    }
  }

  const pw = password.value;
  if (!pw){
    showError(passwordError, "Password is required.");
    valid = false;
  } else if (pw.length < 8){
    showError(passwordError, "Password must be at least 8 characters.");
    valid = false;
  }

  if (!valid){
    ev.preventDefault();
    const firstErr = form.querySelector('.error:not(:empty)');
    if (firstErr){
      const input = firstErr.previousElementSibling?.querySelector('input');
      if (input) input.focus();
    }
  }
});