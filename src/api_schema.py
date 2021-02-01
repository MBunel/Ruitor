"""
Fichier contenant l'ensemble des 
"""

from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, AnyUrl
from fastapi import File, UploadFile


# Types génériques
class Mnt(str, Enum):
    tt = "5"
    ttt = "50"
    tttt = "100"


# Types spatialisation
class Modifieur(BaseModel):
    """
    Classe trop cool
    """

    # Les modifieurs sont définis dans l'ontologie ORL. Pour
    # identifier le modifieur utrilisé il faut fournir son url
    uri: AnyUrl = Field(description="Uri du modifieur dans l'ontologie ORL")


class RelationLocalisation(BaseModel):
    """
    Documentation
    """

    # La relation spatiale est définie par une uri, qui permet
    # d'identifier le concept dans l'ontologie ORL. C'est dans cette
    # ontologie qu'est définie la méthode de spatialisation de la
    # relation de localisation
    uri: AnyUrl = Field(
        description="Uri de la relation de localisation dans l'ontologie ORL"
    )
    # La spatialisation peut être modifié par l'ajout d'un, ou
    # plusieurs modifieurs. L'emploi des modifieurs est totalement
    # facultatif.
    modifieurs: Optional[list[Modifieur]] = Field(
        description="Liste des modifieurs à appliquer à la relation de localisation"
    )


class Site(BaseModel):
    """
    Documentation
    """

    pass


class Indice(BaseModel):
    """
    Documentation
    """

    cible: Optional[str]
    relationLocalisation: RelationLocalisation
    site: Site
    # La confiance est une valeur que le secouriste peut définir pour
    # donner une indication sur sa croyance en la véracité de l'indice
    # de localisation.
    #
    # Cette valeur est optionelle. Si aucune valeur n'est fournie
    # l'indice est spatialisé avec une certitude maximale, 1.
    #
    # La valeur de la confiance doit être comprise dans l'intervalle
    # [0,1]
    confiance: Optional[float] = Field(description="Confiance", ge=0, le=1)


# Retour spatialisation


class Fuzzy:
    pass


# Types Fusion

## Corps Fusion
class Operateur(str, Enum):
    """Défini la famille d'opérateurs flous utilisés pour les opérations
    d'intersection et d'union inter-raster flous.

    Les opérateurs flous sont décrits dans les Chapitres 3 et 8 de la
    la thèse. Le changement des opérateurs de construction a une
    influence considérable sur la ZLC ou la ZLP obtenue. En cas de
    doute se référer au chapitre 8 de la thèse.

    **Bien que cela demeure possible, il n'est pas conseillé de changer
    d'opérateurs entre la spatialisation et la fusion.**

    ```"Zadeh"``` est le paramètre par défaut. Lorsque l'on utilise ce
    paramètre les intersections sont calculés à l'aide de la *t-norme*
    de Zadeh, dont la définition est la suivante :
    t-norme(a,b)=min(a,b) et les unions à l'aide de la t-conorme de
    Zadeh, dont la définition est : t-conorme(a,b)=max(a,b).

    Lorsque la valeur du paramètre est ```"Lukacewiz"``` alors les
    intersections sont calculées à l'aide de la t-norme de Lukacewiz,
    dont la définition est : t-norme(a,b) = max(a+b-1,0) et les union
    à l'aide de la t-conorme de Lukacewicz dont la définition est :
    t-conorme(a,b) = min(a+b,1).

    La valeur ```"Probabiliste"``` permet d'utiliser la t-norme
    probabiliste dont la définition est : t-norme(a,b)=a*b et la
    t-conorme probabiliste dont la définition est :
    t-conorme(a,b)=a+b-a*b.

    La valeur ```"Nilpotent"``` permet d'utiliser la t-norme
    nilpotente dont la définition est : t-norme(a,b)= min(a,b) si a+
    b>1, 0 sinon; et la t-conorme nipotente dont la définition est :
    t-conorme(a,b)=max(a,b) si a+b < 1, 1 sinon.

    La valeur ```"Drastique"``` permet d'utiliser la t-norme
    drastique, dont la définition est : t-norme(a,b) = b si a = 1, a
    si b = 1, 0 sinon; et la t-conorme probabiliste dont la définition
    est : t-conorme(a,b) = b si a = 0, a si b=0; 1 sinon.

    """

    zadeh = "Zadeh"
    lukacewicz = "Lukacewiz"
    probabiliste = "Probabiliste"
    nilpotent = "Nilpotent"
    drastique = "Drastique"


class EvaluationMetric(str, Enum):
    """Définition de la valeur retournée par l'évaluateur.

    **Cette fonctionalité est encore expérimentale, elle ne devrait pas
    être utilisée.**

    ```"Note"``` calcule une note, en fonction de l'évaluateur choisi.

    ```"Rank"``` calcule une note, en fonction de l'évaluateur choisi
    et retourne le rang des zones en fonctions de la valeur
    décroissante de cette note.

    ```"Zone"``` Renvoie l'id de chaque zone. Ce paramètre n'est
    destité qu'au débugage.

    """

    note = "Note"
    zone = "Zone"
    rank = "Rank"


class Evaluator(str, Enum):
    """Défini la méthode utilisée pour l'évaluation de la qualité.

    **Cette fonctionalité est encore expérimentale, elle ne devrait pas
    être utilisée.**

    ```"FIS"``` permet d'évaluer la qualité à l'aide d'un système d'inférence flou.

    ```"DST"``` permet d'évaluer la qualité à l'aide d'un évaluateur
    utilisant la théorie des fonctions de croyances (Beta).

    """

    fuzzy = "FIS"
    dst = "DST"


## Retour Fusion
