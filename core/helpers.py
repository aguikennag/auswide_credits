class Helper() :
    @staticmethod
    def currency_convert(amount,_from,_to) :
        if _from == _to :
            return amount
        else :
            #then we convert
            to_amount  = amount
        """ 
        converts from one currency to another 
        _from and _to should be in currency object
        amount should be in the _from currency"""
        return to_amount 