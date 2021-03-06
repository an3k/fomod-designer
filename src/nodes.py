#!/usr/bin/env python

# Copyright 2016 Daniel Nunes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import sep
from collections import OrderedDict
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import Qt
from lxml import etree, objectify
from jsonpickle import encode, decode, set_encoder_options
from json import JSONDecodeError
from .io import copy_node
from .wizards import WizardFiles, WizardDepend
from .props import PropertyCombo, PropertyInt, PropertyText, PropertyFile, PropertyFolder, PropertyColour, \
    PropertyFlagLabel, PropertyFlagValue, PropertyHTML


class NodeComment(etree.CommentBase):
    """
    The base class for all comment nodes.
    """
    def __init__(self, text=""):
        super(NodeComment, self).__init__(text)

    def _init(self):
        super()._init()
        self.sort_order = "0"
        self.user_sort_order = "0".zfill(7)
        self.allowed_children = ()
        self.allowed_instances = 0
        self.wizard = None
        self.name = "Comment"
        self.is_hidden = False
        self.forbidden_sequences = ["<!- -", "- ->", "--"]
        self.properties = {"<node_text>": PropertyText("Comment")}
        self.model_item = NodeStandardItem(self)
        self.model_item.setForeground(Qt.blue)
        self.update_item_name()

    def update_item_name(self):
        self.model_item.setText(self.name) if not self.text else self.model_item.setText(self.text[:40])

    def parse_attribs(self):
        self.properties["<node_text>"].set_value(self.text)
        self.update_item_name()

    def write_attribs(self):
        self.text = self.properties["<node_text>"].value
        if self.text.startswith("<designer.metadata.do.not.edit>"):
            self.getparent().model_item.takeRow(self.model_item.row())
        else:
            self.model_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled)

    def load_metadata(self):
        pass

    def save_metadata(self):
        pass

    def sort(self):
        pass


class _NodeElement(etree.ElementBase):
    """
    The base class for all nodes. Should never be instantiated directly.
    """
    def _init(self):
        if type(self) is _NodeElement:
            raise AssertionError(str(type(self)) + " is not meant to be instanced. A subclass should be used instead.")
        super()._init()

    def init(self, name, tag, allowed_instances,
             sort_order="0",
             allowed_children=None,
             properties=None,
             wizard=None,
             required_children=None,
             either_children_group=None,
             at_least_one_children_group=None,
             name_editable=False,
             ):

        if not properties:
            properties = OrderedDict()
        if not allowed_children:
            allowed_children = ()
        if not required_children:
            required_children = ()
        if not either_children_group:
            either_children_group = ()
        if not at_least_one_children_group:
            at_least_one_children_group = ()

        self.name = name
        self.tag = tag
        self.sort_order = sort_order
        self.properties = properties
        self.allowed_children = allowed_children
        self.required_children = required_children
        self.either_children_group = either_children_group
        self.at_least_one_children_group = at_least_one_children_group
        self.hidden_children = []
        self.is_hidden = False
        self.allowed_instances = allowed_instances
        self.wizard = wizard
        self.metadata = {}
        self.user_sort_order = "0".zfill(7)

        self.model_item = NodeStandardItem(self)
        self.model_item.setText(self.name)
        if allowed_instances > 1 or not allowed_instances:
            self.model_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsEditable)
        else:
            self.model_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsDropEnabled | Qt.ItemIsEnabled | Qt.ItemIsEditable)
        self.model_item.setEditable(name_editable)

    def can_add_child(self, child):
        """
        Checks if the given child can be added to this node.

        :param child: The child to check.
        :return: True if possible, False if not.
        """
        if child.allowed_instances:
            instances = 0
            for item in self:
                if type(item) == type(child):
                    instances += 1
            if instances >= child.allowed_instances:
                return False
        if type(child) in self.allowed_children or child.tag is etree.Comment:
            return True
        return False

    def add_child(self, child):
        """
        Adds the given child to this node. Includes a check with can_add_child at the start.

        :param child: The child to add.
        """
        if self.can_add_child(child):
            self.append(child)
            self.model_item.appendRow(child.model_item)
            child.write_attribs()
            child.load_metadata()

    def remove_child(self, child):
        """
        Removes the given child from this node.

        :param child: The child to remove.
        """
        if child in self:
            self.model_item.takeRow(child.model_item.row())
            self.remove(child)

    def set_hidden(self, hide: bool):
        self.is_hidden = hide
        if hide:
            self.model_item.setForeground(Qt.green)
            self.getparent().hidden_children.append(self)
        else:
            self.model_item.setForeground(Qt.black)
            self.getparent().hidden_children.remove(self)
        self.getparent().save_metadata()

    def sort(self):
        for parent in self.xpath('//*[./*]'):
            parent[:] = sorted(
                parent,
                key=lambda x: x.sort_order + "." + x.user_sort_order
            )

    def parse_attribs(self):
        """
        Reads the values from the BaseElement's attrib dictionary into the node's properties.
        """
        for key in self.properties:
            if key == "<node_text>":
                self.properties[key].set_value(self.text)
                continue
            if key not in self.attrib.keys():
                continue
            self.properties[key].set_value(self.attrib[key])
        self.update_item_name()

    def write_attribs(self):
        """
        Writes the values from the node's properties into the BaseElement's attrib dictionary.
        """
        self.attrib.clear()
        for key in self.properties:
            if key == "<node_text>":
                self.text = self.properties[key].value
                continue
            self.set(key, str(self.properties[key].value))
        if self.is_hidden:
            self.getparent().save_metadata()

    def update_item_name(self):
        """
        Updates this node's item's display name.

        Override in subclasses as needed.
        """
        return self.name

    def load_metadata(self):
        """
        Loads this node's metadata which is stored in a child comment encoded in json.
        """
        for child in self:
            if type(child) is NodeComment:
                if child.text.startswith("<designer.metadata.do.not.edit>"):
                    try:
                        self.metadata = decode(child.text.split(maxsplit=1)[1])
                    except JSONDecodeError:
                        continue

        self.model_item.setText(self.metadata.get("name", self.update_item_name()))
        self.user_sort_order = self.metadata.get("user_sort", "0".zfill(7))
        if not self.hidden_children:
            hidden_nodes = self.metadata.get("hidden_nodes", [])
            for node_string in hidden_nodes:
                node_string = node_string.replace("<!- -", "<!--").replace("- ->", "-->")
                node = copy_node(etree.fromstring(node_string), self)  # type: _NodeElement
                self.add_child(node) if node.tag is not etree.Comment else self.append(node)
                node.set_hidden(True)
                self.sort()
                self.model_item.sortChildren(0)

    def save_metadata(self):
        """
        Saves this node's metadata.
        """
        if self.model_item.text() != self.name:
            self.metadata["name"] = self.model_item.text()
        else:
            self.metadata.pop("name", None)

        if self.user_sort_order and self.user_sort_order != "0".zfill(7):
            self.metadata["user_sort"] = self.user_sort_order.zfill(7)
        else:
            self.metadata.pop("user_sort", None)

        if self.hidden_children:
            self.metadata["hidden_nodes"] = []
            for element in self.hidden_children:
                objectify.deannotate(element, cleanup_namespaces=True)
                node_string = etree.tostring(element, pretty_print=False, encoding="unicode")
                node_string = node_string.replace("<!--", "<!- -").replace("-->", "- ->")
                self.metadata["hidden_nodes"].append(node_string)
        else:
            self.metadata.pop("hidden_nodes", None)

        if not self.allowed_children and "<node_text>" not in self.properties.keys():
            return
        else:
            meta_comment = None
            set_encoder_options("json", separators=(',', ':'))
            for child in self:
                if type(child) is NodeComment:
                    if child.text.startswith("<designer.metadata.do.not.edit>"):
                        meta_comment = child
                        if self.metadata:
                            child.text = "<designer.metadata.do.not.edit> " + encode(self.metadata)
                        else:
                            self.remove(child)

            if meta_comment is None and self.metadata:
                meta_comment = NodeComment()
                meta_comment.properties["<node_text>"].set_value("<designer.metadata.do.not.edit> " + encode(self.metadata))
                self.add_child(meta_comment)


class NodeStandardItem(QStandardItem):
    """A Standard Item but with an added reference to a xml node."""
    def __init__(self, node):
        self.xml_node = node
        super().__init__()

    def __lt__(self, other):
        self_sort = self.xml_node.sort_order + "." + self.xml_node.user_sort_order
        other_sort = other.xml_node.sort_order + "." + other.xml_node.user_sort_order
        if self_sort < other_sort:
            return True
        else:
            return False


class NodeInfoRoot(_NodeElement):
    """
    A node for the tag fomod
    """
    tag = "fomod"

    def _init(self):
        allowed_children = (
            NodeInfoName,
            NodeInfoAuthor,
            NodeInfoDescription,
            NodeInfoID,
            NodeInfoGroup,
            NodeInfoVersion,
            NodeInfoWebsite
        )
        self.init(
            "Info",
            type(self).tag,
            1,
            allowed_children=allowed_children
        )
        super()._init()


class NodeInfoName(_NodeElement):
    """
    A node for the tag Name
    """
    tag = "Name"

    def _init(self):
        properties = OrderedDict([
            ("<node_text>", PropertyText("Name"))
        ])
        self.init(
            "Name",
            type(self).tag,
            1,
            properties=properties
        )
        super()._init()


class NodeInfoAuthor(_NodeElement):
    """
    A node for the tag Author
    """
    tag = "Author"

    def _init(self):
        properties = OrderedDict([
            ("<node_text>", PropertyText("Author"))
        ])
        self.init(
            "Author",
            type(self).tag,
            1,
            properties=properties
        )
        super()._init()


class NodeInfoVersion(_NodeElement):
    """
    A node for the tag Version
    """
    tag = "Version"

    def _init(self):
        properties = OrderedDict([
            ("<node_text>", PropertyText("Version"))
        ])
        self.init(
            "Version",
            type(self).tag,
            1,
            properties=properties
        )
        super()._init()


class NodeInfoID(_NodeElement):
    """
    A node for the tag Id
    """
    tag = "Id"

    def _init(self):
        properties = OrderedDict([
            ("<node_text>", PropertyText("ID"))
        ])
        self.init(
            "ID",
            type(self).tag,
            1,
            properties=properties
        )
        super()._init()


class NodeInfoWebsite(_NodeElement):
    """
    A node for the tag Website
    """
    tag = "Website"

    def _init(self):
        properties = OrderedDict([
            ("<node_text>", PropertyText("Website"))
        ])
        self.init(
            "Website",
            type(self).tag,
            1,
            properties=properties
        )
        super()._init()


class NodeInfoDescription(_NodeElement):
    """
    A node for the tag Description
    """
    tag = "Description"

    def _init(self):
        properties = OrderedDict([
            ("<node_text>", PropertyText("Description"))
        ])
        self.init(
            "Description",
            type(self).tag,
            1,
            properties=properties
        )
        super()._init()


class NodeInfoGroup(_NodeElement):
    """
    A node for the tag Groups
    """
    tag = "Groups"

    def _init(self):
        allowed_child = (
            NodeInfoElement,
        )
        self.init(
            "Categories Group",
            type(self).tag,
            1,
            allowed_children=allowed_child
        )
        super()._init()


class NodeInfoElement(_NodeElement):
    """
    A node for the tag element
    """
    tag = "element"

    def _init(self):
        properties = OrderedDict([
            ("<node_text>", PropertyText("Category"))
        ])
        self.init(
            "Category",
            type(self).tag,
            0,
            properties=properties
        )
        super()._init()


class NodeConfigRoot(_NodeElement):
    """
    A node for the tag config
    """
    tag = "config"

    def _init(self):
        allowed_children = (
            NodeConfigModName,
            NodeConfigModImage,
            NodeConfigModDepend,
            NodeConfigInstallSteps,
            NodeConfigReqFiles,
            NodeConfigCondInstall
        )
        required = (
            NodeConfigModName,
        )
        at_least_one = (
            NodeConfigModDepend,
            NodeConfigInstallSteps,
            NodeConfigReqFiles,
            NodeConfigCondInstall
        )
        properties = OrderedDict(
            [
                ("{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation",
                 PropertyText(
                     "xsi", "http://qconsulting.ca/fo3/ModConfig5.0.xsd", False
                 ))
            ]
        )
        self.init(
            "Config",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            properties=properties,
            required_children=required,
            at_least_one_children_group=at_least_one
        )
        super()._init()


class NodeConfigModName(_NodeElement):
    """
    A node for the tag moduleName
    """
    tag = "moduleName"

    def _init(self):
        properties = OrderedDict([
            ("<node_text>", PropertyText("Name")),
            ("position", PropertyCombo("Position", ("Left", "Right", "RightOfImage"))),
            ("colour", PropertyColour("Colour", "000000"))
        ])
        self.init(
            "Name",
            type(self).tag,
            1,
            properties=properties,
            sort_order="1"
        )
        super()._init()


class NodeConfigModImage(_NodeElement):
    """
    A node for the tag moduleImage
    """
    tag = "moduleImage"

    def _init(self):
        properties = OrderedDict([
            ("path", PropertyFile("Path")),
            ("showImage", PropertyCombo("Show Image", ("true", "false"))),
            ("showFade", PropertyCombo("Show Fade", ("true", "false"))),
            ("height", PropertyInt("Height", -1, 9999, -1))
        ])
        self.init(
            "Image",
            "moduleImage",
            1,
            properties=properties,
            sort_order="2"
        )
        super()._init()


class NodeConfigModDepend(_NodeElement):
    """
    A node for the tag moduleDependencies
    """
    tag = "moduleDependencies"

    def _init(self):
        allowed_children = (
            NodeConfigDependFile,
            NodeConfigDependFlag,
            NodeConfigDependGame,
            NodeConfigNestedDependencies
        )
        properties = OrderedDict([
            ("operator", PropertyCombo("Type", ["And", "Or"]))
        ])
        self.init(
            "Mod Dependencies",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            properties=properties,
            sort_order="3",
            wizard=WizardDepend
        )
        super()._init()


class NodeConfigReqFiles(_NodeElement):
    """
    A node for the tag requiredInstallFiles
    """
    tag = "requiredInstallFiles"

    def _init(self):
        allowed_children = (
            NodeConfigFile,
            NodeConfigFolder
        )
        self.init(
            "Mod Requirements",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            sort_order="4",
            wizard=WizardFiles
        )
        super()._init()


class NodeConfigInstallSteps(_NodeElement):
    """
    A node for the tag installSteps
    """
    tag = "installSteps"

    def _init(self):
        allowed_children = (
            NodeConfigInstallStep,
        )
        required = (
            NodeConfigInstallStep,
        )
        properties = OrderedDict([
            ("order", PropertyCombo("Order", ["Ascending", "Descending", "Explicit"]))
        ])
        self.init(
            "Installation Steps",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            properties=properties,
            sort_order="5",
            required_children=required
        )
        super()._init()


class NodeConfigCondInstall(_NodeElement):
    """
    A node for the tag conditionalFileInstalls
    """
    tag = "conditionalFileInstalls"

    def _init(self):
        allowed_children = (
            NodeConfigPatterns,
        )
        required = (
            NodeConfigPatterns,
        )
        self.init(
            "Conditional Installation",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            sort_order="6",
            required_children=required
        )
        super()._init()


class NodeConfigDependFile(_NodeElement):
    """
    A node for the tag fileDependency
    """
    tag = "fileDependency"

    def _init(self):
        properties = OrderedDict([
            ("file", PropertyText("File")),
            ("state", PropertyCombo("State", ("Active", "Inactive", "Missing")))
        ])
        self.init(
            "File Dependency",
            type(self).tag,
            0,
            properties=properties
        )
        super()._init()


class NodeConfigDependFlag(_NodeElement):
    """
    A node for the tag flagDependency
    """
    tag = "flagDependency"

    def _init(self):
        properties = OrderedDict([
            ("flag", PropertyFlagLabel("Label")),
            ("value", PropertyFlagValue("Value"))
        ])
        self.init(
            "Flag Dependency",
            type(self).tag,
            0,
            properties=properties
        )
        super()._init()


class NodeConfigDependGame(_NodeElement):
    """
    A node for the tag gameDependency
    """
    tag = "gameDependency"

    def _init(self):
        properties = OrderedDict([
            ("version", PropertyText("Version"))
        ])
        self.init(
            "Game Dependency",
            "gameDependency",
            1,
            properties=properties
        )
        super()._init()


class NodeConfigFile(_NodeElement):
    """
    A node for the tag file
    """
    tag = "file"

    def _init(self):
        properties = OrderedDict([
            ("source", PropertyFile("Source")),
            ("destination", PropertyText("Destination")),
            ("priority", PropertyInt("Priority", 0, 99, 0)),
            ("alwaysInstall", PropertyCombo("Always Install", ("false", "true"))),
            ("installIfUsable", PropertyCombo("Install If Usable", ("false", "true")))
        ])
        self.init(
            "File",
            type(self).tag,
            0,
            properties=properties
        )
        super()._init()

    def update_item_name(self):
        """
        Updates this node's item's display name.

        Override in subclasses as needed.
        """
        if not self.properties["source"].value:
            self.model_item.setText(self.name)
            return self.name
        split_name = self.properties["source"].value.split(sep)
        self.model_item.setText(split_name[len(split_name) - 1])
        return split_name[len(split_name) - 1]


class NodeConfigFolder(_NodeElement):
    """
    A node for the tag folder
    """
    tag = "folder"

    def _init(self):
        properties = OrderedDict([
            ("source", PropertyFolder("Source")),
            ("destination", PropertyText("Destination")),
            ("priority", PropertyInt("Priority", 0, 99, 0)),
            ("alwaysInstall", PropertyCombo("Always Install", ("false", "true"))),
            ("installIfUsable", PropertyCombo("Install If Usable", ("false", "true")))
        ])
        self.init(
            "Folder",
            type(self).tag,
            0,
            properties=properties
        )
        super()._init()

    def update_item_name(self):
        """
        Updates this node's item's display name.

        Override in subclasses as needed.
        """
        if not self.properties["source"].value:
            self.model_item.setText(self.name)
            return self.name
        split_name = self.properties["source"].value.split(sep)
        self.model_item.setText(split_name[len(split_name) - 1])
        return split_name[len(split_name) - 1]


class NodeConfigPatterns(_NodeElement):
    """
    A node for the tag patterns
    """
    tag = "patterns"

    def _init(self):
        allowed_children = (
            NodeConfigPattern,
        )
        required = (
            NodeConfigPattern,
        )
        self.init(
            "Patterns",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            required_children=required
        )
        super()._init()


class NodeConfigPattern(_NodeElement):
    """
    A node for the tag pattern
    """
    tag = "pattern"

    def _init(self):
        allowed_children = (
            NodeConfigFiles,
            NodeConfigDependencies
        )
        required = (
            NodeConfigFiles,
            NodeConfigDependencies
        )
        self.init(
            "Pattern",
            type(self).tag,
            0,
            allowed_children=allowed_children,
            required_children=required,
            name_editable=True
        )
        super()._init()


class NodeConfigFiles(_NodeElement):
    """
    A node for the tag files
    """
    tag = "files"

    def _init(self):
        allowed_children = (
            NodeConfigFile,
            NodeConfigFolder
        )
        self.init(
            "Files",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            sort_order="3",
            wizard=WizardFiles
        )
        super()._init()


class NodeConfigDependencies(_NodeElement):
    """
    A node for the tag dependencies
    """
    tag = "dependencies"

    def _init(self):
        allowed_children = (
            NodeConfigDependFile,
            NodeConfigDependFlag,
            NodeConfigDependGame,
            NodeConfigNestedDependencies
        )
        properties = OrderedDict([
            ("operator", PropertyCombo("Type", ["And", "Or"]))
        ])
        self.init(
            "Dependencies",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            properties=properties,
            sort_order="1",
            wizard=WizardDepend
        )
        super()._init()


class NodeConfigNestedDependencies(_NodeElement):
    """
    A node for the tag dependencies (this one refers to the all the dependencies that have a dependencies as a parent).
    """
    tag = "dependencies"

    def _init(self):
        allowed_children = (
            NodeConfigDependFile,
            NodeConfigDependFlag,
            NodeConfigDependGame,
            NodeConfigNestedDependencies
        )
        properties = OrderedDict([
            ("operator", PropertyCombo("Type", ["And", "Or"]))
        ])
        self.init(
            "Dependencies",
            type(self).tag,
            0,
            allowed_children=allowed_children,
            properties=properties,
            wizard=WizardDepend
        )
        super()._init()


class NodeConfigInstallStep(_NodeElement):
    """
    A node for the tag installStep
    """
    tag = "installStep"

    def _init(self):
        allowed_children = (
            NodeConfigVisible,
            NodeConfigOptGroups
        )
        required = (
            NodeConfigOptGroups,
        )
        properties = OrderedDict([
            ("name", PropertyText("Name"))
        ])
        self.init(
            "Install Step",
            type(self).tag,
            0,
            allowed_children=allowed_children,
            properties=properties,
            required_children=required
        )
        super()._init()

    def update_item_name(self):
        """
        Updates this node's item's display name.

        Override in subclasses as needed.
        """
        if not self.properties["name"].value:
            self.model_item.setText(self.name)
            return self.name
        self.model_item.setText(self.properties["name"].value)
        return self.properties["name"].value


class NodeConfigVisible(_NodeElement):
    """
    A node for the tag visible
    """
    tag = "visible"

    def _init(self):
        allowed_children = (
            NodeConfigDependFile,
            NodeConfigDependFlag,
            NodeConfigDependGame,
            NodeConfigNestedDependencies
        )
        properties = OrderedDict([
            ("operator", PropertyCombo("Type", ["And", "Or"]))
        ])
        self.init(
            "Visibility",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            sort_order="1",
            wizard=WizardDepend,
            properties=properties
        )
        super()._init()


class NodeConfigOptGroups(_NodeElement):
    """
    A node for the tag optionalFileGroups
    """
    tag = "optionalFileGroups"

    def _init(self):
        allowed_children = (
            NodeConfigGroup,
        )
        required = (
            NodeConfigGroup,
        )
        properties = OrderedDict([
            ("order", PropertyCombo("Order", ["Ascending", "Descending", "Explicit"]))
        ])
        self.init(
            "Option Group",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            properties=properties,
            sort_order="2",
            required_children=required
        )
        super()._init()


class NodeConfigGroup(_NodeElement):
    """
    A node for the tag group
    """
    tag = "group"

    def _init(self):
        allowed_children = (
            NodeConfigPlugins,
        )
        required = (
            NodeConfigPlugins,
        )
        properties = OrderedDict([
            ("name", PropertyText("Name")),
            ("type", PropertyCombo("Type", [
                "SelectAny",
                "SelectAtMostOne",
                "SelectExactlyOne",
                "SelectAll",
                "SelectAtLeastOne"
            ]))
        ])
        self.init(
            "Group",
            type(self).tag,
            0,
            allowed_children=allowed_children,
            properties=properties,
            required_children=required
        )
        super()._init()

    def update_item_name(self):
        """
        Updates this node's item's display name.

        Override in subclasses as needed.
        """
        if not self.properties["name"].value:
            self.model_item.setText(self.name)
            return self.name
        self.model_item.setText(self.properties["name"].value)
        return self.properties["name"].value


class NodeConfigPlugins(_NodeElement):
    """
    A node for the tag plugins
    """
    tag = "plugins"

    def _init(self):
        allowed_children = (
            NodeConfigPlugin,
        )
        required = (
            NodeConfigPlugin,
        )
        properties = OrderedDict([
            ("order", PropertyCombo("Order", ["Ascending", "Descending", "Explicit"]))
        ])
        self.init(
            "Plugins",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            properties=properties,
            required_children=required
        )
        super()._init()


class NodeConfigPlugin(_NodeElement):
    """
    A node for the tag plugin
    """
    tag = "plugin"

    def _init(self):
        allowed_children = (
            NodeConfigPluginDescription,
            NodeConfigImage,
            NodeConfigFiles,
            NodeConfigConditionFlags,
            NodeConfigTypeDesc
        )
        required = (
            NodeConfigPluginDescription,
            NodeConfigTypeDesc,
        )
        properties = OrderedDict([
            ("name", PropertyText("Name"))
        ])
        self.init(
            "Plugin",
            type(self).tag,
            0,
            allowed_children=allowed_children,
            properties=properties,
            required_children=required
        )
        super()._init()

    def update_item_name(self):
        """
        Updates this node's item's display name.

        Override in subclasses as needed.
        """
        if not self.properties["name"].value:
            self.model_item.setText(self.name)
            return self.name
        self.model_item.setText(self.properties["name"].value)
        return self.properties["name"].value


class NodeConfigPluginDescription(_NodeElement):
    """
    A node for the tag description
    """
    tag = "description"

    def _init(self):
        properties = OrderedDict([
            ("<node_text>", PropertyHTML("Description"))
        ])
        self.init(
            "Description",
            type(self).tag,
            1,
            properties=properties,
            sort_order="1"
        )
        super()._init()


class NodeConfigImage(_NodeElement):
    """
    A node for the tag image
    """
    tag = "image"

    def _init(self):
        properties = OrderedDict([
            ("path", PropertyFile("Path"))
        ])
        self.init(
            "Image",
            type(self).tag,
            1,
            properties=properties,
            sort_order="2"
        )
        super()._init()


class NodeConfigConditionFlags(_NodeElement):
    """
    A node for the tag conditionFlags
    """
    tag = "conditionFlags"

    def _init(self):
        allowed_children = (
            NodeConfigFlag,
        )
        required = (
            NodeConfigFlag,
        )
        self.init(
            "Flags",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            sort_order="3",
            required_children=required
        )
        super()._init()


class NodeConfigTypeDesc(_NodeElement):
    """
    A node for the tag typeDescriptor
    """
    tag = "typeDescriptor"

    def _init(self):
        allowed_children = (
            NodeConfigDependencyType,
            NodeConfigType
        )
        either_children = (
            NodeConfigDependencyType,
            NodeConfigType
        )
        self.init(
            "Type Descriptor",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            sort_order="4",
            either_children_group=either_children
        )
        super()._init()

    def can_add_child(self, child):
        if super().can_add_child(child):
            if len(self) < 1:
                return True
        return False


class NodeConfigFlag(_NodeElement):
    """
    A node for the tag flag
    """
    tag = "flag"

    def _init(self):
        properties = OrderedDict([
            ("name", PropertyFlagLabel("Label")),
            ("<node_text>", PropertyText("Value")),
        ])
        self.init(
            "Flag",
            type(self).tag,
            0,
            properties=properties,
        )
        super()._init()

    def update_item_name(self):
        """
        Updates this node's item's display name.

        Override in subclasses as needed.
        """
        if not self.properties["name"].value:
            self.model_item.setText(self.name)
            return self.name
        self.model_item.setText(self.properties["name"].value)
        return self.properties["name"].value


class NodeConfigDependencyType(_NodeElement):
    """
    A node for the tag dependencyType
    """
    tag = "dependencyType"

    def _init(self):
        allowed_children = (
            NodeConfigInstallPatterns,
            NodeConfigDefaultType
        )
        required = (
            NodeConfigInstallPatterns,
            NodeConfigDefaultType
        )
        self.init(
            "Dependency Type",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            required_children=required
        )
        super()._init()


class NodeConfigDefaultType(_NodeElement):
    """
    A node for the tag defaultType
    """
    tag = "defaultType"

    def _init(self):
        properties = OrderedDict([
            ("name", PropertyCombo("Type", ["Required", "Recommended", "Optional", "CouldBeUsable", "NotUsable"]))
        ])
        self.init(
            "Default Type",
            type(self).tag,
            1,
            properties=properties,
            sort_order="1"
        )
        super()._init()

    def update_item_name(self):
        """
        Updates this node's item's display name.

        Override in subclasses as needed.
        """
        if not self.properties["name"].value:
            self.model_item.setText(self.name)
            return self.name
        self.model_item.setText(self.properties["name"].value)
        return self.properties["name"].value


class NodeConfigType(_NodeElement):
    """
    A node for the tag type
    """
    tag = "type"

    def _init(self):
        properties = OrderedDict([
            ("name", PropertyCombo("Type", ["Required", "Recommended", "Optional", "CouldBeUsable", "NotUsable"]))
        ])
        self.init(
            "Type",
            type(self).tag,
            1,
            properties=properties,
            sort_order="2"
        )
        super()._init()

    def update_item_name(self):
        """
        Updates this node's item's display name.

        Override in subclasses as needed.
        """
        if not self.properties["name"].value:
            self.model_item.setText(self.name)
            return self.name
        self.model_item.setText(self.properties["name"].value)
        return self.properties["name"].value


class NodeConfigInstallPatterns(_NodeElement):
    """
    A node for the tag patterns
    """
    tag = "patterns"

    def _init(self):
        allowed_children = (
            NodeConfigInstallPattern,
        )
        required = (
            NodeConfigInstallPattern,
        )
        self.init(
            "Patterns",
            type(self).tag,
            1,
            allowed_children=allowed_children,
            sort_order="2",
            required_children=required
        )
        super()._init()


class NodeConfigInstallPattern(_NodeElement):
    """
    A node for the tag pattern
    """
    tag = "pattern"

    def _init(self):
        allowed_children = (
            NodeConfigType,
            NodeConfigDependencies
        )
        required = (
            NodeConfigType,
            NodeConfigDependencies
        )
        self.init(
            "Pattern",
            type(self).tag,
            0,
            allowed_children=allowed_children,
            required_children=required,
            name_editable=True
        )
        super()._init()
