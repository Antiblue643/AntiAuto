from bytebeat import Bytebeat as b
import time

btb = b()


ex = "(((t*(t>>9|t>>8|t>>7|t>>6|t))&64)+((t*(t>>5|t>>4|t>>3|t>>2)/64)&64)+((-t*(t>>3|t>>5|t>>5|t>>6|t>>7)-t)&64))"
btb.start_bytebeat(ex, 8000)
time.sleep(5)
ex = "(-t * (t >> 7 | t >> 6 | t >> 5 | t >> 4 | t >> 3))"
btb.update_bytebeat(ex)
time.sleep(5)
btb.stop_bytebeat()

