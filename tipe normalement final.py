##                  Importation des modules 

from random import random
import time

##                  Déclaration des constantes

oo = 10**9
#durée perdue lors de l'embarquement d'un piéton dans une voiture (en secondes )
DUREE_EMBARQUEMENT = 10
#pourcentage du temps minimal que l'on peut rajouter au maximum sans que le piéton n'abandonne
POURCENTAGE_ACCEPTANCE = 0.1
#vitesse moyenne des voitures en km.h-1
VITESSE_MOYENNE_VOITURE = 30
#durée départ piéton
DUREE_ATTENTE_MAX_PIETON = 300


##                  Lecture de l'entrée 

#récupération des coordonnées de chaque intersection

def recup_coord( file ):
    fichier = open(file,"r")
    coord_noeud = fichier.readlines()
    fichier.close()
    return  list(map(int,"".join(coord_noeud).split( ) ) )
    
#lecture des coordonnées des intersections
x_coord = recup_coord("xxx.txt")
y_coord = recup_coord("yyy.txt")
nbIntersection = len( x_coord )                                            

#lecture du graphe lié à la carte
carte = []
fichier = open("TIPE voisin.txt","r")
for ligne in fichier.readlines():
    carte += [ list(map(int,ligne.split(" ")[:-1] ) ) ]
fichier.close()


#lecture des données
donnee = []
fichier = open("TIPE donnees journee 2.txt","r")
for ligne in fichier.readlines():
    donnee += [ list(map(int,ligne.split(" ") ) ) ]
fichier.close()


###                 Calcul du plus court chemin


def plusCourtChemin( InterDepart, InterArrivee ,vitesse):
    #définie temps minimum d'accès à une intersection
    tempsAccesParIntersection = [ oo for i in range( nbIntersection ) ]
    tempsAccesParIntersection[InterDepart] = 0
    
    #définit la place d'un noeud dans un tas
    placeInterDansTas = [ i + 2 for i in range(0 ,InterDepart) ] + [1] + [ i + 1 for i in range(InterDepart + 1 ,nbIntersection ) ]
    
    #création tas ( commence au noeud 1)
    tas = [-1 , InterDepart ] + [ i for i in range(0 ,InterDepart ) ] + [i for i in range(InterDepart + 1 ,nbIntersection ) ]

    #procedure de remise à jour du tas binaire
    def rafraichit( n ):
        NoeudG = n * 2
        NoeudD = NoeudG + 1
        NoeudMin = n
        if ( NoeudG < len(tas) ) and ( tempsAccesParIntersection[ tas[ NoeudG ] ] < tempsAccesParIntersection[ tas[ NoeudMin ] ] ): NoeudMin = NoeudG
        if ( NoeudD < len(tas) ) and ( tempsAccesParIntersection[ tas[ NoeudD ] ] < tempsAccesParIntersection[ tas[ NoeudMin ] ] ): NoeudMin = NoeudD
        while n != NoeudMin:
            #échange
            placeInterDansTas[ tas[n] ], placeInterDansTas[ tas[NoeudMin] ] = NoeudMin, n
            tas[n], tas[ NoeudMin ] = tas[ NoeudMin ], tas[n]
            #on recommence avec le nouveau noeud
            n = NoeudMin
            NoeudG = n * 2
            NoeudD = NoeudG + 1
            if ( NoeudG < len(tas) ) and ( tempsAccesParIntersection[ tas[ NoeudG ] ] < tempsAccesParIntersection[ tas[ NoeudMin ] ] ): NoeudMin = NoeudG
            if ( NoeudD < len(tas) ) and ( tempsAccesParIntersection[ tas[ NoeudD ] ] < tempsAccesParIntersection[ tas[ NoeudMin ] ] ): NoeudMin = NoeudD
        return ;   
    
    #fonction extraction du minimum du tas
    def extractionMinimum():
        minimum = tas[1]
        tas[1]  = tas.pop()
        placeInterDansTas[ tas[1] ] = 1
        placeInterDansTas[minimum] = -1
        rafraichit(1)
        return minimum
        
    def diminueTemps(inter, dist):
        tempsAccesParIntersection[inter] = dist
        n = placeInterDansTas[inter]
        NoeudP = n // 2
        while n != 1 and ( tempsAccesParIntersection[ tas[ NoeudP ] ] > tempsAccesParIntersection[ tas[n] ] ):
            placeInterDansTas[ tas[n] ], placeInterDansTas[ tas[NoeudP] ] = NoeudP, n
            tas[n], tas[NoeudP] = tas[NoeudP], tas[n]  
            n = NoeudP          
            NoeudP = n // 2   
        return ;
        
    #Dijkstra
    predecesseur = [-1 for i in range(nbIntersection) ]
    while (tas[1] != InterArrivee):
        inter = extractionMinimum()
    
        for v in range(0,nbIntersection):
            if ( carte[inter][v] != 0 ) and ( tempsAccesParIntersection[v] > tempsAccesParIntersection[inter] + carte[inter][v] ):
                diminueTemps( v, tempsAccesParIntersection[inter] + carte[inter][v] )
                predecesseur[v] = inter
    
    #retourne résultats
    chemin = []
    p = InterArrivee
    while predecesseur[p] != -1:
        chemin += [p]
        p= predecesseur[p]
    chemin.append( InterDepart )
    return ( ( 10*tempsAccesParIntersection[InterArrivee]/ (3.6 * vitesse) ) ,  chemin[::-1]  )            


##                  Graphe matching  


def rafraichitGraphMatching():
    correspondances = [ [] for i in range(nbVoiture) ]
    #recherche du temps minimum
    for p in range(nbPieton):
        tempsVoitures = [-1] * nbVoiture
        tempsMin = oo
        for v in range(nbVoiture):
            tempsVoitures[v] = plusCourtChemin( lieuVoiture[v], pietons[p][0], VITESSE_MOYENNE_VOITURE )[0] + DUREE_EMBARQUEMENT + plusCourtChemin( pietons[p][0], pietons[p][1],VITESSE_MOYENNE_VOITURE )[0]
            tempsMin = min( tempsMin, tempsVoitures[v] )
            
        tempsMax = int( ( 1 + POURCENTAGE_ACCEPTANCE ) * tempsMin )
        for v in range(nbVoiture):
            if ( tempsVoitures[v] <= tempsMax and tempsVoitures[v] != -1 ):
                correspondances[v].append( p )


    return correspondances

##                  Algorithme HopCroft-Karp 

def matching( correspondances ):
    voiture_utilisee = [ False ] * nbVoiture
    voiture_associee_pieton = [-1] * nbPieton
    visited = [False] * nbVoiture
    
    
    def chercheDistanceMinimale():
        distanceMinimale = 0
        pile = []
        for v in range(nbVoiture):
            if not voiture_utilisee[v]:
                pile.append( (v,0) )
                visited[v] = True
        
        while pile != [] and ( distanceMinimale == 0 ):
            (v1,d) = pile.pop()
            for p in correspondances[v1]:
                v2 = voiture_associee_pieton[p]
                if (v2 >= 0) and not visited[v2]:
                    visited[v2] = True
                    pile.append( ( v2,d+1 ) )
                elif (v2 < 0):
                    distanceMinimale = d
        return distanceMinimale
    
    def chercheCheminAmeliorant(v1,d,dmax): #dmax représente la distance maximale acceptable
        visited[v1] = True
        for p in correspondances[v1]:
            v2 = voiture_associee_pieton[p]
            #si on finit sur une voiture libre ou non visitée avec la bonne distance et aboutissant à une amélioration
            #inférieur à dmax car sinon pour les coups d'avant on ne pourrait pas rentrer dans la récursion
            if ( v2 < 0 ) or ( not visited[v2] and ( d <= dmax ) and chercheCheminAmeliorant(v2,d+1,dmax) ):
                voiture_associee_pieton[p] = v1
                voiture_utilisee[v1] = True
                return True
        return False
        
    processusTermine = False
    while not processusTermine:
        processusTermine = True
        visited = [False] * nbVoiture
        dmax = chercheDistanceMinimale()
        visited = [False] * nbVoiture
        
        for v in range( nbVoiture ):
            if not voiture_utilisee[v] and chercheCheminAmeliorant(v,0,dmax):
                processusTermine = False
                
    return voiture_associee_pieton



##                  Corps du programme 

n = len( donnee[0] )

pas = donnee[0][1]

list_resul = [ "Total_de_piétons_: Total_de_piétons_pris_: Temps_de_trajet_moyen_: Temps_d'attente_moyen_:\n" ]

nb_voit_deb = 1

nb_voit_fin = 50


for it in range( nb_voit_deb , nb_voit_fin + 1 , 1 ):  #itération par rapport au nombre de voitures
    
    Total_piet_pris = 0
    Total_piet = 0

    Total_voit = 0

    nbVoiture_debut = it
    lieuVoiture_dispo = [ ( 277 , 0 ) for i in range(nbVoiture_debut) ]    # noeuds 76, 77, 78, 79, 163, 237 isolés


    temps_attente = 0
    somme_des_temps = 0

    for i in range( n ): #itérations par rapport aux temps
        
        nbPieton = donnee[1][i]
        pietons = []
        lieuVoiture = []
        liste_ancienne_voit = []
    
    
        for j in range( nbPieton ) :
            pietons.append( ( donnee[2][ Total_piet + j ] , donnee[3][ Total_piet + j ] ) )
        
        nbVoiture = 0
        
        for i in range( len( lieuVoiture_dispo ) ) :
            if lieuVoiture_dispo[i][1] <= 0 :
                lieuVoiture = [ lieuVoiture_dispo[i][0] ] + lieuVoiture
                lieuVoiture_dispo[i] = ( lieuVoiture_dispo[i][0] , 0 )
                nbVoiture += 1
                liste_ancienne_voit = [i] + liste_ancienne_voit  #correspondance entre les voitures et voitures dispo
            else:
                lieuVoiture_dispo[i] = ( lieuVoiture_dispo[i][0] , lieuVoiture_dispo[i][1] - pas )
                
                
        
        
        voiture_associee_pieton = matching( rafraichitGraphMatching() ) 
    
        
        for p,v in enumerate( voiture_associee_pieton ):
            if v != -1:
                p1 = plusCourtChemin( lieuVoiture[v], pietons[p][0], VITESSE_MOYENNE_VOITURE )
                p2 = plusCourtChemin( pietons[p][0], pietons[p][1], VITESSE_MOYENNE_VOITURE )
                
                temps_mis = ( p1[0] + p2[0] ) / 60
                
                temps_attente += p2[0] / 60
                
                lieuVoiture_dispo[ liste_ancienne_voit [v] ] = ( lieuVoiture_dispo[ liste_ancienne_voit [v] ][0] , temps_mis )
                somme_des_temps += temps_mis
        

        
        for el in voiture_associee_pieton :
            if el != -1 :
                Total_piet_pris += 1
                
        Total_piet += nbPieton
        Total_voit += nbVoiture


    moy = somme_des_temps / Total_piet_pris
    

    l1 = [ str( Total_piet ) , str( Total_piet_pris ) , str( moy ) , str( temps_attente / Total_piet_pris ) ]

    list_resul.append(" ".join( l1 ) +  "\n")
    
    print( str( ( it - nb_voit_deb + 1 ) / (nb_voit_fin - nb_voit_deb + 1) * 100) + " %" )  #affichage de la progression de l'algorithme





fich = open( "TIPE resul 3.txt" , "a" )   #stockage des résultats

fich.writelines( list_resul )

fich.close()





