from functools import reduce
from itertools import groupby
from operator import itemgetter

from pathos.multiprocessing import ProcessingPool as Pool

import config


class AggregatorStrategy:

    def __init__(self, context):
        self.context = context
        self.pools = config.multiprocessing['pools']

    def _elem_reduce(self, function, values, pools=6, chuncks=12):
        return reduce(function, values)

    def _agg_objects(self, agg):
        res = self._elem_reduce(lambda x, y: x | y, agg.values())

        if config.log['verbosity'] >= 2:
            print("agg_obj : Done")

        return res


class FirstAggragator(AggregatorStrategy):
    def __init__(self, context):
        super().__init__(context)

    def _elem_reduce(self, function, values, pools=6, chuncks=12):
        return reduce(function, values)
        # Ne marche pas a refaire
        # _tempRes = []
        # p = Pool(processes=pools)
        # def _par_reduce(pool, function, values):
        #     def fun(x): return reduce(function, x)
        #     res = p.map(fun, chuncked(values, chuncks))
        #     return res
        # _tempRes.append(_par_reduce(p, function, valusq))
        # if len(_tempRes) > chuncks:
        #     _par_reduce(p, function, _tempRes)
        # else:
        #     return reduce(function, _tempRes)

    def compute(self):
        """
        Fonction pour l'initialisation du calcul
        """

        # Définition pool pour traitement //
        # des rasters
        sp_list = list(zip(*self.context.items()))

        # sp_list[1][0].compute()

        with Pool(processes=self.pools) as t:
            cmp_res = t.map(self.context.element_compute, sp_list[1])

        if config.log['verbosity'] >= 2:
            print("Compute : Done")

        cmp_dic = {k: v for k, v in zip(sp_list[0], cmp_res)}
        zou = self._agg_spa_rel(cmp_dic)
        zi = self._agg_objects_part(zou)
        zu = self._agg_objects(zi)

        if config.log['int_files']:
            print("writing tempfiles")
            for k, v in cmp_dic.items():
                f_name = "obj%s_part%s_rel%s" % k
                v.write("./_outTest/%s.tif" % f_name)

            for k, v in zou.items():
                f_name = "obj%s_part%s" % k
                v.write("./_outTest/%s.tif" % f_name)

        return zu

    def _agg_objects_part(self, agg):
        """
        """
        res = {}
        keysList = list(agg.keys())
        keysList.sort(key=itemgetter(0))

        grouper = groupby(keysList, key=itemgetter(0))
        for gr in grouper:
            val = itemgetter(*gr[1])(agg)
            try:
                res[gr[0]] = self._elem_reduce(lambda x, y: x | y, val)
            except TypeError:
                res[gr[0]] = val

        if config.log['verbosity'] >= 2:
            print("agg_obj_part : Done")

        return res

    def _agg_spa_rel(self, agg):
        """
        """
        res = {}

        keysList = list(agg.keys())
        keysList.sort(key=itemgetter(0, 1))

        grouper = groupby(keysList, key=itemgetter(0, 1))
        for gr in grouper:
            val = itemgetter(*gr[1])(agg)
            try:
                res[gr[0]] = self._elem_reduce(lambda x, y: x & y, val)
            except TypeError:
                res[gr[0]] = val

        if config.log['verbosity'] >= 2:
            print("agg_spa_rel : Done")

        return res