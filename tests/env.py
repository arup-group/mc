import sys
import os


def set_module():
    sys.path.append(os.path.abspath('../mc'))


def this_dir():
    return os.path.dirname(os.path.abspath(__file__))



# # # append module root directory to sys.path
# # sys.path.append(
# #     os.path.dirname(
# #         os.path.dirname(
# #             os.path.abspath(__file__)
# #         )
# #     )
# # )