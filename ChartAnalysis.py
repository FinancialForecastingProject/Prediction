import contextlib
from datetime import datetime
import requests as req
from typing import List
import requests as req
from statistics import mean
import itertools
from tkinter import *
from dtw import *

class ChartAnalysis():
    def __init__(self):
        self.charts={}
    
    def get_chart(self,symbol:str,timeframe:int=30) -> list:
        # sourcery skip: raise-specific-error
        headers = {
            'x-api-key': "mTd2MNVwEe3WFgj5PQ66Tbpq0CyeP8Q7ESjpmYZ2"
        }
        try:
            url = f"https://yfapi.net/v8/finance/chart/{symbol}?range=1mo&region=FR&interval=1d&lang=en"
            response = req.request("GET", url, headers=headers)



            closes = response.json()["chart"]["result"][0]["indicators"]["quote"][0]['close']
            timesamps = response.json()["chart"]["result"][0]["timestamp"]


            return [{"date":datetime.fromtimestamp(int(timestamp)), "close":close} for timestamp, close in zip(timesamps, closes)]

        except Exception as errorYahoo:
            apiKeys = [
                "mgiQenXQDOEgN365mHVjFjSWoZL16OmOJasdgUwd9zKZtRs8OeaMlBJSdQJN",
                "DPEbphxr0mBRzEp956ORDzCn1DFQMX6Xhhf1g5GVw6t6LtJlNmkwmYDGKVed",
            ]

            for key in apiKeys:
                with contextlib.suppress(Exception):
                    headers = {'X-Mboum-Secret': key}
                    url = f"https://mboum.com/api/v1/hi/history/?symbol={symbol}&interval=1d&diffandsplits=true"

                    response = req.request("GET", url, headers=headers).json()
                    result = [
                        {
                            "date": datetime.fromtimestamp(int(value)),
                            "close": response['data']['items'][value]["close"],
                        }
                        for value in response['data']['items']
                    ]

                    return result[-timeframe:]

            raise Exception(errorYahoo) from errorYahoo
        
    """
    Methode pour charger le graphique d'un actif depuis l'api
    On verifie si l'actif n'a pas encore été chargé
    """
    def loading(self,list_actifs:List[str]):
        for actif in list_actifs:
            if actif not in self.charts:
               self.charts[actif]=self.get_chart(actif)
        
    """Methode qui sauvegarde les differents graphiques de comparaisons des différents actifs passés dans une liste en parametre
    Print dans la console les differentes distances en fonction de l'algorithme utilisé.
    """
    def resultats_rapports(self,list_actifs:List[str],fenetre) -> dict:
        results = {}
        
        # On utilise itertools pour comparer les actifs deux à deux une seule fois
        for actif_reference,actif_comparaison in itertools.combinations(list_actifs, 2):
       
            chart_reference = [value['close'] for value in self.charts[actif_reference]]
            chart_comparison = [value['close'] for value in self.charts[actif_comparaison]]


            results[
                f"distance rapport moyenne {actif_reference} / "
                + actif_comparaison
            ] = self.distance_point_par_point_rapport_moyenne(
                chart_reference,chart_comparison,actif_reference,actif_comparaison,fenetre=fenetre
            )
            

            results[
                f"dynamic time warping rapport moyenne {actif_reference} / "
                + actif_comparaison
            ] = self.dynamic_time_warping_par_rapport_moyenne(
                chart_reference,chart_comparison,actif_reference,actif_comparaison,fenetre=fenetre
            )
        
        return results                



    
    def distance_point_par_point_rapport_moyenne(self,chart_reference,chart_comparison):          
         # Adapte les amplitudes des courbes pour pouvoir les comparer
        
        ## On les ramene à 1 en faisant le rapport par rapport à leur moyenne
        rearange_reference = [value / mean(chart_reference) for value in chart_reference]
        rearange_comparison = [value / mean(chart_comparison) for value in chart_comparison]

        # On calcule les differentes distances entre les points des deux courbes
        distances = [
            abs(rearange_reference[i] - rearange_comparison[i])
            for i in range(len(rearange_reference))
        ]

        return {"distance totale":round(sum(distances),2),"distance moyenne":round(mean(distances),2)}
    

    
    def dynamic_time_warping_par_rapport_moyenne(self,chart_reference,chart_comparison):
        # Adapte les amplitudes des courbes pour pouvoir les comparer
        
        ## On les ramene à 1 en faisant le rapport par rapport à leur moyenne
        rearange_reference = [value / mean(chart_reference) for value in chart_reference]
        rearange_comparison = [value / mean(chart_comparison) for value in chart_comparison]


        # OO method call chain
        warping = dtw(rearange_comparison, rearange_reference, keep_internals=True, step_pattern=rabinerJuangStepPattern(6, "c"))

        
        return {"distance totale":round(warping.distance,2),"distance moyenne":round(warping.distance/len(chart_comparison),2)}
    


        """Recupère les dernières données journalière pour l'actif reference sur une periode de 1 mois
        puis recupere les dernières données journalières pour une serie d'actif dans le S&P500 sur une periode de 3 mois (on gardera uniquement les 2 premiers mois)
        """
    def prediction(self,reference:str,comparison:List[str])->float:
        pass
        