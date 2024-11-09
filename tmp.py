from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QButtonGroup,
    QGridLayout, QLineEdit, QScrollArea
)
from PyQt6.QtCore import Qt
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置主窗口
        self.setWindowTitle("Chat Bot Interface")
        self.setGeometry(100, 100, 800, 600)

        # 创建主布局
        main_layout = QHBoxLayout()

        # 左侧菜单布局
        menu_layout = QVBoxLayout()

        # 创建按钮和按钮组
        self.buttons = {
            "Home": QPushButton("Home"),
            "Roles": QPushButton("Roles"),
            "Custom": QPushButton("Custom"),
            "Pipeline": QPushButton("Pipeline"),
            "Arbitration": QPushButton("Arbitration")
        }

        # 设置按钮样式
        for button in self.buttons.values():
            button.setCheckable(True)
            button.setStyleSheet(
                """
                QPushButton {
                    padding: 10px;
                    border: 1px solid black;
                }
                QPushButton:checked {
                    background-color: #d1e7fd;
                    border: 2px solid black;
                }
                """
            )
            button.clicked.connect(self.change_page)
            menu_layout.addWidget(button)

        # 创建按钮组，确保一次只能有一个按钮被选中
        self.button_group = QButtonGroup()
        for button in self.buttons.values():
            self.button_group.addButton(button)

        # 设置 "Home" 为默认选中
        self.buttons["Home"].setChecked(True)

        # 右侧内容显示区域
        self.stacked_widget = QStackedWidget()

        # 添加页面到右侧显示区域
        self.pages = {
            "Home": QLabel("Home Content"),
            "Roles": QLabel("Roles Content"),
            "Custom": QLabel("Custom Content"),
            "Pipeline": QLabel("Pipeline Content"),
            "Arbitration": QLabel("Arbitration Content")
        }

        # 设置右侧内容区域的样式
        for page in self.pages.values():
            page.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page.setStyleSheet(
                """
                QLabel {
                    border: 1px solid black;
                    font-size: 18px;
                }
                """
            )
            self.stacked_widget.addWidget(page)

        # 添加角色选择页面
        self.roles_page = QWidget()
        roles_layout = QGridLayout()
        roles_layout.setSpacing(10)

        # 创建20个圆形按钮代表角色
        for i in range(20):
            role_button = QPushButton(str(i + 1) if i < 2 else "..")
            role_button.setFixedSize(50, 50)
            role_button.setStyleSheet(
                """
                QPushButton {
                    border: 2px solid black;
                    border-radius: 25px;
                    font-size: 16px;
                }
                """
            )
            role_button.clicked.connect(self.enter_chat)
            roles_layout.addWidget(role_button, i // 5, i % 5)  # 每行5个按钮

        # 将角色选择布局设置为页面布局
        # TODO
        self.roles_page.setLayout(roles_layout)
        self.stacked_widget.addWidget(self.roles_page)

        # 添加对话界面页面
        self.chat_page = QWidget()
        chat_layout = QVBoxLayout()

        # 添加顶部按钮 (Model 和 API-KEY)
        top_buttons_layout = QHBoxLayout()
        model_button = QPushButton("Model")
        api_key_button = QPushButton("API-KEY")
        model_button.setFixedSize(80, 30)
        api_key_button.setFixedSize(80, 30)
        top_buttons_layout.addWidget(model_button)
        top_buttons_layout.addWidget(api_key_button)
        top_buttons_layout.addStretch()

        # 添加聊天显示区域 (滚动区域)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # 创建用于展示消息的容器
        self.chat_display_widget = QWidget()
        self.chat_display_layout = QVBoxLayout(self.chat_display_widget)
        self.chat_display_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 消息从顶部开始显示
        scroll_area.setWidget(self.chat_display_widget)

        # 添加滚动区域到布局中
        chat_layout.addLayout(top_buttons_layout)
        chat_layout.addWidget(scroll_area)

        # 添加底部输入框
        bottom_input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your message here...")
        enter_button = QPushButton("Enter")
        enter_button.setFixedSize(50, 30)
        enter_button.clicked.connect(self.add_message)
        bottom_input_layout.addWidget(self.input_box)
        bottom_input_layout.addWidget(enter_button)

        # 组合布局
        chat_layout.addLayout(bottom_input_layout)
        self.chat_page.setLayout(chat_layout)
        self.stacked_widget.addWidget(self.chat_page)

        # 设置默认显示的页面
        self.stacked_widget.setCurrentWidget(self.pages["Home"])

        # 添加菜单和内容布局到主布局
        main_layout.addLayout(menu_layout)
        main_layout.addWidget(self.stacked_widget)

        # 设置主窗口的主布局
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def change_page(self):
        # 根据点击的按钮名称切换到对应页面
        sender = self.sender()
        if sender == self.buttons["Roles"]:
            self.stacked_widget.setCurrentWidget(self.roles_page)
        else:
            for name, button in self.buttons.items():
                if button.isChecked():
                    self.stacked_widget.setCurrentWidget(self.pages[name])

    def add_message(self):
        # 添加新的消息到聊天记录中
        message = self.input_box.text()
        if message:
            message_label = QLabel(message)
            message_label.setStyleSheet("border: 1px solid black; padding: 5px;")
            self.chat_display_layout.addWidget(message_label)
            self.input_box.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
