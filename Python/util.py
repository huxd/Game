#-*- coding: utf-8 -*-
import os
import xlrd

class Excel(object):
    def __init__(self, path):
        super(Excel, self).__init__()
        self.path = path

    def transferToTxt(self):
        data = xlrd.open_workbook(self.path)
        filename = os.path.basename(self.path)
        filename = filename.split('.')[0]
        txt_dir = os.path.dirname(self.path)
        txt_name = "%s.txt" % filename
        txt_path = os.path.join(txt_dir, txt_name)
        txt_file = open(txt_path, "w")
        sheet = data.sheets()[0]
        for i in xrange(sheet.nrows):
            row = sheet.row(i)
            line = ''
            for cell in row:
                value = cell.value
                if cell.ctype == 2:
                    value = int(value)
                line += "%s " % value
            line = line[:-1] + '\n'
            txt_file.write(line.encode('utf8'))
        txt_file.close()


excel = Excel("word frequency list 60000 English.xlsx")
excel.transferToTxt()