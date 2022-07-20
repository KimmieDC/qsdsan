#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  5 14:31:47 2021

@author: torimorgan
"""
import numpy as np
from warnings import warn
from qsdsan import SanUnit, Construction
from ._decay import Decay
from ..utils import load_data, data_path

__all__ = ('ECR',)

data_path += 'sanunit_data/_ECR_Reclaimer.tsv'


class ECR(SanUnit, Decay):
    '''
   Electrochemical treatment with chlorine dosing 

    Parameters
    ----------
    ins : WasteStream
        Waste for treatment, salt. 
    outs : Treated
        Treated waste, fugitive CH4, and fugitive N2O.
   
        
    References
    ----------
    .. 2019.06 Technical report for BMGF V3 _ CC 2019.06.13.pdf
    See Also
    --------
    :ref:`qsdsan.sanunits.Decay <sanunits_Decay>`
    
    '''
    
    def __init__(self, ID='', ins=None, outs=(), **kwargs):
        SanUnit.__init__(self, ID, ins, outs)
        
        data = load_data(path=data_path)
        for para in data.index:
            value = float(data.loc[para]['expected'])
            setattr(self, para, value)
        del data
        
        for attr, value in kwargs.items():
            setattr(self, attr, value)
    
    
    _N_ins = 3
    _N_outs = 3

#look up literature values for percentages typically removed by anaerobic/follow yalin/john's assumptions \
   
    def _run(self):
        waste, salt, HCl_acid = self.ins
        treated = self.outs[0]
        treated.copy_like(self.ins[0])

        salt.imass['NaCl'] = self.salt_dosing/7 #salt demand per day
        
      
        HCL_density = 1.2 #g/ml
        HCl_acid.imass['HCl'] = self.HCl_dosing/52/24/7 * HCL_density / 1000 #kg/h
        
        
                
#no replacement parts for the anaerobic tank and cleaning performed 
#throughout whole system is considered in TEA 


    def _design(self):
        design = self.design_results
        design['Metal'] = electrode_quant = self.electrode
        design['Pump'] = pump_quant = self.pump
        self.construction = ((Construction(item='Pump', quantity = pump_quant, quantity_unit = 'ea')),
                             (Construction(item='Metal', quantity = electrode_quant, quantity_unit = 'kg')))
        self.add_construction()
 
    def _cost(self):
        
        #purchase_costs is used for capital costs
        #can use quantities from above (e.g., self.design_results['StainlessSteel'])
        #can be broken down as specific items within purchase_costs or grouped (e.g., 'Misc. parts')
        self.purchase_costs['level_guage_cost'] = (self.level_guage_cost)
        self.purchase_costs['pump_cost'] = (self.pump_cost)
        self.purchase_costs['fan_cost'] = (self.fan_cost)
        self.purchase_costs['salt_dosing_device_cost'] = (self.salt_dosing_device_cost)
        self.purchase_costs['UPVC_pipe_cost'] = (self.UPVC_pipe_cost)
        self.purchase_costs['UPVC_electric_ball_cost'] = (self.UPVC_electric_ball_cost)
        self.purchase_costs['GAC_cost'] = (self.GAC_cost)
        self.purchase_costs['electrode_cost'] = (self.electrode_cost)
        self.purchase_costs['ECR_reactor_cost'] = (self.ECR_reactor_cost)
        self.purchase_costs['power_supply_cost'] = (self.power_supply_cost)
        self.purchase_costs['plastic_spraying_cabinent_cost'] = (self.plastic_spraying_cabinent_cost)
        
        
        self._BM = dict.fromkeys(self.purchase_costs.keys(), 1)
        
        #need to be a cost per hour
        ECR_replacement_parts_annual_cost = ((self.electrode_replacement_cost * self.electrode_life) + 
        (self.pump_cost * self.pump_life)+ 
        (self.level_guage_replacement_cost * self.level_guage_life) + 
        (self.GAC_cost * self.GAC_filter_life ) +
        (self.HCL_replacement_cost * self.HCL_life / 365 / 24) +
        (self.salt_replacement_cost / 7 / 24 ))
        
        self.add_OPEX =  (ECR_replacement_parts_annual_cost) / (365 * 24) # USD/hr (all items are per hour)
        
        #self.power_utility(self.power_demand * self.working_time)
        
        # costs associated with full time operators can be added in the TEA as staff
        # Yalin is looking into how to account for annual LCA impact of replacement parts based on lifetime