#!/usr/bin/python
# -*- coding: iso-8859-15

import time, subprocess, getpass

user = getpass.getuser()

CF_PATH_DICT = { 'yetinam' : '/home/yetinam/Dokumente/bsio/software/cuneiform_2_2/cuneiform',
                 'munchmej' : '/vol/fob-vol3/nebenf12/munchmej/bsio/software/cuneiform_2_2/cuneiform' }

CF_PATH = CF_PATH_DICT[user]

# abstract interface for benchmarks
class Benchmark:
    def __init__(self):
        return

    def __str__(self):
        return "Abstract benchmark interface"

    def GenScript(self):
        return ""

    def Validate(self, result):
        return True
        
    def TimePerUnit(self, time):
        return time

class MultiplyThree (Benchmark):
    code = """deftask range(<it> : n) in python *{
it=[str(x) for x in range(1,int(n)+1)]
}*

deftask multiply(prod : a b c) in python *{
prod=str(int(a)*int(b)*int(c))
}*

n=%d;
a=range(n:n);
b=range(n:n);
c=range(n:n);

multiply(a:a,b:b,c:c);    
"""
    
    def __init__(self, n):
        self.n = n
    
    def __str__(self):
        return "MultiplyThree for n="+str(self.n)
    
    def GenScript(self):
        return self.code.replace('%d', str(self.n))
        
    def Validate(self, result):
        result = result.replace('"', '')
        result = result.split()
        count = 0
        for a1 in range(1, self.n+1):
            for a2 in range(1, self.n+1):
                for a3 in range(1, self.n+1):
                    # Dirty hack, to avoid weird unicode character
                    if count == 0:
                        count = 1
                        continue
                    if result[count]!=str(a1*a2*a3):
                        #print result[count] + " != " + str(a1*a2*a3)
                        return False
                    count = count +1
        return True
    
    def TimePerUnit(self, time):
        return time/(self.n**3)

class Pydentity (Benchmark):
    code = """deftask range(<it> : n) in python *{
it=[str(x) for x in range(1,int(n)+1)]
}*

deftask pydentity(out : a) in python *{
out=a
}*

n=%d;
a=range(n:n);

pydentity(a:a);    
"""
    
    def __init__(self, n):
        self.n = n
    
    def __str__(self):
        return "Pydentity for n="+str(self.n)
    
    def GenScript(self):
        return self.code.replace('%d', str(self.n))
        
    def Validate(self, result):
        result = result.replace('"', '')
        result = result.split()
        for a1 in range(1, self.n):
            if result[a1]!=str(a1+1):
                print result[a1] + " != " + str(a1+1)
                return False
        return True
    
    def TimePerUnit(self, time):
        return time/self.n

class Rdentity (Benchmark):
    code = """deftask range(<it> : n) in python *{
it=[str(x) for x in range(1,int(n)+1)]
}*

deftask Rdentity(out : a) in R *{
out<-a
}*

n=%d;
a=range(n:n);

Rdentity(a:a);    
"""
    
    def __init__(self, n):
        self.n = n
    
    def __str__(self):
        return "Rdentity for n="+str(self.n)
    
    def GenScript(self):
        return self.code.replace('%d', str(self.n))
        
    def Validate(self, result):
        result = result.replace('"', '')
        result = result.split()
        for a1 in range(1, self.n):
            if result[a1]!=str(a1+1):
                print result[a1] + " != " + str(a1+1)
                return False
        return True
    
    def TimePerUnit(self, time):
        return time/self.n

def RunBenchmark(bm):
    print "Starting Benchmark " + str(bm)
    code = bm.GenScript()
    code_file = open('/tmp/cf_benchmark.cf','w')
    code_file.write(code)
    code_file.close()
    start_time = time.time()
    p = subprocess.Popen([CF_PATH, '/tmp/cf_benchmark.cf'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    end_time = time.time()
    if p.returncode != 0:
        print "Returncode "+str(p.returncode)+" for Benchmark "+str(bm)
        return False
    valid = bm.Validate(output)
    run_time = end_time - start_time
    if not valid:
        print output
    print str(bm) + " took " + str(run_time) + " seconds ("+str(bm.TimePerUnit(run_time))+" per unit). Result is " + ('VALID' if valid else 'INVALID')
    return valid

if __name__ == "__main__":
    for n in range(10,101,10):
        bm = Rdentity(n)
        if not RunBenchmark(bm):
            break
