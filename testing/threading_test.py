import time
import thread


class MyClass():

    def myThread(self):
        thread.start_new_thread(self.myFunction, ())
        print "Thread started!"

    def myFunction(self):
        a = 0
        for i in range[0,1000000]:
            a = a + i
        print a


foo = MyClass()
foo.myThread()

        

##def myfunction(string,sleeptime,*args):
##    while 1:
##       
##        print string
##        time.sleep(sleeptime) #sleep for a specified amount of time.
##
##if __name__=="__main__":
##
##    thread.start_new_thread(myfunction,("Thread No:1",2))
##
##    while 1:pass
