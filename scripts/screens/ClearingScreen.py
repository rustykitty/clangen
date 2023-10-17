import pygame
import pygame_gui

from .Screens import Screens
from scripts.cat.cats import Cat
from scripts.game_structure.image_button import UISpriteButton, UIImageButton, UITextBoxTweaked
from scripts.utility import get_text_box_theme, scale, shorten_text_to_fit
from scripts.game_structure.game_essentials import game, MANAGER


class ClearingScreen(Screens):
    cat_buttons = {}
    conditions_hover = {}
    cat_names = []

    def __init__(self, name=None):
        super().__init__(name)
        self.help_button = None
        self.log_box = None
        self.log_title = None
        self.log_tab = None
        self.cats_tab = None
        self.nutrition_title = None
        self.satisfied_tab = None
        self.satisfied_cats = None
        self.hungry_tab = None
        self.hungry_cats = None
        self.info_messages = None
        self.cat_bg = None
        self.last_page = None
        self.next_page = None
        self.feed_button = None
        self.pile_base = None
        self.focus_cat = None
        self.focus_cat_object = None
        self.focus_info = None
        self.focus_name = None
        self.current_page = None
        self.back_button = None

        self.tab_showing = self.hungry_tab
        self.tab_list = self.hungry_cats
        self.pile_size = "#freshkill_pile_average"

        self.open_tab = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('camp screen')
            elif event.ui_element == self.feed_button:
                # TODO: feed the current cat
                print("TODO")
            elif event.ui_element == self.next_page:
                self.current_page += 1
                self.update_nutrition_cats()
            elif event.ui_element == self.last_page:
                self.current_page -= 1
                self.update_nutrition_cats()
            elif event.ui_element == self.hungry_tab:
                self.tab_showing.enable()
                self.tab_list = self.hungry_cats
                self.tab_showing = self.hungry_tab
                self.hungry_tab.disable()
                self.update_nutrition_cats()
            elif event.ui_element == self.satisfied_tab:
                self.tab_showing.enable()
                self.tab_list = self.satisfied_cats
                self.tab_showing = self.satisfied_tab
                self.satisfied_tab.disable()
                self.update_nutrition_cats()
            elif event.ui_element in self.cat_buttons.values() and event.ui_element != self.focus_cat:
                self.focus_cat_object = event.ui_element.return_cat_object()
                self.update_focus_cat()
            elif event.ui_element == self.cats_tab:
                self.open_tab = "cats"
                self.cats_tab.disable()
                self.log_tab.enable()
                self.handle_tab_toggles()
            elif event.ui_element == self.log_tab:
                self.open_tab = "log"
                self.log_tab.disable()
                self.cats_tab.enable()
                self.handle_tab_toggles()

    def screen_switches(self):
        self.hide_menu_buttons()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        self.feed_button = UIImageButton(scale(pygame.Rect((1300, 600), (68, 68))), "", object_id="#arrow_right_button"
                                      , manager=MANAGER)
        self.feed_button.hide()

        if game.clan.game_mode != 'classic':
            self.help_button = UIImageButton(scale(pygame.Rect(
                (1450, 50), (68, 68))),
                "",
                object_id="#help_button", manager=MANAGER,
                tool_tip_text="Your clan will catch some amount of prey over each timeskip, but successful hunting patrols are the most "
                              "important source of freshkill. You can see what was consumed and catched in the Log below! "
                              "Freshkill can't be stored endlessly, after four moons prey will rot and will be thrown away."
                              "<br><br>"
                              "Feeding the Clan is very important, therefore cats will be fed before any changes to rank. "
                              "Hover your mouse over the pile to see the current amount and the needed amount of prey of your Clan!",

            )
            self.last_page = UIImageButton(scale(pygame.Rect((660, 1272), (68, 68))), "", object_id="#arrow_left_button"
                                           , manager=MANAGER)
            self.next_page = UIImageButton(scale(pygame.Rect((952, 1272), (68, 68))), "",
                                           object_id="#arrow_right_button"
                                           , manager=MANAGER)

            self.nutrition_title = pygame_gui.elements.UITextBox(
                "Nutrition Overview",
                scale(pygame.Rect((281, 820), (400, 60))),
                object_id=get_text_box_theme("#text_box_40_horizcenter"), manager=MANAGER
            )
            self.log_title = pygame_gui.elements.UITextBox(
                "Freshkill Pile Log",
                scale(pygame.Rect((281, 820), (400, 60))),
                object_id=get_text_box_theme("#text_box_40_horizcenter"), manager=MANAGER
            )
            self.log_title.hide()
            self.cat_bg = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                            ((280, 880), (1120, 400))),
                                                      pygame.image.load(
                                                          "resources/images/sick_hurt_bg.png").convert_alpha()
                                                      , manager=MANAGER)
            self.cat_bg.disable()
            log_text = game.freshkill_event_list.copy()
            self.log_box = pygame_gui.elements.UITextBox(
                f"{f'<br>-------------------------------<br>'.join(log_text)}<br>",
                scale(pygame.Rect
                      ((300, 900), (1080, 360))),
                object_id="#text_box_26_horizleft_verttop_pad_14_0_10", manager=MANAGER
            )
            self.log_box.hide()
            self.cats_tab = UIImageButton(scale(pygame.Rect
                                                ((218, 924), (68, 150))),
                                          "",
                                          object_id="#hurt_sick_cats_button", manager=MANAGER
                                          )
            self.cats_tab.disable()
            self.log_tab = UIImageButton(scale(pygame.Rect
                                               ((218, 1104), (68, 128))),
                                         "",
                                         object_id="#med_den_log_button", manager=MANAGER
                                         )
            self.hungry_tab = UIImageButton(scale(pygame.Rect
                                                   ((920, 818), (224, 70))),
                                             "",
                                             object_id="#out_den_tab", manager=MANAGER)
            self.satisfied_tab = UIImageButton(scale(pygame.Rect
                                                 ((1174, 818), (140, 70))),
                                           "",
                                           object_id="#minor_tab", manager=MANAGER)
            self.tab_showing = self.hungry_tab


            self.satisfied_cats = []
            self.hungry_cats = []
            for the_cat in Cat.all_cats_list:
                if not the_cat.dead and not the_cat.outside:
                    if (the_cat.injuries or the_cat.illnesses):
                        if "starving" in the_cat.illnesses.keys() or "malnourished" in the_cat.illnesses.keys():
                            self.hungry_cats.append(the_cat)
                    else:
                        self.satisfied_cats.append(the_cat)
            self.tab_list = self.hungry_cats
            self.current_page = 1
            self.update_nutrition_cats()

        self.update_focus_cat()

        self.info_messages = UITextBoxTweaked(
            "",
            scale(pygame.Rect((216, 620), (1200, 160))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_vertcenter"),
            line_spacing=1
        )


        information_display = []

        current_prey_amount = game.clan.freshkill_pile.total_amount
        needed_amount = game.clan.freshkill_pile.amount_food_needed()
        warrior_need = game.config["freshkill"]["prey_requirement"]["warrior"]
        warrior_amount = int(current_prey_amount / warrior_need) 
        general_text = f"Up to {warrior_amount} warriors can be fed with this amount of prey."

        concern_text = "This should not appear."
        if current_prey_amount == 0:
            concern_text = "The freshkill pile is empty, the Clan desperately needs prey!"
            self.pile_size = "#freshkill_pile_empty"
        elif 0 < current_prey_amount <= needed_amount / 2:
            concern_text = "The freshkill pile can't even fed half of the Clan. Hunting patrols should be organized imitatively."
            self.pile_size = "#freshkill_pile_verylow"
        elif needed_amount / 2 < current_prey_amount <= needed_amount:
            concern_text = "Only half of the Clan can be fed currently. Hunting patrols should be organized."
            self.pile_size = "#freshkill_pile_low"
        elif needed_amount < current_prey_amount <= needed_amount * 1.5:
            concern_text = "Every mouth of the Clan can be fed, but some more prey would not harm."
            self.pile_size = "#freshkill_pile_average"
        elif needed_amount * 1.5 < current_prey_amount <= needed_amount * 2.5:
            concern_text = "The freshkill pile is overflowing and the Clan can feast!"
            self.pile_size = "#freshkill_pile_good"
        elif needed_amount * 2.5 < current_prey_amount:
            concern_text = "StarClan has blessed the Clan with plentiful prey and the leader sends their thanks to Silverpelt."
            self.pile_size = "#freshkill_pile_full"

        information_display.append(general_text)
        information_display.append(concern_text)
        self.info_messages.set_text("<br>".join(information_display))
        self.draw_pile()

    def handle_tab_toggles(self):
        if self.open_tab == "cats":
            self.log_title.hide()
            self.log_box.hide()

            self.nutrition_title.show()
            self.last_page.show()
            self.next_page.show()
            self.hungry_tab.show()
            self.satisfied_tab.show()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].show()
            for x in range(len(self.cat_names)):
                self.cat_names[x].show()
            for button in self.conditions_hover:
                self.conditions_hover[button].show()
        elif self.open_tab == "log":
            self.nutrition_title.hide()
            self.last_page.hide()
            self.next_page.hide()
            self.hungry_tab.hide()
            self.satisfied_tab.hide()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].hide()
            for x in range(len(self.cat_names)):
                self.cat_names[x].hide()
            for button in self.conditions_hover:
                self.conditions_hover[button].hide()

            self.log_title.show()
            self.log_box.show()

    def update_focus_cat(self):
        if not self.focus_cat_object:
            return
        if self.focus_cat:
            self.focus_cat.kill()
        if self.focus_info:
            self.focus_info.kill()
        if self.focus_name:
            self.focus_name.kill()

        # if the nutrition is full grey the feed button out
        self.feed_button.show()
        nutrition_info = game.clan.freshkill_pile.nutrition_info
        p = 100
        if self.focus_cat_object.ID in nutrition_info:
            p = int(nutrition_info[self.focus_cat_object.ID].percentage)
        if p >= 100:
            self.feed_button.disable()
        else:
            self.feed_button.enable()


        name = str(self.focus_cat_object.name)
        short_name = shorten_text_to_fit(name, 275, 30)
        self.focus_name = pygame_gui.elements.ui_label.UILabel(
            scale(pygame.Rect ((1100, 150), (450, 60))),
            short_name,
            object_id=get_text_box_theme("#text_box_30_horizcenter"), 
            manager=MANAGER
        )
        self.focus_info = UITextBoxTweaked(
            "",
            scale(pygame.Rect((1180, 190), (300, 240))),
            object_id=get_text_box_theme("#text_box_22_horizcenter"),
            line_spacing=1, manager=MANAGER
        )
        self.focus_cat = UISpriteButton(
            scale(pygame.Rect((1180, 290), (300, 300))),
            self.focus_cat_object.sprite,
            cat_object=self.focus_cat_object,
            manager=MANAGER
        )
        info_list = [self.focus_cat_object.skills.skill_string(short=True)]
        nutrition_info = game.clan.freshkill_pile.nutrition_info
        if self.focus_cat_object.ID in nutrition_info:
            info_list.append("nutrition: " + str(int(nutrition_info[self.focus_cat_object.ID].percentage)) + "%")
        work_status = "This cat can work"
        if self.focus_cat_object.not_working():
            work_status = "This cat isn't able to work"
        info_list.append(work_status)

        self.focus_info.set_text("<br>".join(info_list))

    def update_nutrition_cats(self):
        """
        set tab showing as either self.hungry_cats or self.satisfied_cats; whichever one you want to
        display and update
        """
        self.clear_cat_buttons()

        tab_list = self.tab_list

        if not tab_list:
            all_pages = []
        else:
            all_pages = self.chunks(tab_list, 10)

        if self.current_page > len(all_pages):
            if len(all_pages) == 0:
                self.current_page = 1
            else:
                self.current_page = len(all_pages)

        # Check for empty list (no cats)
        if all_pages:
            self.display_cats = all_pages[self.current_page - 1]
        else:
            self.display_cats = []

        # Update next and previous page buttons
        if len(all_pages) <= 1:
            self.next_page.disable()
            self.last_page.disable()
        else:
            if self.current_page >= len(all_pages):
                self.next_page.disable()
            else:
                self.next_page.enable()

            if self.current_page <= 1:
                self.last_page.disable()
            else:
                self.last_page.enable()

        pos_x = 350
        pos_y = 920
        i = 0
        for cat in self.display_cats:
            condition_list = []
            if cat.illnesses:
                if "starving" in cat.illnesses.keys():
                    condition_list.append("starving")
                    nutrition_info = game.clan.freshkill_pile.nutrition_info
                    if cat.ID in nutrition_info:
                        p = int(nutrition_info[cat.ID].percentage)
                        condition_list.append(f" nutrition: {p}%")
                elif "malnourished" in cat.illnesses.keys():
                    condition_list.append("malnourished")
                    nutrition_info = game.clan.freshkill_pile.nutrition_info
                    if cat.ID in nutrition_info:
                        p = int(nutrition_info[cat.ID].percentage)
                        condition_list.append(f" nutrition: {p}%")
            conditions = ",<br>".join(condition_list) if len(condition_list) > 0 else None

            self.cat_buttons["able_cat" + str(i)] = UISpriteButton(scale(pygame.Rect
                                                                         ((pos_x, pos_y), (100, 100))),
                                                                   cat.sprite,
                                                                   cat_object=cat,
                                                                   manager=MANAGER,
                                                                   tool_tip_text=conditions,
                                                                   starting_height=2)


            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 185, 30)
            self.cat_names.append(pygame_gui.elements.UITextBox(short_name,
                                                                scale(
                                                                    pygame.Rect((pos_x - 60, pos_y + 100), (220, 60))),
                                                                object_id="#text_box_30_horizcenter", manager=MANAGER))

            pos_x += 200
            if pos_x >= 1340:
                pos_x = 350
                pos_y += 160
            i += 1

    def draw_pile(self):
        current_prey_amount = game.clan.freshkill_pile.total_amount
        needed_amount = game.clan.freshkill_pile.amount_food_needed()
        hover_display = f"<b>Current amount:</b> {current_prey_amount}<br><b>Needed amount:</b> {needed_amount}"
        self.pile_base = UIImageButton(scale(pygame.Rect
                                            ((500, 50), (600, 600))),
                                      "",
                                      object_id=self.pile_size,
                                      tool_tip_text=hover_display, manager=MANAGER
                                      )

        # TODO: change pile drawing based on size

    def exit_screen(self):
        self.info_messages.kill()
        self.feed_button.kill()
        self.pile_base.kill()
        self.focus_cat_object = None
        if self.focus_info:
            self.focus_info.kill()
        if self.focus_name:
            self.focus_name.kill()
        self.back_button.kill()
        if game.clan.game_mode != 'classic':
            self.help_button.kill()
            self.cat_bg.kill()
            self.last_page.kill()
            self.next_page.kill()
            self.hungry_tab.kill()
            self.satisfied_tab.kill()
            self.clear_cat_buttons()
            self.nutrition_title.kill()
            self.cats_tab.kill()
            self.log_tab.kill()
            self.log_title.kill()
            self.log_box.kill()
        if self.focus_cat:
            self.focus_cat.kill()

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]

    def clear_cat_buttons(self):
        for cat in self.cat_buttons:
            self.cat_buttons[cat].kill()
        for button in self.conditions_hover:
            self.conditions_hover[button].kill()
        for x in range(len(self.cat_names)):
            self.cat_names[x].kill()

        self.cat_names = []
        self.cat_buttons = {}
