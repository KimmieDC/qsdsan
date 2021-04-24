#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
QSDsan: Quantitative Sustainable Design for sanitation and resource recovery systems

This module is developed by:
    Yalin Li <zoe.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/QSDsan/blob/main/LICENSE.txt
for license details.
'''


# %%

import pandas as pd
from warnings import warn
from thermosteam.utils import copy_maybe, registered
from . import currency, SanStream, WasteStream, ImpactIndicator
from ._units_of_measure import auom, parse_unit
from .utils.formatting import format_number as f_num

# indicators = ImpactIndicator.get_all_indi
isinstance = isinstance
getattr = getattr

__all__ = ('ImpactItem', 'StreamImpactItem')

def get_source_item(item):
    return item if not item.source else item.source

@registered(ticket_name='Item')
class ImpactItem:
    '''
    A class for calculation of environmental impacts.
    
    Parameters
    ----------
    ID : str
        ID of the impact item. If no ID is provided, this item will not be
        saved in the ImpactItem dict.
    functional_unit : str
        Functional unit of the impact item.
    price : float
        Price of the item per functional unit.
    price_unit : str
        Unit of the price.
    source : ImpactItem
        If provided, all attributions and properties of this impact item will
        be copied from the provided source.
    register : bool
        Whether to add to the registry.
    indicator_CFs : kwargs
        Impact indicators and their characteriziation factors (CFs),
        can be in the form of str=float or str=(float, unit).
    
    Tip
    ---
    :class:`ImpactItem` should be used for environmental impacts associated with
    construction and transportation.
    For impacts associated with streams (e.g., chemicals, wastes, emissions),
    use :class:`StreamImpactItem` instead.


    Examples
    --------
    Firstly make impact indicators.
    
    >>> import qsdsan as qs
    >>> GWP = qs.ImpactIndicator('GlobalWarming', alias='GWP', unit='kg CO2-eq')
    >>> FEC = qs.ImpactIndicator('FossilEnergyConsumption', alias='FEC', unit='MJ')
    
    We can make impact items in different ways.
    
    >>> Steel = qs.ImpactItem('Steel', 'kg', GWP=2.55)
    >>> Steel.show()
    ImpactItem      : Steel [per kg]
    Price           : 0 USD
    ImpactIndicators:
                               Characterization factors
    GlobalWarming (kg CO2-eq)                      2.55
    >>> # Unit will be automatically converted to match the unit of the impact indicator
    >>> Electricity = qs.ImpactItem('Electricity', functional_unit='kWh',
    ...                             GWP=(480, 'g CO2-eq'), FEC=(5926, 'kJ'))
    >>> Electricity.show()
    ImpactItem      : Electricity [per kWh]
    Price           : 0 USD
    ImpactIndicators:
                                  Characterization factors
    GlobalWarming (kg CO2-eq)                         0.48
    FossilEnergyConsumption (MJ)                      5.93
    >>> # Note that 5.93 appears instead of 5.926 is for nicer print
    >>> Electricity.CFs
    {'GlobalWarming': 0.48, 'FossilEnergyConsumption': 5.926}
    >>> # Items without an ID cannot be added to the registry.
    >>> CO2 = qs.ImpactItem(functional_unit='kg', GWP=1, register=True)
    Traceback (most recent call last):
        ...
    ValueError: Cannot register an impact item without an ID.    
    >>> qs.ImpactItem.get_all_items()
    [<ImpactItem: Electricity>, <ImpactItem: Steel>]

    You can make copies of impact items and choose to link to the source or not.
    
    >>> Steel2 = Steel.copy('Steel2', set_as_source=True, register=True)
    >>> Steel2.CFs['GlobalWarming']
    2.55
    >>> Steel3 = Steel.copy('Steel3', set_as_source=False, register=False)
    >>> Steel3.CFs['GlobalWarming']
    2.55
    
    Once linked, CFs of the copy will update with the source (it works vice versa).
    
    >>> Steel.CFs['GlobalWarming'] = 2
    >>> Steel.CFs['GlobalWarming']
    2
    >>> Steel2.CFs['GlobalWarming']
    2
    >>> Steel3.CFs['GlobalWarming']
    2.55
    
    Manage the registry.
    
    >>> qs.ImpactItem.get_all_items()
    [<ImpactItem: Electricity>, <ImpactItem: Steel>, <ImpactItem: Steel2>]
    >>> Steel2.deregister()
    The impact item "Steel2" has been removed from the registry.
    >>> Steel3.register()
    The impact item "Steel3" has been added to the registry.
    >>> qs.ImpactItem.get_all_items()
    [<ImpactItem: Electricity>, <ImpactItem: Steel>, <ImpactItem: Steel3>]
    >>> qs.ImpactItem.clear_registry()
    All impact items have been removed from registry.
    '''
    
    _items = {}    
    
    __slots__ = ('_ID', '_functional_unit', '_price', '_CFs', '_source',
                 '_registered')
    
    def __init__(self, ID=None, functional_unit='kg', price=0., price_unit='',
                 source=None,
                 # register=True,
                 **indicator_CFs):
        
        self._register(ID)
        # self._ID = ID
        # self._registered = register
        
        if source:
            self.source = source
        else:
            self._source = None
            self._functional_unit = auom(functional_unit)
            self._update_price(price, price_unit)
            self._CFs = {}
            for indicator, value in indicator_CFs.items():
                try:
                    CF_value, CF_unit = value # unit provided for CF
                    self.add_indicator(indicator, CF_value, CF_unit)
                except:
                    self.add_indicator(indicator, value)
            if register:
                if ID:
                    if ID in self._items.keys():
                        old = self._items[ID]
                        for i in old.__slots__:
                            if not getattr(old, i) == getattr(self, i):
                                warn(f'The impact item "{ID}" is replaced in the registry.')
                    else:
                        self._items[ID] = self
                        self._registered = True
                else:
                    raise ValueError('Cannot register an impact item without an ID.')

    
    # This makes sure it won't be shown as memory location of the object
    def __repr__(self):
        return f'<ImpactItem: {self.ID}>'

    def show(self):
        '''Show basic information of this impact item.'''
        info = f'ImpactItem      : {self.ID} [per {self.functional_unit}]'
        if self.source:
            info += f'\nSource          : {self.source.ID}'
        info += f'\nPrice           : {f_num(self.price)} {currency}'
        info += '\nImpactIndicators:'
        print(info)
        if len(self.CFs) == 0:
            print(' None')
        else:
            index = pd.Index((i.ID+' ('+i.unit+')' for i in self.indicators))
            df = pd.DataFrame({
                'Characterization factors': tuple(self.CFs.values())
                },
                index=index)
            print(df.to_string())
        
    _ipython_display_ = show

    def _update_price(self, price=0., unit=''):
        source_item = get_source_item(self)
        if not unit or unit == currency:
            source_item._price = float(price)
        else:
            converted = auom(unit).convert(float(price), currency)
            source_item._price = converted

    def add_indicator(self, indicator, CF_value, CF_unit=''):
        '''Add an indicator with charactorization factor values.'''
        source_item = get_source_item(self)
        if isinstance(indicator, str):
            indicator = ImpactIndicator.get_all_indicators(as_dict=True)[indicator]
            # try: indicator = indicators[indicator]
            # except: breakpoint()
            
        try: CF_unit2 = CF_unit.replace(' eq', '-eq')
        except: pass
    
        if CF_unit and CF_unit != indicator.unit and CF_unit2 != indicator.unit:
            try:
                CF_value = auom(parse_unit(CF_unit)[0]). \
                    convert(CF_value, indicator._ureg_unit.units)
            except:
                raise ValueError(f'Conversion of the given unit {CF_unit} to '
                                 f'the defaut unit {indicator.unit} is not supported.')
        
        source_item._CFs[indicator.ID] = CF_value

    def remove_indicator(self, indicator):
        '''
        Remove an indicator from this impact item.
        
        Parameters
        ----------
        indicator : str or :class:`~.ImpactIndicator`
            The :class:`~.ImpactIndicator` or its ID.
        '''
        ID = indicator if isinstance(indicator, str) else indicator.ID
        source_item = get_source_item(self)
        source_item.CFs.pop(ID)
        print(f'The impact indicator "{ID}" has been removed.')


    def copy(self, new_ID=None, set_as_source=False, register=True):
        '''
        Return a new :class:`ImpactItem` object with the same settings.
        
        Parameters
        ----------
        new_ID : str
            ID of the new impact item.
        set_as_source : bool
            Whether to set the original impact item as the source.
        register : bool
            Whether to register the new impact item.
        '''
        
        new = ImpactItem.__new__(ImpactItem)
        new.ID = new_ID
        
        if set_as_source:
            new.source = self
        else:
            for slot in ImpactItem.__slots__:
                if slot == '_ID':
                    continue
                value = getattr(self, slot)
                setattr(new, slot, copy_maybe(value))
        
        if register:
            self._items[new_ID] = new
            new._registered = True
        else:
            new._registered = False
        
        return new

    __copy__ = copy

    def register(self):
        '''Add this impact item to the registry.'''
        ID = self.ID
        if self._registered:
            warn(f'The impact item "{ID}" is already in registry.')
            return
        else:
            self._items[ID] = self
        
        print(f'The impact item "{ID}" has been added to the registry.')

    def deregister(self):
        '''Remove this impact item from the registry.'''
        ID = self.ID
        self._items.pop(ID)
        self._registered = False
        print(f'The impact item "{ID}" has been removed from the registry.')
    
    @classmethod
    def clear_registry(cls):
        '''Remove all existing impact items from the registry.'''
        for i in cls._items.values():
            i._registered = False
        cls._items = {}
        print('All impact items have been removed from registry.')
    
    @classmethod
    def load_items_from_excel(cls, path):
        '''
        Load impact items from an Excel file.
        
        This Excel should have multiple sheets:
            
            - The "info" sheet should have two columns: "ID" (e.g., Cement) \
            and "functional_unit" (e.g., kg) of different impact items.
            
            - The remaining sheets should contain characterization factors of \
            impact indicators.
            
                - Name of the sheet should be the ID (e.g., GlobalWarming) or \
                alias (e.g., GWP) of the indicator.
                
                - Each sheet should have at least two columns: "unit" (e.g., kg CO2-eq) \
                and "expected" (values) of the CF.
                
                - You can also have additional columns to be used for other purpose \
                (e.g., uncertainty analysis).
        
        .. note::
            
            This function is just one way to batch-load impact items,
            you can always write your own function that fits your datasheet format,
            as long as it provides all the information to construct new impact items.
        
        
        Parameters
        ----------
        path : str
            Complete path of the Excel file.

        Tip
        ---
        Refer to the `Bwaise system <https://github.com/QSD-Group/EXPOsan/tree/main/exposan/bwaise/data>`_
        in the ``Exposan`` repository for a sample file.
        '''
        if not (path.endswith('.xls') or path.endswith('.xlsx')):
            raise ValueError('Only Excel files ends with ".xlsx" or ".xls" can be interpreted.')
        
        data_file = pd.ExcelFile(path, engine='openpyxl')
        items = cls._items
        for sheet in data_file.sheet_names:
            data = data_file.parse(sheet, index_col=0)

            if sheet == 'info':
                for item in data.index:
                    if item in items.keys():
                        warn(f'The impact item "{item}" has been added.')
                    else:
                        new = cls.__new__(cls)
                        new.__init__(ID=item,
                                     functional_unit=data.loc[item]['functional_unit'])
                        items[item] = new
            else:
                for item in data.index:
                    old = items[item]
                    old.add_indicator(indicator=sheet,
                                      CF_value=float(data.loc[item]['expected']),
                                      CF_unit=data.loc[item]['unit'])
    
    @classmethod
    def get_item(cls, ID):
        '''Get an item by its ID.'''
        return cls._items[ID]
    
    @classmethod
    def get_all_items(cls, as_dict=False):
        '''
        Get all impact items.
        
        Parameters
        ----------
        as_dict : bool
            False returns a list and True returns a dict.
        '''
        if as_dict:
            return cls._items

        return sorted(set(i for i in cls._items.values()), key=lambda i: i.ID)
    
    @property
    def source(self):
        '''
        [ImpactItem] If provided, all attributions and properties of this
        impact item will be copied from the provided source.
        '''
        return self._source
    @source.setter
    def source(self, i):
        if not isinstance(i, ImpactItem):
            raise ValueError('`source` can only be an `ImpactItem`, '
                             f'not {type(i).__name__}.')
        self._source = i
    
    @property
    def ID(self):
        '''
        [str] ID of the item. If no ID is provided, this item will not be
        saved in the ImpactItem dict.
        '''
        return self._ID
    @ID.setter
    def ID(self, i):
        self._ID = i
    
    @property
    def functional_unit(self):
        '''[str] Functional unit of the item.'''
        return get_source_item(self)._functional_unit.units
    @functional_unit.setter
    def functional_unit(self, i):
        get_source_item(self)._functional_unit = auom(i)
    
    @property
    def indicators(self):
        ''' [tuple] :class:`ImpactIndicator` objects associated with the item.'''
        return tuple(ImpactIndicator.get_all_indicators(as_dict=True)[i]
                     for i in get_source_item(self)._CFs.keys())
    
    @property
    def price(self):
        '''Price of the item per functional unit.'''
        return get_source_item(self)._price
    @price.setter
    def price(self, price, unit=''):
        get_source_item(self)._update_price(price, unit)
    
    @property
    def CFs(self):
        '''[dict] Characterization factors of the item for different impact indicators.'''
        return get_source_item(self)._CFs
    @CFs.setter
    def CFs(self, indicator, CF_value, CF_unit=''):
        get_source_item(self).add_indicator(indicator, CF_value, CF_unit)
        
    @property
    def registered(self):
        '''[bool] If this impact item is registered in the records.'''
        return self._registered


# %%

class StreamImpactItem(ImpactItem):
    '''
    A class for calculation of environmental impacts associated with streams 
    (e.g., chemical inputs, emissions).
    
    Parameters
    ----------
    linked_stream : :class:`SanStream`
        The associated :class:`SanStream` for environmental impact calculation.
    source : :class:`StreamImpactItem`
        If provided, all attributions and properties of this
        :class:`StreamImpactItem` will be copied from the provided source.
    register : bool
        Whether to add to the registry.
    indicator_CFs : kwargs
        ImpactIndicators and their characteriziation factors (CFs).
    
    Tip
    ---
    For environmental impacts associated with construction and transportation,
    use :class:`ImpactItem` instead.

    Examples
    --------
    Refer to :class:`ImpactItem` for general features.
    Below is about the additional features for :class:`StreamImpactItem`.
    
    Assume we want to account for the globalwarming potential for methane:

    >>> # Make impact indicators
    >>> import qsdsan as qs
    >>> GWP = qs.ImpactIndicator('GlobalWarming', alias='GWP', unit='kg CO2-eq')
    >>> FEC = qs.ImpactIndicator('FossilEnergyConsumption', alias='FEC', unit='MJ')
    >>> # Make an stream impact item
    >>> methane_item = qs.StreamImpactItem('methane_item', register=True, GWP=28)
    >>> methane_item.show()
    StreamImpactItem: [per kg]
    Linked to       : None
    Price           : 0 USD
    ImpactIndicators:
                               Characterization factors
    GlobalWarming (kg CO2-eq)                        28
    >>> # Make a stream and link the stream to the impact item
    >>> cmps = qs.utils.examples.load_example_cmps()
    >>> qs.set_thermo(cmps)
    >>> methane = qs.SanStream('methane', Methane=1, units='kg/hr',
    ...                        impact_item=methane_item)
    >>> methane_item.show()
    StreamImpactItem: [per kg]
    Linked to       : methane
    Price           : 0 USD
    ImpactIndicators:
                               Characterization factors
    GlobalWarming (kg CO2-eq)                        28

    We can make copies of the impact item, and link it to the original one.
    
    >>> methane2 = methane.copy('methane2')
    >>> methane_item2 = methane_item.copy('methane_item2', stream=methane2,
    ...                                   set_as_source=True, register=True)
    >>> methane_item2.CFs['GlobalWarming']
    28
    >>> methane_item2.CFs['GlobalWarming'] = 1
    >>> methane_item.CFs['GlobalWarming']
    1
    
    We can also add or remove impact indicators.
    
    >>> methane_item2.remove_indicator('GlobalWarming')
    The impact indicator "GlobalWarming" has been removed.
    >>> methane_item2.show()
    StreamImpactItem: [per kg]
    Linked to       : methane2
    Source          : methane_item
    Price           : 0 USD
    ImpactIndicators:
     None
    >>> methane_item2.add_indicator('GlobalWarming', 28)
    >>> methane_item2.show()
    StreamImpactItem: [per kg]
    Linked to       : methane2
    Source          : methane_item
    Price           : 0 USD
    ImpactIndicators:
                               Characterization factors
    GlobalWarming (kg CO2-eq)                        28
    '''

    __slots__ = ('_ID', '_linked_stream', '_functional_unit', '_CFs', '_source',
                 '_registered')

    def __init__(self, ID=None, linked_stream=None, source=None, register=True,
                 **indicator_CFs):

        self._linked_stream = None
        self.linked_stream = linked_stream
        self._registered = register

        if not ID and linked_stream:
            ID = self.linked_stream.ID + '_item'
        self._ID = ID

        if source:
            self.source = source
        else:
            self._source = None
            self._functional_unit = auom('kg')
            self._CFs = {}
            for CF, value in indicator_CFs.items():
                try:
                    CF_value, CF_unit = value # unit provided for CF
                    self.add_indicator(CF, CF_value, CF_unit)
                except:
                    self.add_indicator(CF, value)
        
        if register:
            if ID in self._items.keys():
                old = self._items[ID]
                for i in old.__slots__:
                    if not getattr(old, i) == getattr(self, i):
                        warn(f'The impact item "{ID}" is replaced in the registry.')
            else:
                self._items[ID] = self
                self._registered = True


    def __repr__(self):
        if self.linked_stream:
            kind = type(self.linked_stream).__name__
            return f'<StreamImpactItem: {kind} {self.linked_stream}>'
        else:
            return '<StreamImpactItem: no linked stream>'

    def show(self):
        '''Show basic information about this :class:`StreamImpactItem` object.'''
        info = f'StreamImpactItem: [per {self.functional_unit}]'    
        if self.linked_stream:
            info += f'\nLinked to       : {self.linked_stream}'
        else:
            info += '\nLinked to       : None'
        if self.source:
            info += f'\nSource          : {self.source.ID}'
        info += f'\nPrice           : {f_num(self.price)} {currency}'
        info += '\nImpactIndicators:'
        print(info)
        if len(self.CFs) == 0:
            print(' None')
        else:
            index = pd.Index((i.ID+' ('+i.unit+')' for i in self.indicators))
            df = pd.DataFrame({
                'Characterization factors': tuple(self.CFs.values())
                },
                index=index)
            # print(' '*18+df.to_string().replace('\n', '\n'+' '*18))
            print(df.to_string())

    
    _ipython_display_ = show


    def copy(self, new_ID=None, stream=None, set_as_source=False, register=True):
        '''
        Return a new :class:`StreamImpactItem` object with the same settings.

        Parameters
        ----------
        new_ID : str
            ID of the new impact item.
        stream : :class:`~.SanStream`
            Linked stream to the copy.
        set_as_source : bool
            Whether to set the original impact item as the source.
        register : bool
            Whether to register the new impact item.
        '''
        
        new = StreamImpactItem.__new__(StreamImpactItem)
        new.ID = new_ID
        new._linked_stream = None # initiate this attribute
        
        if set_as_source:
            new.source = self
        else:
            for slot in StreamImpactItem.__slots__:
                if slot in ('_ID', '_linked_stream'):
                    continue
                value = getattr(self, slot)
                setattr(new, slot, copy_maybe(value))
        
        if stream:
            stream.impact_item = new
            if not new_ID:
                new.ID = f'{stream.ID}_item'
        
        if register:
            self._items[new.ID] = new
            new._registered = True
        else:
            new._registered = False
        
        return new
    
    __copy__ = copy

    @property
    def source(self):
        '''
        [:class:`StreamImpactItem`] If provided, all attributions and properties of this
        :class:`StreamImpactItem` will be copied from the provided source.
        
        .. note::
            Since the price is copied from the price of the `linked_stream`, it
            can be different form the source.
        '''
        return self._source
    @source.setter
    def source(self, i):
        if not isinstance(i, StreamImpactItem):
            raise ValueError('source can only be a StreamImpactItem, ' \
                             f'not a {type(i).__name__}.')
        self._source = i

    @property
    def linked_stream(self):
        '''
        [:class:`SanStream`] The associated :class:`SanStream` for environmental impact calculation,
        can be set by either the :class:`SanStream` object or its ID.
        '''
        return self._linked_stream
        
    @linked_stream.setter
    def linked_stream(self, new_s):
        if new_s and not isinstance(new_s, SanStream):
            if isinstance(new_s, str):
                try:
                    new_s = getattr(SanStream.registry, new_s)
                except:
                    try:
                        new_s = getattr(WasteStream.registry, new_s)
                    except:
                        raise ValueError(f'The ID "{new_s}" not found in registry.')
            else:
                raise TypeError('`linked_stream` must be a `SanStream` or '
                                f'the ID of a `SanStream`, not {type(new_s).__name__}.')
        
        if self._linked_stream:
            old_s = self._linked_stream
            self._linked_stream.impact_item = None
            warn(f'`ImpactItem` {self.ID} is unlinked from {old_s.ID} and ' \
                 f'linked to {new_s.ID}.', stacklevel=2)
        if new_s:
            if hasattr(self, '_ID'):
                if new_s.impact_item and new_s.impact_item.ID != self.ID:
                    msg = f'The original `StreamImpactItem` linked to stream {new_s} ' \
                        f'is replaced with {self}.'
                    warn(message=msg, stacklevel=2)
            new_s._impact_item = self
        self._linked_stream = new_s

    @property
    def ID(self):
        '''
        [str] ID of the item. If no ID is provided but its `linked_stream` is provided,
        the ID will be set as ID of the `linked_stream` with a suffix '_item'.
        '''
        return self._ID
    @ID.setter
    def ID(self, i):
        self._ID = i

    @property
    def functional_unit(self):
        '''[str] Functional unit of the item, set to 'kg'.'''
        return auom('kg')
    
    @property
    def price(self):
        '''[float] Price of the linked stream.'''
        if self.linked_stream:
            return self.linked_stream.price
        else: return 0.







