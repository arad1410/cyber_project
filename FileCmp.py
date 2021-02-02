import wx
import re

string='''"Have more than thou showest,

Speak less than thou knowest,

Lend less than thou owest,

Ride more than thou goest,

Learn more than thou trowest,

Set less than thou throwest."

-The Fool in King Lear'''

class Quote(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, None, -1)
        self.InitUI()

    def InitUI(self):
        panel=wx.Panel(self)
        word = 'thou'
        word_colour = wx.TextAttr(wx.BLUE)
        word_occurs = self.find_str(word,string)
        self.text=wx.TextCtrl(panel, pos=(20,20), size=(250,220),
            style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text.AppendText(string)
        for i in word_occurs:
            #SetStyle(start pos, end pos, style)
            self.text.SetStyle(i,i+len(word),word_colour)
        self.SetSize((300,300))
        self.Centre()
        self.Show(True)

    def find_str(self,sub,sent): #return positions of the word
        return [x.start() for x in re.finditer(sub,sent)]

def main():
    app=wx.App()
    Quote()
    app.MainLoop()

if __name__ == '__main__':
    main()