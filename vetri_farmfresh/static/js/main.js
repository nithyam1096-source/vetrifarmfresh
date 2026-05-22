document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            setTimeout(function() {
                bsAlert.close();
            }, 5000);
        });
    }, 100);

    document.querySelectorAll('input[type="number"]').forEach(function(input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                this.form.submit();
            }
        });
    });

    let productCards = document.querySelectorAll('.product-card');
    productCards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    let slotRadios = document.querySelectorAll('input[name="delivery_slot"]');
    slotRadios.forEach(function(radio) {
        radio.addEventListener('change', function() {
            document.querySelectorAll('input[name="delivery_slot"] + label').forEach(function(label) {
                label.classList.remove('border-success', 'bg-success', 'bg-opacity-10');
            });
            if (this.checked) {
                this.nextElementSibling.classList.add('border-success', 'bg-success', 'bg-opacity-10');
            }
        });
    });
});
