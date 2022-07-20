#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
QSDsan: Quantitative Sustainable Design for sanitation and resource recovery systems

This module is developed by:
    Yalin Li <mailto.yalin.li@gmail.com>
    Joy Zhang <joycheung1994@gmail.com>
    Lewis Rowles <stetsonsc@gmail.com>
    Hannah Lohman <hlohman94@gmail.com>
    Tori Morgan <vlmorgan@illinois.edu>
    Shion Watabe <swatabe2@illinois.edu>
    Lane To <lane20@illinois.edu>
    Smiti Mittal <smitimittal@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/QSDsan/blob/main/LICENSE.txt
for license details.
'''

# **NOTE** PLEASE ORDER THE MODULES ALPHABETICALLY #

# Units that do not rely on other units
from ._abstract import *
from ._carbonizer_base import *
from ._clarifier import *
from ._combustion import *
from ._controlling import *
from ._crop_application import *
from ._decay import *
from ._dynamic_influent import *
from ._electrochemical_cell import *
from ._encapsulation_bioreactor import *
from ._excretion import *
from ._grinder import *
from ._heat_exchanging import *
from ._housing import *
from ._ion_exchanges import *
from ._lumped_cost import *
from ._pollution_control_device import *
from ._pumping import *
from ._screening import *
from ._sludge_thickening import *
from ._struvite_precipitation import *
from ._suspended_growth_bioreactor import *
from ._tanks import *
from ._trucking import *


# Units that rely on other units
from ._activated_sludge_process import *
from ._anaerobic_reactors import *
from ._internal_circulation_rx import *
from ._lagoon import *
from ._membrane_bioreactors import *
from ._polishing_filter import *
from ._sedimentation import *
from ._toilets import *
from ._treatment_beds import *

from ._murt_toilet import *
from ._primary_reclaimer import *
from ._ultrafiltration_reclaimer import *
from ._ion_exchange_reclaimer import *
from ._ecr_reclaimer import *
from ._housing_reclaimer import *
from ._system_reclaimer import *
from ._sludge_pasteurization_reclaimer import*
from ._solar_reclaimer import*
from ._primaryMBR import*
from ._aerobic_ES_bio import*
from ._anaerobic_ES_bio import*
from ._MBR import*
from ._MBR_ECR import*
from ._recycling_controls import*
from ._solar import*

from ._scg_zyclonic_control_box import *
from ._scg_zyclonic_separator import *
from ._scg_zyclonic_equalizer_tank import *
from ._scg_zyclonic_aquonic1000 import *
from ._scg_zyclonic_treated_water_tank import *
from ._scg_zyclonic_system_pipeline import *
from ._scg_zyclonic_solar import *

from ._ng_anmbr import  *
from ._ng_chlorination import *
from ._ng_controls import  *
from ._ng_foundation import  *
from ._ng_gridtied_power import  *
from ._ng_housing import *
from ._ng_ion_exchange import *
from ._ng_photovoltaic_power import  *
from ._ng_pretreatment import  *
from ._ng_sludge_pasteurization import*

# From then on the order doesn't matter, listed alphabetically
from . import (
        _abstract,
        _activated_sludge_process,
        _anaerobic_reactors,
        _carbonizer_base,
        _clarifier,
        _combustion,
        _controlling,
        _crop_application,
        _decay,
        _dynamic_influent,
        _electrochemical_cell,
        _encapsulation_bioreactor,
        _excretion,
        _grinder,
        _housing,
        _heat_exchanging,
        _internal_circulation_rx,
        _ion_exchanges,
        _lagoon,
        _lumped_cost,
        _membrane_bioreactors,
        _ng_anmbr,
        _ng_chlorination,
        _ng_controls,
        _ng_foundation,
        _ng_gridtied_power,
        _ng_housing,
        _ng_ion_exchange,
        _ng_photovoltaic_power,
        _ng_pretreatment,
        _ng_sludge_pasteurization,
        _polishing_filter,
        _pollution_control_device,
        _pumping,
        _scg_zyclonic_control_box,
        _scg_zyclonic_separator,
        _scg_zyclonic_equalizer_tank,
        _scg_zyclonic_aquonic1000,
        _scg_zyclonic_treated_water_tank,
        _scg_zyclonic_system_pipeline,
        _scg_zyclonic_solar,
        _screening,
        _sedimentation,
        _sludge_thickening,
        _struvite_precipitation,
        _suspended_growth_bioreactor,
        _tanks,
        _toilets,
        _treatment_beds,
        _trucking,
        _murt_toilet,
        _primary_reclaimer,
        _ultrafiltration_reclaimer,
        _ion_exchange_reclaimer,
        _ecr_reclaimer,
        _housing_reclaimer,
        _system_reclaimer,
        _sludge_pasteurization_reclaimer,
        _solar_reclaimer,
        _primaryMBR,
        _aerobic_ES_bio,
        _anaerobic_ES_bio,
        _MBR,
        _MBR_ECR,
        _recycling_controls,
        _solar,
        )


__all__ = (
        *_abstract.__all__,
        *_activated_sludge_process.__all__,
        *_anaerobic_reactors.__all__,
        *_carbonizer_base.__all__,
        *_clarifier.__all__,
        *_combustion.__all__,
        *_controlling.__all__,
        *_crop_application.__all__,
        *_decay.__all__,
        *_dynamic_influent.__all__,
        *_electrochemical_cell.__all__,
        *_encapsulation_bioreactor.__all__,
        *_excretion.__all__,
        *_grinder.__all__,
        *_housing.__all__,
        *_heat_exchanging.__all__,
        *_internal_circulation_rx.__all__,
        *_ion_exchanges.__all__,
        *_lagoon.__all__,
        *_lumped_cost.__all__,
        *_membrane_bioreactors.__all__,
        *_ng_anmbr.__all__,
        *_ng_chlorination.__all__,
        *_ng_controls.__all__,
        *_ng_foundation.__all__,
        *_ng_gridtied_power.__all__,
        *_ng_housing.__all__,
        *_ng_ion_exchange.__all__,
        *_ng_photovoltaic_power.__all__,
        *_ng_pretreatment.__all__,
        *_ng_sludge_pasteurization.__all__,
        *_polishing_filter.__all__,
        *_pollution_control_device.__all__,
        *_pumping.__all__,
        *_scg_zyclonic_control_box.__all__,
        *_scg_zyclonic_separator.__all__,
        *_scg_zyclonic_equalizer_tank.__all__,
        *_scg_zyclonic_aquonic1000.__all__,
        *_scg_zyclonic_treated_water_tank.__all__,
        *_scg_zyclonic_system_pipeline.__all__,
        *_scg_zyclonic_solar.__all__,
        *_screening.__all__,
        *_sedimentation.__all__,
        *_sludge_thickening.__all__,
        *_struvite_precipitation.__all__,
        *_suspended_growth_bioreactor.__all__,
        *_tanks.__all__,
        *_toilets.__all__,
        *_treatment_beds.__all__,
        *_trucking.__all__,
        *_murt_toilet.__all__,
        *_primary_reclaimer.__all__,
        *_ultrafiltration_reclaimer.__all__,
        *_ion_exchange_reclaimer.__all__,
        *_ecr_reclaimer.__all__,
        *_housing_reclaimer.__all__,
        *_system_reclaimer.__all__,
        *_sludge_pasteurization_reclaimer.__all__,
        *_solar_reclaimer.__all__,
        *_primaryMBR.__all__,
        *_aerobic_ES_bio.__all__,
        *_anaerobic_ES_bio.__all__,
        *_MBR.__all__,
        *_MBR_ECR.__all__,
        *_recycling_controls.__all__,
        *_solar.__all__,
        )