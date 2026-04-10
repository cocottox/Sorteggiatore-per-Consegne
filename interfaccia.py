# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 13:02:07 2026

@author: Matteo Senn
"""
"""
In questo file ammetto subito che è stato usato pesantemente il supporto di Gemini, non conoscendo la
libreria Tkinter sarebbe stato estremamente lento imparare ad usarla ho quindi preferito abbreviare i 
tempi e farmi dare una mano per poi studiare il programma e personalizzare il layout
"""
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from ClassIndirizzo import GestoreIndirizzi
from logistica import OttimizzatorePercorsi

class AppIndirizzi:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gestore Giro Pasti")
        self.root.geometry("450x450")
        self.gi = GestoreIndirizzi()
        self.gi.carica_json()
        self.crea_widget()

    def crea_widget(self):
        # I tuoi campi originali (restano invariati)
        self.campi_config = [
            ("nome", "Nome:"),
            ("cognome", "Cognome:"),
            ("via", "Via:"),
            ("whitelist", "Nel giro ?(si/no):"),
            ("note","Note (Richieste ecc..):")
        ]
        
        self.entries = {}
        for i, (chiave, testo) in enumerate(self.campi_config):
            tk.Label(self.root, text=testo).grid(row=i, column=0,columnspan=1, pady=5)
            entry = tk.Entry(self.root)
            entry.grid(row=i, column=1,columnspan=3,pady=5,ipadx=50)
            self.entries[chiave] = entry

        # Questa è la riga di partenza per la grafica, da qua in poi il codice ha preso il soppravvento
        riga_attuale = 5
        
        # tasto SALVA 
        self.btn_salva = tk.Button(self.root, text="Salva", command=self.salva_e_verifica, bg="#7cfc00")
        self.btn_salva.grid(row=riga_attuale, column=0, columnspan=1, pady=5,padx=15,ipadx=30)

        # tastop CERCA
        self.btn_cerca = tk.Button(self.root, text="Cerca", command=self.azione_cerca, bg="#ffbf00")
        self.btn_cerca.grid(row=riga_attuale, column=1, columnspan=1, pady=5,padx=15, ipadx=30)

        # tasto ELIMINA
        self.btn_elimina = tk.Button(self.root, text="Elimina", command=self.azione_elimina, bg="#ff0000")
        self.btn_elimina.grid(row=riga_attuale, column=3, columnspan=1, pady=5,padx=15,ipadx=30)
        riga_attuale += 1
        
        # tasto MOSTRA LISTA 
        self.btn_mostra = tk.Button(self.root, text="Visualizza Lista", command=self.apri_rubrica, bg="#9932cc")
        self.btn_mostra.grid(row=riga_attuale, column=0, columnspan=1, pady=5, ipadx=15)
       

        # IL NUOVO TASTO VERIFICA (aggiunto con grid)
        self.btn_verifica = tk.Button(self.root, text="Verifica Indirizzi", command=self.controlla_database_locale, bg="#00b7eb")
        self.btn_verifica.grid(row=riga_attuale, column=1, columnspan=2, pady=5,padx=15,ipadx=15)
        riga_attuale += 1

        # Spazio e Numero Mezzi
        tk.Label(self.root, text="Numero Mezzi:").grid(row=riga_attuale, column=0, pady=10)
        self.entry_mezzi = tk.Entry(self.root)
        self.entry_mezzi.insert(0, "2")
        self.entry_mezzi.grid(row=riga_attuale, column=1)
        riga_attuale += 1

        # tasto GENERA 
        self.btn_calcola = tk.Button(self.root, text="Genera Percorsi", command=self.apri_finestra_giri, bg="#ffd54f")
        self.btn_calcola.grid(row=riga_attuale, column=0, columnspan=2, pady=10)

        # Assicura che la colonna si allarghi bene
        self.root.grid_columnconfigure(1, weight=1)
        
        # la lista ordinata delle caselle di testo per il focus
        self.lista_focus = [self.entries[chiave] for chiave, _ in self.campi_config]
        self.lista_focus.append(self.entry_mezzi) # Aggiungiamo anche il campo "Numero Mezzi" alla fine
        
        # Collegamento per i tasti (Freccia Giù, Freccia Su, Invio)
        for widget in self.lista_focus:
            widget.bind("<Down>", self.muovi_focus)
            widget.bind("<Return>", self.muovi_focus)
            widget.bind("<Up>", self.muovi_focus_indietro)
            
        # il cursore lampeggiante sulla prima casella (Nome) all'avvio
        if self.lista_focus:
            self.lista_focus[0].focus_set()
        
    def muovi_focus(self, event):
        #Per muoversi all'interno del programma
        current_widget = event.widget
        try:
            index = self.lista_focus.index(current_widget)
            next_widget = self.lista_focus[index + 1]
            next_widget.focus_set()
        except IndexError:
            #Se siamo all'ultimo campo, l'invio preme il tasto salva
            self.azione_aggiungi()
        return "break" #Impedisce il "beep" di sistema su Windows
    
    def muovi_focus_indietro(self, event):
        #Per muoversi indietro
        current_widget = event.widget
        index = self.lista_focus.index(current_widget)
        if index > 0:
            prev_widget = self.lista_focus[index - 1]
            prev_widget.focus_set()
        return "break"

    def azione_aggiungi(self):
        #Azione di aggiunta al nostro JSON file
        nome = self.entries["nome"].get()
        cognome = self.entries["cognome"].get()
        via = self.entries["via"].get()
        whitelist_raw = self.entries["whitelist"].get().lower()
        
        whitelist = (whitelist_raw == "si")

        if nome and cognome and via:
            self.gi.aggiungi_indirizzo(via, nome, cognome, whitelist)
            messagebox.showinfo("Successo", f"Salvato: {nome} {cognome}")
            
            #Dopo aver inserito i campi sopra vengono puliti
            for e in self.entries.values():
                e.delete(0, tk.END)
            self.lista_focus[0].focus_set()
        else:
            messagebox.showwarning("Errore", "I primi tre campi sono obbligatori!")

    def azione_cerca(self):
        #Parte di ricerca sui valori inseriti dall'utente
        n_cerca = self.entries["nome"].get().lower()
        c_cerca = self.entries["cognome"].get().lower()

        if not n_cerca or not c_cerca:
            messagebox.showwarning("Ricerca", "Inserisci Nome e Cognome per cercare.")
            return

        trovato = False
        for i, a in enumerate(self.gi.vault):
            if a.nome.lower() == n_cerca and a.cognome.lower() == c_cerca:
                #Se non lo trova o se lo trova 
                self.entries["via"].delete(0, tk.END)
                self.entries["via"].insert(0, a.via)
                self.entries["whitelist"].delete(0, tk.END)
                self.entries["whitelist"].insert(0, "si" if a.in_whitelist else "no")
                
                self.status.config(text=f"Trovato in posizione {i+1}", fg="blue")
                messagebox.showinfo("Risultato", f"Trovato!\nVia: {a.via}\nWhitelist: {a.in_whitelist}")
                trovato = True
                break
        
        if not trovato:
            messagebox.showwarning("Ricerca", "Nessun risultato trovato.")
            
    def pulisci_campi(self):
        # Svuota tutte le caselle di testo
        for chiave in self.entries:
            self.entries[chiave].delete(0, tk.END)
            
        #Rimette il cursore lampeggiante sulla casella "nome"
        if "nome" in self.entries:
            self.entries["nome"].focus_set()

    def azione_elimina(self):
        nome = self.entries["nome"].get()
        cognome = self.entries["cognome"].get()

        if not nome or not cognome:
            messagebox.showwarning("Attenzione", "Inserisci Nome e Cognome per eliminare l'indirizzo.")
            return

        conferma = messagebox.askyesno("Conferma", f"Sei sicuro di voler eliminare {nome} {cognome}?")
        
        if conferma:
            successo = self.gi.elimina_indirizzo(nome, cognome)
            if successo:
                # Rimossa la riga self.status che causava crash!
                self.pulisci_campi()
                messagebox.showinfo("Eliminato", "Indirizzo rimosso con successo.")
                
                #Aggiorna la rubrica in tempo reale se è aperta
                if hasattr(self, 'finestra_rubrica') and self.finestra_rubrica.winfo_exists():
                    for item in self.tree_rubrica.get_children():
                        self.tree_rubrica.delete(item)
                    for p in self.gi.vault:
                        wl_testo = "Sì" if p.in_whitelist else "No"
                        nota_testo = getattr(p, 'note', '') 
                        self.tree_rubrica.insert("", tk.END, values=(p.nome, p.cognome, p.via, wl_testo, nota_testo))
            else:
                messagebox.showerror("Errore", "Impossibile trovare l'indirizzo da eliminare.")
                
    def apri_rubrica(self):
        top = tk.Toplevel(self.root)
        top.title("Rubrica Indirizzi")
        top.geometry("600x400") 

        colonne = ("nome", "cognome", "via", "whitelist", "note")
        tree = ttk.Treeview(top, columns=colonne, show='headings')
        
        tree.heading("nome", text="Nome")
        tree.heading("cognome", text="Cognome")
        tree.heading("via", text="Indirizzo")
        tree.heading("whitelist", text="Whitelist")
        tree.heading("note", text="Note")
        
        tree.column("nome", width=100)
        tree.column("cognome", width=100)
        tree.column("via", width=180)
        tree.column("whitelist", width=60)
        tree.column("note", width=120)

        for p in self.gi.vault:
            wl_testo = "Sì" if p.in_whitelist else "No"
            nota_testo = getattr(p, 'note', '')
            tree.insert("", tk.END, values=(p.nome, p.cognome, p.via, wl_testo, nota_testo))

        scrollbar = ttk.Scrollbar(top, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def seleziona_elemento(event):
            selezioni = tree.selection()
            if not selezioni:
                return
                
            item = selezioni[0]
            valori = tree.item(item, "values")
            
            self.pulisci_campi()
            self.entries["nome"].insert(0, valori[0])
            self.entries["cognome"].insert(0, valori[1])
            self.entries["via"].insert(0, valori[2])
            self.entries["whitelist"].insert(0, "si" if valori[3] == "Sì" else "no")
            
            #Gestione riempimento Note
            if len(valori) > 4:
                self.entries["note"].delete(0, tk.END)
                self.entries["note"].insert(0, valori[4])
                
            top.destroy()

        #Qua faccio bind dell'azione doppio click
        tree.bind("<Double-1>", seleziona_elemento)
        
        #Salviamo i riferimenti così che non vengano persoi con l'eliminazione
        self.finestra_rubrica = top
        self.tree_rubrica = tree
            
        def seleziona_elemento(event):
            #Ci assicuriamo che sia selezionato
            selezioni = tree.selection()
            if not selezioni:
                return
                
            item = selezioni[0]
            valori = tree.item(item, "values")
            
            #Con queste righe pulisco e riempio i campi con l'elemento selezionato
            self.pulisci_campi()
            self.entries["nome"].insert(0, valori[0])
            self.entries["cognome"].insert(0, valori[1])
            self.entries["via"].insert(0, valori[2])
            self.entries["whitelist"].insert(0, "si" if valori[3] == "Sì" else "no")
            
            #Predisposizione per il campo note
            if len(valori) > 4:
                self.entries["note"].insert(0, valori[4])
                
            top.destroy() #Chiude la rubrica dopo la selezione
        #Non so se è ricorrente ma senza non va lol    
        tree.bind("<Double-1>", seleziona_elemento)

        
        
    def apri_finestra_giri(self):
        #Recupera il numero di mezzi selezionato
        try:
            n_mezzi = int(self.entry_mezzi.get())
        except (AttributeError, ValueError):
            n_mezzi = 2  #Numero di default

        #Sede CRI Trieste (Via dell'Istria)
        ottimizzatore = OttimizzatorePercorsi(45.637, 13.791)
        
        #Otteniamo la lista di liste (un percorso per ogni mezzo)
        tutti_i_giri = ottimizzatore.genera_giri(self.gi.vault, n_mezzi)

        #Creazione Finestra Risultati
        top = tk.Toplevel(self.root)
        top.title(f"Piani di Carico - {len(tutti_i_giri)} Mezzi")
        top.geometry("650x700")

        #Sistema di Scroll
        canvas = tk.Canvas(top)
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        #Colori per distinguere i mezzi
        colori = ["blue", "red", "green", "orange", "purple", "brown", "darkcyan"]

        #Generazione delle tabelle
        for i, giro in enumerate(tutti_i_giri):
            colore_titolo = colori[i % len(colori)]
            # Chiamata al metodo che causava l'errore
            self.crea_tabella_giro(scrollable_frame, f"🚚 MEZZO {i+1}", colore_titolo, giro)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def crea_tabella_giro(self, container, titolo, colore, lista_punti):
        
        frame_settore = tk.LabelFrame(container, text=titolo, font=("Arial", 12, "bold"), fg=colore, padx=10, pady=10)
        frame_settore.pack(fill="x", padx=15, pady=10)

        if not lista_punti:
            tk.Label(frame_settore, text="Nessun indirizzo assegnato a questo mezzo", fg="grey").pack()
            return

        cols = ("pos", "nome", "via", "note")
        tree = ttk.Treeview(frame_settore, columns=cols, show='headings', height=min(len(lista_punti), 6))
        
        tree.heading("pos", text="#")
        tree.heading("nome", text="Nominativo")
        tree.heading("via", text="Indirizzo")
        tree.heading("note", text="Note")
        
        tree.column("pos", width=40, anchor="center")
        tree.column("nome", width=150)
        tree.column("via", width=300)
        tree.column("note", width=150)
        
        for i, p in enumerate(lista_punti, 1):
            #Recupera la nota, gestendo vecchi salvataggi che potrebbero non averla
            nota = getattr(p, 'note', '')
            tree.insert("", tk.END, values=(i, f"{p.nome} {p.cognome}", p.via, nota))
        
        tree.pack(fill="x")
        
    def controlla_database_locale(self):
        
        if not os.path.exists('DataTrieste.json'):
            messagebox.showerror("Errore", "File DataTrieste.json non trovato!")
            return

        with open('DataTrieste.json', 'r', encoding='utf-8') as f:
            db_osm = json.load(f)

        trovati = 0
        mancanti = []
        
        for persona in self.gi.vault:
            #Pulizia per il confronto
            input_pulito = persona.via.lower().strip().replace(",", "")
            
            match_trovato = False
            for elemento in db_osm:
                if elemento.get('categoria') in ['indirizzo', 'edificio']:
                    via_db = str(elemento.get('via', '')).lower().strip()
                    civico_db = str(elemento.get('civico', '')).lower().strip()
                    confronto_db = f"{via_db} {civico_db}".strip()

                    if input_pulito == confronto_db:
                        persona.lat = elemento.get('lat')
                        persona.lon = elemento.get('lon')
                        match_trovato = True
                        trovati += 1
                        break
            
            if not match_trovato:
                mancanti.append(persona.via)

        self.gi.salva_json()
        
        msg = f" Aggiornamento completato!\nIndirizzi con coordinate: {trovati}"
        if mancanti:
            msg += "\n\n❌ Non trovati nel database:\n" + "\n".join(mancanti[:5])
            if len(mancanti) > 5: msg += "\n..."
        
        messagebox.showinfo("Esito Verifica", msg)

    def salva_e_verifica(self):
        
        #Recupera i dati dalle entry pulendoli da spazi vuoti iniziali/finali
        dati = {chiave: self.entries[chiave].get().strip() for chiave, _ in self.campi_config}
        
        if not dati['nome'] or not dati['cognome']:
            messagebox.showwarning("Attenzione", "I campi Nome e Cognome sono obbligatori!")
            return
        if not dati['via']:
            messagebox.showwarning("Attenzione", "Il campo Via è obbligatorio!")
            return
            
        #Converte "si/no" in Booleano
        is_white = dati['whitelist'].lower() == 'si'
        
        #Aggiunge al vault
        self.gi.aggiungi_indirizzo(
            nome=dati['nome'], 
            cognome=dati['cognome'], 
            via=dati['via'], 
            in_whitelist=is_white,
            note=dati.get('note', '') # predisposizione per il punto 4
        )
        
        #Avvia subito la ricerca coordinate per questo nuovo inserimento
        self.controlla_database_locale()
        
        #Pulisco i campi
        self.pulisci_campi()
        messagebox.showinfo("Successo", "Contatto salvato e coordinate verificate!")
    
    
