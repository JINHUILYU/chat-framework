import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QFormLayout, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Bot Interface")
        self.setGeometry(100, 100, 1000, 600)

        # Main layout
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Left-side Navigation Panel
        self.nav_list = QListWidget()
        self.nav_list.addItem("Roles")
        self.nav_list.addItem("Custom")
        self.nav_list.addItem("Pipeline")
        self.nav_list.addItem("Arbitration")
        self.nav_list.currentRowChanged.connect(self.display_content)

        # Stacked widget to hold different pages
        self.stacked_widget = QStackedWidget()

        # Add pages to stacked widget
        self.roles_page = self.create_roles_page()
        self.custom_page = self.create_custom_page()
        self.pipeline_page = self.create_pipeline_page()
        self.arbitration_page = self.create_arbitration_page()

        self.stacked_widget.addWidget(self.roles_page)
        self.stacked_widget.addWidget(self.custom_page)
        self.stacked_widget.addWidget(self.pipeline_page)
        self.stacked_widget.addWidget(self.arbitration_page)

        # Add widgets to main layout
        main_layout.addWidget(self.nav_list)
        main_layout.addWidget(self.stacked_widget)

    def create_roles_page(self):
        # Page for role selection
        roles_page = QWidget()
        layout = QVBoxLayout()

        # Title label
        title = QLabel("Roles")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Circular buttons for roles (simulated with regular buttons for simplicity)
        grid_layout = QGridLayout()
        for i in range(4):
            for j in range(4):
                button = QPushButton(f"{i * 4 + j + 1}")
                button.setFixedSize(60, 60)
                grid_layout.addWidget(button, i, j, alignment=Qt.AlignCenter)

        layout.addLayout(grid_layout)
        roles_page.setLayout(layout)
        return roles_page

    def create_custom_page(self):
        # Page for custom prompts
        custom_page = QWidget()
        layout = QVBoxLayout()

        # Prompt area
        prompt_label = QLabel("Prompt")
        layout.addWidget(prompt_label)

        prompt_input = QTextEdit()
        layout.addWidget(prompt_input)

        # Input box for entering data
        input_layout = QHBoxLayout()
        input_box = QLineEdit()
        enter_button = QPushButton("Enter")
        input_layout.addWidget(input_box)
        input_layout.addWidget(enter_button)

        layout.addLayout(input_layout)
        custom_page.setLayout(layout)
        return custom_page

    def create_pipeline_page(self):
        # Page for pipeline setup
        pipeline_page = QWidget()
        layout = QVBoxLayout()

        # Placeholder for pipeline diagram
        diagram_label = QLabel("Pipeline (diagram placeholder)")
        diagram_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(diagram_label)

        # Multiple input boxes for pipeline stages
        for i in range(3):
            input_box = QLineEdit()
            input_box.setPlaceholderText(f"Prompt-{i + 1}")
            layout.addWidget(input_box)

        enter_button = QPushButton("Enter")
        layout.addWidget(enter_button)
        pipeline_page.setLayout(layout)
        return pipeline_page

    def create_arbitration_page(self):
        # Page for arbitration setup
        arbitration_page = QWidget()
        layout = QVBoxLayout()

        # Placeholder for arbitration diagram
        diagram_label = QLabel("Arbitration (diagram placeholder)")
        diagram_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(diagram_label)

        # Multiple input boxes for arbitration prompts
        for i in range(4):
            input_box = QLineEdit()
            input_box.setPlaceholderText(f"Prompt-{i + 1}")
            layout.addWidget(input_box)

        enter_button = QPushButton("Enter")
        layout.addWidget(enter_button)
        arbitration_page.setLayout(layout)
        return arbitration_page

    def display_content(self, index):
        # Show the selected page based on navigation item
        self.stacked_widget.setCurrentIndex(index)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
