from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, Vertical, Horizontal, CenterMiddle
from textual.message import Message
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Tree, Input, Pretty, Label, Footer

from Constant import Constant
from CustomValidators import GoodWindowSize, GoodTimeout

SERVER_DATA = {
    "name": "root",
    "type": "folder",
    "children": [
        {
            "name": "src",
            "type": "folder",
            "children": [
                {"name": "main.py", "type": "file"},
                {"name": "utils.py", "type": "file"},
                {
                    "name": "components",
                    "type": "folder",
                    "children": [
                        {"name": "header.py", "type": "file"},
                        {"name": "footer.py", "type": "file"},
                    ]
                }
            ]
        },
        {"name": "assets", "type": "folder", "children": []},
        {"name": "config.json", "type": "file"},
        {"name": "README.md", "type": "file"},
    ]
}

class Selected(Message):
    """file selected message."""
    def __init__(self, node_path: str, node_type: str, sender_widget: Widget) -> None:
        self.node_path = node_path
        self.node_type = node_type
        self.sender_widget = sender_widget
        super().__init__()


class RemoteTree(Widget):
    def __init__(self, classes=None, server_data=None):
        super().__init__(classes=classes)
        self.__server_data = server_data if server_data else SERVER_DATA

    def compose(self):
        yield Tree("Project Root", id="json_tree")

    def on_mount(self) -> None:
        tree = self.query_one("#json_tree", Tree)
        tree.show_root = False

        # Start the recursive build from the server data
        for child in self.__server_data.get("children", []):
            self.add_json_node(tree.root, child, parent_path='')

        tree.root.expand()

    def add_json_node(self, parent_node, data, parent_path):
        """Recursively add nodes to the tree."""
        node_name = data.get("name", "Unknown")
        node_type = data.get("type", "undefined")

        full_path = f"{parent_path}/{node_name}"

        node_data = {
            "original_data": data,
            "full_path": full_path,
            "type" : node_type
        }
        if node_type == "folder":
            # Add a branch (directory)
            # allow_expand=False prevents opening empty folders
            branch = parent_node.add(node_name, expand=False, data=node_data)

            for child in data.get("children", []):
                self.add_json_node(branch, child, parent_path=full_path)
        else:
            parent_node.add_leaf(node_name, data=node_data)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        event.stop()  # Stop the internal tree event from bubbling further
        node_data = event.node.data
        if node_data:
            self.log("*" * 50)
            self.log(f"Selected file={node_data["full_path"]}\nThe node is={event.node}")
            self.log("*" * 50)
            msg = Selected(node_data["full_path"], node_data["type"], self)
            self.post_message(msg)


class RemoteTreeScreen(ModalScreen[str]):
    CSS_PATH = "./css/RemoteTreeScree.tcss"
    BINDINGS = [
        ("escape", "back", "Back")
    ]

    def __init__(self, title: str, server_data=None, only_file = False):
        super().__init__()
        self.__server_data = server_data if server_data else SERVER_DATA
        self.__title = title
        self.__only_file = only_file

    def compose(self):
        with Vertical():
            yield Label(self.__title)
            yield RemoteTree(server_data=self.__server_data)
        yield Footer()

    def on_selected(self, message: Selected) -> None:
        self.log(f"Entered on_selected method: dismiss({message.node_path})")
        if self.__only_file and not message.node_type == "file":
            self.notify("Please select a file!", title=self.__title + " OPERATION", severity="warning")
        else:
            self.dismiss(message.node_path)

    def action_back(self):
        self.log("Header [action_back()]\n")
        self.dismiss("")


class MoveScreen(ModalScreen[tuple[str, str]]):
    CSS_PATH = "css/MoveScreen.tcss"
    BINDINGS = [
        ("escape", "back", "Back")
    ]

    def __init__(self, server_data=None, client_data=None):
        super().__init__()
        self.__server_data = server_data if server_data else SERVER_DATA
        self.__client_data = client_data if client_data else SERVER_DATA

        self.__src = ""
        self.__dst = ""

    def compose(self):
        with Vertical(id="dialog"):
            yield Label("Select Source File -> Destination Folder", id="status_lbl")
            with Horizontal():
                with Vertical(classes="column"):
                    yield Label("Source (Files)")
                    yield RemoteTree(server_data=self.__server_data, classes="from_tree")

                with Vertical(classes="column"):
                    yield Label("Destination (Folders)")
                    yield RemoteTree(server_data=self.__server_data, classes="to_tree")
        yield Footer()

    def update_status(self):
        """Helper method to update the UI label."""
        src_text = self.__src if self.__src else "None"
        dst_text = self.__dst if self.__dst else "None"
        self.query_one("#status_lbl", Label).update(f"Move: {src_text} -> {dst_text}")

    def on_selected(self, message: Selected) -> None:
        if message.sender_widget.has_class("from_tree"):

            if message.node_type != "file":
                self.notify("Please select a file to move!", severity="warning")
                return
            self.__src = message.node_path
            self.log(f"Source set to: {self.__src}")
            self.update_status()
            self.check_done()

        elif message.sender_widget.has_class("to_tree"):

            if message.node_type != "folder":
                self.notify("Please select a folder as destination!", severity="error")
                return
            self.__dst = message.node_path
            self.log(f"Dest set to: {self.__dst}")
            self.update_status()
            self.check_done()

    def check_done(self):
        """If both are selected, return the result."""
        if self.__src and self.__dst:
            self.dismiss((self.__src, self.__dst))

    def action_back(self):
        self.log("Header [action_back()]\n")
        self.dismiss(("", ""))


class SettingsScreen(ModalScreen[tuple[int, float]]):
    CSS_PATH = "css/SettingsScreen.tcss"
    BINDINGS = [
        ("escape", "back", "Back")
    ]

    def __init__(self):
        super().__init__()
        self.window_size_good = False
        self.timeout_good = False

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Settings")
            yield Input(
                placeholder=str(Constant.WINDOW_STR.value),
                validators=GoodWindowSize(),
                id="window_input",
                type="integer"
            )
            yield Pretty("", id="window_log")
            yield Input(
                placeholder=str(Constant.TIMEOUT_STR.value),
                validators=GoodTimeout(),
                id="timeout_input",
                type="number"
            )
            yield Pretty("", id="timeout_log")
        yield Footer()

    @on(Input.Changed, "#window_input")
    def check_window(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        if not event.validation_result.is_valid:
            self.query_one("#window_log", Pretty).update(event.validation_result.failure_descriptions)
            self.query_one("#window_log", Pretty).styles.visibility = "visible"
            self.window_size_good = False
        else:
            self.query_one("#window_log", Pretty).styles.visibility = "hidden"
            self.window_size_good = True

    @on(Input.Changed, "#timeout_input")
    def check_input(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        if not event.validation_result.is_valid:
            self.query_one("#timeout_log", Pretty).update(event.validation_result.failure_descriptions)
            self.query_one("#timeout_log", Pretty).styles.visibility = "visible"
            self.timeout_good = False
        else:
            self.query_one("#timeout_log", Pretty).styles.visibility = "hidden"
            self.timeout_good = True

    @on(Input.Submitted)
    def check_submit(self):
        if self.window_size_good and self.timeout_good:
            w = self.query_one("#window_input", Input).value
            t = self.query_one("#timeout_input", Input).value
            w = int(w)
            t = float(t)
            self.dismiss((w, t))

    def action_back(self):
        self.log("Header [action_back()]\n")
        self.dismiss((-1, -1.0))