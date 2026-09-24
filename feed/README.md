# Feed Overture per VetSearch

Questa cartella è un repository GitHub autonomo. Pubblica ogni mese due piccoli file JSON direttamente nel repository pubblico. I file contengono solo strutture Overture `veterinarian` con confidence >= 0,5 all'interno dei confini provinciali ISTAT di Milano (015) e Monza Brianza (108), tralasciando le schede marcate definitivamente chiuse. Il filtro non garantisce che ogni attività sia aperta; l'app richiede verifica prima delle visite.

## Pubblicazione automatica

Il repository `robertotestini-dotcom/vetsearch-feed` contiene già lo script e il workflow. Al primo push, il workflow pubblica `feed/public/milano.json` e `feed/public/monza.json`. Gli indirizzi HTTPS sono `https://raw.githubusercontent.com/robertotestini-dotcom/vetsearch-feed/main/feed/public/milano.json` e `https://raw.githubusercontent.com/robertotestini-dotcom/vetsearch-feed/main/feed/public/monza.json`. VetSearch 1.9 li usa direttamente senza configurazione.

Per installare su un altro repository, carica solo `feed/` e `.github/`, poi cambia l'indirizzo predefinito nell'app o usa “Configura fonte Overture online”. Non caricare keystore o backup del database nel repository pubblico. I push automatici richiedono il permesso GitHub Actions “Read and write permissions” per il repository (Settings → Actions → General); se il workflow riceve 403 nel passo di pubblicazione, abilita quel permesso.

Il workflow si ripete il terzo giorno di ogni mese. Il pulsante SCAN legge i due file pubblicati e interroga Overpass/OpenStreetMap; non scarica l'intero pianeta sul telefono. Se il workflow fallisce, il feed esistente rimane quello dell’ultimo commit pubblicato; l'app mostra la data del feed e la release Overture per poter notare dati vecchi. Se fallisce uno dei due servizi, l'app segnala l'errore e conserva strutture, clienti, visite e note già presenti.

Il processo usa l'ultima release Overture dal catalogo STAC e i confini provinciali del progetto `guglielmo/geojson-italy` (CC BY 4.0, confini ISTAT). Nessun numero di strutture provinciali è stato verificato live in questo ambiente: il workflow deve terminare correttamente prima dell'uso. Il volume di richieste al catalogo può incidere su limiti di esecuzione gratuiti di GitHub Actions.
