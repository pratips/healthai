import os

class Util:
  def __init__(self):
    pass

  def delete_duplcate_files(self, dir_to_check):
    for fl in os.listdir(dir_to_check):
        if "(" in fl:
            if fl[:fl.index("(")-1]+".pdf.txt" in os.listdir(dir_to_check):
                os.remove(os.path.join(dir_to_check,fl))

if __name__ == "__main__":    
    dir_to_check = "C:\\Users\\prati\\Documents\\health_ai_doc\\data\\p2_txt - Copy"
    util = Util()
    util.delete_duplcate_files(dir_to_check)