# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 13:46:57 2026

@author: Matteo Senn
"""
"""
Questo file è stato creato tra gli ultimi in modo da poter associare tutte le vie nel indirizzi.json alle
coordinate presenti nel file DataTrieste.geojson ho scelto di lavorare con coordinate (lat e lon) e non
indicazioni stradati dato il peso di un file osm.pbf eccessivo e la difficoltà effettiva di implementare
una lettura veloce di esso nel programma
"""
import json
import os
from ClassIndirizzo import GestoreIndirizzi

class GestoreCoordinate:
    
    def __init__(self, database_path='DataTrieste.json'):
        self.gi = GestoreIndirizzi()
        self.gi.carica_json() # Carica indirizzi.json
        self.database_path = database_path
    
    def _carica_db_locale(self):
        """Carica i dati estratti da OSM (DataTrieste.json)"""
        if os.path.exists(self.database_path):
            with open(self.database_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def latlon_indirizzi(self):
        """
        Cerca le coordinate nel file DataTrieste.json e 
        aggiorna il vault (che poi verrà salvato su indirizzi.json)
        """
        db_osm = self._carica_db_locale()
        
        if not db_osm:
            print(f"Errore: {self.database_path} non trovato o vuoto.")
            return

        for persona in self.gi.vault:
            # Pulizia della stringa inserita dall'utente (es: "Via Roma 12")
            input_utente = persona.via.lower().strip()
            
            print(f"Ricerca locale per: {persona.via}...")
            trovato = False
            
            for elemento in db_osm:
                # Cerchiamo solo tra gli elementi di tipo 'indirizzo' o 'edificio'
                if elemento.get('categoria') in ['indirizzo', 'edificio']:
                    via_db = elemento.get('via', '').lower().strip()
                    civico_db = str(elemento.get('civico', '')).lower().strip()
                    
                    # Costruiamo il confronto (es: "via roma" + " " + "12")
                    indirizzo_db_completo = f"{via_db} {civico_db}".strip()
                    
                    # Se l'input dell'utente corrisponde esattamente all'indirizzo nel DB OSM
                    if input_utente == indirizzo_db_completo:
                        persona.lat = elemento.get('lat')
                        persona.lon = elemento.get('lon')
                        print(f"Trovato: {persona.lat}, {persona.lon}")
                        trovato = True
                        break
            
            if not trovato:
                print(f"❌ Nessuna corrispondenza in DataTrieste.json per: {persona.via}")
        
        # SALVATAGGIO FINALE: sovrascrive indirizzi.json con le coordinate trovate
        self.gi.salva_json()
        print("\nAggiornamento di indirizzi.json completato.")
        
    
        
