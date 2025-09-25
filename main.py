class Screen:
    def __init__(self, name):
        self.name = name
        self.parent_screen = None
        self.sub_screen = []
        self.selection_screen = False
        self.content = f"self.name: {self.name}"

    def start(self):
        pass

    def get_name(self):
        return self.name

    def get_parent_screen(self):
        return self.parent_screen

    def get_sub_screen(self):
        return self.sub_screen

    def set_parent_screen(self, parent_screen):
        self.parent_screen = parent_screen

    def set_content(self, message):
        self.content = message


    def add_sub_screen(self, screen):
        self.sub_screen.append(screen)
        screen.set_parent_screen(self)

    def input_process(self, user_input):
        pass

class ScreenManager:
    def __init__(self):
        self.focus = None
        #a dictionary {index:screen} with the index representing the number displayed on screen
        #index number 0 is always the parent screen (if it exists)
        self.available_screens = {}

    def update_available_screens(self):
        self.available_screens.clear()
        sub_screens = self.focus.get_sub_screen()
        parent_screen = self.focus.get_parent_screen()
        #index 0 is the parent screen
        if parent_screen:
            self.available_screens.update({0: parent_screen})
        if sub_screens:
            for i, screen in enumerate(sub_screens, start=1):
                self.available_screens.update({i: screen})

    def get_available_screens(self):
        return self.available_screens

    def get_screen_from_index(self, index):
        screen = self.available_screens.get(index)
        if not screen:
            return self.available_screens.get(index), "Invalid Index"

        return self.available_screens.get(index), "Success"

    def get_focus(self):
        return self.focus

    def go_to_screen(self, screen):
        self.focus = screen
        self.update_available_screens()

    def go_back(self):
        if self.focus.get_parent_screen():
            self.focus = self.focus.get_parent_screen()

    def set_focus(self, screen):
        self.focus = screen

    def pass_input(self):
        pass

class ScreenViewer:
    def __init__(self):
        self.prefix = "[SYSTEM]"
        self.error_prefix = "[ERROR]"
        pass

    #displays the content in the screen
    def display_screen(self, screen):
        print(f"\n[{screen.get_name().upper()}]")
        print(screen.content)

    #displays possible routes
    def display_routes(self, sub_screens):
        for index, screen in sub_screens.items():
            #if its the home screen make it a back arrow!
            if index == 0:
                print(f"\t[{index}]: <- {screen.get_name().upper()}")
            else:
                print(f"\t[{index}]: -> {screen.get_name().upper()}")

    def sys_output(self, message):
        print(f"{self.prefix}: {message}")

    def error_output(self, message):
        print(f"{self.error_prefix}: {message}")

class Controller(object):
    def __init__(self):
        self.screen_manager = ScreenManager()
        self.screen_viewer = ScreenViewer()
        self.home = Screen("home")
        self.info = Screen("info")
        self.about = Screen("about")
        #set up text
        self.set_screen_content()
        #set up subscreens
        self.home.add_sub_screen(self.info)
        self.info.add_sub_screen(self.about)
        self.set_current_screen(self.home)

    def set_screen_content(self):
        self.home.set_content("Welcome! Select a screen!")
        self.info.set_content("Select a screen to learn more about this program!")
        self.about.set_content("This is a vending machine that sells food and beverages. It is composed of different "
                               "screens that represent a page of the program!")

    def update_current_screen(self):
        current_screen = self.screen_manager.get_focus()
        sub_screens = self.screen_manager.get_available_screens()
        self.screen_viewer.display_screen(current_screen)
        self.screen_viewer.display_routes(sub_screens)

    def set_current_screen(self, screen):
        self.screen_manager.go_to_screen(screen)
        screens = self.screen_manager.get_available_screens()
        screen = self.screen_manager.get_focus()
        self.screen_viewer.display_screen(screen)
        self.screen_viewer.display_routes(screens)

    def go_back(self):
        self.screen_manager.go_back()

    def error_output(self, message):
        self.screen_viewer.error_output(message)

def main():
    controller = Controller()
    controller.screen_manager.update_available_screens()

    while True:
        q = input("Input: \n> ")
        try:
            q = int(q)
            screen, message = controller.screen_manager.get_screen_from_index(q)
            if screen:
                controller.set_current_screen(screen)
            else:
                controller.error_output(message)
                controller.update_current_screen()
        except ValueError:
            controller.error_output("Please enter an integer")
            controller.update_current_screen()

if __name__ == "__main__":
    main()
