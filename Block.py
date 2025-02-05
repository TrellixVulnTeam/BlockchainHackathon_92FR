import hashlib
import datetime
from Pyro5.api import expose, behavior, Daemon
import encryption as enc
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, VariableListProperty, ListProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Color, Rectangle
import sys
import Pyro4
import Pyro4.util
import schedule

sys.excepthook = Pyro4.util.excepthook

chain = Pyro4.Proxy("PYRO:obj_9fd2a94664ee4b7d9d4eca61d1d2391e@10.42.0.106:36159")

# force size of window here for kivy
Config.set('graphics', 'width', '1380')
Config.set('graphics', 'height', '900')


# global variables
choice = -1
blockchain = ""

# class for containing our data to put inside the block
# dd --> due diligence
class HackathonData:
    def __init__(self, dd_type, dd_doc, dd_date, orig_fi_id, vendor_id, req_fi_id):
        self.dd_type = dd_type
        self.dd_doc = dd_doc  # should be .pdf or some kind of file like that
        self.dd_date = dd_date
        self.orig_fi_id = orig_fi_id
        self.vendor_id = vendor_id
        self.req_fi_id = req_fi_id

    def print_all_data(self):
        print("Type of Due Diligence:", self.dd_type)
        print("Document:", self.dd_doc)
        print("Date Completed:", self.dd_date)
        print("Original FI:", self.orig_fi_id)
        print("3rd Party Vendor:", self.vendor_id)
        print("Requesting FI:", self.req_fi_id)

    def return_all_data(self):
        return "Type of Due Diligence:" + self.dd_type + "\nDocument:" + self.dd_doc +"\nDate Completed:"+ self.dd_date + "\nOriginal FI:" + self.orig_fi_id +"\n3rd Party Vendor:"+ self.vendor_id +"\nRequesting FI:"+ self.req_fi_id + "\n"


# class for our actual Block
class HackathonBlock:
    def __init__(self, index, timestamp, data, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.hashing()

    def hashing(self):
        key = hashlib.sha256()
        key.update(str(self.index).encode('utf-8'))
        key.update(str(self.timestamp).encode('utf-8'))
        key.update(str(self.data).encode('utf-8'))
        key.update(str(self.prev_hash).encode('utf-8'))
        return key.hexdigest()

    def get_index(self):
        return self.index

    def get_timestamp(self):
        return self.timestamp

    def get_data(self):
        return self.data.return_all_data()

    def get_prev_hash(self):
        return self.prev_hash

    def get_hash(self):
        return self.hash

    def print_data(self):
        self.data.print_all_data()


# class for our Chain
@expose
@behavior(instance_mode="single")
class HackathonChain:
    def __init__(self):  # initializes the block chain with a Genesis block
        self.blocks = [self.get_genesis_block()]

    def get_genesis_block(self):
        return HackathonBlock(0, datetime.datetime.utcnow(), None, None)

    def add_block(self, dd_type, dd_doc, dd_date, orig_fi_id, vendor_id, req_fi_id):
        self.blocks.append(HackathonBlock(len(self.blocks),
                                          datetime.datetime.utcnow(),
                                          HackathonData(dd_type, dd_doc, dd_date, orig_fi_id, vendor_id, req_fi_id),
                                          self.blocks[len(self.blocks) - 1].hash))

    def get_chain_size(self):  # exclude genesis block
        return len(self.blocks) - 1

    def get_block_data(self, index):
        return self.blocks[index].get_data()

    def print_block_data(self, index):
        self.blocks[index].print_data()

    def return_chain(self):
        return self.blocks


# build our Blockchain string for printing
def visualize_blockchain(chain):
    str_chain = "\n     *\n     *\n     *\n     *\n     *\n"
    str_genesis = "-------------------------\n| Genesis Block |\n-------------------------"
    str_line="-------------------------\n"
    output = str_genesis+str_chain
    str_block = ""
    for i in range(chain.get_chain_size()):
        str_block += chain.get_block_data(i+1)
        output += str_line+str_block+str_line+str_chain

    return output


# GUI class
class GUI(App):
    def build(self):
        layout = MyGui()
        Clock.schedule_interval(layout.update, 1.0 / 30.0)
        return layout


class MyGui(GridLayout):
    def __init__(self, **kwargs):
        super(MyGui, self).__init__(**kwargs)
        self.cols = 2
        self.old = 0
        global blockchain
        self.blockLabel = Label(text=blockchain , font_size=40)
        self.add_widget(self.blockLabel)
        right = ChoicesGui()
        self.add_widget(right)

    def update(self, dt):
        global choice
        self.updateRight(choice)

    def updateRight(self, choice):
        if self.old != choice:
            self.old = choice
            if self.old == 0:
                self.clear_widgets()
                self.add_widget(self.blockLabel)
                self.add_widget(ChoicesGui())
            elif self.old == 1:
                self.clear_widgets()
                self.add_widget(self.blockLabel)
                self.add_widget(TradeBlockGui())
            elif self.old == 2:
                self.clear_widgets()
                self.add_widget(self.blockLabel)
                self.add_widget(UploadBlockGui())


class BlockchainGui(Label):
    def __init__(self):
        self.meme = 0

class ChoicesGui(GridLayout):
    def __init__(self, **kwargs):
        super(ChoicesGui, self).__init__(**kwargs)
        self.rows = 2

        self.req = Button(text="Create new block", size_hint=[1, .5])
        self.add_widget(self.req)
        self.req.bind(on_press=self.reqPressed)

        self.up = Button(text="Upload", size_hint=[1, .5])
        self.add_widget(self.up)
        self.up.bind(on_press=self.upPressed)

    def reqPressed(self, btn):
        btnPres(1)

    def upPressed(self, btn):
        btnPres(2)


def btnPres(val):
    global choice
    choice = val


class TradeBlockGui(GridLayout):
    def __init__(self, **kwargs):
        super(TradeBlockGui, self).__init__(**kwargs)
        self.cols = 2
        # self.rows = 5

        self.add_widget(MyLabel(text="DD Type", font_size=45))
        self.dd_type = TextInput(multiline=False, font_size=35)
        self.add_widget(self.dd_type)

        self.add_widget(MyLabel2(text="Original ID", font_size=45))
        self.orig_id = TextInput(multiline=False, font_size=35)
        self.add_widget(self.orig_id)

        self.add_widget(MyLabel(text="Vendor ID", font_size=45))
        self.ven_id = TextInput(multiline=False, font_size=35)
        self.add_widget(self.ven_id)

        self.add_widget(MyLabel2(text="Request ID", font_size=45))
        self.req_id = TextInput(multiline=False, font_size=35)
        self.add_widget(self.req_id)

        self.add_widget(Label())
        self.submit = Button(text="Submit", font_size=45)
        self.add_widget(self.submit)
        self.submit.bind(on_press=self.subPress)

    def subPress(self, btn):
        self.printData()
        btnPres(0)

    def printData(self):
        print(self.dd_type.text, self.orig_id.text, self.ven_id.text, self.req_id.text)
        global ddtypeRead
        ddtypeRead = self.dd_type.text
        global origRead
        origRead = self.orig_id.text
        global venRead
        venRead = self.ven_id.text
        global reqRead
        reqRead = self.req_id.text


class UploadBlockGui(GridLayout):
    def __init__(self, **kwargs):
        super(UploadBlockGui, self).__init__(**kwargs)
        self.cols = 2
        # self.rows = 5

        self.add_widget(MyLabel(text="DD Type", font_size=45))
        self.dd_type = TextInput(multiline=False, font_size=35)
        self.add_widget(self.dd_type)

        self.add_widget(MyLabel(text="DD Date", font_size=45))
        self.dd_date = TextInput(multiline=False, font_size=35)
        self.add_widget(self.dd_date)

        self.add_widget(MyLabel(text="DD Loc", font_size=45))
        self.dd_loc = TextInput(multiline=False, font_size=35)
        self.add_widget(self.dd_loc)

        self.add_widget(MyLabel2(text="Original ID", font_size=45))
        self.orig_id = TextInput(multiline=False, font_size=35)
        self.add_widget(self.orig_id)

        self.add_widget(MyLabel(text="Vendor ID", font_size=45))
        self.ven_id = TextInput(multiline=False, font_size=35)
        self.add_widget(self.ven_id)

        self.add_widget(MyLabel2(text="Request ID", font_size=45))
        self.req_id = TextInput(multiline=False, font_size=35)
        self.add_widget(self.req_id)

        self.add_widget(Label())
        self.submit = Button(text="Submit", font_size=45)
        self.add_widget(self.submit)
        self.submit.bind(on_press=self.subPress)

    def subPress(self, btn):
        btnPres(0)


class MyLabel(Label):
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, .82, .863, 0.9)
            Rectangle(pos=self.pos, size=self.size)


class MyLabel2(Label):
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, .82, .953, 0.9)
            Rectangle(pos=self.pos, size=self.size)


def main():
    print("@ top")
    chain = HackathonChain()
    key_chain = enc.HackathonKeyChain()
    chain.add_block('SSAE18 Soc2', 'audit.pdf', '10/27/2018', 'Equifax', 'Amazon', 'FICO')
    print("@ exit")
    global blockchain
    blockchain = visualize_blockchain(chain)
    GUI().run()
    Daemon.serveSimple(
        {
            HackathonChain: "genesis.hackathonchain"
        },
        ns=False)


ddtypeRead = None
origRead = None
venRead = None
reqRead = None


def newRequest(doctype, orig, vendor, requestee):
    chain.add_block(doctype, None, date.today(), orig, vendor, requestee)

print("Chain", chain)
while(ddtypeRead is not None):
    newRequest(ddtypeRead, origRead, venRead, reqRead)
    print("Chain", chain)

if __name__ == "__main__":
    main()
