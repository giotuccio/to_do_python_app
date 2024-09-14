import requests
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import (MDRaisedButton,MDRectangleFlatIconButton)
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.app import MDApp
from kivy.core.window import Window

# URL to your Flask API
API_URL = 'http://127.0.0.1:5000/tasks'


colors = {
    "Teal": {
        "200": "#212121",
        "500": "#212121",
        "700": "#212121",
    },
    "Red": {
        "200": "#C25554",
        "500": "#C25554",
        "700": "#C25554",
    },
    "Light": {
        "StatusBar": "E0E0E0",
        "AppBar": "#202020",
        "Background": "#2E3032",
        "CardsDialogs": "#FFFFFF",
        "FlatButtonDown": "#CCCCCC",
    },
}

class TaskManager(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(TaskManager, self).__init__(**kwargs)
        self.screen_manager = screen_manager
        self.options = kwargs
        # Main layout for the screen
        main_layout = MDBoxLayout(orientation='vertical', spacing=40, padding=(40, 20, 40, 20), size_hint=(1, 1))
        main_layout.md_bg_color = (0.18, 0.2, 0.38, 1)  # Dark background

        # Create an MDTopAppBar at the top of the screen
        toolbar = MDTopAppBar(title="Task Manager")
        toolbar.pos_hint = {"top": 1}
        toolbar.height = '10dp'  # Fixed height for toolbar
        toolbar.md_bg_color = (0.2, 0.1, 0.8, 1)  # Optional: Set a background color
        toolbar.specific_text_color = (1, 1, 1, 1)  # White text in toolbar

        # Add the toolbar to the main layout
        main_layout.add_widget(toolbar)

        # ScrollView for input fields to handle dynamic content size
        input_scroll = ScrollView(size_hint=(1, 2))

        # BoxLayout for input fields within the ScrollView
        input_layout = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        input_layout.bind(minimum_height=input_layout.setter('height'))

        # MDTextField for task name
        self.task_input = MDTextField(
            hint_text="Enter task name",
            size_hint=(1, None),
            required=True,
            icon_right="format-title",
            height='60dp',
            line_color_normal=(1, 1, 1, 1),  # White line color
            hint_text_color_normal=(1, 1, 1, 1)  # White hint text color
        )
        input_layout.add_widget(self.task_input)

        # MDTextField for task description
        self.task_description_input = MDTextField(
            hint_text="Enter task description",
            icon_right="text-box-multiple-outline",
            multiline=True,
            required=True,
            size_hint=(1, None),
            helper_text="This field is required",
            helper_text_mode="on_error",
            height='100dp',
            line_color_normal=(1, 1, 1, 1),  # White line color
            hint_text_color_normal=(1, 1, 1, 1)  # White hint text color
        )

        # Set initial state to not show error
        self.task_description_input.error = False

        # Bind the on_focus event to handle validation manually after user interaction
        self.task_description_input.bind(on_focus=self.validate_task_description)

        input_layout.add_widget(self.task_description_input)

        # Button to open the date picker
        self.task_due_date_button = MDRectangleFlatIconButton(
            text="Select Due Date",
            icon="calendar-blank",
            size_hint=(1, None),
            height='50dp',
            on_release=self.show_date_picker,
            md_bg_color=(0.2, 0.2, 0.2, 1),  # Dark button background
        )
        input_layout.add_widget(self.task_due_date_button)

        # Label to display the selected due date
        self.selected_date_label = MDLabel(
            text="No due date selected",
            size_hint=(1, None),
            height='30dp',
            halign="center",
            text_color=(1, .1, 1, 1)  # White text color
        )
        input_layout.add_widget(self.selected_date_label)

        # Priority dropdown menu setup
        self.priority_button = MDRaisedButton(
            text="Select Priority",
            size_hint=(1, None),
            height='50dp',
            md_bg_color=(0.2, 0.2, 0.2, 1)  # Dark button background
        )
        self.priority_menu = MDDropdownMenu(
            caller=self.priority_button,
            items=[
                {"viewclass": "OneLineListItem", "text": "Low", "on_release": lambda x="Low": self.set_priority(x)},
                {"viewclass": "OneLineListItem", "text": "Medium", "on_release": lambda x="Medium": self.set_priority(x)},
                {"viewclass": "OneLineListItem", "text": "High", "on_release": lambda x="High": self.set_priority(x)}
            ],
            width_mult=4
        )
        self.priority_button.bind(on_release=lambda _: self.open_priority_menu())
        input_layout.add_widget(self.priority_button)

        # Status dropdown menu setup
        self.status_button = MDRaisedButton(
            text="Select Status",
            size_hint=(1, None),
            height='50dp',
            md_bg_color=(0.2, 0.2, 0.2, 1)  # Dark button background
        )
        self.status_menu = MDDropdownMenu(
            caller=self.status_button,
            items=[
                {"viewclass": "OneLineListItem", "text": "Not Started", "on_release": lambda x="Not Started": self.set_status(x)},
                {"viewclass": "OneLineListItem", "text": "In Progress", "on_release": lambda x="In Progress": self.set_status(x)},
                {"viewclass": "OneLineListItem", "text": "Completed", "on_release": lambda x="Completed": self.set_status(x)}
            ],
            width_mult=4
        )
        self.status_button.bind(on_release=lambda _: self.open_status_menu())
        input_layout.add_widget(self.status_button)

        # Button to add task
        self.add_task_button = MDRaisedButton(
            text="Add Task",
            size_hint=(1, None),
            height='50dp',
            on_release=self.add_task,
            disabled_color=(0.5, 0.5, 0.5, 1),  # Dark button background
            md_bg_color_disabled=(0.5, 0.5, 0.5, 1),  # Dark button background
            md_bg_color=(0.2, 0.2, 0.800, 1)  # Dark button background
        )
        input_layout.add_widget(self.add_task_button)

        # Add the input layout to the ScrollView
        input_scroll.add_widget(input_layout)

        # Scrollable view for task list
        self.scroll_view = ScrollView(size_hint=(1, 0.8))  # Takes up 90% of the screen height
        self.task_list_layout = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.task_list_layout.bind(minimum_height=self.task_list_layout.setter('height'))
        self.scroll_view.add_widget(self.task_list_layout)

        # Add ScrollView for inputs and tasks list to the main layout
        main_layout.add_widget(input_scroll)
        main_layout.add_widget(self.scroll_view)

        # Add the layout to the screen
        self.add_widget(main_layout)

        # Fetch initial tasks
        self.get_tasks()

    def validate_task_description(self, instance, value):
        """Custom validation for task description."""
        if not value:  # When focus is lost
            if not instance.text:  # If the text field is still empty
                instance.error = True  # Show the error state
            else:
                instance.error = False  # Clear the error state if text is present

    def show_date_picker(self, instance):
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.on_date_selected)
        date_picker.open()

    def on_date_selected(self, instance, value, date_range):
        self.selected_date_label.text = f"Due Date: {value}"
        self.selected_date = str(value)

    def open_priority_menu(self):
        self.priority_menu.open()

    def open_status_menu(self):
        self.status_menu.open()

    def set_priority(self, priority):
        self.priority_button.text = priority
        self.priority_menu.dismiss()

    def set_status(self, status):
        self.status_button.text = status
        self.status_menu.dismiss()

    def add_task(self, instance):
        task_name = self.task_input.text.strip()
        task_description = self.task_description_input.text.strip()
        task_due_date = self.selected_date if hasattr(self, 'selected_date') else None
        task_priority = self.priority_button.text
        task_status = self.status_button.text

        if not task_name or not task_due_date:
            self.show_error("Task name and due date are required!")
            return

        task_data = {
            'name': task_name,
            'description': task_description,
            'due_date': task_due_date,
            'priority': task_priority,
            'status': task_status
        }

        try:
            response = requests.post(API_URL, json=task_data)
            if response.status_code == 201:
                self.get_tasks()
                self.task_input.text = ""
                self.task_description_input.text = ""
                self.selected_date_label.text = "No due date selected"
            else:
                self.show_error("Failed to add task.")
        except requests.exceptions.RequestException:
            self.show_error("Error connecting to the server.")

    def get_tasks(self, instance=None):
        self.task_list_layout.clear_widgets()

        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                tasks = response.json()

                for task in tasks:
                    self.add_task_card(task)

            else:
                self.show_error("Failed to load tasks.")
        except requests.exceptions.RequestException:
            self.show_error("Error connecting to the server.")

    def add_task_card(self, task):
        card = MDCard(orientation='vertical', size_hint=(1, None), height='50dp', padding=(10, 10), spacing=20)

        # Task details label (clickable button, matching the size of the card)
        task_button = MDRaisedButton(
            text=f"{task['name']} - Priority: {task['priority']} - Due: {task['due_date']} - Status: {task['status']}",
            size_hint=(1, None),  # Full width of the card
            height='250dp',  # Match the height of the card
            on_release=lambda instance, task=task: self.open_task_details(task),
            pos_hint={"center_x": 0.5},  # Center the button horizontally
            md_bg_color=(0.2, 0.2, 0.2, 1)  # Dark button background
        )

        # Add the button (instead of label) to the card so it fills the card size
        card.add_widget(task_button)

        # Add the card to the task list layout
        self.task_list_layout.add_widget(card)

    def open_task_details(self, task):
        # Pass the task to the TaskDetailsScreen and switch to it
        task_details_screen = self.screen_manager.get_screen("task_details")
        task_details_screen.display_task_details(task)
        self.screen_manager.current = "task_details"

    def show_error(self, message):
        popup = Popup(title='Error', content=MDLabel(text=message, halign="center"), size_hint=(0.8, 0.3))
        popup.open()


class TaskDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super(TaskDetailsScreen, self).__init__(**kwargs)

        # Main layout for the screen
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.md_bg_color = (0.18, 0.500, 0.18, 1)  # Dark background
        # Task details label (will be updated with the task data)
        self.task_label = MDLabel(text="Task details will be displayed here", halign="center", theme_text_color="Custom", text_color=(1, 1, 1, 1))
        layout.add_widget(self.task_label)

        # Back button to return to TaskManager screen
        back_button = MDRaisedButton(text="Back", size_hint=(1, None), height='50dp', on_release=self.go_back, md_bg_color=(0.2, 0.2, 0.2, 1))
        layout.add_widget(back_button)

        self.add_widget(layout)

    def display_task_details(self, task):
        # Update the label with task details
        self.task_label.text = (
            f"Task: {task['name']}\n"
            f"Description: {task['description']}\n"
            f"Due Date: {task['due_date']}\n"
            f"Priority: {task['priority']}\n"
            f"Status: {task['status']}"
        )

    def go_back(self, instance):
        # Switch back to the TaskManager screen
        self.parent.current = "task_manager"


class TaskManagerApp(MDApp):
    def build(self):
        # Create a ScreenManager to switch between screens
        screen_manager = ScreenManager()

        # Create the TaskManager and TaskDetailsScreen
        task_manager_screen = TaskManager(name="task_manager", screen_manager=screen_manager)
        task_details_screen = TaskDetailsScreen(name="task_details")

        # Add both screens to the ScreenManager
        screen_manager.add_widget(task_manager_screen)
        screen_manager.add_widget(task_details_screen)

        return screen_manager


if __name__ == '__main__':
    TaskManagerApp().run()

class TaskDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super(TaskDetailsScreen, self).__init__(**kwargs)

        # Main layout for the screen
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.md_bg_color = (0.18, 0.500, 0.18, 1)  # Dark background
        # Task details label (will be updated with the task data)
        self.task_label = MDLabel(text="Task details will be displayed here", halign="center", theme_text_color="Custom", text_color=(1, 1, 1, 1))
        layout.add_widget(self.task_label)

        # Back button to return to TaskManager screen
        back_button = MDRaisedButton(text="Back", size_hint=(1, None), height='50dp', on_release=self.go_back, md_bg_color=(0.2, 0.2, 0.2, 1))
        layout.add_widget(back_button)

        self.add_widget(layout)

    def display_task_details(self, task):
        # Update the label with task details
        self.task_label.text = (
            f"Task: {task['name']}\n"
            f"Description: {task['description']}\n"
            f"Due Date: {task['due_date']}\n"
            f"Priority: {task['priority']}\n"
            f"Status: {task['status']}"
        )

    def go_back(self, instance):
        # Switch back to the TaskManager screen
        self.parent.current = "task_manager"


class TaskManagerApp(MDApp):
    def build(self):
        # Create a ScreenManager to switch between screens
        screen_manager = ScreenManager()

        # Create the TaskManager and TaskDetailsScreen
        task_manager_screen = TaskManager(name="task_manager", screen_manager=screen_manager)
        task_details_screen = TaskDetailsScreen(name="task_details")

        # Add both screens to the ScreenManager
        screen_manager.add_widget(task_manager_screen)
        screen_manager.add_widget(task_details_screen)

        return screen_manager


if __name__ == '__main__':
    TaskManagerApp().run()
