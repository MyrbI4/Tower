
from pymodbus.client import ModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer
import time

def getRealTemp(temp):      #Функция для SRNE перевода температуры.7 бит - отвечает за знак
    return -(temp % 128) if (temp >= 0b10000000) else temp

#ID устройств

firstidslave = 1
secondlidslave = [1, 2]
thirdidslave = [1, 5, 6, 7, 11, 12]
ThirdNameSlave = ["1-1", "1-5", "1-6", "2-1", "2-5","2-6"]

#IP адреса преобразователей протокола Modbus RTU/ASCII в Modbus TCP
Thefirstclient = ModbusTcpClient('192.168.1.11', port=502, framer=ModbusRtuFramer)             #Метеостанция
Thesecondclient = ModbusTcpClient("192.168.1.12", port=503, framer=ModbusRtuFramer)            #PZEM подключенные к ветрогенераторам
Thethirdclient = ModbusTcpClient('192.168.1.12', port=502, framer=ModbusRtuFramer)             #Контроллеры заряда SRNE
while True:
    try:
        # Метеостанция '192.168.1.11', port=502
        result = Thefirstclient.read_holding_registers(50, 32, slave=firstidslave)          # Метеостанция регистры
        AverageTemp = (result.registers[0] + (result.registers[1] * 65536)) / 100                 # Температура средняя(ПТС)
        AveragePressure = (result.registers[2] + (result.registers[3] * 65536)) / 100             # Давление среднее
        Averagehumidity = (result.registers[4] + (result.registers[5] * 65536)) / 100             # Влажность средняя
        AverageWindspeed = (result.registers[6] + (result.registers[7] * 65536)) / 100            # Скорость ветра средняя
        AverageWinddirection = (result.registers[8] + (result.registers[9] * 65536)) / 100        # Направление ветра среднее
        MaxWindspeed = (result.registers[10] + (result.registers[11] * 65536)) / 100              # Максимум скорости ветра
        Recipitation = (result.registers[12] + (result.registers[13] * 65536)) / 100              # Осадки
        CurrentTemp = (result.registers[14] + (result.registers[15] * 65536)) / 100               # Температура текущая(ПТС)
        CurrentPressure = (result.registers[16] + (result.registers[17] * 65536)) / 100           # Давление текущее
        CurrentRecipitation = (result.registers[18] + (result.registers[19] * 65536)) / 100       # Влажность текущая
        CurrentWindspeed = (result.registers[20] + (result.registers[21] * 65536)) / 100          # Скорость ветра текущая
        CurrentWinddirection = (result.registers[22] + (result.registers[23] * 65536)) / 100      # Направление ветра текущее
        QuartzTemp = (result.registers[24] + (result.registers[25] * 65536)) / 100                # Температура кварца
        HumiditySensorTemp = (result.registers[26] + (result.registers[27] * 65536)) / 100        # Температура датчика влажности
        CodeTemp = (result.registers[28] + (result.registers[29] * 65536)) / 100                  # Код температуры
        QuartzFreq = (result.registers[30] + (result.registers[31] * 65536)) / 100                # Частота кварца
        print("The First client")                                                               # Для отладки
        print("Meteostation")
        print("AverageTemp:\t" + str(AverageTemp) + "°C")                                       # Для отладки вывод значений
        print("AveragePressure:\t" + str(AveragePressure) + "Pa")
        print("Averagehumidity:\t" + str(Averagehumidity) + "%")
        print("AverageWindspeed:\t" + str(AverageWindspeed) + "meters per second")
        print("AverageWinddirection:\t" + str(AverageWinddirection) + "°")
        print("MaxWindspeed:\t" + str(MaxWindspeed) + "meters per second")
        print("Recipitation:\t" + str(Recipitation))
        print("CurrentTemp:\t" + str(CurrentTemp) + "°C")
        print("CurrentPressure:\t" + str(CurrentPressure) + "Pa")
        print("CurrentRecipitation:\t" + str(CurrentRecipitation))
        print("CurrentWindspeed:\t" + str(CurrentWindspeed) + "meters per second")
        print("CurrentWinddirection:\t" + str(CurrentWinddirection) + "°")
        print("QuartzTemp:\t" + str(QuartzTemp) + "°C")
        print("HumiditySensorTemp:\t" + str(HumiditySensorTemp) + "°C")
        print("CodeTemp:\t" + str(CodeTemp))
        print("QuartzFreq:\t" + str(QuartzFreq) + "Hz")
        time.sleep(2)                                                                           # Задержка,для протокола Modbus необходима 2-3 секунды между сообщениями иначе ошибка "Отстуствие ответа"(в симуляторе работает без нее,на прототипе нужна проверка)
    except Exception as error:
        print("IP: 192.168.1.11 Port:502")
        print("Meteostation got problem")

    #PZEM "192.168.1.12", port=503
    for id in range(len(secondlidslave)):                                                              #Опрос всех PZEM находящихся на данной линии
        try:
            secresult = Thesecondclient.read_input_registers(0x0000, 6, slave=secondlidslave[id])      # Считываем регистры
            voltage = secresult.registers[0] / 100  # Напряжение
            amperage = secresult.registers[1] / 100  # Ток
            power = (secresult.registers[2] + secresult.registers[3] * 65536) / 10  # Мощность
            print("The Second client", "ID device = ", secondlidslave[id])  # Вывод опрашиваемого датчика
            print("PZEM Voltage:\t" + str(voltage) + "V")  # Значения(Вывод для отладки)
            print("PZEM Amperage:\t" + str(amperage) + "A")
            print("PZEM Power:\t" + str(power) + "W")
            time.sleep(2)                                                                              # Задержка,для протокола Modbus необходима 2-3 секунды между сообщениями иначе ошибка "Отстуствие ответа"(в симуляторе работает без нее,на прототипе нужна проверка)
        except Exception as error:                                                                     # Обработка исключения(В случае поломки преобразователя выводит ошибку со всех устройств:) 
            print("IP: 192.168.1.12 Port: 503")
            print("PZEM device:", "ID device", secondlidslave[id], "got problem")                 


    #SRNE '192.168.1.12', port=502
    faultCodes = [                      #Коды ошибок(Описание в даташите)SRNE ML4860
      "Charge MOS short circuit",     #0
      "Anti-reverse MOS short",       #1
      "PV panel reversely connected", #2
      "PV working point over voltage",#3
      "PV counter current",           #4
      "PV input side over-voltage",   #5
      "PV input side short circuit",  #6
      "PV input overpower",           #7
      "Ambient temp too high",        #8
      "Controller temp too high",     #9
      "Load over-power/current",      #10
      "Load short circuit",           #11
      "Battery undervoltage warning", #12
      "Battery overvoltage",          #13
      "Battery over-discharge"]		  #14 
    for id in range(len(thirdidslave)):                                                                         #Опрос контроллеров заряда
        try:
            thirdresult = Thethirdclient.read_holding_registers(256, 35, slave=thirdidslave[id])                # Снимаем регистры
            modeoffset = 0  # Проверка режима зарядки
            loadstatus = False
            if (thirdresult.registers[32] > 6):
                loadstatus = True
                modeoffset = 32768
                chargeMode = " "
            if (thirdresult.registers[32] == 0 + modeoffset):
                chargeMode = "OFF"
            elif (thirdresult.registers[32] == 1 + modeoffset):
                chargeMode = "Normal"
            elif (thirdresult.registers[32] == 2 + modeoffset):
                chargeMode = "MPPT"
            elif (thirdresult.registers[32] == 3 + modeoffset):
                chargeMode = "Equalizing"
            elif (thirdresult.registers[32] == 4 + modeoffset):
                chargeMode = "Boost"
            elif (thirdresult.registers[32] == 5 + modeoffset):
                chargeMode = "Floating mode"
            elif (thirdresult.registers[32] == 6 + modeoffset):
                chargeMode = "Current limiting"
            faults = "None"  # Проверка ошибок работы контроллера заряда
            faultID = thirdresult.registers[34]
            if (faultID != 0):
                faults = ""
                count = 0
                while (faultID != 0):
                    if (faultID >= pow(2, 15 - count)):
                        if (count > 0):
                            faults += '\n'
                        faults += '- ' + faultCodes[count - 1]
                        faultID -= pow(2, 15 - count)
                    count += 1

            # Динамическая информация контроллера
            BatteryCap = thirdresult.registers[0]  # Емкость аккумулятора
            BatteryVolt = round(thirdresult.registers[1] * 0.1, 2)  # Напряжение аккумулятора
            ChargingCurr = thirdresult.registers[2] * 0.01  # Ток зарядки
            ControllerTemp = getRealTemp(int(str.zfill(hex(thirdresult.registers[3])[2:4], 2), 16))                 # Температура контроллера
            BatteryTemp = getRealTemp(int(str.zfill(hex(thirdresult.registers[3])[4:6], 2), 16))                    # Температура аккумулятора
            LoadVolt = round(thirdresult.registers[4] * 0.1, 2)                                                     # Напряжение постоянного тока нагрузки
            LoadCurr = thirdresult.registers[5] * 0.01                                                              # Постоянный ток нагрузки
            LoadPower = thirdresult.registers[6]                                                                    # Мощность нагрузки постоянного тока

            # Информация о солнечных панелей
            SolPanelVolt = thirdresult.registers[7] * 0.1                                                           # Напряжение на солнечной панели
            SolPanelCurr = thirdresult.registers[8] * 0.01                                                          # Ток солнечной панели
            ChargingPower = thirdresult.registers[9]                                                                # Зарядная мощность

            # Информация об аккумуляторе(батареи)
            LoadCMD = thirdresult.registers[10]  # Команда включения/выключения зарядки
            BattMinVoltoftheCurrentDay = round(thirdresult.registers[11] * 0.1,2)                                   # Минимальное напряжение аккумулятора(батареи) за текущий день
            BattMaxVoltoftheCurrentDay = round(thirdresult.registers[12] * 0.1,2)                                   # Максимальное напряжение аккумулятора(батареи) за текущий день
            MaxChargingCurrentofCurrentDay = round(thirdresult.registers[13] * 0.01,2)                              # Максимальный зарядный ток текущего дня
            MaxDischargingCurrentofCurrentDay = thirdresult.registers[14] * 0.01                                    # Максимальный ток разряда текущего дня
            MaxChargingPowerofCurrentDay = thirdresult.registers[15]                                                # Максимальная зарядная мощность текущего дня
            MaxDischargingPowerofCurrentDay = thirdresult.registers[16]                                             # Максимальная мощность разряда текущего дня
            ChargingAmpofCurrentDay = thirdresult.registers[17]                                                     # Ампер-часы зарядки за текущий день
            DisChargingAmpofCurrentDay = thirdresult.registers[18]                                                  # Ампер-часы разрядки за текущий день
            PowerGenerationofCurrentDay = thirdresult.registers[19]                                                 # Выработка электроэнергии за день
            PowerConsumptionofCurrentDay = thirdresult.registers[20]                                                # Потребление энергии в течение дня

            # Данные за длительный период времени
            TotalWorkDays = thirdresult.registers[21]                                                               # Общее количество дней работы
            Numberofbatteryoverdischarges = thirdresult.registers[22]                                               # Общее количество разрядов аккумуляторов
            Numberofbatteryfullcharges = thirdresult.registers[23]                                                  # Общее количество зарядов аккумуляторов
            TotalchargingAmpHrs = (thirdresult.registers[24] * 65536 + thirdresult.registers[25])                     # Общее время зарядки аккумулятора в амперах-часах
            TotaldischargingAmpHrs = (thirdresult.registers[26] * 65536 + thirdresult.registers[27])                  # Общее время разрядки аккумуляторов в амперах-часах
            CumulPowerGener = (thirdresult.registers[28] * 65536 + thirdresult.registers[29])                         # Совокупная выработка электроэнергии
            CumulPowerConsumption = (thirdresult.registers[30] * 65536 + thirdresult.registers[31])                   # Совокупное энергопотребление

            print("The Third client", "ID device = ", ThirdNameSlave[id])  # Номер устройства
            # Динамическая информация контроллера(Вывод для отладки)
            print("------------- Real Time Data -------------")
            print("Charging Mode:\t\t\t" + str(chargeMode))
            print("Battery SOC:\t\t\t" + str(BatteryCap) + "%")
            print("Battery Voltage:\t\t" + str(BatteryVolt) + "V")
            print("Battery Charge Current:\t\t" + str(ChargingCurr) + "A")
            print("Controller Temperature:\t\t" + str(ControllerTemp) + "°C")
            print("Battery Temperature:\t\t" + str(BatteryTemp) + "°C")
            print("Load Voltage:\t\t\t" + str(LoadVolt) + " Volts")
            print("Load Current:\t\t\t" + str(LoadCurr) + " Amps")
            print("Load Power:\t\t\t" + str(LoadPower) + " Watts")

            # Информация о солнечных панелей(Вывод для отладки)
            print("Panel Volts:\t\t\t" + str(SolPanelVolt) + "V")
            print("Panel Amps:\t\t\t" + str(SolPanelCurr) + "A")
            print("Panel Power:\t\t\t" + str(ChargingPower) + "W")

            # Информация об аккумуляторе(батареи)(Вывод для отладки)
            print("--------------- DAILY DATA ---------------")
            print("Load Enabled:\t\t\t" + str(LoadCMD))
            print("Battery Minimum Voltage:\t" + str(BattMinVoltoftheCurrentDay) + "V")
            print("Battery Maximum Voltage:\t" + str(BattMaxVoltoftheCurrentDay) + "V")
            print("Maximum Charge Current:\t\t" + str(MaxChargingCurrentofCurrentDay) + "A")
            print("Maximum Charge Power:\t\t" + str(MaxChargingPowerofCurrentDay) + "W")
            print("Maximum Load Discharge Current:\t" + str(MaxDischargingCurrentofCurrentDay) + "A")
            print("Maximum Load Discharge Power:\t" + str(MaxDischargingPowerofCurrentDay) + "W")
            print("Charge Amp Hours:\t\t" + str(ChargingAmpofCurrentDay) + "Ah")
            print("Charge Power:\t\t\t" + str(PowerGenerationofCurrentDay) + "Wh")
            print("Load Amp Hours:\t\t\t" + str(DisChargingAmpofCurrentDay) + "Ah")
            print("Load Power:\t\t\t" + str(MaxDischargingPowerofCurrentDay) + "Wh")

            # Данные за длительный период времени(Вывод для отладки)
            print("-------------- GLOBAL DATA ---------------")
            print("Days Operational:\t\t" + str(TotalWorkDays) + " Days")
            print("Times Over Discharged:\t\t" + str(Numberofbatteryoverdischarges))
            print("Times Fully Charged:\t\t" + str(Numberofbatteryfullcharges))
            print("Cumulative Amp Hours:\t\t" + str(TotalchargingAmpHrs) + "Ah")
            print("Cumulative Power:\t\t" + str(CumulPowerGener) + "Wh")
            print("Load Amp Hours:\t\t\t" + str(TotaldischargingAmpHrs) + "Ah")
            print("Load Power:\t\t\t" + str(CumulPowerConsumption) + "Wh")
            print("------------------------------------------")

            # Вывод неисправностей(Вывод для отладки)
            print("--------------- FAULT DATA ---------------")
            print(faults)
            print("------------------------------------------")
            time.sleep(2)                                             # Задержка,для протокола Modbus необходима 2-3 секунды между сообщениями иначе ошибка "Отстуствие ответа"(в симуляторе работает без нее,на прототипе нужна проверка)
        except Exception as error:                                    # Обработка исключения(В случае поломки преобразователя выводит ошибку со всех устройств:) 
            print("IP: 192.168.1.12 Port:502")
            print("SRNE device:", "ID device", thirdidslave[id], "got problem")
