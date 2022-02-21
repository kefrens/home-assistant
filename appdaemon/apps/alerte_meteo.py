import hassapi as hass
import datetime
from datetime import datetime

# Niveau de JOURNALISATION (log): 0=rien ou 1 =info ou 2=debug 
JOURNAL=2 
h_forcast={}
FLAG=0

class AlerteMeteo(hass.Hass):
    def initialize(self):
        self.notification("Initialisation Alerte Meteo..",1,"")
        # Ecoute l'arrivée de la pluie imminente
        self.listen_state(self.change_pluie, self.args["entité"])
        
        forcast = self.get_state(self.args["entité"],attribute="forecast_time_ref")
        self.log(f"Forecast: {forcast}", log="test_log")
        
        infov=self.convert_utc(forcast)
        infov=self.time()
        infov=self.get_timezone()
        infov=self.get_tz_offset()
        self.log(f"infov: {infov}", log="test_log")
        
        # Ecoute une alerte méteo
        self.listen_state(self.change_alerte, self.args["alerte"])
        #alerte_w = self.get_state(self.args["alerte"],attribute="state")
        #self.log(f"Alerte Meteo: {alerte_w}", log="test_log")

        #self.notifie_pluie(kwargs=forcast)

    def change_pluie(self, entity, attribute, old, new, kwargs):
        global FLAG
        message_notification= "New: "+new+" / Old: "+old+" / Flag="+ str(FLAG)
        self.notification(message_notification,2,"")
        dic_forcast = self.get_state(self.args["entité"],attribute="1_hour_forecast")
        h_forcast[0] = dic_forcast['0 min']
        h_forcast[1] = dic_forcast['5 min']
        h_forcast[2] = dic_forcast['10 min']
        h_forcast[3] = dic_forcast['15 min']
        h_forcast[4] = dic_forcast['20 min']
        h_forcast[5] = dic_forcast['25 min']
        h_forcast[6] = dic_forcast['35 min']
        h_forcast[7] = dic_forcast['45 min']
        h_forcast[8] = dic_forcast['55 min']
        for h in range(8):
            message_notification= "h"+str(h)+"_Forecast:"+h_forcast[h]
            self.notification(message_notification,2,"")

        etat = self.get_state(self.args["entité"],attribute="state")
        #self.log(f'Etat: {etat}', log="test_log")
        h_pluie= etat[11:16] # Extrait l'heure de la chaine de caracteres

        if new!="unknown" and FLAG==0:
            message_notification= ": La pluie est attendue a "+ format(h_pluie)
            self.notification(message_notification,0,"teleg")
            FLAG = 1

        if new=="unknown" or h_forcast[0] != "Temps sec":
            message_notification= ": Plus de pluie attendue."
            FLAG=0
            self.notification(message_notification,0,"teleg")


    def change_alerte(self, entity, attribute, old, new, kwargs):
        heure = str(self.time())[:8]
        alerte_w = self.get_state(self.args["alerte"],attribute="state")
        Inondation= self.get_state(self.args["alerte"],attribute="Inondation")
        Grand_Froid= self.get_state(self.args["alerte"],attribute="Grand-froid")
        Neige_Verglas= self.get_state(self.args["alerte"],attribute="Neige-verglas")
        Orages= self.get_state(self.args["alerte"],attribute="Orages")
        Pluie_inondation= self.get_state(self.args["alerte"],attribute="Pluie-inondation")
        Vent_violent=self.get_state(self.args["alerte"],attribute="Vent violent")
        attribution= self.get_state(self.args["alerte"],attribute="attribution")
        
        if alerte_w != 'Vert' or alerte_w != 'unavailable':
            if Inondation != 'Vert':
                message_notification= ": Alerte Innondation :"+ Inondation
                self.notification(message_notification,2,"")

            if Grand_Froid != 'Vert':
                message_notification= ": Alerte Grand-froid :"+Grand_Froid
                self.notification(message_notification,2,"")

            if Neige_Verglas != 'Vert':
                message_notification= ": Alerte Neige Verglas :"+Neige_Verglas
                self.notification(message_notification,2,"")

            if Orages != 'Vert':
                message_notification= ": Alerte Orages :"+Orages
                self.notification(message_notification,2,"")

            if Pluie_inondation != 'Vert':
                message_notification= ": Alerte Pluie Inondation :"+Pluie_inondation
                self.notification(message_notification,2,"")

            if Vent_violent != 'Vert':
                message_notification= ": Alerte vents Violents :"+Vent_violent
                self.notification(message_notification,2,"")

        if alerte_w == 'unavailable':
                message_notification= ": Fin Alerte Météo "
                self.notification(message_notification,2,"")
                
    # Fonction Notification
    # message =  Texte à afficher
    # niveau = niveau de journalisation 0,1,2
    # si notif == "teleg" on notifie aussi sur Télégram
    def notification(self,texte_message,niveau,notif):
        global JOURNAL
        heure = str(self.time())[:8]
        if niveau <= JOURNAL:
            message_notification= format(heure)+": "+ texte_message
            self.log(message_notification, log="test_log")
            if notif=="teleg":
                self.call_service('notify/telegram', message=message_notification)
                self.call_service('persistent_notification/create', message=message_notification)