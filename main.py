from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QButtonGroup,
    QGridLayout, QLineEdit, QScrollArea, QComboBox, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt
import sys
from LLM import LLM, pipeline, arbitration
from prompts import prompts
import os, sys


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


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

        # Arbitration
        self.arbitrationBot = None
        self.arbitrationBotFlag = False
        self.arbitration_model = None
        self.arbitration_api_key = None

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

        # 创建角色按钮
        i = 0
        for key, val in prompts.items():
            role_button = QPushButton(key)
            role_button.setFixedSize(200, 100)
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
            i += 1
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

        # 右侧显示当前的Role，用于提示用户当前选择的角色
        self.role_label = QLabel("Role: " + str(self.role))
        self.role_label.setFixedSize(100, 30)

        role_chat_page_top_buttons_layout.addWidget(self.role_label)
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

        # 创建 Pipeline 页面
        self.pipeline_page = QWidget()
        pipeline_layout = QVBoxLayout(self.pipeline_page)

        # 添加流程图图片
        target_width = 1000
        target_height = 1000

        # 添加流程图图片
        pipeline_flowchart = QLabel()
        pipeline_pixmap = QPixmap(get_resource_path("images/pipeline.png"))
        # 缩放图片以适应目标尺寸
        pipeline_scaled_pixmap = pipeline_pixmap.scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)

        pipeline_flowchart.setPixmap(pipeline_scaled_pixmap)  # 设置缩放后的图片
        pipeline_flowchart.setScaledContents(False)  # 禁用 QLabel 自动缩放，已手动缩放
        # pipeline_flowchart.setPixmap(QPixmap(get_resource_path("images/pipeline.png")))  # 加载并显示图片
        # pipeline_flowchart.setScaledContents(True)  # 缩放图片以适应标签大小
        pipeline_flowchart.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pipeline_flowchart.setStyleSheet("border: 1px solid black; padding: 10px;")
        pipeline_layout.addWidget(pipeline_flowchart)

        # # 添加流程图占位符
        # pipeline_flowchart = QLabel("Pipeline Flowchart")  # 替换为您实际的流程图实现
        # pipeline_flowchart.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # pipeline_flowchart.setStyleSheet("border: 1px solid black; padding: 10px;")
        # pipeline_layout.addWidget(pipeline_flowchart)

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
        # 创建arbitration页面
        self.arbitration_page = QWidget()
        arbitration_layout = QVBoxLayout(self.arbitration_page)

        arbitration_flowchart = QLabel()
        arbitration_pixmap = QPixmap(get_resource_path("images/arbitration.png"))
        # 缩放图片到目标尺寸
        arbitration_scaled_pixmap = arbitration_pixmap.scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        arbitration_flowchart.setPixmap(arbitration_scaled_pixmap)  # 设置缩放后的图片
        arbitration_flowchart.setScaledContents(False)  # 禁用 QLabel 自动缩放，已手动缩放
        # arbitration_flowchart.setPixmap(QPixmap(get_resource_path("images/arbitration.png")))  # 加载并显示图片
        # arbitration_flowchart.setScaledContents(True)  # 缩放图片以适应标签大小
        arbitration_flowchart.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arbitration_flowchart.setStyleSheet("border: 1px solid black; padding: 10px;")
        arbitration_layout.addWidget(arbitration_flowchart)

        # # 添加流程图占位符
        # arbitration_flowchart = QLabel("Arbitration Flowchart")  # 替换为您实际的流程图实现
        # arbitration_flowchart.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # arbitration_flowchart.setStyleSheet("border: 1px solid black; padding: 10px;")
        # arbitration_layout.addWidget(arbitration_flowchart)

        # 添加 Prompt-1, Prompt-2, Prompt-3, Prompt-4 的输入框
        self.arbitration_inputs = []
        for i in range(1, 5):
            prompt_label = QLabel(f"Prompt-{i}")
            prompt_input = QLineEdit()
            prompt_input.setPlaceholderText(f"Input for Prompt-{i}")
            prompt_layout = QHBoxLayout()
            prompt_layout.addWidget(prompt_label)
            prompt_layout.addWidget(prompt_input)
            arbitration_layout.addLayout(prompt_layout)
            self.arbitration_inputs.append(prompt_input)

        # 添加 Enter 按钮
        arbitration_enter_button = QPushButton("Enter")
        arbitration_enter_button.clicked.connect(self.arbitration_submit)
        arbitration_layout.addWidget(arbitration_enter_button)

        # 添加 Arbitration 页面到 stacked_widget
        self.stacked_widget.addWidget(self.arbitration_page)

        # 设置 Arbitration 对话页面
        self.arbitration_chat_page = QWidget()
        arbitration_chat_layout = QVBoxLayout(self.arbitration_chat_page)

        # 添加顶部按钮 (Model 和 API-KEY)
        arbitration_chat_page_top_buttons_layout = QHBoxLayout()

        # Model 下拉框
        self.arbitration_chat_page_model_combo = QComboBox()
        self.arbitration_chat_page_model_combo.addItems(["Default", "Kimi", "GPT-3.5", "GPT-4", "GPT-4o"])  # 添加模型名称
        self.arbitration_chat_page_model_combo.setCurrentIndex(0)  # 默认选中第一个
        self.arbitration_chat_page_model_combo.setFixedSize(100, 30)

        # API-KEY 输入框
        self.arbitration_api_key_input = QLineEdit()
        self.arbitration_api_key_input.setPlaceholderText("Enter API-KEY")
        self.arbitration_api_key_input.setFixedSize(150, 30)

        arbitration_chat_page_top_buttons_layout.addWidget(self.arbitration_chat_page_model_combo)
        arbitration_chat_page_top_buttons_layout.addWidget(self.arbitration_api_key_input)
        arbitration_chat_page_top_buttons_layout.addStretch()

        # 添加聊天显示区域(支持滚动)
        arbitration_chat_scroll_area = QScrollArea()
        arbitration_chat_scroll_area.setWidgetResizable(True)

        # 创建用于展示消息的容器
        self.arbitration_chat_display_widget = QWidget()
        self.arbitration_chat_display_layout = QVBoxLayout(self.arbitration_chat_display_widget)
        self.arbitration_chat_display_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 消息从顶部开始显示
        arbitration_chat_scroll_area.setWidget(self.arbitration_chat_display_widget)

        # 添加滚动区域到布局中
        arbitration_chat_layout.addLayout(arbitration_chat_page_top_buttons_layout)
        arbitration_chat_layout.addWidget(arbitration_chat_scroll_area)

        # 添加底部输入框
        arbitration_bottom_input_layout = QHBoxLayout()
        self.arbitration_input_box = QLineEdit()
        self.arbitration_input_box.setPlaceholderText("Type your message here...")
        arbitration_enter_button = QPushButton("Enter")
        arbitration_enter_button.setFixedSize(50, 30)
        arbitration_enter_button.clicked.connect(self.arbitration_add_message)  # 点击按钮发送消息
        arbitration_bottom_input_layout.addWidget(self.arbitration_input_box)
        arbitration_bottom_input_layout.addWidget(arbitration_enter_button)

        # 组合布局
        arbitration_chat_layout.addLayout(arbitration_bottom_input_layout)
        self.arbitration_chat_page.setLayout(arbitration_chat_layout)
        self.stacked_widget.addWidget(self.arbitration_chat_page)

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
        self.clear_arbitration_messages()
        self.pipelineBotFlag = False
        self.customBotFlag = False
        self.roleBotFlag = False
        self.arbitrationBotFlag = False

    def change_page(self):
        # 切换右侧显示页面
        sender = self.sender()
        self.clear()  # 清空聊天记录
        # self.clear_custom_messages()  # 清空聊天记录
        # self.customBotFlag = False
        # self.clear_roles_messages()  # 清空聊天记录
        # self.roleBotFlag = False
        # self.pipelineBotFlag = False
        if sender == self.buttons["Roles"]:
            self.stacked_widget.setCurrentWidget(self.roles_page)
        elif sender == self.buttons["Custom"]:
            self.stacked_widget.setCurrentWidget(self.custom_chat_page)
        elif sender == self.buttons["Pipeline"]:
            self.stacked_widget.setCurrentWidget(self.pipeline_page)
        elif sender == self.buttons["Arbitration"]:
            self.stacked_widget.setCurrentWidget(self.arbitration_page)
        else:
            for name, button in self.buttons.items():
                if button.isChecked():
                    self.stacked_widget.setCurrentWidget(self.pages[name])

    def enter_chat(self, role_button):
        self.role = role_button.text()
        # print(self.role)
        self.clear()
        # self.pipelineBotFlag = False
        # self.clear_custom_messages()
        # self.customBotFlag = False
        # self.clear_roles_messages()
        # self.roleBotFlag = False
        # 更新角色标签的文本
        self.role_label.setText("Role: " + str(self.role))
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
        self.arbitrationBotFlag = False
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
                self.pipelineBot = pipeline(model=self.pipeline_model, key=self.pipeline_api_key, prompt_1=prompt_1,
                                            prompt_2=prompt_2, prompt_3=prompt_3)
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

    def arbitration_submit(self):
        # 提交 Arbitration 输入框内容
        prompt_texts = [input_box.text() for input_box in self.arbitration_inputs]
        print("Arbitration Inputs:", prompt_texts)
        # 进入Arbitration聊天页面
        self.clear()
        # self.pipelineBotFlag = False
        # self.customBotFlag = False
        # self.roleBotFlag = False
        # 切换到聊天页面
        self.stacked_widget.setCurrentWidget(self.arbitration_chat_page)

    def arbitration_add_message(self):
        # 添加新的消息到聊天记录中
        message = self.arbitration_input_box.text()
        print(message)
        if message:
            # 如果model或者api_key修改了，重新初始化聊天机器人
            if self.arbitrationBot and (
                    self.arbitration_chat_page_model_combo.currentText() != self.arbitration_model or
                    self.arbitration_api_key_input.text() != self.arbitration_api_key):
                self.arbitrationBot = None
                self.arbitrationBotFlag = False

            # 初始化聊天机器人
            if not self.arbitrationBot or not self.arbitrationBotFlag:
                # 根据角色初始化聊天机器人
                prompt_1 = self.arbitration_inputs[0].text()  # 获取角色对应的对话模板
                prompt_2 = self.arbitration_inputs[1].text()  # 获取角色对应的对话模板
                prompt_3 = self.arbitration_inputs[2].text()  # 获取角色对应的对话模板
                prompt_4 = self.arbitration_inputs[3].text()  # 获取角色对应的对话模板
                print(prompt_1, prompt_2, prompt_3, prompt_4)
                self.arbitration_model = self.arbitration_chat_page_model_combo.currentText()  # 获取下拉框中选择的模型
                self.arbitration_api_key = self.arbitration_api_key_input.text()  # 获取输入框中输入的API-KEY
                # 如果模型不为Default，且API-KEY为空，则提示用户输入API-KEY
                if self.arbitration_model != "Default" and not self.arbitration_api_key:
                    # 弹窗提示用户输入API-KEY
                    QMessageBox.warning(self, "API-KEY Required", "Please enter your API-KEY to use this model.")
                    return  # 中断，避免继续执行后续逻辑
                print(self.arbitration_model, self.arbitration_api_key)
                self.arbitrationBot = arbitration(model=self.arbitration_model, key=self.pipeline_api_key,
                                                  prompt_1=prompt_1, prompt_2=prompt_2, prompt_3=prompt_3,
                                                  prompt_4=prompt_4)
                self.pipelineBotFlag = True

            message_label = QLabel("User:\n" + message)
            message_label.setWordWrap(True)  # 启用自动换行
            message_label.setStyleSheet("border: 1px solid black; padding: 5px;")
            self.arbitration_chat_display_layout.addWidget(message_label)
            self.arbitration_input_box.clear()
            # 与聊天机器人交互
            answer = self.arbitrationBot.query(message)
            message_label = QLabel("Chat Bot:\n" + answer)
            message_label.setWordWrap(True)  # 启用自动换行
            message_label.setStyleSheet("border: 1px solid black; padding: 5px;")
            self.arbitration_chat_display_layout.addWidget(message_label)

    def clear_arbitration_messages(self):
        # 清空聊天记录
        for i in range(self.arbitration_chat_display_layout.count()):
            self.arbitration_chat_display_layout.itemAt(i).widget().deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
