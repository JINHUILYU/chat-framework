from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QButtonGroup,
    QGridLayout, QLineEdit, QScrollArea, QComboBox, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt
import sys
from LLM import LLM, pipeline

# 角色对应的对话模板
prompts = {
    "Assist": "You are an AI assistant. You should answer the user's question politely.",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Role
        self.roleBot = None
        self.roleBotFlag = False
        self.role = None
        self.role_model = None
        self.role_api_key = None

        # Custom
        self.customBot = None
        self.customBotFlag = False
        self.custom_model = None
        self.custom_api_key = None

        # Pipeline
        self.pipelineBot = None
        self.pipelineBotFlag = False
        self.pipeline_model = None
        self.pipeline_api_key = None

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
            button.clicked.connect(self.change_page)  # 槽函数，实现右侧页面切换
            menu_layout.addWidget(button)  # 添加按钮到菜单布局

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

        # TODO: 设置Home页面

        # 添加角色选择页面
        self.roles_page = QWidget()
        roles_layout = QGridLayout(self.roles_page)
        roles_layout.setSpacing(10)

        # 创建10个圆形按钮代表角色
        for i in range(10):
            if i == 0:
                role_button = QPushButton("Assist")
            else:
                role_button = QPushButton(str(i + 1) if i < 20 else "..")
            role_button.setFixedSize(50, 50)
            role_button.setStyleSheet(
                """
                QPushButton {
                    border: 2px solid black;
                    font-size: 16px;
                }
                """
            )
            # 用户点击时获取角色名称
            role_button.clicked.connect(lambda _, btn=role_button: self.enter_chat(btn))  # 点击角色进入聊天页面
            roles_layout.addWidget(role_button, i // 5, i % 5)  # 每行5个按钮
        # 角色选择页面布局
        self.roles_page.setLayout(roles_layout)
        self.stacked_widget.addWidget(self.roles_page)

        # 添加对话界面页面
        self.role_chat_page = QWidget()
        role_chat_layout = QVBoxLayout(self.role_chat_page)

        # 添加顶部按钮 (Model 和 API-KEY)
        role_chat_page_top_buttons_layout = QHBoxLayout()

        # Model 下拉框
        self.role_chat_page_model_combo = QComboBox()
        self.role_chat_page_model_combo.addItems(["Default", "Kimi", "GPT-3.5", "GPT-4", "GPT-4o"])  # 添加模型名称
        self.role_chat_page_model_combo.setCurrentIndex(0)  # 默认选中第一个
        self.role_chat_page_model_combo.setFixedSize(100, 30)

        # API-KEY 输入框
        self.role_api_key_input = QLineEdit()
        self.role_api_key_input.setPlaceholderText("Enter API-KEY")
        self.role_api_key_input.setFixedSize(150, 30)

        role_chat_page_top_buttons_layout.addWidget(self.role_chat_page_model_combo)
        role_chat_page_top_buttons_layout.addWidget(self.role_api_key_input)
        role_chat_page_top_buttons_layout.addStretch()

        # 添加聊天显示区域(支持滚动)
        role_chat_scroll_area = QScrollArea()
        role_chat_scroll_area.setWidgetResizable(True)

        # 创建用于展示消息的容器
        self.role_chat_display_widget = QWidget()
        self.role_chat_display_layout = QVBoxLayout(self.role_chat_display_widget)
        self.role_chat_display_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 消息从顶部开始显示
        role_chat_scroll_area.setWidget(self.role_chat_display_widget)

        # 添加滚动区域到布局中
        role_chat_layout.addLayout(role_chat_page_top_buttons_layout)
        role_chat_layout.addWidget(role_chat_scroll_area)

        # 添加底部输入框
        role_bottom_input_layout = QHBoxLayout()
        self.role_input_box = QLineEdit()
        self.role_input_box.setPlaceholderText("Type your message here...")
        role_enter_button = QPushButton("Enter")
        role_enter_button.setFixedSize(50, 30)
        role_enter_button.clicked.connect(self.roles_add_message)  # 点击按钮发送消息
        role_bottom_input_layout.addWidget(self.role_input_box)
        role_bottom_input_layout.addWidget(role_enter_button)

        # 组合布局
        role_chat_layout.addLayout(role_bottom_input_layout)
        self.role_chat_page.setLayout(role_chat_layout)
        self.stacked_widget.addWidget(self.role_chat_page)

        # 设置Custom页面
        self.custom_chat_page = QWidget()
        custom_chat_layout = QVBoxLayout(self.custom_chat_page)

        # 添加顶部按钮 (Model 和 API-KEY)
        custom_chat_page_top_buttons_layout = QHBoxLayout()

        # Model 下拉框
        self.custom_chat_page_model_combo = QComboBox()
        self.custom_chat_page_model_combo.addItems(["Default", "Kimi", "GPT-3.5", "GPT-4", "GPT-4o"])  # 添加模型名称
        self.custom_chat_page_model_combo.setCurrentIndex(0)  # 默认选中第一个
        self.custom_chat_page_model_combo.setFixedSize(100, 30)

        # API-KEY 输入框
        self.custom_api_key_input = QLineEdit()
        self.custom_api_key_input.setPlaceholderText("Enter API-KEY")
        self.custom_api_key_input.setFixedSize(150, 30)

        custom_chat_page_top_buttons_layout.addWidget(self.custom_chat_page_model_combo)
        custom_chat_page_top_buttons_layout.addWidget(self.custom_api_key_input)
        custom_chat_page_top_buttons_layout.addStretch()

        # 添加聊天显示区域(支持滚动)
        custom_chat_scroll_area = QScrollArea()
        custom_chat_scroll_area.setWidgetResizable(True)

        # 创建用于展示消息的容器
        self.custom_chat_display_widget = QWidget()
        self.custom_chat_display_layout = QVBoxLayout(self.custom_chat_display_widget)
        self.custom_chat_display_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 消息从顶部开始显示
        custom_chat_scroll_area.setWidget(self.custom_chat_display_widget)

        # 添加滚动区域到布局中
        custom_chat_layout.addLayout(custom_chat_page_top_buttons_layout)
        custom_chat_layout.addWidget(custom_chat_scroll_area)

        # 添加底部输入框
        custom_bottom_input_layout = QHBoxLayout()
        self.custom_input_box = QLineEdit()
        self.custom_input_box.setPlaceholderText("Type your message here...")
        custom_enter_button = QPushButton("Enter")
        custom_enter_button.setFixedSize(50, 30)
        custom_enter_button.clicked.connect(self.custom_add_message)  # 点击按钮发送消息
        custom_bottom_input_layout.addWidget(self.custom_input_box)
        custom_bottom_input_layout.addWidget(custom_enter_button)

        # 组合布局
        custom_chat_layout.addLayout(custom_bottom_input_layout)
        self.custom_chat_page.setLayout(custom_chat_layout)
        self.stacked_widget.addWidget(self.custom_chat_page)

        # TODO:设置pipeline页面
        # 创建 Pipeline 页面
        self.pipeline_page = QWidget()
        pipeline_layout = QVBoxLayout(self.pipeline_page)

        # 添加流程图占位符
        pipeline_flowchart = QLabel("Pipeline Flowchart")  # 替换为您实际的流程图实现
        pipeline_flowchart.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pipeline_flowchart.setStyleSheet("border: 1px solid black; padding: 10px;")
        pipeline_layout.addWidget(pipeline_flowchart)

        # 添加 Prompt-1, Prompt-2, Prompt-3 的输入框
        self.pipeline_inputs = []
        for i in range(1, 4):
            prompt_label = QLabel(f"Prompt-{i}")
            prompt_input = QLineEdit()
            prompt_input.setPlaceholderText(f"Input for Prompt-{i}")
            prompt_layout = QHBoxLayout()
            prompt_layout.addWidget(prompt_label)
            prompt_layout.addWidget(prompt_input)
            pipeline_layout.addLayout(prompt_layout)
            self.pipeline_inputs.append(prompt_input)

        # 添加 Enter 按钮
        pipeline_enter_button = QPushButton("Enter")
        pipeline_enter_button.clicked.connect(self.pipeline_submit)
        pipeline_layout.addWidget(pipeline_enter_button)

        # 添加 Pipeline 页面到 stacked_widget
        self.stacked_widget.addWidget(self.pipeline_page)

        # 设置pipeline对话页面
        self.pipeline_chat_page = QWidget()
        pipeline_chat_layout = QVBoxLayout(self.pipeline_chat_page)

        # 添加顶部按钮 (Model 和 API-KEY)
        pipeline_chat_page_top_buttons_layout = QHBoxLayout()

        # Model 下拉框
        self.pipeline_chat_page_model_combo = QComboBox()
        self.pipeline_chat_page_model_combo.addItems(["Default", "Kimi", "GPT-3.5", "GPT-4", "GPT-4o"])  # 添加模型名称
        self.pipeline_chat_page_model_combo.setCurrentIndex(0)  # 默认选中第一个
        self.pipeline_chat_page_model_combo.setFixedSize(100, 30)

        # API-KEY 输入框
        self.pipeline_api_key_input = QLineEdit()
        self.pipeline_api_key_input.setPlaceholderText("Enter API-KEY")
        self.pipeline_api_key_input.setFixedSize(150, 30)

        pipeline_chat_page_top_buttons_layout.addWidget(self.pipeline_chat_page_model_combo)
        pipeline_chat_page_top_buttons_layout.addWidget(self.pipeline_api_key_input)
        pipeline_chat_page_top_buttons_layout.addStretch()

        # 添加聊天显示区域(支持滚动)
        pipeline_chat_scroll_area = QScrollArea()
        pipeline_chat_scroll_area.setWidgetResizable(True)

        # 创建用于展示消息的容器
        self.pipeline_chat_display_widget = QWidget()
        self.pipeline_chat_display_layout = QVBoxLayout(self.pipeline_chat_display_widget)
        self.pipeline_chat_display_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 消息从顶部开始显示
        pipeline_chat_scroll_area.setWidget(self.pipeline_chat_display_widget)

        # 添加滚动区域到布局中
        pipeline_chat_layout.addLayout(pipeline_chat_page_top_buttons_layout)
        pipeline_chat_layout.addWidget(pipeline_chat_scroll_area)

        # 添加底部输入框
        pipeline_bottom_input_layout = QHBoxLayout()
        self.pipeline_input_box = QLineEdit()
        self.pipeline_input_box.setPlaceholderText("Type your message here...")
        pipeline_enter_button = QPushButton("Enter")
        pipeline_enter_button.setFixedSize(50, 30)
        pipeline_enter_button.clicked.connect(self.pipeline_add_message)  # 点击按钮发送消息
        pipeline_bottom_input_layout.addWidget(self.pipeline_input_box)
        pipeline_bottom_input_layout.addWidget(pipeline_enter_button)

        # 组合布局
        pipeline_chat_layout.addLayout(pipeline_bottom_input_layout)
        self.pipeline_chat_page.setLayout(pipeline_chat_layout)
        self.stacked_widget.addWidget(self.pipeline_chat_page)
        # TODO:设置arbitration页面


        # 设置默认显示的页面
        self.stacked_widget.setCurrentWidget(self.pages["Home"])

        # 添加菜单和内容布局到主布局
        main_layout.addLayout(menu_layout)
        main_layout.addWidget(self.stacked_widget)

        # 设置主窗口的主布局
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def clear(self):
        self.clear_pipeline_messages()
        self.clear_custom_messages()
        self.clear_roles_messages()

    def change_page(self):
        # 切换右侧显示页面
        sender = self.sender()
        self.clear()  # 清空聊天记录
        # self.clear_custom_messages()  # 清空聊天记录
        self.customBotFlag = False
        # self.clear_roles_messages()  # 清空聊天记录
        self.roleBotFlag = False
        self.pipelineBotFlag = False
        if sender == self.buttons["Roles"]:
            self.stacked_widget.setCurrentWidget(self.roles_page)
        elif sender == self.buttons["Custom"]:
            self.stacked_widget.setCurrentWidget(self.custom_chat_page)
        elif sender == self.buttons["Pipeline"]:
            self.stacked_widget.setCurrentWidget(self.pipeline_page)
        else:
            for name, button in self.buttons.items():
                if button.isChecked():
                    self.stacked_widget.setCurrentWidget(self.pages[name])

    def enter_chat(self, role_button):
        self.role = role_button.text()
        self.clear()
        self.pipelineBotFlag = False
        # self.clear_custom_messages()
        self.customBotFlag = False
        # self.clear_roles_messages()
        self.roleBotFlag = False
        # 切换到聊天页面
        self.stacked_widget.setCurrentWidget(self.role_chat_page)

    def roles_add_message(self):
        # 添加新的消息到聊天记录中
        message = self.role_input_box.text()
        print(message)
        if message:
            # 如果model或者api_key修改了，重新初始化聊天机器人
            if self.roleBot and (self.role_chat_page_model_combo.currentText() != self.role_model or
                                 self.role_api_key_input.text() != self.role_api_key):
                self.roleBot = None
                self.roleBotFlag = False

            # 初始化聊天机器人
            if not self.roleBot or not self.roleBotFlag:
                # 获取选择的角色
                print(self.role)
                # 根据角色初始化聊天机器人
                prompt = prompts[self.role]  # 获取角色对应的对话模板
                self.role_model = self.role_chat_page_model_combo.currentText()  # 获取下拉框中选择的模型
                self.role_api_key = self.role_api_key_input.text()  # 获取输入框中输入的API-KEY
                # 如果模型不为Default，且API-KEY为空，则提示用户输入API-KEY
                if self.role_model != "Default" and not self.role_api_key:
                    # 弹窗提示用户输入API-KEY
                    QMessageBox.warning(self, "API-KEY Required", "Please enter your API-KEY to use this model.")
                    return  # 中断，避免继续执行后续逻辑
                print(self.role_model, self.role_api_key)
                self.roleBot = LLM(prompt=prompt, model=self.role_model, key=self.role_api_key)
                self.roleBotFlag = True


            message_label = QLabel("User:\n" + message)
            message_label.setWordWrap(True)  # 启用自动换行
            message_label.setStyleSheet("border: 1px solid black; padding: 5px;")
            self.role_chat_display_layout.addWidget(message_label)
            self.role_input_box.clear()
            # 与聊天机器人交互
            answer = self.roleBot.query(message)
            message_label = QLabel("Chat Bot:\n" + answer)
            message_label.setWordWrap(True)  # 启用自动换行
            message_label.setStyleSheet("border: 1px solid black; padding: 5px;")
            self.role_chat_display_layout.addWidget(message_label)

    def clear_roles_messages(self):
        # 清空聊天记录
        for i in range(self.role_chat_display_layout.count()):
            self.role_chat_display_layout.itemAt(i).widget().deleteLater()

    def custom_add_message(self):
        # 添加新的消息到聊天记录中
        message = self.custom_input_box.text()
        print(message)
        if message:
            # 如果model或者api_key修改了，重新初始化聊天机器人
            if self.customBot and (self.custom_chat_page_model_combo.currentText() != self.custom_model or
                                   self.custom_api_key_input.text() != self.custom_api_key):
                self.customBot = None
                self.customBotFlag = False

            # 初始化聊天机器人
            if not self.customBot or not self.customBotFlag:
                # 根据角色初始化聊天机器人
                prompt = message  # 获取角色对应的对话模板
                self.custom_model = self.custom_chat_page_model_combo.currentText()  # 获取下拉框中选择的模型
                self.custom_api_key = self.custom_api_key_input.text()  # 获取输入框中输入的API-KEY
                # 如果模型不为Default，且API-KEY为空，则提示用户输入API-KEY
                if self.custom_model != "Default" and not self.custom_api_key:
                    # 弹窗提示用户输入API-KEY
                    QMessageBox.warning(self, "API-KEY Required", "Please enter your API-KEY to use this model.")
                    return  # 中断，避免继续执行后续逻辑
                print(self.custom_model, self.custom_api_key)
                self.customBot = LLM(prompt=prompt, model=self.custom_model, key=self.custom_api_key)
                self.customBotFlag = True

            message_label = QLabel("User:\n" + message)
            message_label.setWordWrap(True)  # 启用自动换行
            message_label.setStyleSheet("border: 1px solid black; padding: 5px;")
            self.custom_chat_display_layout.addWidget(message_label)
            self.custom_input_box.clear()
            # 与聊天机器人交互
            answer = self.customBot.query(message)
            message_label = QLabel("Chat Bot:\n" + answer)
            message_label.setWordWrap(True)  # 启用自动换行
            message_label.setStyleSheet("border: 1px solid black; padding: 5px;")
            self.custom_chat_display_layout.addWidget(message_label)

    def clear_custom_messages(self):
        # 清空聊天记录
        for i in range(self.custom_chat_display_layout.count()):
            self.custom_chat_display_layout.itemAt(i).widget().deleteLater()

    def pipeline_submit(self):
        # 提交 Pipeline 输入框内容
        prompt_texts = [input_box.text() for input_box in self.pipeline_inputs]
        print("Pipeline Inputs:", prompt_texts)
        # 进入pipeline聊天页面
        self.clear()
        self.pipelineBotFlag = False
        self.customBotFlag = False
        self.roleBotFlag = False
        # 切换到聊天页面
        self.stacked_widget.setCurrentWidget(self.pipeline_chat_page)

    def pipeline_add_message(self):
        # 添加新的消息到聊天记录中
        message = self.pipeline_input_box.text()
        print(message)
        if message:
            # 如果model或者api_key修改了，重新初始化聊天机器人
            if self.pipelineBot and (self.pipeline_chat_page_model_combo.currentText() != self.pipeline_model or
                                   self.pipeline_api_key_input.text() != self.pipeline_api_key):
                self.pipelineBot = None
                self.pipelineBotFlag = False

            # 初始化聊天机器人
            if not self.pipelineBot or not self.pipelineBotFlag:
                # 根据角色初始化聊天机器人
                prompt_1 = self.pipeline_inputs[0].text()  # 获取角色对应的对话模板
                prompt_2 = self.pipeline_inputs[1].text()  # 获取角色对应的对话模板
                prompt_3 = self.pipeline_inputs[2].text()  # 获取角色对应的对话模板
                print(prompt_1, prompt_2, prompt_3)
                self.pipeline_model = self.pipeline_chat_page_model_combo.currentText()  # 获取下拉框中选择的模型
                self.pipeline_api_key = self.pipeline_api_key_input.text()  # 获取输入框中输入的API-KEY
                # 如果模型不为Default，且API-KEY为空，则提示用户输入API-KEY
                if self.pipeline_model != "Default" and not self.pipeline_api_key:
                    # 弹窗提示用户输入API-KEY
                    QMessageBox.warning(self, "API-KEY Required", "Please enter your API-KEY to use this model.")
                    return  # 中断，避免继续执行后续逻辑
                print(self.pipeline_model, self.pipeline_api_key)
                self.pipelineBot = pipeline(model=self.pipeline_model, key=self.pipeline_api_key, prompt_1=prompt_1, prompt_2=prompt_2, prompt_3=prompt_3)
                self.pipelineBotFlag = True

            message_label = QLabel("User:\n" + message)
            message_label.setWordWrap(True)  # 启用自动换行
            message_label.setStyleSheet("border: 1px solid black; padding: 5px;")
            self.pipeline_chat_display_layout.addWidget(message_label)
            self.pipeline_input_box.clear()
            # 与聊天机器人交互
            answer = self.pipelineBot.query(message)
            message_label = QLabel("Chat Bot:\n" + answer)
            message_label.setWordWrap(True)  # 启用自动换行
            message_label.setStyleSheet("border: 1px solid black; padding: 5px;")
            self.pipeline_chat_display_layout.addWidget(message_label)

    def clear_pipeline_messages(self):
        # 清空聊天记录
        for i in range(self.pipeline_chat_display_layout.count()):
            self.pipeline_chat_display_layout.itemAt(i).widget().deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
