import numpy as np
from sklearn import linear_model


class NumberOfSamplesTrigger():
    def __init__(self):
        self.sample_count = 0

    def updateData(self, data):
        self.sample_count += 1
    
    def getValue(self):
        return self.sample_count
    
    def reset(self):
        self.sample_count = 0

class ConstantTrigger():
    def __init__(self, value):
        self.value = value
        pass

    def updateData(self, data):
        pass

    def getValue(self):
        return self.value

    def reset(self):
        pass

class ValueTrigger():
    def __init__(self):
        self.data = 0
        pass

    def updateData(self, data):
        self.data = data
        pass

    def getValue(self):
        return self.data

    def reset(self):
        self.data = None
        pass

class Comparator():
    def __init__(self, comparison_type, trigger_1, trigger_2):
        self.comparison_type = comparison_type
        self.trigger_1 = trigger_1
        self.trigger_2 = trigger_2
        self.condition_met = False
    
    def isConditionMet(self):
        return self.condition_met

    def reset(self):
        self.condition_met = False
        self.trigger_1.reset()
        self.trigger_2.reset()

    def compare(self):
        value_1 = self.trigger_1.getValue()
        value_2 = self.trigger_2.getValue()
        condition_met = False
        if value_1 != None and value_2 != None:
            if self.comparison_type == '>':
                if value_1 > value_2:
                    condition_met = True
            elif self.comparison_type == '>=':
                if value_1 >= value_2:
                    condition_met = True
            elif self.comparison_type == '==':
                if value_1 == value_2:
                    condition_met = True
            elif self.comparison_type == '!=':
                if value_1 != value_2:
                    condition_met = True
            elif self.comparison_type == '<=':
                if value_1 <= value_2:
                    condition_met = True
            elif self.comparison_type == '<':
                if value_1 < value_2:
                    condition_met = True

        self.condition_met = condition_met

class Trigger(dict):
    def __init__(self, condition_A, condition_B, comparison_type):
        super().__init__()
        lhs_trigger = self.__createTriggerHandler(condition_A) 
        rhs_trigger = self.__createTriggerHandler(condition_B) 

        lhs = {
            'name': condition_A,
            'obj': lhs_trigger
        }
        
        rhs = {
            'name': condition_B,
            'obj': rhs_trigger
        }

        comparator = Comparator(comparison_type, lhs_trigger, rhs_trigger)
        self['lhs'] = lhs
        self['rhs'] = rhs
        self['comparator'] = comparator

    def __createTriggerHandler(self, condition_name):
        if condition_name == '/Number of samples':
            return NumberOfSamplesTrigger()
        elif condition_name.split(':')[0] == '/Constant':
            return ConstantTrigger(float(condition_name.split(':')[1]))
        else:
            return ValueTrigger()
    