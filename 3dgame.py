# pip install panda3d

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import WindowProperties, Point3
import math
from panda3d.core import AmbientLight, DirectionalLight, PointLight, Spotlight, PerspectiveLens, Vec4 , CollisionTraverser, CollisionHandlerPusher
from panda3d.core import CollisionNode, CollisionSphere, CollisionBox, Point3, CollisionPlane, Plane, Vec3
from direct.showbase import Audio3DManager

from direct.gui.OnscreenText import OnscreenText  # ⬅️
from panda3d.core import TextNode  # ⬅️
import time  # ⬅️
from direct.gui.DirectGui import DirectButton, DirectFrame  # ⬅️


from panda3d.core import loadPrcFileData
#loadPrcFileData('', 'win-size 1920 1080')

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #  Завантаження моделей
        self.player = loader.loadModel('models/Boy/Boy')
        self.player.reparentTo(render)
        self.player.setPos(50, 50, 12)
        self.player.setScale(3)

        self.model_room = loader.loadModel('models/bedroom/bedroom')
        self.model_room.setScale(3)
        self.model_room.reparentTo(render)
        self.model_room.setPos(50, 50, 0)
        self.model_room.setH(self.model_room.getH() - 0)

        self.model_sky = loader.loadModel('models/blue_sky_sphere/blue_sky_sphere')
        self.model_sky.setScale(0.07)
        self.model_sky.reparentTo(render)
        self.model_sky.setPos(0, 0, 0)
        self.model_sky.setH(self.model_sky.getH() - 20)

        self.model_Counter = loader.loadModel('models/Counter/Counter')
        self.model_Counter.setScale(2.4)
        self.model_Counter.reparentTo(render)
        self.model_Counter.setPos(30, 14, 7)
        self.model_Counter.setH(self.model_Counter.getH())

        self.model_Table = loader.loadModel('models/BigTable/BigTable')
        self.model_Table.setScale(2.4)
        self.model_Table.reparentTo(render)
        self.model_Table.setPos(75, 9, 7)
        self.model_Table.setH(self.model_Table.getH())

        self.model_room2 = loader.loadModel('models/rooom2/scene.gltf')
        self.model_room2.setScale(20)
        self.model_room2.reparentTo(render)
        self.model_room2.setPos(300, -200, -50)
        self.model_room2.setH(self.model_room2.getH())
        self.model_room2.setHpr(0, 90, 90)

        self.model_room2.setTexture(loader.loadTexture('models/rooom2/maps/render_baseColor.jpeg'))



        # --- 📦 КОЛІЗІЇ ---
        # Створюємо менеджер колізій
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        # Колізія для стійки
        counter_min_pt, counter_max_pt = self.model_Counter.getTightBounds()
        counter_solid_1 = CollisionBox(counter_min_pt, (counter_min_pt[0] + 6, counter_max_pt[1], counter_max_pt[2]))
        counter_solid_2 = CollisionBox(counter_min_pt, (counter_max_pt[0], counter_min_pt[1] + 6, counter_max_pt[2]))
        counter_node = CollisionNode('counter')
        counter_node.addSolid(counter_solid_1)
        counter_node.addSolid(counter_solid_2)
        counter_np = render.attachNewNode(counter_node)
        # Показати бокс (для тесту)
        #counter_np.show()  # побачити колізію

        # Колізія для гравця (сфера навколо моделі)
        player_min_pt, player_max_pt = self.player.getTightBounds()
        # print(player_min_pt, player_max_pt)
        radius = 1.75
        player_solid = CollisionSphere(0, 0, 0.1 , radius)  # трохи менше для точнос
        player_node = CollisionNode("player")
        player_node.addSolid(player_solid)
        player_nodepath = self.player.attachNewNode(player_node)
        # Щоб бачити колізію (лише для тесту)
        #player_nodepath.show()

        BigTable_min_pt, BigTable_max_pt = self.model_Table.getTightBounds()
        BigTable_solid = CollisionBox(BigTable_min_pt, (BigTable_max_pt[0], BigTable_min_pt[1] + 6, BigTable_max_pt[2]))
        BigTable_node = CollisionNode('BigTable')
        BigTable_node.addSolid(BigTable_solid)
        BigTable_np = render.attachNewNode(BigTable_node)

        #BigTable_np.show()



        #  Камера
        self.disableMouse()
        self.camera_distance = 35
        self.camera_height = 12
        self.camera_angle_h = 0

        # Сховати курсор
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        # Щоб камера могла рухатись від миші
        self.center_mouse()

        #  Клавіші
        self.keys = {"w": False, "s": False, "a": False, "d": False}
        for key in self.keys.keys():
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])

        # Мишка
        self.accept("escape", exit)  # Вихід по ESC
        self.taskMgr.add(self.update, "UpdateTask")
        self.taskMgr.add(self.mouse_update, "MouseTask")

        #Налаштовуємо світло
        ambient = AmbientLight('ambient')
        ambient.setColor(Vec4(0.6, 0.6, 0.6, 1))
        ambient_np = render.attachNewNode(ambient)
        render.setLight(ambient_np)
        # спрямоване світло (сонце)
        sun = DirectionalLight('sun')
        sun.setColor(Vec4(0.2, 0.2, 0.2, 1))  # теплий відтінок сонця
        sun_np = render.attachNewNode(sun)
        sun_np.setHpr(20, -70, 0)  # кут падіння світла
        render.setLight(sun_np)
        # точкове світло (лампочка)
        lamp = PointLight('lamp')
        lamp.setColor(Vec4(5, 2, 2, 1))  # тепле світло
        lamp_np = self.player.attachNewNode(lamp)
        lamp_np.setPos(0, 0, 0)  # положення лампи
        render.setLight(lamp_np)
        lamp.setAttenuation((1, 0.08, 0))

        # 4️⃣ Додаємо обробку зіткнень
        self.pusher.addCollider(player_nodepath, self.player)
        self.cTrav.addCollider(player_nodepath, self.pusher)


        # Створюємо звуковий менеджер
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)

        # Фонова музика
        self.bg_music = loader.loadMusic('sounds/a_new_beginning.mp3')
        self.bg_music.setLoop(True)
        self.bg_music.play()

        # Звук при дії
        #self.washing_sound = loader.loadSfx('sounds/386508-pub_glass_wash_rinse.wav')

        self.start_time = time.time()  # ⬅️
        self.timer_text = OnscreenText(
            text="Time: 0 s",
            pos=(-1.7, 0.9),
            scale=0.07,
            mayChange=True,
            align=TextNode.ALeft,  # вирівнювання
            fg=(1, 1, 1, 1),  # колір (білий)
        )

        # Додаємо задачу, яка виконується щотакту
        self.taskMgr.add(self.update_timer, "UpdateTimerTask")

        # ⬇️⬇️⬇️
        # прапорець меню
        self.menu_open = False

        # створюємо фрейм меню (фон меню)
        self.menu_frame = DirectFrame(
            frameColor=(1, 0, 0, 0.7),  # напівпрозорий чорний
            frameSize=(-0.5, 0.5, -0.5, 0.5),
            pos=(0, 0, 0)
        )
        self.menu_frame.hide()  # спочатку меню приховане

        # створюємо 3 кнопки в меню
        self.buttons = []
        for i in range(3):
            btn = DirectButton(
                text=f"Button {i + 1}",
                scale=0.07,
                pos=(0, 0, 0.2 - i * 0.2),
                parent=self.menu_frame,
                command=self.button_clicked,
                extraArgs=[i + 1]
            )
            self.buttons.append(btn)

        # прив’язуємо клавішу M
        self.accept("m", self.toggle_menu)

    #  Обробка клавіш
    def set_key(self, key, value):
        self.keys[key] = value

    #  Центрування миші
    def center_mouse(self):
        self.win.movePointer(0, int(self.win.getXSize()/2), int(self.win.getYSize()/2))

    #  Рух камери мишкою
    def mouse_update(self, task):
        if self.mouseWatcherNode.hasMouse():
            x = self.win.getPointer(0).getX()
            center_x = self.win.getXSize() / 2

            # Поворот за мишкою
            self.camera_angle_h -= (x - center_x) * 0.2

            # Повернути мишку назад до центру
            self.center_mouse()
        return Task.cont

    #  Ігровий цикл
    def update(self, task):
        speed = 0.5

        #  Рух гравця (WASD)
        if self.keys["w"]: self.player.setY(self.player, -speed)
        if self.keys["s"]: self.player.setY(self.player, speed)
        if self.keys["a"]: self.player.setX(self.player, speed)
        if self.keys["d"]: self.player.setX(self.player, -speed)

        #  Оберт гравця спиною до камери
        self.player.setH(self.camera_angle_h + 180) #  задає горизонтальний кут об’єкта (heading)

        #  оберт камери по колу
        px, py, pz = self.player.getPos()
        rad = math.radians(self.camera_angle_h)
        cam_x = px + self.camera_distance * math.sin(rad)
        cam_y = py - self.camera_distance * math.cos(rad)

        self.camera.setPos(cam_x, cam_y, pz + self.camera_height)
        self.camera.lookAt(self.player.getPos() + Point3(0, 0, 5))

        return Task.cont

    def update_timer(self, task):  # ⬅️⬅️⬅️
        elapsed = int(time.time() - self.start_time)
        self.timer_text.setText(f"Time: {elapsed} c")
        return Task.cont

        # ⬇️⬇️⬇️
        # прапорець меню
        self.menu_open = False

        # створюємо фрейм меню (фон меню)
        self.menu_frame = DirectFrame(
            frameColor=(1, 0, 0, 0.7),  # напівпрозорий чорний
            frameSize=(-0.5, 0.5, -0.5, 0.5),
            pos=(0, 0, 0)
        )
        self.menu_frame.hide()  # спочатку меню приховане

        # створюємо 3 кнопки в меню
        self.buttons = []
        for i in range(3):
            btn = DirectButton(
                text=f"Button {i + 1}",
                scale=0.07,
                pos=(0, 0, 0.2 - i * 0.2),
                parent=self.menu_frame,
                command=self.button_clicked,
                extraArgs=[i + 1]
            )
            self.buttons.append(btn)

        # прив’язуємо клавішу M
        self.accept("m", self.toggle_menu)

        # ⬇️⬇️⬇️
    def toggle_menu(self):
        """Відкрити/закрити меню"""
        if self.menu_open:
            # Показати курсор
            props = WindowProperties()
            props.setCursorHidden(True)
            self.win.requestProperties(props)
            self.menu_frame.hide()
            self.taskMgr.add(self.mouse_update, "MouseTask")
        else:
            # Сховати курсор
            props = WindowProperties()
            props.setCursorHidden(False)
            self.win.requestProperties(props)
            self.menu_frame.show()
            self.taskMgr.remove("MouseTask")
        self.menu_open = not self.menu_open

    # ⬇️⬇️⬇️
    def button_clicked(self, button_number):
        """Подія натискання кнопки"""
        print(f"Button {button_number} is clicked!")


base = Game()
base.run()
