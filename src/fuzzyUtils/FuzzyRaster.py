"""
FuzzyRaster

Module décrivant la classe FuzzyRaster.

"""

from . import Fuzzyfiers
from . import FuzzyOperators

import numpy as np
import matplotlib.pyplot as pyplot

import rasterio


class FuzzyRaster:
    """Classe FuzzyRaster
    """

    default_fuzzy_operators_strategy = FuzzyOperators.ZadehOperators
    default_fuzzyfier_strategy = Fuzzyfiers.FuzzyfierMoreSpeeeeed

    def __init__(self, fuzzy_operators_strategy=None,
                 fuzzyfier_strategy=None, **kwargs):
        """Initialisation de l'objet

        :param fuzzy_operators_strategy: Strategie d'opérateurs flous
        :param fuzzyfier_strategy: Strategie de fuzzyfication

        :return: Une instance de FuzzyRaster
        """

        # Définition des opérateurs flous
        if fuzzy_operators_strategy:
            self.fuzzy_operators = fuzzy_operators_strategy(self)
        else:
            self.fuzzy_operators = self.default_fuzzy_operators_strategy(self)

        # Stratégie de fuzzyfication
        if fuzzyfier_strategy:
            self.fuzzyfier = fuzzyfier_strategy(self)
        else:
            self.fuzzyfier = self.default_fuzzyfier_strategy(self)

        # Construction raster flou
        if 'raster' in kwargs:
            raster = kwargs.get('raster')
            self._init_from_rasterio(raster)
        elif 'array' in kwargs:
            array = kwargs.get('array')
            meta = kwargs.get('meta', None)
            self._init_from_numpy(array, meta)
        else:
            raise ValueError("Bad parameters")

        # Fuzzyfication
        if 'fuzzyfication_parameters' in kwargs:
            fuzzyfication_parameters = kwargs.get('fuzzyfication_parameters')
            self.fuzzyfication(fuzzyfication_parameters)

    def fuzzyfication(self, parameters):
        """
        Fonction de fuzzyfication.

        Prend en paramètre une liste de tuples dont la première valeur est un seuil
        et la seconde le degré flou qui y est associé. 

        :param parameters: liste de tuples contenant les paramètres de fuzzyfication
        :type parameters: liste de 2-uples

        :return: None	
        """
        self.fuzzy_values = self.fuzzyfier.fuzzyfy(
            self.crisp_values, parameters)
        self.values = self.fuzzy_values

    def _init_from_rasterio(self, raster):
        """
        Fonction d'initialisation à partir d'un raster rasterio	
        """

        self.crisp_values = raster.read()
        self.values = self.crisp_values[0]
        self.raster_meta = raster.meta

    def _init_from_numpy(self, array, meta=None):
        """
        Fonction d'initialisation à partir d'un array numpy	
        """

        self.crisp_values = array
        self.values = self.crisp_values

        if meta:
            self.raster_meta = meta
        else:
            try:
                count = array.shape[2]
            except IndexError:
                count = 1

            self.raster_meta = {
                'count': count,
                'crs': None,
                'driver': 'GTiff',
                'dtype': array.dtype,
                'height': array.shape[0],
                'width': array.shape[1],
                'nodata': -99999.0,
                'transform': None
            }

    # @property
    # def values(self):
    #   return self.values[self.values != self.raster_meta['nodata']]

    def plot(self):
        pyplot.matshow(self.values, cmap='gray')

    def summarize(self):
        rastmin = self.values.min()
        rastmed = np.median(self.values)
        rastmax = self.values.max()

        description_string = """
        min    : {}
        median : {}
        max    : {}        
        -------------------------------
        {}
        -------------------------------
        {}
        """.format(rastmin, rastmed, rastmax, self.fuzzy_operators, self.fuzzyfier)

        print(description_string)

    def __and__(self, other):
        """
        blabla	
        """
        # La gestion des opérations inter-raster est pas top à revoir
        # -> construire les paramètres du raster construit
        return FuzzyRaster(array=self.fuzzy_operators.norm(other),
                           meta=self.raster_meta,
                           fuzzy_operators_strategy=self.fuzzy_operators.__class__)

    def __or__(self, other):
        return FuzzyRaster(array=self.fuzzy_operators.conorm(other),
                           meta=self.raster_meta,
                           fuzzy_operators_strategy=self.fuzzy_operators.__class__)

    def write(self, path, write_params=None):
        """
        Enregistrement du raster

        Par défaut, la fonction utilise les paramètres de self.raster_meta

        :param path: Emplacement du fichier
        :param write_params: Paramètres d'enregistrement
        """

        if not write_params:
            write_params = self.raster_meta

        # Ecriture du raster avec les paramètres initaux
        with rasterio.open(path, 'w', **write_params) as dst:
            dst.write(self.values)