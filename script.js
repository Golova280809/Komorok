
// Инициализация EmailJS
(function() {
    emailjs.init("IQvj7D0L_8dJYjJL");
})();

// Форма на странице "в разработке"
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const status = document.getElementById('status');
        status.textContent = 'Отправка...';
        
        emailjs.send("service_b9h18pb", "template_rh9kqaq", {
            from_name: document.getElementById('name').value,
            reply_to: document.getElementById('email').value,
            message: document.getElementById('message').value
        }).then(() => {
            status.textContent = '✓ Сообщение отправлено!';
            status.style.color = '#4CAF50';
            this.reset();
        }).catch((err) => {
            status.textContent = 'Ошибка: ' + err.text;
            status.style.color = '#e94560';
        });
    });
}

// Форма в футере
const footerForm = document.getElementById('footerContact');
if (footerForm) {
    footerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const status = document.getElementById('footerStatus');
        const inputs = this.querySelectorAll('input');
        
        status.textContent = '...';
        emailjs.send("service_b9h18pb", "template_rh9kqaq", {
            from_name: inputs[0].value,
            reply_to: inputs[1].value,
            message: "Сообщение из футера"
        }).then(() => {
            status.textContent = '✓ Отправлено!';
            this.reset();
        }).catch(() => {
            status.textContent = 'Ошибка';
        });
    });
}