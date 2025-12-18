document.addEventListener("DOMContentLoaded", function() {

    // --- 1. Flash Mesajlarını Otomatik Kapat ---
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            $(alert).fadeOut(300, function() {
                $(this).alert('close');
            });
        }, 5000);
    });

    // --- 2. CANLI ARAMA (Live Search) ---
    const searchInput = document.getElementById('search-input');
    const resultsArea = document.getElementById('results-area');

    if (searchInput && resultsArea) {
        let timeout = null;

        searchInput.addEventListener('input', function() {
            const query = this.value.trim();

            // Loading göstergesi
            if (query.length > 0) {
                resultsArea.innerHTML = '<div class="text-center mt-5"><i class="fas fa-spinner fa-spin fa-2x text-info"></i><p class="mt-3">Aranıyor...</p></div>';
            }

            // Performans için: Kullanıcı yazmayı bitirene kadar 300ms bekle (Debounce)
            clearTimeout(timeout);

            timeout = setTimeout(function() {
                if (query.length === 0) {
                    // Boşsa sayfayı yenile
                    window.location.href = window.location.pathname;
                    return;
                }

                // API'ye istek at
                fetch(`/api/search_books?q=${encodeURIComponent(query)}`)
                    .then(response => response.text()) // HTML cevabı al
                    .then(html => {
                        // Fade in animasyonu ile göster
                        resultsArea.style.opacity = '0';
                        setTimeout(function() {
                            resultsArea.innerHTML = html;
                            resultsArea.style.transition = 'opacity 0.3s';
                            resultsArea.style.opacity = '1';
                        }, 100);
                    })
                    .catch(error => {
                        console.error('Arama hatası:', error);
                        resultsArea.innerHTML = '<div class="alert alert-danger text-center">Arama sırasında bir hata oluştu.</div>';
                    });
            }, 300); // 300ms bekleme süresi
        });
    }

// --- 3. İADE VE FORM BUTONLARI ---
    // HATA ÇÖZÜMÜ: 'click' yerine 'submit' olayını dinliyoruz.
    $(document).on('submit', 'form', function() {
        const btn = $(this).find('button[type="submit"]');

        // Eğer form zaten gönderiliyorsa tekrar basılmasını engelle
        if (btn.prop('disabled')) {
            return false;
        }

        // Form geçerliyse işlemi başlat
        if (this.checkValidity()) {
            // 1. Butonun genişliğini sabitle (Titremeyi önler)
            const width = btn.outerWidth();
            btn.css('width', width + 'px');

            // 2. Butonun orijinal metnini sakla
            const originalText = btn.html();

            // 3. ÇOK ÖNEMLİ: Butonu hemen disable yapma, submit işleminin başlaması için
            // 50ms gecikme ver. Yoksa tarayıcı formu göndermez!
            setTimeout(function() {
                btn.prop('disabled', true);
                btn.html('<i class="fas fa-spinner fa-spin"></i>');
            }, 50);

            // 4. Emniyet Sübapı: Eğer sunucu 8 saniye cevap vermezse butonu tekrar aç
            setTimeout(function() {
                btn.prop('disabled', false);
                btn.html(originalText);
            }, 8000);
        }
    });

    // Modal kapandığında bazen ekran gri kalıyor (backdrop), bunu temizleyelim:
    $('.modal').on('hidden.bs.modal', function () {
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
        // Modal içindeki formları sıfırla
        $(this).find('form').trigger('reset');
    });
    
    // Form submit edildiğinde modal'ı kapat
    $(document).on('submit', 'form[id^="return-form-"]', function() {
        const modal = $(this).closest('.modal');
        setTimeout(function() {
            modal.modal('hide');
        }, 300);
    });

    // Modal açıldığında animasyon
    $('.modal').on('show.bs.modal', function() {
        $(this).find('.modal-dialog').css({
            'transform': 'scale(0.8)',
            'transition': 'transform 0.3s ease-out'
        });
    });

    $('.modal').on('shown.bs.modal', function() {
        $(this).find('.modal-dialog').css('transform', 'scale(1)');
    });

    // Modal kapanırken animasyon
    $('.modal').on('hide.bs.modal', function() {
        $(this).find('.modal-dialog').css('transform', 'scale(0.8)');
    });

    // --- 4. SMOOTH SCROLL ---
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // --- 5. KART HOVER EFEKTLERİ ---
    const bookCards = document.querySelectorAll('.book-card-item');
    bookCards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // --- 6. BUTON RIPPLE EFEKTİ ---
    document.querySelectorAll('.btn').forEach(function(button) {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(function() {
                ripple.remove();
            }, 600);
        });
    });

    // --- 7. TOOLTIP BAŞLATMA (Bootstrap) ---
    $('[data-toggle="tooltip"]').tooltip();

    // --- 8. SAYFA YÜKLENDİĞİNDE FADE IN ---
    document.body.style.opacity = '0';
    setTimeout(function() {
        document.body.style.transition = 'opacity 0.5s';
        document.body.style.opacity = '1';
    }, 100);
});

// --- AI ASİSTAN FONKSİYONLARI ---
function askAboutBook(bookName) {
    // AI asistan sayfasına yönlendir ve kitap hakkında soru sor
    const question = `${bookName} hakkında bilgi verir misin?`;
    window.location.href = `/ai/assistant?q=${encodeURIComponent(question)}`;
}