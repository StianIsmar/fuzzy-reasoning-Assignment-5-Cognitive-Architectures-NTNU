from collections import defaultdict

class FuzzyReasoning:

    def __init__(self,distance, delta):
        self.distance = distance
        self.delta = delta

    def triangle(self, pos, x0, x1, x2, clip):
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

    def uphill(self, pos, x0, x1, clip):
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

    def downhill(self, pos, x0, x1, clip):
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
                d[set_name] = self.downhill(distance, set_interval[0], set_interval[1],1)
            if set_name == "verybig":
                d[set_name] = self.uphill(distance, set_interval[0], set_interval[1],1)
            if set_name == "small" or set_name == "perfect" or set_name == "big":
                x1 = (set_interval[1]-set_interval[0])/2 + set_interval[0]
                d[set_name] = self.triangle(distance, set_interval[0], x1, set_interval[1],1)
            # Delta:
            if set_name == "shrinkingfast":
                d[set_name] = self.downhill(distance, set_interval[0], set_interval[1],1)
            if set_name == "growingfast":
                d[set_name] = self.uphill(distance, set_interval[0], set_interval[1],1)
            if set_name == "shrinking" or set_name == "stable" or set_name == "growing":
                x1 = (set_interval[1]-set_interval[0])/2 + set_interval[0]
                d[set_name] = self.triangle(distance, set_interval[0], x1, set_interval[1],1)
        return d

    def distance_delta_sets(self, distance_pos,delta_pos):
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

    # The given rules:
    def rule1(self, small_value, growing_value):
        minimize_value = min(small_value, growing_value)
        return minimize_value

    def rule2(self, small_value, stable_value):
        minimize_value = min(small_value, stable_value)
        return minimize_value

    def rule3(self, perfect_value, growing_value):
        minimize_value = min(perfect_value, growing_value)
        return minimize_value

    def rule4(self, verybig_value, val):
        minimize_value = min (verybig_value, val)
        if val == 1:
            return minimize_value
        else:
            return 0
    def rule5(self, verysmall_value ):
        return verysmall_value

    def fire_which_rule(self, distance_set, delta_set):
        rule_results = {}
        for distance_set_name, y in distance_set.items():
            if distance_set_name == "small":
                for delta_set_name, z in delta_set.items():
                    if delta_set_name == "growing":
                        rule_results["none"] = self.rule1(y, z)
                    if delta_set_name == "stable":
                        rule_results["slowdown"] = self.rule2(y, z)
            if distance_set_name == "perfect":
                for delta_set_name2, x in delta_set.items():
                    if delta_set_name2 == "growing":
                        rule_results["speedup"] = self.rule3(y, x)
            if distance_set_name == "verybig":
                for delta_set_name3, v in delta_set.items():
                    if delta_set_name3 == "growing":
                        for delta_set_name4, b in delta_set.items():
                            if delta_set_name4 == "growingfast":
                                rule_results["floorit"] = self.rule4(y, 0)
                    else:
                        rule_results["floorit"] = self.rule4(y, 1)
            if distance_set_name == "verysmall":
                rule_results["brakehard"] = self.rule5(y)
        return rule_results



    def range_inc(self, start, stop, inc):
        my_list = [0]
        i = start
        while i < stop:
            i = i + inc
            my_list.append(i)
        return my_list

    # Aggregate of the rules:
        # First, clip the results in the action-set:
    def area(self, action_set):
        action_intervals_dict ={
            "brakehard": [-8.0, -5.0],
            "slowdown": [-7.0, -1.0],
            "none": [-3.0, 3.0],
            "speedup": [1.0, 7.0],
            "floorit": [5.0, 8.0]
             }

        aggrigate_dict = defaultdict(list)
        for action_name, calc_clip in action_set.items():
            if action_name == "brakehard":
                i = -10
                while i < 10:
                    set_interval = action_intervals_dict.get("brakehard")
                    aggrigate_dict["brakehard"].append(self.downhill(i, set_interval[0], set_interval[1], calc_clip))
                    i += 1

            if action_name == "floorit":
                i = -10
                while i < 10:
                    set_interval = action_intervals_dict.get("floorit")
                    aggrigate_dict["floorit"].append(self.uphill(i, set_interval[0], set_interval[1], calc_clip))
                    i += 1
            if action_name == "slowdown":

                i = -10
                while i < 10:

                    set_interval = action_intervals_dict.get("slowdown")
                    x1 = (set_interval[1] - set_interval[0]) / 2 + set_interval[0]
                    aggrigate_dict["slowdown"].append(self.triangle(i, set_interval[0], x1, set_interval[1], calc_clip))
                    i += 1
            if action_name == "none":
                i = -10
                while i < 10:
                    set_interval = action_intervals_dict.get("none")
                    x1 = (set_interval[1] - set_interval[0]) / 2 + set_interval[0]
                    aggrigate_dict["none"].append(self.triangle(i, set_interval[0], x1, set_interval[1], calc_clip))
                    i += 1

            if action_name == "speedup":
                i = -10
                while i < 10:
                    set_interval = action_intervals_dict.get("speedup")
                    x1 = (set_interval[1] - set_interval[0]) / 2 + set_interval[0]
                    aggrigate_dict["speedup"].append(self.triangle(i, set_interval[0], x1, set_interval[1], calc_clip))
                    i += 1
        return aggrigate_dict

    def summerise_area(self, dict):
        aggregate_list = [0] * 20
        for set_name, y_vals_list in dict.items():
            i = 0
            for val in y_vals_list:
                aggregate_list[i] = max(val, aggregate_list[i])
                i = i + 1
        denomerator = sum(aggregate_list)
        numerator =


    def call_all(self):
        dist_set, del_set = self.distance_delta_sets(self.distance, self.delta)
        list_with_values = self.fire_which_rule(dist_set, del_set)
        dict = task1.area(list_with_values)
        l = self.summerise_area(dict)
        return l


# ******** Main: *************
task1 = FuzzyReasoning(3.7, 1.2)
result_list = task1.call_all()
print(result_list)
print(sum(result_list,0))

numerator = 0
i = 0
    for val in result_list:
            numerator += val * result_list[i]
            i += 1
        return numerator

    


