# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:04:22 2026

@author: Matteo Senn
"""
"""
In questo file è stata implementata la logica di divisione e ordinazione degli indirizzi, per la divisione
ho utilizzato una logica matematica con calcolo della distanza attraverso Pitagora e calcolo di angolo
rispetto al nodo di origine (Sede CRI o Ospedale Maggiore) in modo da creare una retta che possa dividere 
equamente gli indirizzi. L'ordinamento è stato fatto con una logica del vicino più "vicino" in modo da non
far pesare troppo l'algoritmo dato che con almeno 20+ nodi in cui passare avrebbe avuto una lentezza di
lavoro notevole.
"""
import math

class OttimizzatorePercorsi:
    def __init__(self, sede_lat=45.650, sede_lon=13.781): 
        #Punto di partenza: Ospedale Maggiore, Trieste
        self.sede = {"lat": sede_lat, "lon": sede_lon}

    def calcola_distanza(self, lat1, lon1, lat2, lon2):
        #Calcolo euclideo per distanze cittadine
        return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

    def ordina_percorso(self, punti):
        
        percorso = []
        rimanenti = punti.copy()
        
        attuale_lat, attuale_lon = self.sede["lat"], self.sede["lon"]

        while rimanenti:
            vicino = min(rimanenti, key=lambda p: self.calcola_distanza(attuale_lat, attuale_lon, p.lat, p.lon))
            percorso.append(vicino)
            attuale_lat, attuale_lon = vicino.lat, vicino.lon
            rimanenti.remove(vicino)
        return percorso

    def genera_giri(self, lista_indirizzi, n_mezzi=1):
        #Solo whitelist e con coordinate valide
        validi = [p for p in lista_indirizzi if p.lat and p.lon and p.in_whitelist]
        
        if not validi:
            return []

        n_mezzi = min(n_mezzi, len(validi))
        if n_mezzi < 1: return []

        # qua ho scelto lo sweep algorithm una sorta di radar attorno
        sede_lat, sede_lon = self.sede["lat"], self.sede["lon"]
        
        def calcola_angolo(p):
            #Calcola l'angolo dell'indirizzo rispetto all'Ospedale
            return math.atan2(p.lat - sede_lat, p.lon - sede_lon)

        validi_ordinati = sorted(validi, key=calcola_angolo)

        dimensione_blocco = math.ceil(len(validi_ordinati) / n_mezzi)
        giri_per_mezzo = [validi_ordinati[i:i + dimensione_blocco] for i in range(0, len(validi_ordinati), dimensione_blocco)]
        
        while len(giri_per_mezzo) < n_mezzi:
            giri_per_mezzo.append([])

        giri_ottimizzati = []
        for gruppo in giri_per_mezzo:
            if gruppo:
                percorso_veloce = self.ordina_percorso(gruppo)
                giri_ottimizzati.append(percorso_veloce)
            else:
                giri_ottimizzati.append([])
        
        return giri_ottimizzati
