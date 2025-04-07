# Importando bibliotecas
import glfw
from OpenGL.GL import *
import glm
from asserts.camera import Camera
from asserts.shader import Shader
from asserts.model import Model
from asserts.camera import CameraMovement

# Configurações da tela
WIDTH, HEIGHT = 1200, 800

# Camera
camera = Camera(glm.vec3(3750.0, 1500.0, -1000.0))
ultimo_x = WIDTH / 2.0
ultimo_y = HEIGHT / 2.0
first_mouse = True
modo_camera = False

# Tempo
intervalo_entre_frames = 0.0
tempo_ultimo_frame = 0.0
tempo = 0.0

def framebuffer_size_callback(window, width, height):
    """
    Classe para quando a janela é redimensionada, atualizar a viewport do OpenGL
    """
    glViewport(0, 0, width, height)

def mouse_callback(window, xpos, ypos):
    """
    Classe que processa o movimento do mouse.
    """
    global ultimo_x, ultimo_y, first_mouse

    # Verifica se o mouse foi movido
    if first_mouse:
        ultimo_x = xpos
        ultimo_y = ypos
        first_mouse = False

    xoffset = xpos - ultimo_x
    yoffset = ultimo_y - ypos  # invertido pois Y cresce de baixo pra cima no OpenGL
    ultimo_x = xpos
    ultimo_y = ypos

    # Processa o movimento do mouse
    camera.process_mouse_movement(xoffset, yoffset)

def scroll_callback(window, xoffset, yoffset):
    """
    Classe que processa o scroll do mouse.
    """
    camera.process_mouse_scroll(yoffset)

def process_input(window):
    """
    Classe que processa as entradas do teclado
    """
    global intervalo_entre_frames, modo_camera

    # Verifica se Shift está pressionado
    multiplier = 1.0
    if (glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS or
        glfw.get_key(window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS):
        multiplier = 5.0  # Fator de velocidade extra

    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)
        
    if glfw.get_key(window, glfw.KEY_M) == glfw.PRESS:
        modo_camera = not modo_camera
        if modo_camera:
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        else:
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    # Movimentação WASD
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.FORWARD, intervalo_entre_frames * multiplier)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.BACKWARD, intervalo_entre_frames * multiplier)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.LEFT, intervalo_entre_frames * multiplier)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.RIGHT, intervalo_entre_frames * multiplier)
    

def main():
    global tempo_ultimo_frame, intervalo_entre_frames, tempo

    # Inicializa o GLFW
    if not glfw.init():
        print("Falha ao inicializar GLFW")
        return

    # Configura versão do OpenGL e perfil
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # Cria a janela
    window = glfw.create_window(WIDTH, HEIGHT, "Sistema Solar em Python", None, None)
    if not window:
        print("Falha ao criar a janela GLFW")
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # Modo do mouse desabilitado => escondido e "preso" ao centro
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # Ativa depth test no OpenGL
    glEnable(GL_DEPTH_TEST)

    # Carrega shaders
    planetas_shader = Shader("asserts/shaders/model_loading.vert", "asserts/shaders/model_loading.frag")
    cor_shader      = Shader("asserts/shaders/model_loading.vert", "asserts/shaders/color.frag")
    light_shader    = Shader("asserts/shaders/lightSun.vert", "asserts/shaders/lightSun.frag")

    # Carrega modelos
    Sun      = Model("asserts/models/Sun/Sun.obj")
    Mercury  = Model("asserts/models/Mercury/Mercury.obj")
    Venus    = Model("asserts/models/Venus/Venus.obj")
    Earth    = Model("asserts/models/Earth/Earth.obj")
    Moon     = Model("asserts/models/Moon/Moon.obj")
    Mars     = Model("asserts/models/Mars/Mars.obj")
    Jupiter  = Model("asserts/models/Jupiter/Jupiter.obj")
    Saturn   = Model("asserts/models/Saturn/Saturn.obj")
    Uranus   = Model("asserts/models/Uranus/Uranus.obj")
    Neptune  = Model("asserts/models/Neptune/Neptune.obj")

    # Background
    Stars    = Model("asserts/models/Stars/Stars.obj")
    Orbita   = Model("asserts/models/Line/Line.obj")
    Orbita2  = Model("asserts/models/Line2/Line2.obj")
    Orbita3  = Model("asserts/models/Line3/Line3.obj")

    # Loop principal
    while not glfw.window_should_close(window):
        # Tempo e delta_time
        frame_atual = glfw.get_time()
        intervalo_entre_frames = frame_atual - tempo_ultimo_frame
        tempo_ultimo_frame = frame_atual
        tempo += intervalo_entre_frames

        # Input
        process_input(window)

        # Limpa buffers
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Configura matrizes de projeção e view
        projecao = glm.perspective(glm.radians(camera.Zoom), float(WIDTH)/float(HEIGHT), 0.1, 25000.0)
        visualizacao = camera.get_view_matrix()

        # ----- Desenho do Background com planetas_shader -----
        planetas_shader.use()
        planetas_shader.set_mat4("projection", projecao)
        planetas_shader.set_mat4("view", visualizacao)

        # Background
        background_mat = glm.mat4(1.0)
        background_mat = glm.translate(background_mat, glm.vec3(0.0, 0.0, 0.0))
        background_mat = glm.scale(background_mat, glm.vec3(4000, 4000, 4000))
        planetas_shader.set_mat4("model", background_mat)
        Stars.draw(planetas_shader)

        # Sol
        sun_mat = glm.mat4(1.0)
        sun_mat = glm.scale(sun_mat, glm.vec3(50, 50, 50))
        planetas_shader.set_mat4("model", sun_mat)
        Sun.draw(planetas_shader)

        # ----- Desenho dos planetas com light_shader -----
        light_shader.use()
        light_shader.set_mat4("projection", projecao)
        light_shader.set_mat4("view", visualizacao)

        # Mercury
        mercury = glm.mat4(1.0)
        mercury = glm.translate(mercury, glm.vec3(0.0, 0.0, 0.0))
        mercury = glm.scale(mercury, glm.vec3(10, 10, 10))
        mercury = glm.rotate(mercury, tempo, glm.vec3(0,1,0))
        mercury = glm.translate(mercury, glm.vec3(0.0, 0.0, 17.5))
        light_shader.set_mat4("model", mercury)
        Mercury.draw(light_shader)

        # Venus
        venus = glm.mat4(1.0)
        venus = glm.translate(venus, glm.vec3(0.0, 0.0, 0.0))
        venus = glm.scale(venus, glm.vec3(15,15,15))
        venus = glm.rotate(venus, tempo/2, glm.vec3(0,1,0))
        venus = glm.translate(venus, glm.vec3(0,0,22))
        light_shader.set_mat4("model", venus)
        Venus.draw(light_shader)

        # Earth
        earth = glm.mat4(1.0)
        earth = glm.translate(earth, glm.vec3(0.0, 0.0, 0.0))
        earth = glm.scale(earth, glm.vec3(17,17,17))
        earth = glm.rotate(earth, tempo/6, glm.vec3(0,1,0))
        earth = glm.translate(earth, glm.vec3(0,0,26))
        light_shader.set_mat4("model", earth)
        Earth.draw(light_shader)
        # Moon (da Terra)
        earth = glm.scale(earth, glm.vec3(0.5,0.5,0.5))
        earth = glm.rotate(earth, tempo/6, glm.vec3(0,1,0))
        earth = glm.translate(earth, glm.vec3(-3,0,8))
        light_shader.set_mat4("model", earth)
        Moon.draw(light_shader)

        # Mars
        mars = glm.mat4(1.0)
        mars = glm.translate(mars, glm.vec3(0,0,0))
        mars = glm.scale(mars, glm.vec3(13,13,13))
        mars = glm.rotate(mars, tempo / 6.5, glm.vec3(0,1,0))
        mars = glm.translate(mars, glm.vec3(0,0,50))
        light_shader.set_mat4("model", mars)
        Mars.draw(light_shader)

        # Jupiter
        jupiter = glm.mat4(1.0)
        jupiter = glm.translate(jupiter, glm.vec3(0,0,0))
        jupiter = glm.scale(jupiter, glm.vec3(45,45,45))
        jupiter = glm.rotate(jupiter, tempo/8, glm.vec3(0,1,0))
        jupiter = glm.translate(jupiter, glm.vec3(0,0,30))
        light_shader.set_mat4("model", jupiter)
        Jupiter.draw(light_shader)

        moon1 = jupiter
        moon2 = jupiter
        moon3 = jupiter
        moon4 = jupiter
        moon5 = jupiter
        moon6 = jupiter
        moon7 = jupiter
        moon8 = jupiter

        # Luas de Júpiter
        jupiter = glm.scale(jupiter, glm.vec3(0.1,0.1,0.1))
        jupiter = glm.rotate(jupiter, tempo/4, glm.vec3(0,1,0))
        jupiter = glm.translate(jupiter, glm.vec3(-40,0,10))
        light_shader.set_mat4("model", jupiter)
        Moon.draw(light_shader)

        moon1 = glm.scale(moon1, glm.vec3(0.1,0.1,0.1))
        moon1 = glm.rotate(moon1, tempo/4, glm.vec3(0,1,0))
        moon1 = glm.translate(moon1, glm.vec3(-30, 15, -20))
        light_shader.set_mat4("model", moon1)
        Moon.draw(light_shader)

        moon2 = glm.scale(moon2, glm.vec3(0.1,0.1,0.1))
        moon2 = glm.rotate(moon2, tempo/4, glm.vec3(0,1,0))
        moon2 = glm.translate(moon2, glm.vec3(-25, -10, 10))
        light_shader.set_mat4("model", moon2)
        Moon.draw(light_shader)

        moon3 = glm.scale(moon3, glm.vec3(0.1,0.1,0.1))
        moon3 = glm.rotate(moon3, tempo/4, glm.vec3(0,1,0))
        moon3 = glm.translate(moon3, glm.vec3(-25, 10, 20))
        light_shader.set_mat4("model", moon3)
        Moon.draw(light_shader)

        moon4 = glm.scale(moon4, glm.vec3(0.1,0.1,0.1))
        moon4 = glm.rotate(moon4, tempo/4, glm.vec3(0,1,0))
        moon4 = glm.translate(moon4, glm.vec3(-40, -15, 10))
        light_shader.set_mat4("model", moon4)
        Moon.draw(light_shader)

        moon5 = glm.scale(moon5, glm.vec3(0.1,0.1,0.1))
        moon5 = glm.rotate(moon5, tempo / 4, glm.vec3(0,1,0))
        moon5 = glm.translate(moon5, glm.vec3(-20, 5, 5))
        light_shader.set_mat4("model", moon5)
        Moon.draw(light_shader)

        moon6 = glm.scale(moon6, glm.vec3(0.1,0.1,0.1))
        moon6 = glm.rotate(moon6, tempo / 4, glm.vec3(0,1,0))
        moon6 = glm.translate(moon6, glm.vec3(-22, -3, 3))
        light_shader.set_mat4("model", moon6)
        Moon.draw(light_shader)

        moon7 = glm.scale(moon7, glm.vec3(0.1,0.1,0.1))
        moon7 = glm.rotate(moon7, tempo / 4, glm.vec3(0,1,0))
        moon7 = glm.translate(moon7, glm.vec3(-28, 2, 2))
        light_shader.set_mat4("model", moon7)
        Moon.draw(light_shader)

        moon8 = glm.scale(moon8, glm.vec3(0.1,0.1,0.1))
        moon8 = glm.rotate(moon8, tempo / 4, glm.vec3(0,1,0))
        moon8 = glm.translate(moon8, glm.vec3(-30, -1, 1))
        light_shader.set_mat4("model", moon8)
        Moon.draw(light_shader)

        # Saturn
        saturn = glm.mat4(1.0)
        saturn = glm.translate(saturn, glm.vec3(0,0,0))
        saturn = glm.scale(saturn, glm.vec3(42,42,42))
        saturn = glm.rotate(saturn, tempo/10, glm.vec3(0,1,0))
        saturn = glm.translate(saturn, glm.vec3(0,0,60))
        light_shader.set_mat4("model", saturn)
        Saturn.draw(light_shader)
        # Saturno (anéis)
        saturn = glm.scale(saturn, glm.vec3(4,4,4))
        saturn = glm.rotate(saturn, float(glfw.get_time())-60, glm.vec3(0,1,0))
        saturn = glm.translate(saturn, glm.vec3(0,0,0))
        light_shader.set_mat4("model", saturn)
        Orbita3.draw(light_shader)

        # Uranus
        uranus = glm.mat4(1.0)
        uranus = glm.translate(uranus, glm.vec3(0,0,0))
        uranus = glm.scale(uranus, glm.vec3(30,30,30))
        uranus = glm.rotate(uranus, tempo/12, glm.vec3(0,1,0))
        uranus = glm.translate(uranus, glm.vec3(0,0,120))
        light_shader.set_mat4("model", uranus)
        Uranus.draw(light_shader)

        # Neptune
        neptune = glm.mat4(1.0)
        neptune = glm.translate(neptune, glm.vec3(0,0,0))
        neptune = glm.scale(neptune, glm.vec3(29,29,29))
        neptune = glm.rotate(neptune, tempo/14, glm.vec3(0,1,0))
        neptune = glm.translate(neptune, glm.vec3(0,0,180))
        light_shader.set_mat4("model", neptune)
        Neptune.draw(light_shader)
        neptune = glm.scale(neptune, glm.vec3(4,4,4))
        neptune = glm.rotate(neptune, tempo/4, glm.vec3(0,0,1))
        neptune = glm.translate(neptune, glm.vec3(0,0,0))
        light_shader.set_mat4("model", neptune)
        Orbita3.draw(light_shader)

        # as órbitas (cor_shader)
        cor_shader.use()
        cor_shader.set_mat4("projection", projecao)
        cor_shader.set_mat4("view", visualizacao)
        
        orbitaMercurio = glm.mat4(1.0)
        orbitaMercurio = glm.translate(orbitaMercurio, glm.vec3(0,0,0))
        orbitaMercurio = glm.scale(orbitaMercurio, glm.vec3(180,180,180))
        cor_shader.set_mat4("model", orbitaMercurio)
        Orbita.draw(cor_shader)

        orbitaVenus = glm.mat4(1.0)
        orbitaVenus = glm.translate(orbitaVenus, glm.vec3(0,0,0))
        orbitaVenus = glm.scale(orbitaVenus, glm.vec3(350,350,350))
        cor_shader.set_mat4("model", orbitaVenus)
        Orbita.draw(cor_shader)

        orbitaTerra = glm.mat4(1.0)
        orbitaTerra = glm.translate(orbitaTerra, glm.vec3(0,0,0))
        orbitaTerra = glm.scale(orbitaTerra, glm.vec3(450,450,450))
        cor_shader.set_mat4("model", orbitaTerra)
        Orbita.draw(cor_shader)

        orbitaMarte = glm.mat4(1.0)
        orbitaMarte = glm.translate(orbitaMarte, glm.vec3(0,0,0))
        orbitaMarte = glm.scale(orbitaMarte, glm.vec3(655,655,655))
        cor_shader.set_mat4("model", orbitaMarte)
        Orbita.draw(cor_shader)

        orbitaJupiter = glm.mat4(1.0)
        orbitaJupiter = glm.translate(orbitaJupiter, glm.vec3(0,0,0))
        orbitaJupiter = glm.scale(orbitaJupiter, glm.vec3(1350,1350,1350))
        cor_shader.set_mat4("model", orbitaJupiter)
        Orbita.draw(cor_shader)

        orbitaSaturno = glm.mat4(1.0)
        orbitaSaturno = glm.translate(orbitaSaturno, glm.vec3(0,0,0))
        orbitaSaturno = glm.scale(orbitaSaturno, glm.vec3(2550,2550,2550))
        cor_shader.set_mat4("model", orbitaSaturno)
        Orbita.draw(cor_shader)

        orbitaUrano = glm.mat4(1.0)
        orbitaUrano = glm.translate(orbitaUrano, glm.vec3(0,0,0))
        orbitaUrano = glm.scale(orbitaUrano, glm.vec3(3650,3650,3650))
        cor_shader.set_mat4("model", orbitaUrano)
        Orbita.draw(cor_shader)

        orbitaNetuno = glm.mat4(1.0)
        orbitaNetuno = glm.translate(orbitaNetuno, glm.vec3(0,0,0))
        orbitaNetuno = glm.scale(orbitaNetuno, glm.vec3(5300,5300,5300))
        cor_shader.set_mat4("model", orbitaNetuno)
        Orbita.draw(cor_shader)

        # Limpa a tela e troca os buffers
        glfw.swap_buffers(window)
        glfw.poll_events()

    # Pede para a GLFW destruir a janela
    glfw.terminate()

# Chama a função principal
if __name__ == "__main__":
    main()