from utils.harmonization_utils import hut_calc_arc_len, hut_canonicalize_deg


class Sector:
    def __init__(self, start_deg, range_deg):
        self.__start_deg = start_deg
        self.__range_deg = range_deg
    
    def get_start_deg(self, offset=0.):
        return self.__start_deg + offset
    
    @property
    def range_deg(self):
        return self.__range_deg
    
    @property
    def centre_of_arc(self):
        return hut_canonicalize_deg(self.__start_deg + (self.__range_deg / 2.))
    
    @property
    def arc_len(self):
        return hut_calc_arc_len(self.__range_deg)
    
    def __str__(self):
        return f'SECT: [{self.__start_deg} - {self.__start_deg + self.__range_deg}]'
