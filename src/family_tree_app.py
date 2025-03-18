import os
from family_tree_handler import FamilyTreeHandler


def display_menu(handler_instance):
    working_directory = os.environ.get("BUILD_WORKING_DIRECTORY")
    menu_options = {
        "1": "Load family tree data from file (Protobuf text)",
        "2": "Update output file (family tree diagram) location",
        "3": "Display family tree",
        "4": "Find person",
        "5": "Exit",
    }
    while True:
        print("Menu:")
        for key, value in menu_options.items():
            print(f"{key}: {value}")
        choice = input("Enter your choice: ")
        if choice == "1":
            input_file = input(
                "Enter the path to the input file: (Default: ./input_data/sample_data.txtpb): "
            )
            if not input_file:
                input_file = f"{working_directory}/input_data/sample_data.txtpb"
            handler_instance.update_data_source(input_file)
            handler_instance.load_from_protobuf()
        elif choice == "2":
            output_file = input(
                "Enter the path to the output file: (Default: ./outputs/family_tree.html)"
            )
            if not output_file:
                os.makedirs(f"{working_directory}/outputs", exist_ok=True)
                output_file = f"{working_directory}/outputs/family_tree.html"
            handler_instance.update_output_file(output_file)
        elif choice == "3":
            handler_instance.display_family_tree()
        elif choice == "4":
            handler_instance.find_person()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    family_tree_handler = FamilyTreeHandler()
    display_menu(family_tree_handler)
