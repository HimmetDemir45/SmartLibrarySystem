document.addEventListener("DOMContentLoaded", function() {

    // --- 1. Flash Mesajlarını Otomatik Kapat ---
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            $(alert).alert('close');
        }, 5000);
    });

    // --- 2. CANLI ARAMA (Live Search) ---
    const searchInput = document.getElementById('search-input');
    const resultsArea = document.getElementById('results-area');

    if (searchInput && resultsArea) {
        let timeout = null;

        searchInput.addEventListener('input', function() {
            const query = this.value.trim();

            // Performans için: Kullanıcı yazmayı bitirene kadar 300ms bekle (Debounce)
            clearTimeout(timeout);

            timeout = setTimeout(function() {
                // API'ye istek at
                fetch(`/api/search_books?q=${encodeURIComponent(query)}`)
                    .then(response => response.text()) // HTML cevabı al
                    .then(html => {
                        // Gelen HTML'i sayfaya bas
                        resultsArea.innerHTML = html;
                    })
                    .catch(error => console.error('Arama hatası:', error));
            }, 300); // 300ms bekleme süresi
        });
    }
});