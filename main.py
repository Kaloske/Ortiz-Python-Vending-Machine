class Item:
    def __init__(self, name: str, price: float, stock: int):
        self.name = name
        self.price = price
        self.stock = stock

class User:
    def __init__(self, balance=100):
        self.balance = balance
        self.inventory = []

    def add_item(self, item: Item, quantity):
        for user_item in self.inventory:
            if user_item.name == item.name:
                user_item.stock += quantity
                return

        new_item = Item(item.name, item.price, quantity)
        self.inventory.append(new_item)

class VendingMachine:
    def __init__(self):
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

    def attempt_purchase(self, item: Item, quantity, bill: int, balance: int):
        order_price = item.price * quantity
        if item.stock < quantity:
            return False, balance, f"Not enough stock to purchase {item.name.upper()}."
        if bill > balance:
            return False, balance, f"Not enough balance to insert selected amount."
        if order_price > bill:
            return False, balance, f"Inserted amount insufficient to purchase {item.name.upper()}."

        change = bill - (item.price * quantity)
        new_balance = (balance - bill) + change

        #check if change is 0
        if change <= 0:
            message = f"Successfully purchased {item.name.upper()}! No change."
        else:
            message = f"Successfully purchased {item.name.upper()}! AED {bill:.2f} inserted and AED {change:.2f} in change returned."

        return True, new_balance, message

class Screen:
    def __init__(self, name):
        self.name = name
        self.parent_screen = None
        self.sub_screen = []
        self.content = f"self.name: {self.name}"

    def add_sub_screen(self, *screens):
        for screen in screens:
            self.sub_screen.append(screen)
            screen.parent_screen = self

    def get_content(self):
        return self.content

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

class ConfirmScreen(Screen):
    def __init__(self, name):
        super().__init__(name)

class ExitScreen(Screen):
    def __init__(self, name):
        super().__init__(name)

class UserInventory(Screen):
    def __init__(self, name):
        super().__init__(name)
        self.user = None

    def set_user(self, user):
        self.user = user

    def get_content(self):
        if not self.user.inventory:
            return f"Nothing here... maybe you should buy something?"
        else:
            return f"Here are the items you've purchased!"

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
            return None, "Invalid Index."
        return screen, "Success."

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
    def display_screen(self, screen, balance, inventory):
        print(f"\n[{screen.name.upper()}]")

        print(screen.get_content())

        if isinstance(screen, (BuyScreen, InventoryScreen)):
            print(f"Balance: AED {balance:,.2f}")
            pass

    def display_confirmation(self):
            print(f"\t[1]: Yes")
            print(f"\t[2]: No")

    #displays possible routes
    def display_routes(self, sub_screens):
        for index, screen in sub_screens.items():
            #if its the home screen make it a back arrow!
            if index == 0:
                print(f"\t[{index}]: <- {screen.name.upper()}")
            else:
                print(f"\t[{index}]: -> {screen.name.upper()}")

    def display_inventory(self, screen):
        if isinstance(screen, BuyScreen):
            inventory = screen.vending_machine.inventory
            for i, item in enumerate(inventory, start=1):
                print(f"[{i}] {item.name.upper()}: AED {item.price:,.2f}, x{item.stock}")
        elif isinstance(screen, InventoryScreen):
            inventory = screen.vending_machine.inventory
            for i, item in enumerate(inventory, start=1):
                print(f"Item {i}: {item.name.upper()}, AED {item.price:,.2f}, x{item.stock}")
        elif isinstance(screen, UserInventory):
            inventory = screen.user.inventory
            for i, item in enumerate(inventory, start=1):
                print(f"Item {i}: {item.name.upper()}, x{item.stock}")

    def sys_output(self, message):
        print(f"\n{self.prefix}: {message}")

    def error_output(self, message):
        print(f"\n{self.error_prefix}: {message}")

    def get_input(self, prompt):
        return input(f"\n{prompt}\n> ")

class ScreenHandler:
    def __init__(self, user):
        self.screen_manager = ScreenManager()
        self.screen_viewer = ScreenViewer()
        self.user = user

    def update(self):
        current_screen = self.screen_manager.focus
        sub_screens = self.screen_manager.available_screens

        #Exit screen doesn't display anything, so we just leave.
        if isinstance(current_screen, ExitScreen):
            return

        self.screen_viewer.display_screen(current_screen, self.user.balance, self.user.inventory)

        if isinstance(current_screen, (BuyScreen, InventoryScreen, UserInventory)):
            self.screen_viewer.display_inventory(current_screen)
        elif isinstance(current_screen, ConfirmScreen):
            self.screen_viewer.display_confirmation()

        self.screen_viewer.display_routes(sub_screens)

    def get_current_screen(self):
        return self.screen_manager.focus

    def go_to_screen(self, screen):
        self.screen_manager.go_to_screen(screen)
        self.update()

    def go_back(self):
        self.screen_manager.go_back()
        self.update()

class Controller:
    def __init__(self, user):
        self.user = user
        #prepare components
        self.screen_handler = ScreenHandler(user)
        self.vending_machine = VendingMachine()
        self.bev_vending_machine = VendingMachine()
        #create screens
        self.home = Screen("home")
        self.info = Screen("info")
        self.about = Screen("about")
        self.confirm= ConfirmScreen("confirm")
        self.inventory = InventoryScreen("food inventory")
        self.bev_inventory = InventoryScreen("beverage inventory")
        self.user_inventory = UserInventory("user inventory")
        self.exit = ExitScreen("exit")
        #set up text
        self.set_screen_content()
        #set up subscreens
        self.home.add_sub_screen(self.info, self.inventory, self.bev_inventory, self.user_inventory, self.exit)
        self.info.add_sub_screen(self.about)
        self.set_current_screen(self.home)
        #Set vending machine
        self.inventory.set_vending_machine(self.vending_machine)
        self.bev_inventory.set_vending_machine(self.bev_vending_machine)
        self.user_inventory.set_user(self.user)

    def set_screen_content(self):
        self.home.content = "Welcome to the Nishie's Vending Machine! Select a screen!"
        self.info.content = "Select a screen to learn more about this program!"
        self.about.content = ("This is a vending machine that sells food and beverages. It is composed of different "
                               "screens that represent a page of the program!")
        self.inventory.content = "To purchase a food item, please select the buy option."
        self.bev_inventory.content = "To purchase a beverage, please select the buy option."
        self.user_inventory.content = "These are the products that you have purchased."

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

    def get_confirmation(self, message = "Confirm"):
        previous_screen = self.screen_handler.get_current_screen()
        self.confirm.content = message
        self.set_current_screen(self.confirm)
        while True:
            user_input = self.screen_handler.screen_viewer.get_input("Awaiting Confirmation:")

            if not check_int(user_input):
                self.error_output("Invalid input.")
                self.update_current_screen()
                continue

            match user_input:
                case "1":
                    self.set_current_screen(previous_screen)
                    return True

                case "2":
                    self.set_current_screen(previous_screen)
                    return False

    def purchase(self, user_input, vending_machine):
        # Check if using the input as an index returns an item.
        item, message = vending_machine.get_item_from_index(user_input)
        if not item:
            self.error_output(message)
            self.update_current_screen()
            return
        #Item is present, do logic
        quantity = self.ask_for_pos_int("quantity")
        bill = self.ask_for_pos_float("bill")
        success, new_balance, message = vending_machine.attempt_purchase(item, quantity, bill, self.user.balance)
        if success:
            #Everything lines up, time to finalize the transaction.
            confirm_prompt= f"Confirm purchase of {quantity}x {item.name.upper()} for AED {item.price * quantity:.2f}"
            if self.get_confirmation(confirm_prompt):
                self.sys_output(message)
                vending_machine.sell_item(item, quantity)
                self.user.add_item(item, quantity)
                self.user.balance = new_balance
        else:
            self.error_output(message)

        self.update_current_screen()

    def navigate(self, user_input):
        screen, message = self.screen_handler.screen_manager.get_screen_from_index(user_input)
        if screen:
            self.set_current_screen(screen)
        else:
            self.error_output(message)
            self.update_current_screen()

    def ask_for_pos_float(self, value_name):
        while True:
            try:
                value = float(input(f"Input {value_name}:\n> "))
                if value > 0:
                    return value
                self.error_output(f"Please enter a positive float.")
            except ValueError:
                self.error_output(f"Invalid input.")

    def ask_for_pos_int(self, value_name):
        while True:
            try:
                value = int(input(f"Input {value_name}:\n> "))
                if value > 0:
                    return value
                self.error_output(f"Please enter a positive integer.")
            except ValueError:
                self.error_output(f"Invalid input.")

def check_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def main():
    #Create user and controller
    user = User()
    controller = Controller(user)

    #Make our food
    cheetos = Item("flaming hot cheetos", 5, 10)
    lays_tomato = Item("lay's tomato chips", 2.5, 10)
    lays_spicy = Item("lay's spicy chips", 2.5, 10)
    chocolate = Item("chocolate", 10, 10)
    sw_egg = Item("egg sandwich", 15, 10)
    sw_turkey = Item("turkey sandwich", 15, 10)

    #Make our beverages
    cola = Item("cola", 2.5, 10)
    sprite = Item("sprite", 2.5, 10)
    water = Item("water", 1, 10)
    redbull = Item("redbull", 10, 10)
    j_apple = Item("apple juice", 2, 10)
    j_grape = Item("grape juice", 2, 10)

    #Add the items to our vending machines
    controller.add_item(controller.vending_machine, cheetos, lays_tomato, lays_spicy, sw_egg, sw_turkey, chocolate)
    controller.add_item(controller.bev_vending_machine, cola, sprite, water, redbull, j_apple, j_grape)

    while True:
        current_screen = controller.screen_handler.get_current_screen()
        #Check if we should exit
        if isinstance(current_screen, ExitScreen):
            #Confirmation
            if controller.get_confirmation("Do you really want to leave?"):
                break
            #If we aren't exiting go back to home screen
            #The confirmation screen automatically returns to the previous screen (exit) do it one more time for home.
            controller.go_back()
            continue

        user_input = controller.screen_handler.screen_viewer.get_input("Awaiting Input:")

        if not check_int(user_input):
            controller.error_output("Please enter a number.")
            controller.update_current_screen()
            continue

        user_input = int(user_input)

        #Handle buying if its a buy screen, 0 is used to return so ignore it
        if isinstance(current_screen, BuyScreen) and user_input != 0:
            #buy screen gives you the vending machine.
            vending_machine = current_screen.vending_machine
            controller.purchase(user_input, vending_machine)
        else:
            controller.navigate(user_input)
            #If it isn't a buy screen use it to navigate

if __name__ == "__main__":
    main()
