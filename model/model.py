from database.impianto_DAO import ImpiantoDAO
from database.consumo_DAO import ConsumoDAO


'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        lista_tuple = []
        for i in self._impianti:
            consumi = ConsumoDAO.get_consumi(i.id)
            consumo = 0
            numero_occorrenze = 0
            for j in consumi:
                data = j.data
                if data.month == mese:
                    numero_occorrenze += 1
                    consumo += j.kwh
            media = consumo / numero_occorrenze
            lista_tuple.append((i.nome, media))
        return lista_tuple



    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        if giorno ==8:
            self.__sequenza_ottima= sequenza_parziale  ##quando si arriva all'ottavo giorno aggiorno tutti i valori
            self.__costo_ottimo = costo_corrente
        else:
            id_costo_minore = ""
            costo_minore = 10000000000000000000     ##imposto un costo iniziale tendente all'infinito in modo tale che il primo paragone
            for key,val in consumi_settimana.items():  ##sia sicuramente vero
                if not ultimo_impianto:            ##durante il primo ciclo dato che ultimo_impianto = none
                    somma = int(val[giorno-1])
                    if somma<costo_minore:
                        id_costo_minore = key
                        costo_minore = somma
                else:                            ##in caso non sia None
                    id_corrente = ultimo_impianto
                    if key == id_corrente:        ##se la chiave è uguale all'id_corrente allora calcolo senza l'aggiunta di 5
                        somma = int(val[giorno-1])
                        if somma<costo_minore:
                            id_costo_minore = key
                            costo_minore = somma
                    else:                         ##in caso contrario aggiungo 5 poichè bisogna spostarsi in un altro impianto
                        somma = int(val[giorno-1])+5
                        if somma<costo_minore:
                            id_costo_minore = key
                            costo_minore = somma
            giorno+=1
            ultimo_impianto= id_costo_minore
            costo_corrente+=costo_minore        ##riaggionro i parametri prima di effttuare la ricorsione nuovamente
            sequenza_parziale.append(ultimo_impianto)
            return self.__ricorsione(sequenza_parziale, giorno,ultimo_impianto, costo_corrente, consumi_settimana)



    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        dizionario = {}
        for i in self._impianti:
            consumi = ConsumoDAO.get_consumi(i.id)
            lista_consumi_giorni = [0] * 7   ##nell'eccezione in cui non ci siano valori per quel giorno
            for j in consumi:
                if j.data.month == mese and 1 <= j.data.day <= 7:
                    lista_consumi_giorni[j.data.day - 1] = j.kwh ##in modo tale che sia anche una lista ordinata
            dizionario[i.id] = lista_consumi_giorni
        return dizionario





