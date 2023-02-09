from sense_hat import SenseHat
from time import sleep
import datetime
from sense_hat_matrix.Graph import Graph
from sense_hat_matrix.GraphUtil import temp_colour
from sense_hat_matrix.GraphUtil import rescale
from State import StateManager, State


class WeatherStation:

    def __init__(self, minimum_temperature, maximum_temperature):
        self.sense = SenseHat()
        self.white = (200, 200, 200)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.min_temp = minimum_temperature
        self.max_temp = maximum_temperature
        self.g = Graph(self.min_temp, self.max_temp)

    def __compensated_temperature(self):
        return self.sense.get_temperature() - 1

    def __temperature(self):
        temp = self.__compensated_temperature()
        scaled_temp = rescale(self.min_temp, self.max_temp, temp) - 1
        col = temp_colour(scaled_temp, self.blue, self.green, self.red)
        self.sense.show_message(str(round(temp, 1)) + "C", 0.1, col)

    def __humidity(self):
        hum = self.sense.get_humidity()
        self.sense.show_message(str(round(hum, 1)) + "%", 0.1, self.white)

    def __graph(self):
        temp = self.__compensated_temperature()
        pixels = self.g.render(temp)
        self.sense.set_pixels(pixels)
        sleep(10)

    def __time(self):
        dtNow = datetime.datetime.now()
        timeNow = dtNow.strftime('%H:%M:%S.%Z')
        self.sense.show_message(timeNow, 0.1, self.white)

    def run(self):
        self.sense.set_rotation(180)
        self.sense.low_light = True
        # sense.gamma = [1] * 32
        self.sense.clear()

        temperature_state = State(self.__temperature)
        humidity_state = State(self.__humidity)
        graph_state = State(self.__graph)
        time_state = State(self.__time)
        state_manager = StateManager([graph_state, temperature_state, humidity_state, time_state])

        loop_state = True
        try:
            while True:
                for event in self.sense.stick.get_events():
                    print("event", event)
                    if event.action == "pressed":
                        if event.direction == "middle":
                            loop_state = True  # reset to the normal screen cycle
                        elif event.direction == "right":
                            loop_state = False
                            state_manager.next()

                if loop_state:
                    state_manager.next()
                else:
                    state_manager.refresh()
                    sleep(2)
        except KeyboardInterrupt:
            self.sense.show_message("Bye!")
        except Exception as e:
            self.sense.clear()
            print("Error {0}".format(str(e.args[0])).encode("utf-8"))

        exit()
