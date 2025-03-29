from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGroupBox, QFormLayout, QComboBox
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSettings
import pyperclip

def calculate_fuel_mix(tank_capacity, current_fuel, current_ethanol, target_ethanol):
    available_space = tank_capacity - current_fuel
    
    if available_space <= 0:
        return "No space available in the tank to add fuel."
    
    if target_ethanol == 0.85:  # When target ethanol is 85%
        # Calculate the resulting ethanol percentage if the rest of the tank is filled with E85
        total_fuel = current_fuel + available_space
        total_ethanol = current_fuel * current_ethanol + available_space * 0.85
        resulting_ethanol = total_ethanol / total_fuel
        return f"Resulting Ethanol Percentage: {round(resulting_ethanol * 100, 2)}%"
    
    x = (target_ethanol * tank_capacity - current_fuel * current_ethanol - 0.10 * available_space) / (0.85 - 0.10)
    y = available_space - x  
    
    if x < 0 or y < 0:
        return "Desired ethanol percentage cannot be achieved with given constraints."
    
    return f"E85 Needed: {round(x, 2)} gallons\nRegular Gasoline Needed: {round(y, 2)} gallons\nNew Ethanol Percentage: {round(target_ethanol * 100, 2)}%"

class E85Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("E85Calculator", "Settings")
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        self.setWindowTitle('E85 Fuel Mixer')
        self.setStyleSheet("background-color: #2C3E50; color: white;")
        
        font = QFont("Arial", 12)
        self.setFont(font)
        
        self.layout = QVBoxLayout()
        
        self.input_group = QGroupBox("Enter Fuel Details")
        self.input_layout = QFormLayout()
        self.inputs = {}
        
        fields = {
            "Tank Capacity (gal)": "tank_capacity",
            "Current Fuel (gal)": "current_fuel",
            "Current Ethanol % (e.g., 10 for 10%)": "current_ethanol"
        }
        
        prev_input = None
        for label, key in fields.items():
            lbl = QLabel(label)
            lbl.setFont(font)
            line_edit = QLineEdit()
            line_edit.setStyleSheet("padding: 5px; border-radius: 5px;")
            line_edit.setAlignment(Qt.AlignCenter)
            line_edit.returnPressed.connect(self.focus_next_input)
            self.input_layout.addRow(lbl, line_edit)
            self.inputs[key] = line_edit
            
            if prev_input:
                prev_input.next_input = line_edit
            prev_input = line_edit
        
        lbl_target = QLabel("Target Ethanol %")
        lbl_target.setFont(font)
        self.target_ethanol_combo = QComboBox()
        self.target_ethanol_combo.addItems(["10", "15", "30", "50", "85"])
        self.input_layout.addRow(lbl_target, self.target_ethanol_combo)
        
        self.input_group.setLayout(self.input_layout)
        self.layout.addWidget(self.input_group)
        
        self.calculate_button = QPushButton('Calculate')
        self.calculate_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.calculate_button.setStyleSheet("background-color: #1ABC9C; color: white; padding: 10px; border-radius: 5px;")
        self.calculate_button.clicked.connect(self.calculate)
        self.layout.addWidget(self.calculate_button)
        
        self.copy_button = QPushButton('Copy Result')
        self.copy_button.setFont(QFont("Arial", 12))
        self.copy_button.setStyleSheet("background-color: #F39C12; color: white; padding: 10px; border-radius: 5px;")
        self.copy_button.clicked.connect(self.copy_result)
        self.layout.addWidget(self.copy_button)
        
        self.clear_button = QPushButton('Clear')
        self.clear_button.setFont(QFont("Arial", 12))
        self.clear_button.setStyleSheet("background-color: #E74C3C; color: white; padding: 10px; border-radius: 5px;")
        self.clear_button.clicked.connect(self.clear_inputs)
        self.layout.addWidget(self.clear_button)
        
        self.result_label = QLabel('')
        self.result_label.setFont(QFont("Arial", 12))
        self.result_label.setStyleSheet("padding: 10px; background-color: #34495E; border-radius: 5px;")
        self.layout.addWidget(self.result_label)
        
        self.setLayout(self.layout)
    
    def focus_next_input(self):
        sender = self.sender()
        if hasattr(sender, 'next_input') and sender.next_input:
            sender.next_input.setFocus()
        else:
            self.calculate_button.setFocus()
    
    def calculate(self):
        try:
            tank_capacity = float(self.inputs["tank_capacity"].text())
            current_fuel = float(self.inputs["current_fuel"].text())
            current_ethanol = float(self.inputs["current_ethanol"].text()) / 100
            target_ethanol = float(self.target_ethanol_combo.currentText()) / 100
            
            result = calculate_fuel_mix(tank_capacity, current_fuel, current_ethanol, target_ethanol)
            self.result_label.setText(result)
            self.save_settings()
        except ValueError:
            self.result_label.setText("Please enter valid numbers.")
    
    def copy_result(self):
        pyperclip.copy(self.result_label.text())
    
    def clear_inputs(self):
        for field in self.inputs.values():
            field.clear()
        self.result_label.setText('')
    
    def save_settings(self):
        for key, field in self.inputs.items():
            self.settings.setValue(key, field.text())
    
    def load_settings(self):
        for key, field in self.inputs.items():
            field.setText(self.settings.value(key, ""))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = E85Calculator()
    window.show()
    sys.exit(app.exec_())
