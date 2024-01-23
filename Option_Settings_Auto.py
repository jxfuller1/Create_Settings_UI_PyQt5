from typing import Dict, Union, List

# options file must be in same directory as program
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QLayout, QLineEdit, QSpinBox, \
    QDoubleSpinBox, QCheckBox, QComboBox, QGroupBox, QRadioButton, QFrame
from ast import literal_eval
import os
import getpass
import shutil


"""
Program Will add UI elements based on a TXT File

- Use create_options_UI() Function to create the elements
- Use getAllElements() to get all widgets to create signal connections in main program

TXT file can accept only this formatting

1) name = x, y or z                ->   returns QLineEdits() if STR, QSpinBoxes if INT/FLOAT
2) name = (x, y, TRUE/FALSE, z)    ->   returns GroupBox() w/ QRadioButtons()   (true will be the radiobutton checked)
3) name = TRUE/FALSE               ->   returns QCheckBox()  w/ True/False as checkstate()
4) name = [[x, y, z, INT]]         ->   returns QCombobox()  w/ INT as the currentindex() 

"""



def getOptions(path: str) -> dict:
    main_settings_dict = None

    file_valid = False
    if os.path.exists(path):
        file = path.split(".")
        if file[-1][-3:] == "txt":
            file_valid = True

    if file_valid:
        main_settings = open(path, "r")
        main_settings_list = main_settings.readlines()

        main_settings_list = [x.strip('\n') for x in main_settings_list if x.count('=') == 1]
        main_settings_dict = {key_value[0].strip(): key_value[1].strip() for key_value in (i.split("=") for i in main_settings_list)}

    return main_settings_dict


# change data types in options text file, handles only tuples (items with commas), digits, strings, bools
def options_affix_datatypes(options_dict: Dict[str, str]) -> Dict[str, Union[tuple, str, int, float, list]]:
    for key in options_dict:
        # make a tuple of strings or tuple of integers
        if "," in options_dict[key]:
            temp_split = options_dict[key].split(",")
            final_value = [x.strip() for x in temp_split]

            # () make a tuple
            if "(" == final_value[0][0] and ")" == final_value[-1][-1]:
                final_value[0] = final_value[0].strip("(")
                final_value[-1] = final_value[-1].strip(")")
                final_value = tuple(x for x in final_value)

            # [[]] make a list with list
            elif "[[" == final_value[0][0:2] and "]]" == final_value[-1][-2:]:
                final_value[0] = final_value[0].strip("[[")
                final_value[-1] = final_value[-1].strip("]]")
                final_value = [[x for x in final_value]]

            # if all integers turn into list of integers
            elif all(x.isdigit() for x in final_value):
                    final_value = [int(x) for x in final_value]

            # turn them all to bools to see if they are all bool
            else:
                try:
                    final_value = [literal_eval(s) for s in final_value]
                except:
                    pass

            options_dict[key] = final_value

        # make bool
        elif "TRUE" == options_dict[key].upper() or "FALSE" == options_dict[key].upper():
            options_dict[key] = bool(options_dict[key])

        # make integer
        elif options_dict[key].isdigit():
            options_dict[key] = int(options_dict[key])

        # make float
        else:
            try:
                options_dict[key] = float(options_dict[key])
            except:
                pass

    return options_dict


def getAllElements(widget_layout: [QWidget, QLayout]) -> dict:
    """
    function that gets all items in a layout recursively and passes into a dict
    :param element: Qwidget or layout
    :return:  return as a dict, all layout/widget/layout items object names as keys with the values as the layout/widget/layout item
    """
    element_items = {}

    if isinstance(widget_layout, QWidget):
        layout = widget_layout.layout()
    else:
        layout = widget_layout

    def traverse_layout(l):
        try:
            if l.objectName().strip() == "":
                element_items[str(hex(id(l)))] = l
            else:
                element_items[l.objectName()] = l
        except:
            element_items[str(hex(id(l)))] = l

        for i in range(l.count()):
            item = l.itemAt(i)
            item_to_check = None

            if item:
                obj = item.widget()
                lay = item.layout()

                if obj:
                    item_to_check = obj
                elif lay:
                    item_to_check = lay
                else:
                    item_to_check = item

                try:
                    if item_to_check.objectName().strip() == "":
                        element_items[str(hex(id(item_to_check)))] = item_to_check
                    else:
                        element_items[item_to_check.objectName()] = item_to_check
                except:
                    element_items[str(hex(id(item_to_check)))] = item_to_check

            if item_to_check:
                if isinstance(item_to_check, QLayout):
                    traverse_layout(item_to_check)

                if isinstance(item_to_check, QWidget):
                    lay = item_to_check.layout()
                    if lay:
                        traverse_layout(lay)

    traverse_layout(layout)

    return element_items


def create_options_UI(user_path: str = None, columns: int = 0, inner_key_font: QFont() = None,
                      inner_format: dict = None, outer_format: dict = None, save_default_buttons: bool = False, default_path: str = None):

    """
    This program mainly for creating easy to add options settings in any program you want to have user defined settings

    :param user_path:  ------- Path to user settings TXT file

    :param columns: -------- Number of columns you want elements to be separated into so all the widgets
                    aren't all in 1 big list on the UI

    :param inner_key_font: --------Qfont() for labels for the widgets

    :param inner_format: -------- For formatting inner element layouts by datatype, takes the form of:
                        {str: {"spacing": None, "label_alignment": None, "widget_alignment": None, "front_end_stretch": None, "backend_stretch": stretch}}
                        spacing = provides spacing between elements must be an integer value
                        label_alignment = must be a Qt.Alignment flag to give label alignment
                        widget_alignment = must be a Qt.Alignment flag to give widget alignment
                        front_end_stretch / backend_stretch = only accepts "stretch" for value if you want to .addstretch() to layout

    :param outer_format: ------- For formatting outer element layouts, takes the form of:
                        {"front_end_stretch": None, "spacing": None,  "backend_stretch": "stretch"}
                        if you want to addstretch() to layout, put in "stretch", if you want spacing to front or end
                        of layout add integer value.
                        NOTE: At this time can't put spacing between elements of the layout

    :param save_default_buttons: -------- Adds Save/Reset Default buttons

    :param default_path:  ------- Path to default settings TXT file

    :return: QWidget
    """

    # read given txt file to extract options
    main_settings_dict = None
    if user_path:

        main_settings_dict = getOptions(user_path)
    elif default_path:
        main_settings_dict = getOptions(default_path)

    # return data types from the txt file
    try:
        options = options_affix_datatypes(main_settings_dict)
    except:
        print("ERROR NO VALID PATHS PASSED")

    # changes inner format if user passes in new values
    inner_format = inner_element_format(inner_format)

    # change outer format if user passes in new values
    outer_format = outer_element_format(outer_format)

    # turns all options into UI elements based on datatypes
    total_elements = []
    for key, value in options.items():

        element = return_UI_element(key, value, key_font=inner_key_font, inner_format=inner_format)
        if element:
            total_elements.append(element)

    # divide elements into columns if user doesn't want all UI elements in a big long vertical list
    divided = divide_elements(total_elements, columns)

    # widget to be passed to window
    upper_widget = QWidget()

    save_layout = None
    if save_default_buttons and default_path:
        save_layout = create_default_buttons(default_path=default_path, user_path=user_path, option_items_upper_widget=upper_widget)

    # if more than 1 column of elements to split
    if len(divided) >= 2:
        upper_vert_layout = QVBoxLayout()
        
        column_elements = []
        for i in divided:
            # vertical line for separation between each "column" of elements
            frame = QFrame()
            frame.setFrameShape(QFrame.VLine)
            frame.setFrameShadow(QFrame.Sunken)

            VLayout = build_outer_element(i, outer_format=outer_format, layout=QVBoxLayout())
            column_elements.append(VLayout)

            # don't add qframe to end
            if divided.index(i)+1 != len(divided):
                column_elements.append(frame)

        layout = build_outer_element(column_elements, outer_format=outer_format, layout=QHBoxLayout())

        upper_vert_layout.addLayout(layout)
        if save_layout:
            upper_vert_layout.addLayout(save_layout)

        upper_widget.setLayout(upper_vert_layout)

    # if only 1 column
    if len(divided) <= 1:

        upper_layout = build_outer_element(divided[0], outer_format=outer_format, layout=QVBoxLayout())
        if save_layout:
            upper_layout.addLayout(save_layout)

        upper_widget.setLayout(upper_layout)

    return upper_widget


def create_layout(*args, layout: QLayout) -> QLayout:
    """
    :param args:  List of elements to add to the layout.
                  Supported types: QWidget, Layouts, AlignmentFlags, int (for spacing), "stretch" (add .addStretch()
                  with no parameters)
    :param layout:  QHBoxLayout, QVBoxLayout mainly supported, may work for other layouts
    :return:  Returns Layout with added elements/flags/spacing/stretching
    """

    for i in args:
        if isinstance(i, QWidget):
            layout.addWidget(i)
        elif isinstance(i, QLayout):
            layout.addLayout(i)

        # add alignment for previous element
        elif isinstance(i, Qt.AlignmentFlag):
            try:
                index = (args.index(i))-1
                layout.setAlignment(args[index], i)
            except:
                pass

        elif type(i) == int:
            layout.addSpacing(i)
        elif type(i) == str:
            if i.upper() == "STRETCH":
                layout.addStretch()

    return layout


def return_UI_element(key: str, value: [tuple, str, int, float, list], key_font: QFont()=None,
                      inner_format: dict=None) -> Union[QWidget, QLayout, None]:
    element = None

    if type(value) == str:
        label = create_element_label(key, key_font, inner_format[str]["label_alignment"])

        line = QLineEdit()
        line.setText(value)
        line.setObjectName(key + "_edit")

        element = build_inner_element(data_type=str, inner_format=inner_format, label=label, widget=line, layout=QHBoxLayout())

    elif type(value) == int:
        label = create_element_label(key, key_font, inner_format[int]["label_alignment"])

        spin = QSpinBox()
        spin.setMinimum(0)
        spin.setMaximum(10000000)
        spin.setValue(value)
        spin.setObjectName(key + "_spin")

        element = build_inner_element(data_type=int, inner_format=inner_format, label=label, widget=spin, layout=QHBoxLayout())

    elif type(value) == float:
        label = create_element_label(key, key_font, inner_format[float]["label_alignment"])

        spin = QDoubleSpinBox()
        spin.setDecimals(2)
        spin.setMinimum(0)
        spin.setMaximum(10000000)
        spin.setValue(value)
        spin.setObjectName(key + "_spin")

        element = build_inner_element(data_type=float, inner_format=inner_format, label=label, widget=spin, layout=QHBoxLayout())

    elif type(value) == bool:
        check = QCheckBox(key)
        check.setObjectName(key + "_check")
        if value == True:
            check.setCheckState(Qt.Checked)
        else:
            check.setCheckState(Qt.Unchecked)

        element = build_inner_element(data_type=bool, inner_format=inner_format, widget=check, layout=QHBoxLayout())

    elif type(value) == list:
        if type(value[0]) != list:
            label = create_element_label(key, key_font, inner_format[list]["label_alignment"])

            total = []
            for i in value:
                if type(i) == int:
                    spin = QSpinBox()
                    spin.setMinimum(0)
                    spin.setMaximum(100000)
                    spin.setValue(i)
                    spin.setObjectName(key + str(value.index(i)) + "_spin")
                    total.append(spin)

                elif type(i) == float:
                    spin = QDoubleSpinBox()
                    spin.setMinimum(0)
                    spin.setMaximum(100000)
                    spin.setDecimals(2)
                    spin.setValue(i)
                    spin.setObjectName(key + str(value.index(i)) + "_spin")
                    total.append(spin)

                elif type(i) == str:
                    line = QLineEdit()
                    line.setText(i)
                    line.setObjectName(key + str(value.index(i)) + "_edit")
                    total.append(line)

            if len(total) != 0:
                element = build_inner_element(data_type=list, inner_format=inner_format, label=label, widget=total, layout=QHBoxLayout())

        else:
            if type(value[0]) == list:
                combo = QComboBox()
                # items except last one, which will be the active index
                items = value[0][:-1]
                combo.addItems(items)

                if value[0][-1].isdigit:
                    combo.setCurrentIndex(int(value[0][-1]))

                combo.setObjectName(key + "_combo")

                # reuse bool data type argument for this one
                element = build_inner_element(data_type=bool, inner_format=inner_format, widget=combo, layout=QHBoxLayout())

    elif type(value) == tuple:
        group = QGroupBox(key)
        group.setObjectName(key + "_group")

        radio_buttons = []
        check_index = 0
        for i in value:
            if i.upper() == "TRUE":
                check_index = value.index(i)-1
            else:
                radio = QRadioButton(i)
                radio.setObjectName(key + str(value.index(i)) + "_radio")
                radio_buttons.append(radio)

        radio_buttons[check_index].setChecked(True)

        if len(radio_buttons) != 0:
            group_layout = build_inner_element(data_type=tuple, inner_format=inner_format, widget=radio_buttons, layout=QVBoxLayout())
            group.setLayout(group_layout)

        element = group

    return element


# for building the options to pass into create_layout function
def build_inner_element(data_type: type, inner_format: dict, label: QLabel=None
                        , widget: Union[QWidget, list, tuple]=None, layout: QLayout=None) -> QLayout:

    spacing = inner_format[data_type]["spacing"]
    widget_alignment = inner_format[data_type]["widget_alignment"]
    front_stretch = inner_format[data_type]["front_end_stretch"]
    back_stretch = inner_format[data_type]["backend_stretch"]

    if layout:
        layout.setObjectName(str(hex(id(layout))))

    if data_type != list and data_type != tuple:
        element = create_layout(front_stretch, label, spacing, widget, widget_alignment, back_stretch, layout=layout)
    elif data_type == list or data_type == tuple:
        element = create_layout(front_stretch, label, spacing, *widget, back_stretch, layout=layout)

    return element


# for building the options to pass into create_layout function
def build_outer_element(elements: list, outer_format: dict, layout: QLayout=None) -> QLayout:
    print(outer_format)

    front_stretch = outer_format["front_end_stretch"]
    spacing = outer_format["spacing"]
    back_stretch = outer_format["backend_stretch"]

    if layout:
        layout.setObjectName(str(hex(id(layout))))

    element = create_layout(front_stretch, spacing, *elements, spacing, back_stretch, layout=layout)

    return element


def create_element_label(key: str, font: QFont()=None, alignment: Qt.AlignmentFlag=None) -> QLabel:
    label = QLabel(key)
    label.setObjectName(key + "_label")
    if font:
        label.setFont(font)
    if alignment:
        try:
            label.setAlignment(alignment)
        except:
            pass

    return label


def divide_elements(total_elements: list, divide_number: int) -> List[list]:
    divided_elements = []

    if divide_number >= 2:
        avg_part_size = len(total_elements) // divide_number
        remainder = len(total_elements) % divide_number

        start = 0

        for i in range(divide_number):
            end = start + avg_part_size + (1 if i < remainder else 0)
            divided_elements.append(total_elements[start:end])
            start = end

    else:
        divided_elements.append(total_elements)

    return divided_elements


def inner_element_format(inner_format: dict=None) -> dict:
    # default format
    format = {str: {"spacing": None, "label_alignment": None, "widget_alignment": None, "front_end_stretch": None, "backend_stretch": "stretch"},
              int: {"spacing": None, "label_alignment": None, "widget_alignment": None, "front_end_stretch": None, "backend_stretch": "stretch"},
              float: {"spacing": None, "label_alignment": None, "widget_alignment": None, "front_end_stretch": None, "backend_stretch": "stretch"},
              bool: {"spacing": None, "label_alignment": None, "widget_alignment": None, "front_end_stretch": None, "backend_stretch": "stretch"},
              list: {"spacing": None, "label_alignment": None, "widget_alignment": None, "front_end_stretch": None, "backend_stretch": "stretch"},
              tuple: {"spacing": None, "label_alignment": None, "widget_alignment": None,"front_end_stretch": None, "backend_stretch": "stretch"}}

    # change inner formatting if user passes in new values
    if inner_format:
        for key, value in inner_format.items():
            if key in format.keys():

                for inner_key, new_value in value.items():
                    if inner_key in format[key].keys():
                        format[key][inner_key] = new_value

    return format


def outer_element_format(outer_format: dict=None) -> dict:
    format = {"front_end_stretch": None, "spacing": None,  "backend_stretch": "stretch"}

    if outer_format:
        for key, value in outer_format.items():
            if key in format.keys():
                format[key] = value

    return format


def create_default_buttons(default_path: str = None, user_path: str = None, option_items_upper_widget: QWidget = None) -> QLayout:
    format = outer_element_format({"front_end_stretch": "stretch", "backend_stretch": "stretch"})

    save_button = QPushButton("Save")
    save_button.setObjectName("save_button")
    save_button.clicked.connect(lambda: save_settings(user_path=user_path, default_path=default_path,
                                                      options_widget=option_items_upper_widget))

    default_button = QPushButton("Reset Defaults")
    default_button.setObjectName("default_button")
    default_button.clicked.connect(lambda: default_settings(user_path=user_path, default_path=default_path,
                                                            options_widget=option_items_upper_widget))

    save_layout = build_outer_element([save_button, default_button], outer_format=format,
                                      layout=QHBoxLayout())

    return save_layout


def save_settings(default_path: str, options_widget: dict, user_path: str = None):
    # if not user_path for user option files given, create it
    if not user_path:
        default_broken = default_path.split("\\")
        default_filename = default_broken[-1].split(".")
        user = getpass.getuser()
        my_path = os.path.abspath(os.path.dirname(__file__))
        user_path = my_path + "\\" + default_filename[0] + "_" + user + ".txt"

        if not os.path.exists(user_path):
            shutil.copy(default_path, user_path)

    get_text_widgets = [QLineEdit]
    get_value_widgets = [QSpinBox, QDoubleSpinBox]
    get_checkbox_widgets = [QCheckBox]
    get_radio_widgets = [QRadioButton]
    get_list_widgets = [QComboBox]

    elements = getAllElements(options_widget)
    retreive_options = getOptions(user_path)

    # build dict to save back text file with current values in the widgets
    text_dict = {}

    for key, value in retreive_options.items():
        total_items = []
        widget = None

        for name, obj in elements.items():
            if any(isinstance(obj, cls) for cls in get_text_widgets):
                if key in obj.objectName():
                    total_items.append(obj.text())
                    widget = obj

            elif any(isinstance(obj, cls) for cls in get_value_widgets):
                if key in obj.objectName():
                    total_items.append(str(obj.value()))
                    widget = obj

            elif any(isinstance(obj, cls) for cls in get_checkbox_widgets):
                if key in obj.objectName():
                    total_items.append(str(obj.isChecked()))
                    widget = obj

            elif any(isinstance(obj, cls) for cls in get_radio_widgets):
                if key in obj.objectName():
                    total_items.append(str(obj.text()))
                    if obj.isChecked():
                        total_items.append(str(obj.isChecked()))
                    widget = obj

            elif any(isinstance(obj, cls) for cls in get_list_widgets):
                if key in obj.objectName():
                    for i in range(obj.count()):
                        total_items.append(obj.itemText(i))

                    total_items.append(str(obj.currentIndex()))
                    widget = obj

        # turn list into proper format for dict
        if isinstance(widget, QLineEdit):
            edit_value = ', '.join(total_items)
            text_dict[key] = edit_value

        # turn list into proper format for dict
        if isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
            edit_value = ', '.join(total_items)
            text_dict[key] = edit_value

        # turn list into proper format for dict
        if isinstance(widget, QCheckBox):
            edit_value = ', '.join(total_items)
            text_dict[key] = edit_value

        # turn list into proper format for dict
        if isinstance(widget, QRadioButton):
            total_items[0] = "(" + total_items[0]
            total_items[-1] = total_items[-1] + ")"
            edit_value = ', '.join(total_items)
            text_dict[key] = edit_value

        # turn list into proper format for dict
        if isinstance(widget, QComboBox):
            total_items[0] = "[[" + total_items[0]
            total_items[-1] = total_items[-1] + "]]"
            edit_value = ', '.join(total_items)
            text_dict[key] = edit_value

    # Iterate through the dictionary items and write to the file
    with open(user_path, 'w') as file:
        for key, value in text_dict.items():
            file.write(f'{key} = {value}\n')


def default_settings(default_path: str, options_widget: dict, user_path: str = None):
    get_text_widgets = [QLineEdit]
    get_value_widgets = [QSpinBox, QDoubleSpinBox]
    get_checkbox_widgets = [QCheckBox]
    get_radio_widgets = [QRadioButton]
    get_list_widgets = [QComboBox]

    # read text file to get data
    retreive_options = getOptions(default_path)

    # turn text file data to datatypes
    data_dict = options_affix_datatypes(retreive_options)

    # get all objects that i want to change values on from default text file
    elements = getAllElements(options_widget)

    # iterate through default data text file
    for key, value in data_dict.items():
        total_items = []
        widget = None

        # iterate through all elements to get the objects i want to change values on
        for name, obj in elements.items():
            if any(isinstance(obj, cls) for cls in get_text_widgets):
                if key in obj.objectName():
                    total_items.append(obj)
                    widget = obj

            elif any(isinstance(obj, cls) for cls in get_value_widgets):
                if key in obj.objectName():
                    total_items.append(obj)
                    widget = obj

            elif any(isinstance(obj, cls) for cls in get_checkbox_widgets):
                if key in obj.objectName():
                    total_items.append(obj)
                    widget = obj

            elif any(isinstance(obj, cls) for cls in get_radio_widgets):
                if key in obj.objectName():
                    total_items.append(obj)
                    widget = obj

            elif any(isinstance(obj, cls) for cls in get_list_widgets):
                if key in obj.objectName():
                    total_items.append(obj)
                    widget = obj

        # change object values/states from objects gathered
        if isinstance(widget, QLineEdit):
            if isinstance(value, List):
                for index, text in enumerate(value):
                    total_items[index].setText(str(text))
            else:
                total_items[0].setText(str(value))

        if isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
            if isinstance(value, List):
                for index, text in enumerate(value):
                    total_items[index].setValue(text)
            else:
                total_items[0].setValue(value)

        if isinstance(widget, QCheckBox):
            if isinstance(value, List):
                for index, text in enumerate(value):
                    if text[index]:
                        total_items[index].setCheckState(Qt.Checked)
                    if not text[index]:
                        total_items[index].setCheckState(Qt.Unchecked)
            else:
                if value:
                    total_items[0].setCheckState(Qt.Checked)
                if not value:
                    total_items[0].setCheckState(Qt.Unchecked)

        if isinstance(widget, QRadioButton):
            if isinstance(value, List):
                for index, text in enumerate(value):
                    if text == True:
                        total_items[index-1].setChecked(True)
            else:
                if value == True:
                    total_items[0].setChecked(True)

        if isinstance(widget, QComboBox):
            if value[0][-1].isdigit():
                total_items[0].setCurrentIndex(int(value[0][-1]))

    # save settings back to default for user text file
    save_settings(default_path=default_path, options_widget=options_widget, user_path=user_path)


if __name__ == "__main__":
    pass