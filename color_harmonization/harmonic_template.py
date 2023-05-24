import copy

from color_harmonization.harmonic_sector import Sector
from utils.harmonization_utils import hut_calc_arc_len, hut_canonicalize_deg


# the base class for harmonic templates
class HarmonicTemplate_Base:
    def __init__(self):
        self._sector_list = []
    
    def add_sector(self, start_deg, range_deg):
        self._sector_list.append(Sector(start_deg, range_deg))
    
    @property
    def sectors(self):
        return copy.deepcopy(self._sector_list)
    
    # check if the given degree w/ an alpha (offset) is in any sectors
    def is_in(self, inp_deg, alpha=0.):
        inp_deg = hut_canonicalize_deg(inp_deg)
        for sector in self._sector_list:
            start = sector.get_start_deg() + alpha
            start = hut_canonicalize_deg(start)
            end = start + sector.range_deg
            if end < 180:
                if start <= inp_deg <= end:
                    return True, copy.deepcopy(sector)
            else:
                end = hut_canonicalize_deg(end)
                if start <= inp_deg or inp_deg <= end:
                    return True, copy.deepcopy(sector)
        return False, None
    
    # obtain the minimal distance and moving direction from the given degree w/ an alpha (offset) to any sectors
    def get_min_dis(self, inp_deg, alpha=0.):
        # print(inp_deg, alpha, end=' -> ')
        inp_deg = hut_canonicalize_deg(inp_deg)
        _is_in, _ = self.is_in(inp_deg, alpha=alpha)
        min_dis = float('inf')
        move_dir = 0
        for sector in self._sector_list:
            start = sector.get_start_deg() + alpha
            start = hut_canonicalize_deg(start)
            end = start + sector.range_deg
            l_to_start = hut_calc_arc_len(inp_deg, start)
            l_to_end = hut_calc_arc_len(inp_deg, end)
            if l_to_start < min_dis:
                min_dis = l_to_start
                move_dir = -1 if _is_in else 1
            if l_to_end < min_dis:
                min_dis = l_to_end
                move_dir = 1 if _is_in else -1
        # print(min_dis)
        return min_dis, move_dir

    def find_nearest_sector_by_certain_dir(self, inp_deg, alpha, move_dir):
        assert move_dir in (0, 1,)
        _is_in, sect = self.is_in(inp_deg, alpha=alpha)
        if _is_in:
            return 0, sect
        inp_deg = hut_canonicalize_deg(inp_deg)
        min_dis = float('inf')
        ret_sect = None
        for sector in self._sector_list:
            start = sector.get_start_deg() + alpha
            start = hut_canonicalize_deg(start)
            # clockwisely
            if move_dir == 1:
                _dis = 180. - (inp_deg - start) if start < inp_deg else start - inp_deg
            # counterclockwisely
            else: # elif move_dir == 0:
                end = hut_canonicalize_deg(start + sector.range_deg)
                _dis = inp_deg - end if end < inp_deg else 180. - (end - inp_deg)
            if _dis < min_dis:
                min_dis = _dis
                ret_sect = sector
        return hut_calc_arc_len(min_dis), copy.deepcopy(ret_sect)
    
# i-type
class Template_i(HarmonicTemplate_Base):
    def __init__(self):
        super().__init__()
        self.add_sector(start_deg=-4.5, range_deg=9.)


# V-type
class Template_V(HarmonicTemplate_Base):
    def __init__(self):
        super().__init__()
        self.add_sector(start_deg=-23.4, range_deg=46.8)


# L-type
class Template_L(HarmonicTemplate_Base):
    def __init__(self):
        super().__init__()
        self.add_sector(start_deg=-4.5, range_deg=9.)
        self.add_sector(start_deg=-23.4 + 45., range_deg=46.8)


# I-type
class Template_I(HarmonicTemplate_Base):
    def __init__(self):
        super().__init__()
        self.add_sector(start_deg=-4.5, range_deg=9.)
        self.add_sector(start_deg=-4.5 + 90., range_deg=9.)


# T-type
class Template_T(HarmonicTemplate_Base):
    def __init__(self):
        super().__init__()
        self.add_sector(start_deg=0., range_deg=90.)


# Y-type
class Template_Y(HarmonicTemplate_Base):
    def __init__(self):
        super().__init__()
        self.add_sector(start_deg=-23.4, range_deg=46.8)
        self.add_sector(start_deg=-4.5 + 90., range_deg=9.)


# X-type
class Template_X(HarmonicTemplate_Base):
    def __init__(self):
        super().__init__()
        self.add_sector(start_deg=-23.4, range_deg=46.8)
        self.add_sector(start_deg=-23.4 + 90., range_deg=46.8)


# no N-type implemented (nor discussed in the original paper)
