class test:
    def range_inc(self,start, stop, step, inc):
        list =[0]
        i = start
        while i < stop:
            i=i+inc
            list.append(i)
        return list

t1 = test()
l=t1.range_inc(0,100,1,0.5)
print(l)