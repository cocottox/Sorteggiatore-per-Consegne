"""
Created on Mon Mar 23 10:15:00 2026

@author: Matteo Senn
"""
"""
Questo file è stato fatto per manipolare i dati presenti dentro il file indirizzi.json ho inizialmente
costruito questa parte perchè la ritenevo la più importante per salvare gli indirizzi dalla ram in modo 7
da non perderli dopo ogni utilizzo del file.
-carica_json per caricare le informazioni dal .json alla ram del sistema
-aggiungi_indirizzo per aggiungere un elemento e controllarne la ridondanza
-salva_json per salvarli, in questo caso ho deciso di eliminare e ricreare in json in modo da avere sempre
i dati corretti, con il rischio però di perdere tutto con eventuali errori(non ho implementato un backup)

"""

from dataclasses import dataclass, asdict
from typing import List
import json
import os

#Ho deciso di utilizzare la libreria dataclasses
@dataclass
class indirizzo:
    via: str
    nome: str
    cognome: str
    in_whitelist: bool
    note: str = ""
    lat: float = None
    lon: float = None

class GestoreIndirizzi:
    
    def __init__(self):
        self.vault: List[indirizzo] = []
        
    def carica_json(self, nome_file="indirizzi.json"):
        #Voglio leggere il file solo se esiste ed ha qualche informazione dentro
        if os.path.exists(nome_file) and os.path.getsize(nome_file) > 0: #size > 0
            try:
                with open(nome_file, "r", encoding="utf-8") as f: # r = "reading"
                    dati_caricati = json.load(f)
                    self.vault = [indirizzo(**d) for d in dati_caricati]
                print(f"Dati caricati con successo ({len(self.vault)} indirizzi)")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Errore nella decodifica del file: {e}")
                self.vault = [] #se ne ottengo errore creo una lista vuota
        else:
            #Se il file non esiste o è vuoto
            print("File non trovato o vuoto. Inizializzazione vault vuoto.")
            self.vault = []     #creo lista vuota
    
    def aggiungi_indirizzo(self, via: str, nome: str, cognome: str, in_whitelist: bool, note: str=""):
        
        nuovo_utente = indirizzo(via, nome, cognome, in_whitelist, note)
        for i,a in enumerate(self.vault): #loop per cercare nella List indicizzata
            if a.nome.lower() == nome.lower() and a.cognome.lower() == cognome.lower():
                del self.vault[i]   #cancello l'indirizzo i trovato
                print("Elemento ridondante... eliminato")
        self.vault.append(nuovo_utente) #Aggiungo il nuovo elemento alla fine
        print(f"L'indirizzo {nome} {cognome} è stato aggiunto alla lista.")
        self.salva_json() #Richiamo per salvare il file JSON
        
        
    def salva_json(self, nome_file="indirizzi.json"):
        dati = [asdict(addr) for addr in self.vault]            #Faccio un dump di
        with open(nome_file, "w", encoding="utf-8") as f:       # dati all'interno
            json.dump(dati, f, indent=4, ensure_ascii=False)    # del JSON
        print(f"Dati salvati con successo in {nome_file}")
    
    def insert_indirizzo(self):
        
        self.carica_json("indirizzi.json")
        
        while True:
            nome_input = input("Inserisci nome: ")
            cognome_input = input("Inserisci cognome: ")
            via_input = input("Inserisci via: ")
            
            #Essendo input <str> il bool ha valore False solo se stringa vuota
            val = input("Inserisci 'si' per whitelist, premi Invio per No: ")
            in_whitelist_input = val.lower() == "si" #devo trovare soluzione migliore
            
            #Richiamo la funzione aggiungi_indirizzo con i valori aggiornati
            self.aggiungi_indirizzo(
                nome=nome_input,
                cognome=cognome_input,
                via=via_input,
                in_whitelist=in_whitelist_input
            )
            
            fine = input("Vuoi aggiungerne un altro? (y/n): ")
            if fine.lower() == "n":
                print("Uscita in corso...")
                break
    
    def cerca_indirizzo(self):
        
        nome_cerca = input("Inserisci nome da cercare:")
        cognome_cerca = input("inserisci cognome da cercare:")
        
        self.carica_json("indirizzi.json")
        
        for i, a in enumerate(self.vault):
            if a.nome.lower() == nome_cerca.lower() and a.cognome.lower() == cognome_cerca.lower():
                print(f"{nome_cerca}-{cognome_cerca} | trovato nell'indice <{i+1}>")
                print(self.vault[i])
                
    def elimina_indirizzo(self, nome: str, cognome: str):
        original_len = len(self.vault)
        # Filtriamo il vault mantenendo solo chi NON corrisponde al nome e cognome
        self.vault = [a for a in self.vault if not (a.nome.lower() == nome.lower() and a.cognome.lower() == cognome.lower())]
        
        if len(self.vault) < original_len:
            print(f"L'indirizzo di {nome} {cognome} è stato eliminato.")
            self.salva_json()
            return True
        else:
            print("Indirizzo non trovato.")
            return False