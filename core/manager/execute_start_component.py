# Python Import

# Core import
from add_component_directory import mkdir
from add_installed_component import added_component
from assgin_init_component import execute_assign


def start_component(name):

    try:
        # First step
        mkdir(name)

        # Second step
        execute_assign(name)

        # Third step
        added_component(name)

    except Exception as e:
        print e
