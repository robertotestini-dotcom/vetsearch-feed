# Feed Overture per VetSearch

Questa cartella è un repository GitHub autonomo. Pubblica ogni mese due piccoli file JSON su GitHub Pages. I file contengono solo strutture Overture `veterinarian` con confidence >= 0,5 all'interno dei confini provinciali ISTAT di Milano (015) e Monza Brianza (108), tralasciando le schede marcate definitivamente chiuse. Il filtro non garantisce che ogni attività sia aperta; l'app richiede verifica prima delle visite.

## Pubblicazione (una volta sola)

1. Crea un repository **pubblico** GitHub, ad esempio `vetsearch-feed`.
2. Carica il contenuto di questo archivio nella radice del repository: cartella `.github` e cartella `feed`. Non caricare file `.keystore`, database o backup dell'app. La pubblicazione su GitHub Pages di repository pubblici è gratuita secondo il piano applicabile.
3. In **Settings → Pages → Build and deployment**, scegli **GitHub Actions**.
4. In **Actions → Aggiorna feed Overture → Run workflow**, avvia il primo aggiornamento. Controlla che il workflow termini correttamente e che i file `milano.json` e `monza.json` risultino disponibili a `https://NOMEUTENTE.github.io/vetsearch-feed/`.
5. In VetSearch 1.8 scegli **Configura fonte Overture online** e inserisci l'indirizzo della cartella, ad esempio `https://NOMEUTENTE.github.io/vetsearch-feed/`, poi premi SCAN.

Il workflow si ripete il terzo giorno di ogni mese. Il pulsante SCAN legge i due file pubblicati e interroga Overpass/OpenStreetMap; non scarica l'intero pianeta sul telefono. Se il workflow fallisce, il feed esistente rimane quello della pubblicazione precedente; l'app mostra la data del feed e la release Overture per poter notare dati vecchi. Se fallisce uno dei due servizi, l'app segnala l'errore e conserva strutture, clienti, visite e note già presenti.

Il processo usa l'ultima release Overture dal catalogo STAC e i confini provinciali del progetto `guglielmo/geojson-italy` (CC BY 4.0, confini ISTAT). Nessun numero di strutture provinciali è stato verificato live in questo ambiente: il workflow deve terminare correttamente prima dell'uso. Il volume di richieste al catalogo può incidere su limiti di esecuzione gratuiti di GitHub Actions.
