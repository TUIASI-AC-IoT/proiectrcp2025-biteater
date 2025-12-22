from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Tree, Input, Pretty

from Constant import Constant
from CustomValidators import GoodWindowSize, GoodTimeout

SERVER_DATA = {
    "name": "root",
    "type": "dir",
    "children": [
        {
            "name": "src",
            "type": "dir",
            "children": [
                {"name": "main.py", "type": "file"},
                {"name": "utils.py", "type": "file"},
                {
                    "name": "components",
                    "type": "dir",
                    "children": [
                        {"name": "header.py", "type": "file"},
                        {"name": "footer.py", "type": "file"},
                    ]
                }
            ]
        },
        {"name": "assets", "type": "dir", "children": []},
        {"name": "config.json", "type": "file"},
        {"name": "README.md", "type": "file"},
    ]
}


class RemoteTreeScreen(ModalScreen[str]):
    # CSS_PATH = "client.tcss"

    def __init__(self, server_data = None):
        super().__init__()
        if server_data is None:
            self.server_data = SERVER_DATA
        else:
            self.server_data = server_data


    def compose(self):
        yield Tree("Project Root", id="json_tree", )


    def on_mount(self) -> None:
        tree = self.query_one("#json_tree", Tree)
        tree.root.expand()

        # Start the recursive build from the server data
        for child in SERVER_DATA["children"]:
            self.add_json_node(tree.root, child, parent_path='')


    def add_json_node(self, parent_node, data, parent_path):
        """Recursively add nodes to the tree."""
        name = data["name"]
        node_type = data.get("type", "file")

        full_path = f"{parent_path}/{name}"
        node_data = {
            "original_data": data,
            "full_path": full_path
        }
        if node_type == "dir":
            # Add a branch (directory)
            # allow_expand=False prevents opening empty folders
            branch = parent_node.add(name, expand=False, data=node_data)

            for child in data.get("children", []):
                self.add_json_node(branch, child, parent_path=full_path)
        else:
            parent_node.add_leaf(name, data=node_data)


    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node_data = event.node.data
        if node_data:
            self.log("*" * 50)
            self.log(f"Selected file={node_data["full_path"]}\nThe node is={event.node}")
            self.log("*" * 50)
            self.dismiss(node_data["full_path"])



class SettingsScreen(ModalScreen[tuple[int, float]]):
    CSS = """
        Input.-valid {
            border: tall $success 60%;
        }
        Input.-valid:focus {
            border: tall $success;
        }
        Input {
            margin: 1 1;
        }
        Label {
            margin: 1 2;
        }
        Pretty {
            margin: 1 2;
            visibility: hidden;
        }
        """

    def __init__(self):
        super().__init__()
        self.window_size_good = False
        self.timeout_good = False


    def compose(self) -> ComposeResult:
        yield Input(
            placeholder=Constant.WINDOW_STR.value,
            validators=GoodWindowSize(),
            id="window_input",
            type="integer"
        )
        yield Pretty("", id="window_log")
        yield Input(
            placeholder=Constant.TIMEOUT_STR.value,
            validators=GoodTimeout(),
            id="timeout_input",
            type="number"
        )
        yield Pretty("", id="timeout_log")


    @on(Input.Changed, "#window_input")
    def check_window(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        if not event.validation_result.is_valid:
            self.query_one("#window_log",Pretty).update(event.validation_result.failure_descriptions)
            self.query_one("#window_log",Pretty).styles.visibility = "visible"
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
            w = int(t)
            t = float(w)
            self.dismiss((w, t))

