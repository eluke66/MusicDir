class FirstDigitAggregator:


    # Input: DB Entry tags
    # Output: List of aggregated entries 
    def aggregate(self,entries):
        firstLetters = {}
        for entry in entries:
            if (entry is not None and entry != ""):
                firstLetters[entry[0].lower()] = None
        return [item.encode("latin-1") for item in firstLetters.keys()]
        
    
class DecadeAggregator:
    
    # Input: DB Entry tags
    # Output: List of aggregated entries
    def aggregate(self,entries):
        decades = []
        for year in entries:
            if ( year.lower() == "unknown" or year == "0" or year == ""):
                decade = "Unknown"
            else:
                decade = year[0:-1] + "0s"
            if ( decades.count(decade) == 0 ):
                decades.append(decade)

        return [decade.encode("latin-1") for decade in decades]
