from library import app

if __name__ == '__main__':
    # use_reloader=False -> Otomatik yenilemeyi kapat (Debugger şaşırmasın)
    # debug=True -> Hata detaylarını görmeye devam et
    app.run(debug=True, use_reloader=False)