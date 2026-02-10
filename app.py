from flask import Flask, render_template, abort, request, session, redirect, url_for
import random
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'chiave_segreta_molto_meme'

# Funzione per ottenere tutte le foto di un modello
def get_model_photos(nome_modello):
    """Restituisce la lista di foto per un modello specifico"""
    foto_dir = Path('static/foto_unifocus')
    if not foto_dir.exists():
        return []
    
    # Cerca file con pattern foto_[nome][numero].jpg
    pattern = f"foto_{nome_modello.lower()}"
    photos = []
    
    for file in sorted(foto_dir.glob(f"{pattern}*.jpg")):
        photos.append(f"foto_unifocus/{file.name}")
    
    return photos if photos else ["foto_unifocus/default.jpg"]  # Fallback

GIGOLO_DB = {
    "1": {
        "nome": "Fra",
        "tagline": "Come Dr Jekyll e Mr. hyde. Di giorno ingegnere, di notte... Batman ",
        "specialita": "Esame oCULIstico gratuito",
        "disponibilita": "H24",
        "prezzo": 500,
        "foto": "foto_unifocus/foto_fra1.jpg",  # Foto principale per la home
        "foto_multiple": [],  # Verrà popolato dinamicamente
        "recensioni": [
            {"autore": "Sofia, 28", "voto": 5, "testo": "Ha debuggato il mio cuore e fixato la mia autostima. 10/10 consigliato!", "data": "15 Gen 2025"},
            {"autore": "Martina, 31", "voto": 5, "testo": "Finalmente qualcuno che capisce i miei loop infiniti emotivi. Tornerò sicuramente!", "data": "8 Gen 2025"},
            {"autore": "Chiara, 26", "voto": 4, "testo": "Ottimo servizio, anche se a volte parla troppo di Java. Ma ne vale la pena!", "data": "2 Gen 2025"},
            {"autore": "Alessia, 29", "voto": 5, "testo": "Ha refactorato la mia vita sentimentale. Best investment ever.", "data": "28 Dic 2024"}
        ]
    },
    "2": {
        "nome": "Thomi",
        "tagline": "L'unifocus più veloce d'italia. Tranquille non sono veloce in tutto",
        "specialita": "Multitasking, fino a 4 le gestisco bene come i gin tonic",
        "disponibilita": "Solo weekend",
        "prezzo": 450,
        "foto": "foto_unifocus/foto_thomi1.jpg",
        "foto_multiple": [],
        "recensioni": [
            {"autore": "Giulia, 25", "voto": 5, "testo": "Spritz perfetto, balli scatenati. Ha ballato la macarena come nessuno mai. Wow!", "data": "12 Gen 2025"},
            {"autore": "Francesca, 27", "voto": 5, "testo": "Weekend indimenticabile. Lo spritz non era l'unica cosa che girava la testa 😏", "data": "5 Gen 2025"},
            {"autore": "Elena, 30", "voto": 4, "testo": "Ottimo performer, ma troppo competitivo a Uno. Comunque promosso!", "data": "30 Dic 2024"}
        ]
    },
    "3": {
        "nome": "Pilo",
        "tagline": "Le faccio innamorare tutte dicendo, 'ti va una Red Bull fresca?' ",
        "specialita": "50'enni milf coogar",
        "disponibilita": "Solo notte",
        "prezzo": 400,
        "foto": "foto_unifocus/foto_pilo1.jpg",
        "foto_multiple": [],
        "recensioni": [
            {"autore": "Anna, 24", "voto": 5, "testo": "Ha trasformato la mia noiosa serata in un rave illegale. Chef's kiss! 💋", "data": "10 Gen 2025"},
            {"autore": "Laura, 32", "voto": 5, "testo": "Gin Lemon perfetto, conversazione ancora meglio. Ha persino pagato il taxi. Gentleman!", "data": "3 Gen 2025"},
            {"autore": "Valentina, 26", "voto": 5, "testo": "Carisma da vendere. Letteralmente. L'ho noleggiato di nuovo la settimana dopo.", "data": "27 Dic 2024"},
            {"autore": "Serena, 29", "voto": 4, "testo": "Eccellente, solo un po' troppo energico alle 4 del mattino. Ma adorabile!", "data": "20 Dic 2024"}
        ]
    }
}

# EASTER EGGS DATABASE
EASTER_EGGS = {
    "konami": {
        "codice": "↑↑↓↓←→←→BA",
        "messaggio": "🎮 CODICE KONAMI ATTIVATO! Hai sbloccato lo sconto segreto 'NERD69' per il 69% di sconto!"
    },
    "clicks": {
        "numero": 10,
        "messaggio": "🎉 Hai cliccato 10 volte sul logo! Sei ufficialmente ossessionata. Ecco il codice 'STALKER50' per il 50% di sconto!"
    }
}

@app.route('/')
def index():
    return render_template('index.html', staff=GIGOLO_DB)

@app.route('/prenota/<id>')
def prenota(id):
    gigolo = GIGOLO_DB.get(id)
    if not gigolo:
        abort(404)
    
    # Carica le foto multiple per questo modello
    gigolo['foto_multiple'] = get_model_photos(gigolo['nome'])
    
    # Calcola media recensioni
    if gigolo.get('recensioni'):
        media_voti = sum(r['voto'] for r in gigolo['recensioni']) / len(gigolo['recensioni'])
        gigolo['media_recensioni'] = round(media_voti, 1)
    else:
        gigolo['media_recensioni'] = 0
    
    return render_template('prenota.html', gigolo=gigolo, gigolo_id=id)

@app.route('/aggiungi_carrello/<id>')
def aggiungi_carrello(id):
    if 'carrello' not in session:
        session['carrello'] = []
    
    if id in GIGOLO_DB:
        if id not in session['carrello']:
            session['carrello'].append(id)
            session.modified = True
    
    return redirect(url_for('checkout'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    ids_nel_carrello = session.get('carrello', [])
    prodotti_scelti = [GIGOLO_DB[id] for id in ids_nel_carrello if id in GIGOLO_DB]
    totale = sum(p['prezzo'] for p in prodotti_scelti)
    
    sconto = 0
    messaggio_sconto = ""
    
    if request.method == 'POST':
        codice = request.form.get('codice_sconto', '').upper()
        
        # Codici sconto
        if codice == "ALICE20":
            sconto = totale * 0.20
            totale -= sconto
            messaggio_sconto = "🎂 Sconto 'Compleanno Alice' applicato! -20%"
        elif codice == "GIGOLO69":
            totale = 0
            messaggio_sconto = "🎁 Codice 'OMAGGIO' applicato! È tutto gratis!"
        elif codice == "NERD69":
            sconto = totale * 0.69
            totale -= sconto
            messaggio_sconto = "🎮 Easter Egg Konami! -69% perché sei una gamer!"
        elif codice == "STALKER50":
            sconto = totale * 0.50
            totale -= sconto
            messaggio_sconto = "👀 Easter Egg Clicks! -50% per la tua dedizione!"
        else:
            messaggio_sconto = "❌ Codice non valido. Riprova!"
    
    return render_template('checkout.html', prodotti=prodotti_scelti, totale=totale, messaggio=messaggio_sconto)

@app.route('/svuota')
def svuota():
    session.pop('carrello', None)
    return redirect(url_for('index'))

@app.route('/conferma', methods=['POST'])
def conferma():
    # Recupera i prodotti prima di svuotare
    ids_nel_carrello = session.get('carrello', [])
    prodotti_confermati = [GIGOLO_DB[id] for id in ids_nel_carrello if id in GIGOLO_DB]
    
    session.pop('carrello', None)
    
    # Messaggi random divertenti
    messaggi_divertenti = [
        "La tua carta di credito piange, ma il tuo cuore sorride! 💳😭",
        "Prenotazione confermata! Preparati a una serata indimenticabile (o che vorresti dimenticare).",
        "Ottima scelta! Ricorda: ciò che succede con GigoLove, rimane con GigoLove... più o meno.",
        "Ordine ricevuto! Il tuo gigolò sta già lustrando il suo fascino.",
        "Congratulazioni! Hai appena fatto l'investimento migliore della tua vita (forse)."
    ]
    
    messaggio_random = random.choice(messaggi_divertenti)
    
    return render_template('successo.html', prodotti=prodotti_confermati, messaggio=messaggio_random)

# EASTER EGG: Pagina segreta
@app.route('/segreto')
def segreto():
    return render_template('segreto.html')

if __name__ == '__main__':
    app.run(debug=True)