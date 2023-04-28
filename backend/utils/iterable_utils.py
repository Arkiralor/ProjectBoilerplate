from statistics import mean

from utils import logger


class OverloadedList(list):
    """
    Overloaded <list> class to add additional methods.
    """

    def mean(self):
        return sum(self)/len(self)

    def sort(self):
        return sorted(self)

    def rms(self):
        try:
            # return (mean([item**2 for item in self])**(1/2))
            return (OverloadedList([item**2 for item in self]).mean()**(1/2))
        except Exception as ex:
            logger.exception(f"{ex}")
            return float()

    def median(self):
        try:
            _sorted, _l = self.sort(), self.len
            if _l <= 0:
                logger.exception(f"Size error: Length <{_l}>")
                return float()

            if _l % 2 == 0:
                return (_sorted[_l//2]+_sorted[(_l//2)+1])/2
            else:
                return _sorted[(_l//2)+1]
        except Exception as ex:
            logger.exception(f"{ex}")
            return float()

    @property
    def len(self):
        return len(self)
    
    @property
    def frequencies(self):
        try:
            _set = set(self)
            frequencies = OverloadedList()
            values = OverloadedList()

            for item in _set:
                frequencies.append(self.count(item))
                values.append(item)

            return values, frequencies
        except Exception as ex:
            logger.exception(f"{ex}")
            return OverloadedList(), OverloadedList()


class OverloadedSet(set):
    """
    Overloaded <set> class to add additional methods.
    """

    def mean(self):
        return sum(self)/len(self)

    def sort(self):
        return set(sorted(self))

    def rms(self):
        try:
            # return (mean([item**2 for item in self])**(1/2))
            return (OverloadedSet([item**2 for item in self]).mean()**(1/2))
        except Exception as ex:
            logger.exception(f"{ex}")
            return float()

    def median(self):
        try:
            _sorted, _l = list(self.sort()), self.len
            if _l <= 0:
                logger.exception(f"Size error: Length <{_l}>")
                return float()

            if _l % 2 == 0:
                return (_sorted[_l//2]+_sorted[(_l//2)+1])/2
            else:
                return _sorted[(_l//2)+1]
        except Exception as ex:
            logger.exception(f"{ex}")
            return float()

    @property
    def len(self):
        return len(self)
