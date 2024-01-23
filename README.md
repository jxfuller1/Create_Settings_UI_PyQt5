Program Will add UI elements based on a TXT File

- Use create_options_UI() Function to create the elements - Returns a QWidget() with all the UI elements

  a) contains parameters for customizing alignments/fonts/stretches for the layouts

- Use getAllElements() to get all widgets to create signal connections in main program


TXT file can accept only this formatting

1) name = x, y or z                ->   returns QLineEdits() if STR, QSpinBoxes if INT/FLOAT
2) name = (x, y, TRUE/FALSE, z)    ->   returns GroupBox() w/ QRadioButtons()   (true will be the radiobutton checked)
3) name = TRUE/FALSE               ->   returns QCheckBox()  w/ True/False as checkstate()
4) name = [[x, y, z, INT]]         ->   returns QCombobox()  w/ INT as the currentindex() 


Turns this:

![1](https://github.com/jxfuller1/Create_Settings_UI_PyQt5/assets/123666150/2b2e9bce-8591-4772-a936-ef03cb57083a)

Into this:

![2](https://github.com/jxfuller1/Create_Settings_UI_PyQt5/assets/123666150/e9b275e6-a07b-48ee-8dde-7b5120efffb5)
