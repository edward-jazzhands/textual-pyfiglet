###############################
# ListView Class modification #
###############################
# This was all done to add indexing abilities
# into the ListView class. Will probably turn this into a PR
# for Textual.
# The monkey patching is not ideal but its the only way to add this stuff
# until I submit a full PR.

# ~ Type Checking (Pyright and MyPy) - Strict Mode
# ~ Linting - Ruff
# ~ Formatting - Black - max 110 characters / line

from __future__ import annotations
from typing import cast

from textual.message import Message
from textual.widgets import ListView, ListItem


def _on_list_item__child_clicked(self, event: ListItem._ChildClicked) -> None:  # type: ignore
    event.stop()
    self.focus()  # type: ignore[unused-ignore]
    self.index = self._nodes.index(event.item)  # type: ignore[unused-ignore]
    self.post_message(self.Selected(self, event.item, self.index))  # type: ignore[unused-ignore]


# Monkey patch the ListView class
ListView._on_list_item__child_clicked = _on_list_item__child_clicked  # type: ignore


class Selected(Message):

    ALLOW_SELECTOR_MATCH = {"item"}

    def __init__(self, list_view: CustomListView, item: ListItem, index: int) -> None:
        super().__init__()
        self.list_view: CustomListView = list_view
        """The view that contains the item selected."""
        self.item: ListItem = item
        """The selected item."""
        self.index: int = index

    @property
    def control(self) -> CustomListView:
        return self.list_view


# Instead of directly assigning, create a new attribute using setattr
setattr(ListView, "Selected", Selected)


class CustomListView(ListView):

    def action_select_cursor(self) -> None:
        selected_child = self.highlighted_child
        if selected_child is None:
            return
        index = self._nodes.index(selected_child)
        self.post_message(self.Selected(self, selected_child, index))  # type: ignore

    # HERE FOR EXAMPLE ONLY. This is monkey patched above. It would be
    # preferable to do it this way, but it doesn't work:
    # def _on_list_item__child_clicked(self, event: ListItem._ChildClicked) -> None:
    #     event.stop()
    #     self.focus()
    #     self.index = self._nodes.index(event.item)
    #     self.post_message(self.Selected(self, event.item, self.index))

    def get_index(self, widget: ListItem) -> int | None:
        try:
            index = self._nodes.index(widget)
        except Exception as e:
            self.log.error(f"Node not found: {e}")
            return None
        else:
            return index

    def __getitem__(self, index: int) -> ListItem:
        return cast(ListItem, self._nodes[index])
