from App import App 
import time

if __name__ == "__main__":
    s_time = time.time()
    App().run()
    e_time = time.time()
    print("Run time: ", e_time - s_time)
