import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5.QtCore import pyqtSlot
import resources.qtextramods as qte 
import resources.smartghost as smartghost

ref_logic = smartghost.cls_obj_logic()

class cls_stack_widget(qtw.QFrame):

    sig_delete = qtc.pyqtSignal(qtc.QObject)
    sig_update = qtc.pyqtSignal()

    def __init__(self, wgt_pass, wgt_salt, var_domain):
        super().__init__()

        temp_font_id = qtg.QFontDatabase.addApplicationFont(
            os.path.join(
            os.path.dirname(__file__), "typewcond_demi.otf"))
        temp_font_family = qtg.QFontDatabase.applicationFontFamilies(temp_font_id)[0]
        var_font = qtg.QFont(temp_font_family)
        var_font.setPointSize(15)
        var_font_small = qtg.QFont(temp_font_family)
        var_font_small.setPointSize(10)
        del temp_font_id
        del temp_font_family

        self.wgt_pass = wgt_pass
        self.wgt_salt = wgt_salt

        self.settings = qtc.QSettings('most_ghost', 'ghostpass').value('--ghostconfig/order')


        self.setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Fixed
        )

        self.setLineWidth(5)
        self.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Plain)



        lo_vertical = qtw.QVBoxLayout()
        self.setLayout(lo_vertical)

        struct_top_strip = qtw.QWidget()
        struct_top_strip.setSizePolicy(
            qtw.QSizePolicy.Preferred,
            qtw.QSizePolicy.Fixed)
        lo_horizontal = qtw.QHBoxLayout()
        struct_top_strip.setLayout(lo_horizontal)
        lo_vertical.addWidget(struct_top_strip)

        self.wgt_domain_name = qtw.QLineEdit(var_domain)
        self.wgt_domain_name.setSizePolicy(
            qtw.QSizePolicy.Maximum,
            qtw.QSizePolicy.Minimum)
        self.wgt_domain_name.editingFinished.connect(
            lambda : self.wgt_domain_name.setText(self.wgt_domain_name.text().lower()))
        # self.wgt_domain_name.editingFinished.connect(self.sig_update.emit)
        # This is a bit of a clunky way to force lower case, but it works without having to set a validator.
        # Maybe there's a potential use where a user needs to have passwords for both Google and google,
        # but I think it's more likely that having the option to mix and match, when a single letter capitalized
        # means a totally different hash, is just going to lead to potential headaches.
        self.wgt_domain_name.setFont(var_font)
        lo_horizontal.addWidget(self.wgt_domain_name)

        self.wgt_generated = qtw.QLineEdit(
            self,
            readOnly = True,
            placeholderText = ''
            )
        self.wgt_generated.mouseReleaseEvent = lambda _: self.slot_force_highlight(self.wgt_generated)
        lo_vertical.addWidget(self.wgt_generated) 

        struct_spacer = qtw.QSpacerItem(40, 20, qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Minimum)
        lo_horizontal.addSpacerItem(struct_spacer)



        struct_toggle_type = qtw.QWidget()
        struct_toggle_type.setSizePolicy(
            qtw.QSizePolicy.Fixed,
            qtw.QSizePolicy.Ignored)
        struct_toggle_type.setFixedHeight(5)
        # We'll overwrite this later, but for right now I don't want the size of this section messing with
        # the calculated size of the full top strip.
        lo_toggle_type = qtw.QVBoxLayout(struct_toggle_type)
        self.wgt_toggle_type_switch = qte.AnimatedToggle(
            pulse_checked_color="#FF000000", # First two letters are alpha
            pulse_unchecked_color="#FF000000"
            )
        self.wgt_toggle_type_switch.clicked.connect(self.func_phrase_clicked)
        lo_toggle_type.addWidget(self.wgt_toggle_type_switch)
        self.wgt_toggle_type_label = qtw.QLabel('...')
        self.wgt_toggle_type_label.setFont(var_font_small)
        self.wgt_toggle_type_label.setAlignment(qtc.Qt.AlignHCenter)
        lo_toggle_type.addWidget(self.wgt_toggle_type_label) 
        lo_horizontal.addWidget(struct_toggle_type)

        self.wgt_size_spinbox = qtw.QSpinBox()
        self.wgt_size_spinbox.wheelEvent = lambda _: None 
        # I'm sure there are 4 or 5 people who use the mouse wheel to activate one of these. 
        # For everyone else, the mouse wheel is there to scroll the window, not screw with values.
        # There's nothing worse than trying to scroll the window and instead the mouse catches on a
        # value box for a moment and stops scrolling and starts adjusting the thing in the box instead.
        self.wgt_size_spinbox.setFont(var_font)
        #self.widget_size_phrase.valueChanged.connect(self.signal_update.emit)
        lo_horizontal.addWidget(self.wgt_size_spinbox)


        var_dynamic_height = int(struct_top_strip.sizeHint().height())
        struct_toggle_type.setFixedHeight(var_dynamic_height)



        self.wgt_generate_button = qtw.QPushButton('generate')
        self.wgt_generate_button.clicked.connect(self.slot_generating_pass)
        self.wgt_generate_button.setFont(var_font)
        lo_horizontal.addWidget(self.wgt_generate_button)

        self.wgt_delete_button = qtw.QPushButton('-')
        self.wgt_delete_button.setSizePolicy(
            qtw.QSizePolicy.Maximum,
            qtw.QSizePolicy.Maximum)
        self.wgt_delete_button.clicked.connect(self.slot_requesting_delete)
        self.wgt_delete_button.setFont(var_font)
        self.wgt_delete_button.setStyleSheet("""
        QPushButton:hover {
            background-color: #7d0f1f;
            border-color: #ff252b;
            } """)
        lo_horizontal.addWidget(self.wgt_delete_button)

        self.var_delete_double_check = False

        self.func_initialize_values()
        self.func_save_settings()

        qtc.QTimer.singleShot(10, lambda:
                               self.wgt_size_spinbox.setFixedWidth(
                               self.wgt_size_spinbox.sizeHint().width() + 12))
        # This is clunky but it gets the job done. 12 pixels seems to be the 
        # magic number to make the contents of the spinbox 'solid'.



    @pyqtSlot()
    def slot_requesting_delete(self):
        if self.var_delete_double_check == True:
            self.sig_delete.emit(self)
        elif self.var_delete_double_check == False:
            self.func_delete_activated()


    def func_delete_activated(self):
        self.var_delete_double_check = True
        self.wgt_delete_button.setText('!')
        self.wgt_delete_button.setStyleSheet("""
        QPushButton:hover {
            background-color: #d3181c;
            border-color: #ff252b;
            } """)
        qtc.QTimer.singleShot(1000, self.func_delete_deactivated)
                              
    def func_delete_deactivated(self):
        self.var_delete_double_check = False
        self.wgt_delete_button.setText('-')
        self.wgt_delete_button.setStyleSheet("""
        QPushButton:hover {
            background-color: #7d0f1f;
            border-color: #ff252b;
            } """)

    




    @pyqtSlot()
    def slot_generating_pass(self):
        var_password = self.wgt_pass.text()
        var_salt = self.wgt_salt.text()
        var_size = self.wgt_size_spinbox.value()
        var_domain = self.wgt_domain_name.text()
        var_salt_toggle = self.settings.value('--ghostconfig/second_required')

        if var_password == '':
            self.wgt_generated.setText('')
            self.wgt_generated.setPlaceholderText('please enter a password.')
        elif len(var_password) < 8:
            self.wgt_generated.setText('')
            self.wgt_generated.setPlaceholderText('please enter a longer password.')
        elif var_salt_toggle == 'yes' and var_salt == '':
            self.wgt_generated.setText('')
            self.wgt_generated.setPlaceholderText('please enter a second password.')
        elif var_salt_toggle == 'yes' and len(var_salt) < 8:
            self.wgt_generated.setText('')
            self.wgt_generated.setPlaceholderText('please enter a longer second password.')
        else:
            if self.var_global_toggle_state == 2:
                self.wgt_generated.setText(ref_logic.func_hash_gen(var_domain, var_password, var_size, var_salt))
            elif self.var_global_toggle_state == 0:
                self.wgt_generated.setText(ref_logic.func_passphrase_gen(var_domain, var_password, var_size, var_salt))
            self.wgt_generated.setCursorPosition(0)

    @pyqtSlot()
    def slot_fake_gen_click(self):
        self.wgt_generate_button.click()

    @pyqtSlot()
    def slot_force_highlight(self, wgt_generated):
        wgt_generated.end(False)
        wgt_generated.home(True)

    def func_phrase_clicked(self):
        self.var_global_toggle_state = self.wgt_toggle_type_switch.checkState()
        self.func_change_max_type()
        self.func_save_settings()

    def func_change_max_type(self):
        wgt_toggle = self.wgt_toggle_type_switch
        wgt_spinbox = self.wgt_size_spinbox
        var_domain = self.wgt_domain_name.text()

        try:
            if var_domain == 'domain':
                raise TypeError # We want 'domain' to return default so we'll raise a fake error
            var_hash = int(self.settings.value(f'{var_domain}/hash_length'))
            var_word = int(self.settings.value(f'{var_domain}/word_length'))
        except TypeError:
            var_hash = int(self.settings.value('--ghostconfig/default_len_hash'))
            var_word = int(self.settings.value('--ghostconfig/default_len_word'))



        if wgt_toggle.checkState() == 2: # Secure Hash
            wgt_spinbox.setMaximum(258)
            wgt_spinbox.setMinimum(20)
            wgt_spinbox.setValue(var_hash)
            wgt_spinbox.setSuffix(' chars')
            self.wgt_toggle_type_label.setText('hash')
        if wgt_toggle.checkState() == 0: # Passphrase
            wgt_spinbox.setMaximum(20)
            wgt_spinbox.setMinimum(6)
            wgt_spinbox.setValue(var_word)
            wgt_spinbox.setSuffix(' words')
            self.wgt_toggle_type_label.setText('passphrase')




    
    def func_save_settings(self):
        var_domain = self.wgt_domain_name.text()
        var_toggle = self.wgt_toggle_type_switch.checkState()
        var_size = self.wgt_size_spinbox.value()
        var_default_hash = self.settings.value('--ghostconfig/default_len_hash')
        var_default_word =self.settings.value('--ghostconfig/default_len_word')


        self.settings.setValue(f'{var_domain}/toggle_state', f'{var_toggle}')
        
        if var_toggle == 2:
           self.settings.setValue(f'{var_domain}/hash_length', f'{var_size}')
           self.settings.setValue(f'{var_domain}/word_length', f'{var_default_word}')
        elif var_toggle == 0:
           self.settings.setValue(f'{var_domain}/hash_length', f'{var_default_hash}')
           self.settings.setValue(f'{var_domain}/word_length', f'{var_size}')

    def func_save_order(self):
        var_domain = self.wgt_domain_name.text()
        settings_order = self.settings.value('--ghostconfig/order')
        updated_order = settings_order + var_domain + '|'
        self.settings.setValue(f'--ghostconfig/order', updated_order)

    def func_initialize_values(self):

        self.settings = qtc.QSettings('most_ghost', 'ghostpass')

        var_domain = self.wgt_domain_name.text()

        var_list_domains = set()
        temp_settings_keys = self.settings.allKeys()
        for i in temp_settings_keys:
            var_list_domains.add(i.split('/')[0])

        if var_domain in var_list_domains and var_domain != 'domain':
            var_toggle = int(self.settings.value(f'{var_domain}/toggle_state'))
        else:
            var_default = self.settings.value('--ghostconfig/default_type')
            if var_default == 'hash':
                var_toggle = 2
            elif var_default == 'word':
                var_toggle = 0

        self.wgt_toggle_type_switch.setCheckState(var_toggle)
        self.func_phrase_clicked()


