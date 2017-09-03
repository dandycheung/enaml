#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import sys
import types
from time import sleep

import pytest

from enaml import imports
from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.testing.utils import (close_all_windows, close_all_popups,
                                 handle_dialog, handle_question)
from enaml.widgets.api import PopupView, Window

try:
    import matplotlib
except ImportError:
    MATPLOTLIB_AVAILABLE = False
else:
    MATPLOTLIB_AVAILABLE = True


try:
    from PyQt4 import Qsci
except ImportError:
    SCINTILLA_AVAILABLE = False
else:
    SCINTILLA_AVAILABLE = True


try:
    import vtk
except ImportError:
    VTK_AVAILABLE = False
else:
    VTK_AVAILABLE = True


# XXX add dedicated handlers for dynamics
def handle_conditional_example():
    """
    """
    pass


def handle_fields_example():
    """
    """
    pass


def handle_looper_example():
    """
    """
    pass


def handle_notebook_pages_example():
    """
    """
    pass


def handle_popup_view_example(app, window):
    """Test showing the popups.

    """
    def close_popup(app, popup):
        popup.central_widget().widgets()[-1].clicked = True

    popup_triggers = window.central_widget().widgets()
    with close_all_popups(app):
        with handle_dialog(app, handler=close_popup, skip_answer=True,
                           cls=PopupView):
            popup_triggers[0].clicked = True

        for t in popup_triggers[1:]:
            t.clicked = True
            app.process_events()


def handle_window_closing(app, window):
    """Test answering the question to close the window.

    """
    with handle_question(app, 'yes'):
        window.close()

    app.process_events()

    assert not Window.windows


@pytest.mark.parametrize("path, handler",
                         [('aliases/chained_attribute_alias.enaml', None),
                          ('aliases/chained_widget_alias.enaml', None),
                          ('aliases/simple_attribute_alias.enaml', None),
                          ('aliases/simple_widget_alias.enaml', None),
                          pytest.param('applib/live_editor.enaml', None,
                                       marks=pytest.mark.skipif(
                                           not SCINTILLA_AVAILABLE,
                                           reason='Requires scintilla')),
                          ('dynamic/conditional.enaml', None),
                          ('dynamic/fields.enaml', None),
                          ('dynamic/looper.enaml', None),
                          ('dynamic/notebook_pages.enaml', None),
                          ('functions/declare_function.enaml', None),
                          ('functions/observe_model_signal.enaml', None),
                          ('functions/override_function.enaml', None),
                          ('layout/basic/align_offset.enaml', None),
                          ('layout/basic/align.enaml', None),
                          ('layout/basic/grid.enaml', None),
                          ('layout/basic/hbox_equal_widths.enaml', None),
                          ('layout/basic/hbox_spacing.enaml', None),
                          ('layout/basic/hbox.enaml', None),
                          ('layout/basic/horizontal.enaml', None),
                          ('layout/basic/linear_relations.enaml', None),
                          ('layout/basic/vbox.enaml', None),
                          ('layout/basic/vertical.enaml', None),
                          ('layout/advanced/button_ring.enaml', None),
                          ('layout/advanced/factory_func.enaml', None),
                          ('layout/advanced/find_replace.enaml', None),
                          ('layout/advanced/fluid.enaml', None),
                          ('layout/advanced/manual_hbox.enaml', None),
                          ('layout/advanced/manual_vbox.enaml', None),
                          ('layout/advanced/nested_boxes.enaml', None),
                          ('layout/advanced/nested_containers.enaml', None),
                          ('layout/advanced/override_layout_constraints.enaml',
                           None),
                          ('stdlib/mapped_view.enaml', None),
                          ('stdlib/message_box.enaml', None),
                          ('stdlib/slider_transform.enaml', None),
                          ('stdlib/task_dialog.enaml', None),
                          ('styling/banner.enaml', None),
                          ('styling/dock_item_alerts.enaml', None),
                          ('styling/gradient_push_button.enaml', None),
                          ('templates/basic.enaml', None),
                          ('templates/advanced.enaml', None),
                          ('widgets/buttons.enaml', None),
                          ('widgets/context_menu.enaml', None),
                          ('widgets/dock_area.enaml', None),
                          ('widgets/dock_pane.enaml', None),
                          ('widgets/dual_slider.enaml', None),
                          ('widgets/file_dialog.enaml', None),
                          ('widgets/flow_area.enaml', None),
                          ('widgets/focus_traversal.enaml', None),
                          ('widgets/form_spacing.enaml', None),
                          ('widgets/form.enaml', None),
                          ('widgets/group_box.enaml', None),
                          ('widgets/h_group.enaml', None),
                          ('widgets/image_view.enaml', None),
                          ('widgets/main_window.enaml', None),
                          ('widgets/menu_bar.enaml', None),
                          pytest.param('widgets/mpl_canvas.enaml', None,
                                       marks=pytest.mark.skipif(
                                           not MATPLOTLIB_AVAILABLE,
                                           reason='Requires matplotlib')),
                          ('widgets/notebook.enaml', None),
                          ('widgets/popup_menu.enaml', None),
                          ('widgets/popup_view.enaml',
                           handle_popup_view_example),  # Requires handler
                          ('widgets/progress_bar.enaml', None),
                          ('widgets/scroll_area.enaml', None),
                          ('widgets/slider.enaml', None),
                          ('widgets/spin_box.enaml', None),
                          ('widgets/splitter.enaml', None),
                          ('widgets/tool_bar.enaml', None),
                          ('widgets/tool_buttons.enaml', None),
                          ('widgets/v_group.enaml', None),
                          pytest.param('widgets/vtk_canvas.enaml', None,
                                       marks=pytest.mark.skipif(
                                           not VTK_AVAILABLE,
                                           reason='Requires vtk')),
                          ('widgets/window_children.enaml', None),
                          ('widgets/window_closing.enaml',
                           handle_window_closing),
                          ('widgets/window.enaml', None)])
def test_examples(qt_app, enaml_sleep, path, handler):
    """ Test the enaml examples.

    """
    dir_path = os.path.abspath(os.path.split(os.path.dirname(__file__))[0])
    enaml_file = os.path.join(dir_path, 'examples', os.path.normpath(path))

    with open(enaml_file, 'rU') as f:
        enaml_code = f.read()

    # Parse and compile the Enaml source into a code object
    ast = parse(enaml_code, filename=enaml_file)
    code = EnamlCompiler.compile(ast, enaml_file)

    # Create a proper module in which to execute the compiled code so
    # that exceptions get reported with better meaning
    try:
        module = types.ModuleType('enaml_test')
        module.__file__ = os.path.abspath(enaml_file)
        sys.modules['enaml_test'] = module
        ns = module.__dict__

        # Put the directory of the Enaml file first in the path so relative
        # imports can work.
        sys.path.insert(0, os.path.abspath(os.path.dirname(enaml_file)))
        with imports():
            exec code in ns

        with close_all_windows(qt_app):
            window = ns['Main']()
            window.show()
            window.send_to_front()
            qt_app.process_events()
            sleep(enaml_sleep)

            if handler is not None:
                handler(qt_app, window)

    finally:
        pass
        # Make sure we clean up the sys modification before leaving
        sys.path.pop(0)
        del sys.modules['enaml_test']
