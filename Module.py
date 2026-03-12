import numpy as np
import matplotlib.pyplot as plt
from scapy.all import Ether, IP, ICMP
import scipy
import scipy.signal
########################################################################################
########################################################################################
########################################################################################
##########                                                                  ############
##########                                                                  ############
##########                               MODEM                              ############
##########                                                                  ############
##########                                                                  ############
########################################################################################
########################################################################################
########################################################################################

class Modem :
    """
    
    Classe permettant d"implémenter un MODulateur/dEModulateur PAM ou ASK (2,4,8), QPSK et 16QAM.
    
    """

    def __init__(self, ModType, NbSymboles, bits):
        """
        Contructeur de la classe

        Parametres:
        ----------
            ModType: type de modulation, PAM, ASK, PSK ou QAM.

            NbSymboles: nombre de symboles de la modulation. 2, 4 ou 8 pour PAM ou ASK, 4 pour PSK et 16 pour QAM.
            
            bits: tableau de bits numpy.
        ----------  

        """
        self.modtype = ModType
        self.nsymb = NbSymboles
        self.mod = (ModType, NbSymboles)
        self.bits = bits
        
        if ModType == "PAM" or ModType == "ASK" :
            self.symb_type = "reel"
        else : 
            self.symb_type = "complexe"

        if (self.nsymb & (self.nsymb-1) == 0) and self.nsymb != 0 :
            self.bits_par_symb=int(np.log2(self.nsymb))
        else :
            raise ValueError("La deuxième valeur qui correspond au nombre de symboles \
            doit être une puissance de 2 : 2, 4, 8, 16, 32, 64, ...")
        
        self.symbs_num = bits.reshape(int(len(bits)/self.bits_par_symb), self.bits_par_symb)
            

    def create_MP(self, amplitude, phase_origine=0):
        """
        Fonction en charge de créer la table de mapping de chaque modulation
    
        Paramètres:
        ----------
            amplitude: amplitude maximale des sybmole de modulation pour une modulation PAM ou ASK,
                       amplitude max de la sinusoide pour une modulation PSK et amplitude max de I
                       et Q pour une modulation QAM.

            phase_ori: utilisé seulement pour la modulation QPSK, phase à l"origine du premier
                       symbole (par déffaut = 0).
        ----------

        Renvoie mapping_table: la table de mapping sous forme d"un dictionnaire.
        """
        match self.mod:
            case ("PAM",2)| ("ASK",2) :
                mapping_table = {(0,) : -1,
                                (1,) : 1}
           
            case ("PAM",4)| ("ASK",4) :
                mapping_table = {(0,0) : -3,
                                (0,1) : -1,
                                (1,0) : 1,
                                (1,1) : 3}
            
            case ("PAM",8)| ("ASK",8) :
                mapping_table = {(0,0,0) : -7,
                                (0,0,1) : -5,
                                (0,1,0) : -3,
                                (0,1,1) : -1,
                                (1,0,0) : 1,
                                (1,0,1) : 3,
                                (1,1,0) : 5,
                                (1,1,1) : 7}
            case ("PSK", 4) :
                mapping_table = {(0,0) : amplitude*np.exp(1j*(phase_origine+np.pi/4)),
                                 (0,1) : amplitude*np.exp(1j*(phase_origine+3*np.pi/4)),
                                 (1,0) : amplitude*np.exp(1j*(phase_origine+5*np.pi/4)),
                                 (1,1) : amplitude*np.exp(1j*(phase_origine+7*np.pi/4))}
                
            case ("QAM", 16) :  mapping_table = {(0,0,0,0) : -3-3j, (1,0,0,0) : 3+3j, 
                                                (0,0,0,1) : -3-1j,  (1,0,0,1) : 3+1j,
                                                (0,0,1,0) : -3+3j,  (1,0,1,0) : 3-3j,
                                                (0,0,1,1) : -3+1j,  (1,0,1,1) : 3-1j,
                                                (0,1,0,0) : -1+3j,  (1,1,0,0) : 1-3j,
                                                (0,1,0,1) : -1+1j,  (1,1,0,1) : 1-1j,
                                                (0,1,1,0) : -1-3j,  (1,1,1,0) : 1+3j,
                                                (0,1,1,1) : -1-1j,  (1,1,1,1) : 1+1j}
                                                
                                                
                                                
                                                
                                               
                                                
                                                
                                              
                

            case _:
                mapping_table = None
                print(f"La modulation {self.nsymb}{self.modtype} n\"est pas implémentée")
        self.mapping_table = mapping_table
        
        return(mapping_table)

    

    
    
    def mapping(self, amplitude, phase_origine=0):
        """
        Fonction en charge de mapper à une liste de symbole numérique aux symboles de modulations .

        Paramètres:
        ----------
            amplitude: valeur maximum et minimum du symbole de modulation.

            phase origine: phase à l"origine du symbole de modulation complexe.
        ----------

        Renvoie symbs_mod: les symboles modulés
        """
        #crée la table de mapping grâce à la méthode Create_MP
        self.mapping_table = self.create_MP(amplitude, phase_origine)
        #associe les symboles numériques à la table de mapping grâce à une compréhension de liste
        symbs_mod=np.array([self.mapping_table[tuple(symb)] for symb in self.symbs_num])

        return(symbs_mod)
    



    
    def filtre_MF(self, symboles_mod, NbEchParSymb, type = "NRZ"):
        """
        Fonction en charge de générer un signal pseudo-continu à partir des symboles modulés.

        Paramètres:
        ----------
            symboles_mod: symboles modulés.

            NbEchParSymb: nombre d"échantillons nécessaires pour mettre en forme le signal.
        
            type: forme du signal voulue ex:(NRZ, Manchester, gaussienne, cosinus surélevé).
        ----------

        Renvoie signal_PAM: le signal pseudo-continu
        """
        self.nech = NbEchParSymb
        if type == "NRZ":
            signal_PAM = np.repeat(symboles_mod, NbEchParSymb)
        else:
            raise ValueError ("Le nombre d\"échantillons par symbole doit être un multiple de deux" )
        
        return (signal_PAM)
    




    def upconv(self, env_complexe, fp, te):
        """
        Fonction en charge de moduler l"enveloppe complexe sur une fréquence porteuse.

        Paramètres:
        ----------
        env_complexe: enveloppe complexe du signal modulé sur fréquence porteuse
        fp: fréquence porteuse.
        te: periode de l"enveloppe complexe.
        ----------

        Renvoie la partie réelle du signal modulé sur fréquence porteuse.
        """
        #Création de l"exponentielle complexe
        t = np.arange(0, len(env_complexe)*te, te)
        exp = np.exp(2j*np.pi*fp*t)

        #Translation de fréquence upconversion
        sig_analytique = env_complexe*exp
        sig_module = np.real(sig_analytique)

        return (sig_module)
    



    
    def filtre_rcv(self, signal_down, type = "butter", fc = 10, fe = 100, order = 3):
        """
        Fonction en charge de filtrer le signal PSK ou QAM  reçue.

        Paramètres:
        ----------
            signal_rcv: signal reçu après translation de fréquences.

            type: type de filtre (butter par défaut).

            fc: fréquence de coupure (10 par défaut).

            fe: fréquence d"échantillonage (100 par défaut).

            order: ordre du filtre (3 par défaut).
        ----------

        Renvoie le signal reçu filtré.
        """

        #Caractéristiques du filtre
        fcn = fc/(fe/2)
        
        #Création du filtre
        b, a = scipy.signal.butter(order, fcn, btype = "low", analog = False)
        
        #Application du filtre
        signal_filtre = 2*scipy.signal.filtfilt(b, a, signal_down)

        return (signal_filtre)
    




    def downsample(self, signal, downsampling, offset = 0,):
        """
        Fonction en charge de sous échantilloné le signal 

        Paramètres :
        ----------
            signal: signal pseudo-continu.

            downsampling: facteur de sous-échantillonage.

            offset: premier echantillon pris en compte parmis les n échantillons du symbole modulé.
        ----------

        Renvoie signal_down: le signal sous-échantilloné
        """

        if self.symb_type == "complexe":
            signal_down = np.array([], dtype = complex)
        else:
            signal_down = np.array([])
        for i in range(offset, len(signal), downsampling):
            signal_down = np.append(signal_down, signal[i])

        return (signal_down)



   



    def downconv(self, signal, fp, te, symb_type = "complexe"):
        """
        Fonction en charge de translater la fréquence du signal vers une fréquence plus basse (0).

        Paramètres:
        ----------
        signal: signal modulé sur fréquence porteuse.

        fp: fréquence porteuse du signal.

        te: periode d"échantillonage du recépteur.

        symb_type: type de symbole, réel pour les modulations ASK ou complexe
                   pour les modulations PSK et QAM.
        ----------

        """
        t = np.arange(0, len(signal)*te, te)
        real = np.cos(2*np.pi*fp*t)
        im = np.sin(2*np.pi*fp*t)
        exp = real -1j*im

        if symb_type == "complexe":
            signal_down = exp*signal
        else:
            signal_down = real*signal
        
        return (signal_down)
    
    



    def detection(self, signal_down):
        """
        Fonction en charge d"associer l"échantillon reçue en fonction du diagramme de constellation initial.

        Paramètres:
        ----------
            signal _down: signal desenchantilloné
        ----------

        Renvoie symbs_detect: les symboles modulés séléctionnés pour reproduire le les informations envoyées.
        """
        constellation = np.array([val for val in self.mapping_table.values()])
        if self.symb_type == "complexe":
            symbs_detect = np.array([min(constellation, key=lambda symb_mod:abs(np.square(np.real(symbr)-np.real(symb_mod))+np.square(np.imag(symbr)-np.imag(symb_mod)))) for symbr in signal_down])
        else:
            symbs_detect=np.array([min(constellation, key=lambda symb_mod:abs(symbr-symb_mod)) for symbr in signal_down])
        
        return (symbs_detect) 
    


    
    
    def demapping(self, symbs_rcv):
        """
        Fonction en charge de demapper une liste de symboles modulés aux symboles numériques.
        
        Paramètres:
        ----------
        symbs_rcv: symbole de modulation reçues après détection d"erreurs 
        ----------
        
        Renvoie les symboles numériques associés aux symboles modulés reçus.
        """
        demapping_table = {v : k for  k, v in self.mapping_table.items()}
        symbs_num = np.array([demapping_table[symb] for symb in symbs_rcv])
        bits_rcv = np.ravel(symbs_num)
        
        return (bits_rcv)
        
########################################################################################
########################################################################################
########################################################################################
##########                                                                  ############
##########                                                                  ############
##########                              MESURE                              ############
##########                                                                  ############
##########                                                                  ############
########################################################################################
########################################################################################
########################################################################################

class Mesure:
    """
    
    Classe permettant de faire toutes les mesures sur les signaux générés : DSP, diagramme de constellation, puissance, … 
    
    """
    


    @staticmethod
    def dsp(s, fe, type = "bilateral", unit = "dBm") :
        """
        Fonction en charge d"afficher la densité spectral d"un 
          Paramètre :
          ----------
            fe : fréquence d"échantillonage
            type : affichage mono ou bilatéral (bilatéral par défaut)
            unit : affichage en Volts efficace ou dBm (dBm par défaut)
            NB_points : Nombres de points du signal
        ----------
        """
        Nb_points = len(s)

        tfd = 1/Nb_points*np.fft.fft(s)

        if type == "bilateral" :
            fft = 1/Nb_points*np.fft.fftshift(np.fft.fft(s))
            mag = np.abs(fft)
            freqs = np.arange(-fe/2, fe/2, (fe/Nb_points))
        elif type == "monolateral" :
            fft = np.concatenate((tfd[0:1], 2*tfd[1:int(Nb_points/2)]))
            mag = np.abs(fft)
            freqs = np.arange(0, fe/2, (fe/Nb_points))
        else :
            raise ValueError ("Saisisser une représentation valide, monolateral ou bilateral par défaut")
        if unit  == "dBm" :
            dspp = 10*np.log10(np.square(mag/np.sqrt(2))/50*1000)
        elif unit == "eff" :
            dspp = mag/np.sqrt(2)
        else :
            print ("Saisissez une unité valide, (eff), (dBm par défaut)")
        
        return (dspp,freqs)
    



    
    @staticmethod
    def constellation(symb_mod, symbols=None, width = 8, title = "Diagramme de Constellation") :
        """"
        Paramètre :
        
            symb_mod : symbole de modulation sous forme d"un array numpy
            width : taille de la fenêtre du graphique
            title : titre de la fenêtre du graphique
        """

        fig, ax = plt.subplots(figsize = (width, width))
        ax.plot(np.real(symb_mod), np.imag(symb_mod), "o", mew = 6)
        # Annoter les symboles numériques au-dessus des points
        if symbols is not None :
            for idx, (real, imag) in enumerate(zip(np.real(symb_mod), np.imag(symb_mod))):
        # Convertir le symbole numérique en chaîne
                num_symbol = ''.join(map(str, symbols[idx]))
                ax.text(real, imag + 0.2, num_symbol, color="black", fontsize=12, ha='center', va='bottom')
        ax.set_xlim([-3.5, 3.5])
        ax.set_ylim([-3.5, 3.5])
        ax.set_ylabel("Partie imaginaire qk des \n symboles de modulation", fontsize = 16)
        ax.set_xlabel("Partie réelle ik des symbole de modulation", fontsize = 16)
        ax.set_title(title, fontsize = 16)
        ax.xaxis.set_tick_params(labelsize = 14)
        ax.yaxis.set_tick_params(labelsize = 14)
        ax.grid()
        plt.tight_layout()





    @staticmethod
    def comparaison(arr1, arr2):
        """
        Compare deux tableaux et renvoie le taux d"erreur.
        
        Le taux d"erreur est défini comme le pourcentage d"éléments qui diffèrent entre les deux tableaux.
        
        :param arr1: Premier tableau (array-like)
        :param arr2: Deuxième tableau (array-like)
        :return: Taux d"erreur (float)
        """
        # Vérifier si les deux tableaux ont la même longueur
        if len(arr1) != len(arr2):
            raise ValueError("Les tableaux doivent avoir la même longueur pour être comparés.")

        # Convertir les tableaux en numpy arrays (si ce ne sont pas déjà des numpy arrays)
        arr1 = np.array(arr1)
        arr2 = np.array(arr2)

        # Calculer le nombre d"éléments différents
        differences = np.sum(arr1 != arr2)

        # Calculer le taux d"erreur (en pourcentage)
        taux_erreur = (differences / len(arr1)) * 100

        return (taux_erreur)

########################################################################################
########################################################################################
########################################################################################
##########                                                                  ############
##########                                                                  ############
##########                               SOURCE                             ############
##########                                                                  ############
##########                                                                  ############
########################################################################################
########################################################################################
########################################################################################

class Source:
    """
        Classe permettant de générer des séquences binaires aleatoires ou des paquet ICMP
    """
    @staticmethod
    def random (nb_bits) :
        """
        Fonction de en charge de générer un vecteur de bits aléatoirement selon une loi binomial

        Paramètres :
        ----------
            nb_bits : Nombre de bits générés aléatoirement
        ----------
        """
        return np.random.binomial(1,0.5,nb_bits)
    




    @staticmethod
    def icmp(IP_DEST, IP_SRC = "192.168.1.1", MAC_SRC = "00:01:02:03:04:05", MAC_DST = "06:07:08:09:0A:0B", type = "echo-request") :
        """"
        Paramètres:
        ----------
            IP_DEST: IP de destination du paquet ICMP
            IP_SRC: IP source du paquet ICMP
            MAC_SRC: MAC source du paquet ICMP
            MAC_DST: MAC de destination du paquet ICMP
            type: envoie ICMP ou réponse ICMP
        ----------
        """
        frame_tr = Ether(src = MAC_SRC, dst = MAC_DST) / IP(src=IP_SRC, dst = IP_DEST)/ ICMP()
        frame_dec = list(bytes(frame_tr))
        frame_bin = []
        for val in frame_dec :
            #La fonction format converti une str au format désiré ici binaire "b" en remplissant de 0 pour avoir 8 bits
            z = format(val, "08b")
            #Sépare le mot de code sur 8 bits en une liste de 8 éléments et l"ajoute à la liste frame_bin
            frame_bin += list(z)

        bits_tr = np.array([int(x) for x in frame_bin])
      
        return (bits_tr)




    @staticmethod
    def decodage(trame) :
        """
        Paramètres:
        ----------
            trame: Trame Ethernet à decodé en format décimal après recépetion
        ----------
        """

        #Passage de données binaire en une matrice de 8 bits par ligne
        frame_bits8 = trame.reshape(int(len(trame)/8), 8)
        #Conversion des octets en leurs valeurs décimales
        frame_dec = np.packbits(frame_bits8)
        #Conversion des octets au format hexadecimal
        frame_bytes = frame_dec.tobytes()

        data = Ether(frame_bytes)

        return (data)

########################################################################################
########################################################################################
########################################################################################
##########                                                                  ############
##########                                                                  ############
##########                              CANAL                               ############
##########                                                                  ############
##########                                                                  ############
########################################################################################
########################################################################################
########################################################################################

class Canal:
    """
    Classe permettant de simuler un canal AWGN
    """

    @staticmethod
    def awgn(signal, mean, std):
        """
        Paramètres :
            signal : signal en entrée du canal
            mean : moyenne du bruit
            std : écart type
        """
        #Nombre d"échantillons du signal après filtre de mise en forme
        num_samples = len(signal)
        #Création du vecteur de bruit blanc gaussien
        noise = np.random.normal(mean, std, size = num_samples)
        #Addition du bruit blanc gaussien au signal
        signal_bruite = signal + noise

        return (signal_bruite)
    
