class Item:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

class VendingMachine:
    def __init__(self, balance):
        self.balance = balance
        self.inventory = []

    def add_item(self, items):
        for item in items:
            self.inventory.append(item)

    def get_item_from_index(self, index):
        index -= 1
        if index >= len(self.inventory) or index < 0:
            return None, "Index out of range."
        else:
            return self.inventory[index], "Success."

    def sell_item(self, item: Item, quantity):
        item.stock -= quantity
        self.balance -= item.price * quantity

    def attempt_purchase(self, item: Item, quantity):
        order_price = item.price * quantity
        if item.stock < quantity:
            return False, f"Not enough stock to purchase {item.name}."
        if order_price > self.balance:
            return False, f"Not enough balance to purchase {item.name}."
        self.sell_item(item, quantity)
        return True, f"Successfully purchased {item.name}!"


class Screen:
    def __init__(self, name):
        self.name = name
        self.parent_screen = None
        self.sub_screen = []
        self.content = f"self.name: {self.name}"

    def start(self):
        pass

    def add_sub_screen(self, *screens):
        for screen in screens:
            self.sub_screen.append(screen)
            screen.parent_screen = self

class BuyScreen(Screen):
    def __init__(self, name, vending_machine):
        super().__init__(name)
        self.vending_machine = vending_machine

class InventoryScreen(Screen):
    def __init__(self, name):
        super().__init__(name)
        self.buy_screen = None
        self.vending_machine = None

    def set_vending_machine(self, vending_machine):
        self.vending_machine = vending_machine
        self.buy_screen = BuyScreen("buy", self.vending_machine)
        self.buy_screen.content = "Enter the item index to purchase it."
        self.add_sub_screen(self.buy_screen)

class ScreenManager:
    def __init__(self):
        self.focus = None
        #a dictionary {index:screen} with the index representing the number displayed on screen
        #index number 0 is always the parent screen (if it exists)
        self.available_screens = {}

    def update_available_screens(self):
        self.available_screens.clear()
        sub_screens = self.focus.sub_screen
        parent_screen = self.focus.parent_screen
        #index 0 is the parent screen
        if parent_screen:
            self.available_screens.update({0: parent_screen})
        if sub_screens:
            for i, screen in enumerate(sub_screens, start=1):
                self.available_screens.update({i: screen})

    def get_screen_from_index(self, index):
        screen = self.available_screens.get(index)
        if not screen:
            return self.available_screens.get(index), "Invalid Index"
        return self.available_screens.get(index), "Success"

    def go_to_screen(self, screen):
        self.focus = screen
        self.update_available_screens()

    def go_back(self):
        if self.focus.parent_screen:
            self.focus = self.focus.parent_screen
            self.update_available_screens()

class ScreenViewer:
    def __init__(self):
        self.prefix = "[SYSTEM]"
        self.error_prefix = "[ERROR]"
        pass

    #displays the content in the screen
    def display_screen(self, screen):
        print(f"\n[{screen.name.upper()}]")
        print(screen.content)
        if isinstance(screen, (BuyScreen, InventoryScreen)):
            balance = screen.vending_machine.balance
            print(f"Balance: ${balance:,.2f}")
            pass

    #displays possible routes
    def display_routes(self, sub_screens):
        for index, screen in sub_screens.items():
            #if its the home screen make it a back arrow!
            if index == 0:
                print(f"\t[{index}]: <- {screen.name.upper()}")
            else:
                print(f"\t[{index}]: -> {screen.name.upper()}")

    def display_inventory(self, screen):
        inventory = screen.vending_machine.inventory
        if type(screen) == BuyScreen:
            for i, item in enumerate(inventory, start=1):
                print(f"[{i}] {item.name.title()}: ${item.price:,.2f} x{item.stock}")
        else:
            for i, item in enumerate(inventory, start=1):
                print(f"Item {i}: {item.name.title()}, ${item.price:,.2f}, x{item.stock}")

    def sys_output(self, message):
        print(f"{self.prefix}: {message}")

    def error_output(self, message):
        print(f"{self.error_prefix}: {message}")

    def get_input(self, prompt):
        return input(f"\n{prompt}\n> ")

class ScreenHandler:
    def __init__(self):
        self.screen_manager = ScreenManager()
        self.screen_viewer = ScreenViewer()

    def update(self):
        current_screen = self.screen_manager.focus
        sub_screens = self.screen_manager.available_screens

        self.screen_viewer.display_screen(current_screen)

        if isinstance(current_screen, (BuyScreen, InventoryScreen)):
            self.screen_viewer.display_inventory(current_screen)

        self.screen_viewer.display_routes(sub_screens)

    def get_current_screen(self):
        return self.screen_manager.focus

    def go_to_screen(self, screen):
        self.screen_manager.go_to_screen(screen)
        self.update()

    def go_back(self):
        self.screen_manager.go_back()
        self.update()

class Controller(object):
    def __init__(self):
        #prepare components
        self.screen_handler = ScreenHandler()
        self.food_vending_machine = VendingMachine(100)
        #create screens
        self.home = Screen("home")
        self.info = Screen("info")
        self.about = Screen("about")
        self.inventory = InventoryScreen("inventory")
        #set up text
        self.set_screen_content()
        #set up subscreens
        self.home.add_sub_screen(self.info, self.inventory)
        self.info.add_sub_screen(self.about)
        self.set_current_screen(self.home)
        #Set vending machine
        self.inventory.set_vending_machine(self.food_vending_machine)

    def set_screen_content(self):
        self.home.content = "Welcome! Select a screen!"
        self.info.content = "Select a screen to learn more about this program!"
        self.about.content = ("This is a vending machine that sells food and beverages. It is composed of different "
                               "screens that represent a page of the program!")
        self.inventory.content = "To purchase an item, please select the buy option."

    def update_current_screen(self):
        self.screen_handler.update()

    def set_current_screen(self, screen):
        self.screen_handler.go_to_screen(screen)

    def go_back(self):
        self.screen_handler.go_back()

    def error_output(self, message):
        self.screen_handler.screen_viewer.error_output(message)

    def sys_output(self, message):
        self.screen_handler.screen_viewer.sys_output(message)

    def add_item(self, vending_machine, *item):
        vending_machine.add_item(item)

    def buy_item(self, vending_machine, item, quantity):
        success, message = vending_machine.attempt_purchase(item, quantity)
        if success:
            self.sys_output(message)
        else:
            self.error_output(message)

    def ask_for_pos_int(self, value_name):
        while True:
            try:
                value = int(input(f"Input {value_name}:\n> "))
                if value > 0:
                    return value
                self.error_output(f"Please enter a positive integer")
            except ValueError:
                self.error_output(f"Invalid input.")


def main():
    controller = Controller()
    chips = Item("chips", 20, 10)
    chocolate = Item("chocolate", 20, 10)
    controller.add_item(controller.food_vending_machine, chips, chocolate)

    while True:
        q = controller.screen_handler.screen_viewer.get_input("Awaiting Input:")
        try:
            q = int(q)
            current_screen = controller.screen_handler.get_current_screen()
            #Handle buying if its a buy screen
            if type(current_screen) == BuyScreen and q != 0:
                vending_machine = current_screen.vending_machine
                item, message = vending_machine.get_item_from_index(q)
                if item:
                    quantity = controller.ask_for_pos_int("quantity")
                    controller.buy_item(vending_machine, item, quantity)
                    controller.update_current_screen()
                else:
                    controller.error_output(message)
                    controller.update_current_screen()
            else:
                #If it isn't a buy screen use it to navigate
                screen, message = controller.screen_handler.screen_manager.get_screen_from_index(q)
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
