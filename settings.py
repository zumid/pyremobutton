# coding: UTF-8

BUTTON = {
    '1':{
        'NAME':'BUS_BUTTON',   
        'MAC':'FF:FF:29:57:B5:94',
        'COMMAND':'/opt/ir/bin/bedroom_light.sh'
        #'COMMAND':'echo "`date` pushed" >>/tmp/test.txt'
    },
    '2':{
        'NAME':'WALL_BUTTON',
        'MAC':'FF:FF:54:61:0D:94',
        #'COMMAND':'echo "`date`pushed2" >>/tmp/test.txt'
        'COMMAND':'/opt/ir/bin/bedroom_light.sh'
    }
}
