# import time
#
# if __name__ == '__main__':
#     print("hello Wolrd python222")
#     time.sleep(3000)

import os, sys


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
