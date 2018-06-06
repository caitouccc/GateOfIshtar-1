from datetime import datetime

class UnSupportedTypeException(Exception): 
    pass

class Champion(object):

    def __init__(self, type, name=None):
        self.loglevel = 'debug'
        if name is None:
            self.name = type
        else:
            self.name = name
        self.type = type

        try:    
            if type == 'Human':
                hp = 100
            elif type == 'Wizard':
                hp = 100
            elif type == 'Spirit':
                hp = 100
            elif type == 'Giant':
                hp = 150
            elif type == 'Vampire':
                hp = 110
            else:
                raise UnSupportedTypeException("Not supported champion type!") 
            self.hp = hp
        
            '''
            mapping between hour and bit, to ensure only lose HP once every hour:
            bit  hight                                                       low
                 |23|22|21|20|19|18|17|16|15|14|13|12|11|10|9|8|7|6|5|4|3|2|1|0|
            hour |23|22|21|20|19|18|17|16|15|14|13|12|11|10|9|8|7|6|5|4|3|2|1|0|
                 |no guard   |guard at gate                        |no guard   |
            e.g. champion lose HP at 6:00-6:59, then it's set to:
                 |0 |0 |0 |0 |0 |0 |0 |0 |0 |0 |0 |0 |0 |0 |0|0|0|1|0|0|0|0|0|0|
            '''
            self.hour_bitmap = 0
            #print("name:",self.name,"|champion:",self.type,"|hour_bitmap:",self.hour_bitmap)
            self.log("name: "+self.name+"|champion: "+self.type+"|HP: "+str(self.hp)+"|hour_bitmap: "+str(self.hour_bitmap))
        except UnSupportedTypeException as e:
            #print(e)
            self.log(e)
            
    def __del__(self):
        self = None

    '''
    who is recording the timestamp when champing passing the gate in one day?
    normally the hp shall be updated in time, in case champion could be dead, need reborn?
    ''' 
    def calculate_champion_health(self, date_string_intervals):
        '''
        calculate amount of health remained when a champion
        at the end of a day
    
        @param champion - type of the champion (e.g. 'Wizard', 'Human')
        @param date_string_intervals - list of date intervals strings
            when a champion passing the gate (e.g. ['XXXX-XX-XX XX:XX'])
    
        '''
        champion = self.type
        total_damage = 0
        for i, date_string in enumerate(date_string_intervals):
            date = datetime.strptime(date_string, "%Y-%m-%d %H:%M")
            try:
                date_next = datetime.strptime(date_string_intervals[i+1], "%Y-%m-%d %H:%M")
            except IndexError:
                date_next = date
    
            next_damage = calculate_damage_taken(self, date)
    
            interval = (date_next - date).total_seconds()
    
            if (interval >= 3600 or i == len(date_string_intervals) -1):
                total_damage += next_damage
    
        return total_damage
    
    def holly_day(self, date):
        '''
        Tuesday, Thursday are holly day, no guards around the gate
        '''
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        dow = days[date.weekday()]
        if dow == 'Tuesday' or dow == 'Thursday':
            ret = True 
        else:
            ret = False
        return ret
    
    def hour_bitmap_set(self, hour, damage, guarder):
        if damage == 0:
            return

        hour_bitmap_value = 1 << hour
        if (self.hour_bitmap & hour_bitmap_value) == 0:
            self.hour_bitmap |= hour_bitmap_value

            if self.hp <= damage:
                damage = self.hp
                self.hp = 0
            else:
                self.hp -= damage

            self.log("lose HP("+str(damage)+") to Guarder "+guarder)
            self.log("name: "+self.name+"|champion: "+self.type+"|HP: "+str(self.hp)+"|hour_bitmp: "+str(self.hour_bitmap))
        else:
            #print("Champion can only lose HP once every hour.")
            #self.log("#info#Champion can only lose HP once every hour.")
            pass
    
    '''
    update champion's hp when he/she under attack 
    '''
    def calculate_damage_taken(self, date):
        #print("date:",date)
        self.log("enter guarder's attack range at "+str(date))

        if self.holly_day(date) or self.invincible_champion():
            guarder=""
            damage = 0
            return damage
        # "Janna" demon of Wind spawned
        if (date.hour == 6 and date.minute >= 0 and date.minute <= 29):
            guarder="Janna"
            damage = 7
        # "Tiamat" goddess of Oceans spawned
        elif (date.hour == 6 and date.minute >= 30 and date.minute <= 59):
            guarder="Tiamat"
            damage = 18
        # "Mithra" goddess of sun spawned
        elif (date.hour == 7 and date.minute >= 0 and date.minute <= 59):
            guarder="Mithra"
            damage = 25
        # "Warwick" God of war spawned
        elif (date.hour == 8 and date.minute >= 0 and date.minute <= 29):
            guarder="Warwick"
            damage = 18
        # "Kalista" demon of agony spawned
        elif (date.hour >= 8 and date.hour <= 14 and date.minute >= 30 and date.minute <= 59):
            guarder="Kalista"
            damage = 7
        # "Ahri" goddess of wisdom spawned
        elif (date.hour == 15 and date.minute >= 0 and date.minute <= 29):
            guarder="Ahri"
            damage = 13
        # "Brand" god of fire spawned
        elif (date.hour == 15 and date.minute >= 0 or date.hour == 16 and date.minute <= 59):
            guarder="Brand"
            damage = 25
        # "Rumble" god of lightning spawned
        elif (date.hour == 17 and date.minute >= 0 and date.minute <= 59):
            guarder="Rumble"
            damage = 18
        # "Skarner" the scorpion demon spawned
        elif (date.hour >= 18 and date.hour <= 19 and date.minute >= 0 and date.minute <= 59):
            guarder="Skarner"
            damage = 7
        # "Luna" The goddess of the moon spawned
        elif (date.hour == 20 and date.minute <=59):
            guarder="Luna"
            damage = 13
        else:
            guarder=""
            damage = 0
    
        self.hour_bitmap_set(date.hour,damage,guarder)
    
        #print("attemped damage:",damage,"|remain hp:",self.hp,"|hour_bitmap:",self.hour_bitmap)
        #self.log("attemped damage:"+str(damage)+" |remain hp:"+str(self.hp)+" |hour_bitmap:"+str(self.hour_bitmap))
        return damage
    
    def get_hp(self):
        return self.hp
    
    def newday(self):
        self.hour_bitmap = 0
    
    def invincible_champion(self):
        champion=self.type
        if champion == 'Wizard':
            ret = True
        if champion == 'Spirit':
            ret = True
        if champion == 'Human' or champion == 'Giant' or champion == 'Vampire':
            ret = False
        return ret

    def log(self,info):
        if self.loglevel == 'debug':
            print(info)
    
def main():

    print("======UC1======")
    champion1 = Champion('Human','caitou1')
    champion1.calculate_damage_taken(datetime.now())

    print("======UC2======")
    champion2 = Champion('Spirit','caitou2')
    T2 = datetime.strptime("2018-06-04 12:10", "%Y-%m-%d %H:%M")
    champion2.calculate_damage_taken(T2)

    print("======UC3======")
    champion3 = Champion('Giant','caitou3')
    T3 = datetime.strptime("2018-06-06 06:20", "%Y-%m-%d %H:%M")
    champion3.calculate_damage_taken(T3)
    T3 = datetime.strptime("2018-06-06 06:40", "%Y-%m-%d %H:%M")
    champion3.calculate_damage_taken(T3)
    T3 = datetime.strptime("2018-06-06 06:59", "%Y-%m-%d %H:%M")
    champion3.calculate_damage_taken(T3)

    print("======UC4======")
    champion4 = Champion('Vampire')
    T4 = datetime.strptime("2018-06-06 09:40", "%Y-%m-%d %H:%M")
    champion4.calculate_damage_taken(T4)

    print("======UC5======")
    champion5 = Champion('NotKnown','caitou5')
    #champion5.calculate_damage_taken(datetime.now())

    print("======UC6======")
    champion6 = Champion('Wizard','caitou6')
    T6 = datetime.strptime("2018-06-06 17:10", "%Y-%m-%d %H:%M")
    champion6.calculate_damage_taken(T6)
