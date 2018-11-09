class FuzzyReasoning():
    
    def __init__(self,distance, delta):
        self.distance = distance
        self.delta = delta

    def triangle(self, pos, x0, x1, x2):
        clip = 1.0
        value = 0.0
        if pos >= x0 and pos <= x1:
            value = (pos - x0) / (x1-x0)
        elif pos >= x1 and pos <= x2:
            value = (x2 - pos) / (x1 - x0)
        # Outside position:
        if pos < x0:
            return 0
        if pos > x2:
            return 0
        return value

    def uphill(self, pos, x0,x1):
        clip = 1.0
        value = 0.0

        # Pos to the left of x0:
        if pos < x0:
            return 0.0

        if pos >= x1:
            value = 1.0
        elif pos <= x0:
            value = 0.0
        else:
            value = (pos - x0) / (x1 - x0)
        if value > clip:
            value = clip
        return value

    def downhill(self, pos, x0, x1):
        clip = 1.0
        value = 0.0
        if pos <= x0:
            value = 1.0
        elif pos >= x1:
            value = 0.0
        else:
            value = (x1 - pos) / (x1 - x0)
        if value > clip:
            value = clip
        return value

    def calculate_set_value(self, set_name_dict, distance):
        d = {}
        for set_name, set_interval in set_name_dict.items():
            if set_name == "verysmall":
                d[set_name] = self.downhill(distance, set_interval[0], set_interval[1])
            if set_name == "verybig":
                d[set_name] = self.uphill(distance, set_interval[0], set_interval[1])
            if set_name == "small" or set_name == "perfect" or set_name == "big":
                x1 = (set_interval[1]-set_interval[0])/2 + set_interval[0]
                d[set_name] = self.triangle(distance, set_interval[0], x1, set_interval[1])
            # Delta:
            if set_name == "shrinkingfast":
                d[set_name] = self.downhill(distance, set_interval[0], set_interval[1])
            if set_name == "growingfast":
                d[set_name] = self.uphill(distance, set_interval[0], set_interval[1])
            if set_name == "shrinking" or set_name == "stable" or set_name == "growing":
                x1 = (set_interval[1]-set_interval[0])/2 + set_interval[0]
                d[set_name] = self.triangle(distance, set_interval[0], x1, set_interval[1])
        return d

    def distance_delta_sets(self, distance_pos,delta_pos ):
        overlapping_sets = []
        distance_dictionary = {"verysmall": [1.0, 2.0],
                               "small": [1.5, 4.5], "perfect": [3.5, 6.5],"big": [5.5, 8.5],
                               "verybig":[7.5, 10.0]}
        delta_dictionary = {"shrinkingfast": [-4.5, -2.5],
                            "shrinking": [-3.5, -0.5], "stable": [-1.5, 1.5], "growing": [0.5, 3.5],
                            "growingfast":[2.5, 4]}

        # Making a dict with the overlapping sets and their intervals!
        # Distance:
        distance_overlapping_sets_dict = {}
        for x, y in distance_dictionary.items():
            if y[0] <= distance_pos <= y[1]:
                distance_overlapping_sets_dict[x] = y

        # Delta:
        delta_overlapping_sets_dict = {}
        for x, y in delta_dictionary.items():
            if y[0] <= delta_pos <= y[1]:
                delta_overlapping_sets_dict[x] = y

        # calculate and return the functino value in each set:
        # After for-loop, calculate the values in the corresponding sets:
        distance_set_name_calc_values_dict = self.calculate_set_value(distance_overlapping_sets_dict, distance_pos)
        delta_set_name_calc_values_dict = self.calculate_set_value(delta_overlapping_sets_dict, delta_pos)
        return distance_set_name_calc_values_dict, delta_set_name_calc_values_dict


# call all functions from here.
    def call_all(self):
        return self.distance_delta_sets(self.distance, self.delta)


## MAIN ##:
# The object
task1 = FuzzyReasoning(3.7, 1.2)
# task1.call_all()
# Check and print which sets it overlaps in the distance_set:
(distance_set, delta_set) = task1.call_all()
print("distance_set", distance_set, "delta_set:", delta_set)
